import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from backend.services.vector_store import VectorStoreService
from backend.services.embedding_service import EmbeddingService
from backend.services.retrieval_service import RetrievalService

vs = VectorStoreService()
emb = EmbeddingService()
ret = RetrievalService(vs, emb)

queries = [
    "What does E17 mean?",
    "What observations should be collected for repeated low hydraulic pressure?",
    "What is the maximum operating pressure?",
    "How often do I replace the hydraulic oil filter?",
    "What is the AC-90 rated discharge pressure?",
    "How do I program the CNC lathe and what is the salary of the operator?"
]

for q in queries:
    hits = ret.retrieve(q, "M-HP200")
    if hits:
        top = hits[0]
        meta = top["metadata"]
        print(f"Query: {q[:45]:<45} -> Top hit sim: {top['similarity']:.4f} | doc: {meta['document_id']} p.{meta['page_number']}")
