"""
Smoke test for standalone services:
PDFProcessor -> ChunkingService -> EmbeddingService -> VectorStoreService -> RetrievalService -> RAGService
"""
import os
import sys
from pathlib import Path

# Add project root to sys.path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from backend.services.pdf_processor import PDFProcessor
from backend.services.chunking_service import ChunkingService
from backend.services.embedding_service import EmbeddingService
from backend.services.vector_store import VectorStoreService
from backend.services.retrieval_service import RetrievalService
from backend.services.rag_service import RAGService, INSUFFICIENT_EVIDENCE_TEXT

def test_full_pipeline():
    print("--- 1. Initializing Services ---")
    chunker = ChunkingService(chunk_size=800, overlap=100)
    embedder = EmbeddingService()
    vector_store = VectorStoreService()
    collection = vector_store.get_collection()

    manuals = [
        ("M-HP200", "HP-OPS-01", "1.0", "data/Manuals/HP200_Operations_Rev1_0.pdf", "HP200_Operations_Rev1_0.pdf"),
        ("M-HP200", "HP-MNT-01", "1.0", "data/Manuals/HP200_Maintenance_Rev1_0.pdf", "HP200_Maintenance_Rev1_0.pdf"),
        ("M-AC90", "AC-OM-01", "1.0", "data/Manuals/AC90_Operations_Maintenance_Rev1_0.pdf", "AC90_Operations_Maintenance_Rev1_0.pdf"),
    ]

    total_chunks = 0
    for machine_code, doc_id, rev, pdf_path, fname in manuals:
        pages = PDFProcessor.extract_pages(pdf_path)
        chunks = chunker.process_pages(
            pages=pages,
            machine_code=machine_code,
            document_name=doc_id,
            revision=rev,
            filename=fname
        )
        total_chunks += len(chunks)
        print(f"Processed {doc_id}: {len(pages)} pages -> {len(chunks)} chunks")

        # Upsert into vector collection
        ids = [c["embedding_id"] for c in chunks]
        docs = [c["chunk_text"] for c in chunks]
        metas = [
            {
                "machine_id": c["machine_code"],
                "document_id": c["document_name"],
                "revision": c["revision"],
                "page_number": c["page_number"],
                "filename": c["filename"],
            }
            for c in chunks
        ]
        vectors = embedder.embed_texts(docs)
        collection.upsert(ids=ids, documents=docs, metadatas=metas, embeddings=vectors)

    print(f"Total passages in collection: {collection.count()}")
    assert collection.count() == total_chunks, "Passage count mismatch"

    retriever = RetrievalService(vector_store=vector_store, embedding_service=embedder)
    rag = RAGService(retrieval_service=retriever)

    print("\n--- 2. Scenario 1: Supported Question (E17) on HP-200 ---")
    res1 = rag.ask("What does E17 mean?", machine_code="M-HP200", machine_name="HP-200")
    print("Status:", res1["evidence_status"])
    print("Answer:", res1["answer"][:120], "...")
    print("Citations:", [(c["document_id"], c["pdf_page"], c["pdf_url"]) for c in res1["citations"]])
    assert res1["evidence_status"] == "ANSWERED"
    assert any("E17" in c["supporting_passage"] for c in res1["citations"])
    assert res1["citations"][0]["pdf_page"] == 2
    assert res1["citations"][0]["document_id"] == "HP-OPS-01"

    print("\n--- 3. Scenario 2: Multi-Document Question on HP-200 ---")
    res2 = rag.ask(
        "What should be inspected during maintenance, and what operating limits should be checked?",
        machine_code="M-HP200",
        machine_name="HP-200"
    )
    print("Status:", res2["evidence_status"])
    print("Answer:", res2["answer"][:120], "...")
    docs_cited = {c["document_id"] for c in res2["citations"]}
    print("Documents cited:", docs_cited)
    assert res2["evidence_status"] == "ANSWERED"
    assert len(docs_cited) == 2, f"Expected 2 documents cited, got {docs_cited}"
    assert "HP-OPS-01" in docs_cited and "HP-MNT-01" in docs_cited

    print("\n--- 4. Scenario 3: Machine Isolation (AC-90 question on HP-200) ---")
    res3 = rag.ask("What is the AC-90 rated discharge pressure?", machine_code="M-HP200", machine_name="HP-200")
    print("Status:", res3["evidence_status"])
    print("Answer:", res3["answer"])
    assert res3["evidence_status"] == "INSUFFICIENT_EVIDENCE"
    assert res3["answer"] == INSUFFICIENT_EVIDENCE_TEXT

    print("\n--- 5. Scenario 4: Unsupported Question (Pump price / CNC lathe) ---")
    res4 = rag.ask("What is the pump replacement price from the supplier?", machine_code="M-HP200", machine_name="HP-200")
    print("Status:", res4["evidence_status"])
    print("Answer:", res4["answer"])
    assert res4["evidence_status"] == "INSUFFICIENT_EVIDENCE"
    assert res4["answer"] == INSUFFICIENT_EVIDENCE_TEXT

    print("\n=== ALL STANDALONE SERVICE CHECKS PASSED ===")

if __name__ == "__main__":
    test_full_pipeline()
