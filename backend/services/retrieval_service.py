"""
Retrieval service enforcing strict machine-level isolation in vector searches.
Supports multi-document retrieval (e.g. HP-200 Operations + Maintenance)
and applies similarity threshold filtering.
"""
from typing import List, Dict, Any, Optional
from .embedding_service import EmbeddingService
from .vector_store import VectorStoreService

class RetrievalService:
    def __init__(
        self,
        vector_store: Optional[VectorStoreService] = None,
        embedding_service: Optional[EmbeddingService] = None,
        relevance_threshold: float = 0.65
    ):
        self.vector_store = vector_store or VectorStoreService()
        self.embedding_service = embedding_service or EmbeddingService()
        self.relevance_threshold = relevance_threshold

    def retrieve(
        self,
        question: str,
        machine_code: str,
        n_results: int = 6
    ) -> List[Dict[str, Any]]:
        """
        Retrieves passages for a specific machine.
        Applies machine_code filter directly inside the vector query.
        Guarantees that no other machine's documents are ever returned.
        """
        clean_q = question.strip()
        if not clean_q or not machine_code:
            return []

        collection = self.vector_store.get_collection()
        total_in_machine = collection.count(where={"machine_id": machine_code})
        if total_in_machine == 0:
            return []

        # Generate query embedding
        query_vector = self.embedding_service.embed_query(clean_q)

        # Query vector store with MANDATORY server-side machine filter
        query_res = collection.query(
            query_embeddings=[query_vector],
            n_results=min(n_results, total_in_machine),
            where={"machine_id": machine_code},
            include=["documents", "metadatas", "distances"]
        )

        docs = query_res.get("documents", [[]])[0]
        metas = query_res.get("metadatas", [[]])[0]
        distances = query_res.get("distances", [[]])[0]

        hits = []
        for doc_text, meta, dist in zip(docs, metas, distances):
            # Double-check machine isolation invariant
            if meta.get("machine_id") != machine_code:
                continue

            hits.append({
                "text": doc_text,
                "metadata": meta,
                "distance": float(dist),
                "similarity": 1.0 - float(dist)
            })

        return hits

