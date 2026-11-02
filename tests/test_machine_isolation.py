import tempfile
from pathlib import Path
from django.test import TestCase
from rest_framework.test import APIClient

from backend.apps.accounts.models import User
from backend.apps.machines.models import Machine
from backend.services.embedding_service import EmbeddingService
from backend.services.vector_store import VectorStoreService, VectorCollection
from backend.services.retrieval_service import RetrievalService

class MachineIsolationTests(TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = Path(self.temp_dir.name) / "test_vectors.db"
        self.collection = VectorCollection(self.db_path, "test_manual_passages")
        
        # Patch vector store to use temporary test collection
        self.vector_store = VectorStoreService(vector_dir=self.temp_dir.name)
        self.vector_store._collection = self.collection
        self.embedder = EmbeddingService()
        self.retriever = RetrievalService(vector_store=self.vector_store, embedding_service=self.embedder)

        # Ingest distinct chunks for M-HP200 and M-AC90
        hp_docs = [
            "HP-200 maximum operating pressure is 250 bar. Never exceed 250 bar under any load.",
            "Alarm E17 indicates Main Ram Proportional Valve Command Signal Failure on HP-200 press.",
            "Inspect guide columns and grease weekly with NLGI Grade 2 lithium grease on HP-200."
        ]
        hp_ids = ["hp_chunk_1", "hp_chunk_2", "hp_chunk_3"]
        hp_metas = [
            {"machine_id": "M-HP200", "document_id": "HP-OPS-01", "revision": "1.0", "page_number": 1},
            {"machine_id": "M-HP200", "document_id": "HP-OPS-01", "revision": "1.0", "page_number": 2},
            {"machine_id": "M-HP200", "document_id": "HP-MNT-01", "revision": "1.0", "page_number": 1},
        ]
        hp_vecs = self.embedder.embed_texts(hp_docs)
        self.collection.upsert(ids=hp_ids, documents=hp_docs, metadatas=hp_metas, embeddings=hp_vecs)

        ac_docs = [
            "AC-90 rated discharge pressure is 8.0 bar. Certified safety relief valve opens at 10.0 bar.",
            "Alarm H03 indicates high discharge air temperature exceeding 105 degrees on AC-90.",
            "Replace AC-90 air intake filter cartridge every 2000 operating hours."
        ]
        ac_ids = ["ac_chunk_1", "ac_chunk_2", "ac_chunk_3"]
        ac_metas = [
            {"machine_id": "M-AC90", "document_id": "AC-OM-01", "revision": "1.0", "page_number": 1},
            {"machine_id": "M-AC90", "document_id": "AC-OM-01", "revision": "1.0", "page_number": 2},
            {"machine_id": "M-AC90", "document_id": "AC-OM-01", "revision": "1.0", "page_number": 3},
        ]
        ac_vecs = self.embedder.embed_texts(ac_docs)
        self.collection.upsert(ids=ac_ids, documents=ac_docs, metadatas=ac_metas, embeddings=ac_vecs)

    def tearDown(self):
        try:
            self.temp_dir.cleanup()
        except Exception:
            pass

    def test_mandatory_2_machine_retrieval_isolation(self):
        """
        MANDATORY TEST 2: MACHINE RETRIEVAL ISOLATION
        - Create chunks for M-HP200.
        - Create chunks for M-AC90.
        - Search using selected machine M-HP200.
        - Verify that no M-AC90 chunks are returned.
        - Search using selected machine M-AC90.
        - Verify that no M-HP200 chunks are returned.
        """
        # Query HP-200 with an AC-90 specific term (e.g. 8.0 bar discharge pressure / H03)
        hp_hits = self.retriever.retrieve(
            question="What is the 8.0 bar rated discharge pressure and H03 alarm?",
            machine_code="M-HP200"
        )
        self.assertTrue(len(hp_hits) > 0, "HP-200 query should return hits from HP-200 collection")
        for hit in hp_hits:
            machine_id = hit["metadata"].get("machine_id")
            self.assertEqual(
                machine_id, "M-HP200",
                f"Isolation violation! Expected M-HP200, got {machine_id}"
            )
            self.assertNotIn("AC-90", hit["text"])
            self.assertNotEqual(hit["metadata"].get("document_id"), "AC-OM-01")

        # Query AC-90 with an HP-200 specific term (e.g. 250 bar pressure / E17)
        ac_hits = self.retriever.retrieve(
            question="What is the 250 bar operating pressure limit and E17 valve fault?",
            machine_code="M-AC90"
        )
        self.assertTrue(len(ac_hits) > 0, "AC-90 query should return hits from AC-90 collection")
        for hit in ac_hits:
            machine_id = hit["metadata"].get("machine_id")
            self.assertEqual(
                machine_id, "M-AC90",
                f"Isolation violation! Expected M-AC90, got {machine_id}"
            )
            self.assertNotIn("HP-200", hit["text"])
            self.assertNotEqual(hit["metadata"].get("document_id"), "HP-OPS-01")
            self.assertNotEqual(hit["metadata"].get("document_id"), "HP-MNT-01")

    def test_multi_document_retrieval_for_hp200(self):
        """Verifies that retrieval for M-HP200 can pull passages from both HP-OPS-01 and HP-MNT-01."""
        hits = self.retriever.retrieve(
            question="Operating limits pressure and guide column grease inspection",
            machine_code="M-HP200",
            n_results=6
        )
        doc_ids = {h["metadata"]["document_id"] for h in hits}
        self.assertIn("HP-OPS-01", doc_ids)
        self.assertIn("HP-MNT-01", doc_ids)
