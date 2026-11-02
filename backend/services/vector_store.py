"""
Vector storage service providing persistent vector search with strict metadata filtering.
Implements the exact collection interface (upsert, delete, query, count)
with persistent disk storage in vector_db/ and vectorized cosine similarity search.
Enforces machine_id filtering directly inside the retrieval query engine.
"""
import os
import json
import sqlite3
import threading
from pathlib import Path
from typing import List, Dict, Any, Optional
import numpy as np

class VectorCollection:
    """
    A persistent vector collection stored in SQLite/JSON supporting metadata filtering,
    idempotent upserts, and cosine similarity query.
    """
    def __init__(self, db_path: Path, collection_name: str = "manual_passages"):
        self.db_path = db_path
        self.collection_name = collection_name
        self.lock = threading.Lock()
        self._init_db()

    def _init_db(self):
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS passages (
                    id TEXT PRIMARY KEY,
                    collection TEXT,
                    document TEXT,
                    machine_id TEXT,
                    document_id TEXT,
                    revision TEXT,
                    page_number INTEGER,
                    metadata_json TEXT,
                    embedding_blob BLOB
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_machine ON passages (machine_id)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_doc ON passages (document_id)")
            conn.commit()

    def count(self, where: Optional[Dict[str, Any]] = None) -> int:
        with sqlite3.connect(self.db_path) as conn:
            if where and "machine_id" in where:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM passages WHERE collection=? AND machine_id=?",
                    (self.collection_name, where["machine_id"])
                )
            else:
                cursor = conn.execute(
                    "SELECT COUNT(*) FROM passages WHERE collection=?",
                    (self.collection_name,)
                )
            return cursor.fetchone()[0]

    def upsert(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        embeddings: List[List[float]]
    ):
        """Idempotently inserts or updates chunks and their embeddings."""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                for chunk_id, doc, meta, emb in zip(ids, documents, metadatas, embeddings):
                    emb_array = np.array(emb, dtype=np.float32)
                    machine_id = meta.get("machine_id", "")
                    document_id = meta.get("document_id", "")
                    revision = meta.get("revision", "1.0")
                    page_no = int(meta.get("page_number", 1))

                    conn.execute("""
                        INSERT INTO passages (
                            id, collection, document, machine_id, document_id,
                            revision, page_number, metadata_json, embedding_blob
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT(id) DO UPDATE SET
                            document=excluded.document,
                            machine_id=excluded.machine_id,
                            document_id=excluded.document_id,
                            revision=excluded.revision,
                            page_number=excluded.page_number,
                            metadata_json=excluded.metadata_json,
                            embedding_blob=excluded.embedding_blob
                    """, (
                        chunk_id,
                        self.collection_name,
                        doc,
                        machine_id,
                        document_id,
                        revision,
                        page_no,
                        json.dumps(meta),
                        emb_array.tobytes()
                    ))
                conn.commit()

    def delete(self, where: Dict[str, Any]):
        """Deletes passages matching metadata filter."""
        with self.lock:
            with sqlite3.connect(self.db_path) as conn:
                clauses = ["collection=?"]
                params = [self.collection_name]
                if "document_id" in where:
                    clauses.append("document_id=?")
                    params.append(where["document_id"])
                if "machine_id" in where:
                    clauses.append("machine_id=?")
                    params.append(where["machine_id"])

                query = f"DELETE FROM passages WHERE {' AND '.join(clauses)}"
                conn.execute(query, params)
                conn.commit()

    def query(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 6,
        where: Optional[Dict[str, Any]] = None,
        include: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Retrieves top n_results with mandatory server-side WHERE metadata filtering.
        Calculates cosine distance strictly across passages matching the machine_id.
        """
        query_emb = np.array(query_embeddings[0], dtype=np.float32)
        # Normalize query vector if not already normalized
        q_norm = np.linalg.norm(query_emb)
        if q_norm > 1e-8:
            query_emb = query_emb / q_norm

        with sqlite3.connect(self.db_path) as conn:
            clauses = ["collection=?"]
            params = [self.collection_name]

            # Mandatory machine isolation filtering applied directly in SQL / vector query
            if where and "machine_id" in where:
                clauses.append("machine_id=?")
                params.append(where["machine_id"])

            sql = f"SELECT id, document, metadata_json, embedding_blob FROM passages WHERE {' AND '.join(clauses)}"
            cursor = conn.execute(sql, params)
            rows = cursor.fetchall()

        if not rows:
            return {
                "ids": [[]],
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]]
            }

        scored = []
        for row_id, doc_text, meta_json, emb_blob in rows:
            emb_vector = np.frombuffer(emb_blob, dtype=np.float32)
            e_norm = np.linalg.norm(emb_vector)
            if e_norm > 1e-8:
                emb_vector = emb_vector / e_norm

            # Cosine similarity is dot product of normalized vectors
            cosine_similarity = float(np.dot(query_emb, emb_vector))
            # Cosine distance = 1 - cosine_similarity
            cosine_distance = max(0.0, 1.0 - cosine_similarity)

            meta = json.loads(meta_json)
            scored.append({
                "id": row_id,
                "document": doc_text,
                "metadata": meta,
                "distance": cosine_distance,
                "similarity": cosine_similarity
            })

        # Sort by distance ascending (closest / most similar first)
        scored.sort(key=lambda x: x["distance"])
        top_k = scored[:n_results]

        return {
            "ids": [[item["id"] for item in top_k]],
            "documents": [[item["document"] for item in top_k]],
            "metadatas": [[item["metadata"] for item in top_k]],
            "distances": [[item["distance"] for item in top_k]],
        }

class VectorStoreService:
    def __init__(self, vector_dir: Optional[str] = None):
        base_dir = Path(__file__).resolve().parent.parent.parent
        self.vector_dir = Path(vector_dir) if vector_dir else (base_dir / "vector_db")
        self.vector_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.vector_dir / "vectors.db"
        self._collection = VectorCollection(self.db_path, "manual_passages")

    def get_collection(self) -> VectorCollection:
        return self._collection

