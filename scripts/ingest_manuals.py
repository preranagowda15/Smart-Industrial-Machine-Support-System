"""
Ingestion script for processing manuals from a ZIP file or directory.
Usage: python scripts/ingest_manuals.py [path_to_zip_or_dir]
"""
import os
import sys
import csv
import zipfile
import tempfile
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.config.settings")

import django
django.setup()

from django.core.files import File
from backend.apps.accounts.models import User
from backend.apps.machines.models import Machine
from backend.apps.manuals.models import Manual, DocumentChunk
from backend.services.pdf_processor import PDFProcessor
from backend.services.chunking_service import ChunkingService
from backend.services.embedding_service import EmbeddingService
from backend.services.vector_store import VectorStoreService

def ingest(source_path: Path):
    admin_user = User.objects.filter(role=User.Role.ADMIN).first()
    if not admin_user:
        admin_user = User.objects.create_superuser("admin_system", "admin@local.host", "AdminPass123!")

    chunker = ChunkingService(chunk_size=850, overlap=120)
    embedder = EmbeddingService()
    vector_store = VectorStoreService()
    collection = vector_store.get_collection()

    temp_dir_obj = None
    if source_path.is_file() and source_path.suffix.lower() == ".zip":
        temp_dir_obj = tempfile.TemporaryDirectory()
        with zipfile.ZipFile(source_path) as z:
            z.extractall(temp_dir_obj.name)
        base = Path(temp_dir_obj.name)
    else:
        base = source_path

    csv_file = base / "machine_manual_index.csv"
    if not csv_file.exists():
        csv_file = base / "data" / "machine_manual_index.csv"

    if not csv_file.exists():
        print(f"Error: machine_manual_index.csv not found in {base}")
        return

    count = 0
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            m_code = row["machine_id"]
            model = row["model"]
            m_name = row["machine_name"]
            doc_id = row["document_id"]
            rev = row["revision"]
            pdf_name = row["pdf_filename"]

            machine, _ = Machine.objects.get_or_create(
                machine_code=m_code,
                defaults={"machine_name": m_name, "manufacturer": "Apex Machining Systems", "is_active": True}
            )

            # Locate PDF
            pdf_path = base / "Manuals" / pdf_name
            if not pdf_path.exists():
                pdf_path = base / "data" / "Manuals" / pdf_name
            if not pdf_path.exists():
                pdf_path = BASE_DIR / "data" / "Manuals" / pdf_name

            if not pdf_path.exists():
                print(f"Warning: Manual file {pdf_name} not found.")
                continue

            manual, _ = Manual.objects.get_or_create(
                document_name=doc_id,
                defaults={"machine": machine, "revision": rev, "uploaded_by": admin_user}
            )
            with open(pdf_path, "rb") as fh:
                manual.pdf_file.save(pdf_name, File(fh), save=False)
            manual.save()

            pages = PDFProcessor.extract_pages(manual.pdf_file.path)
            manual.total_pages = len(pages)

            chunks = chunker.process_pages(
                pages=pages,
                machine_code=m_code,
                document_name=doc_id,
                revision=rev,
                manual_id=manual.id,
                filename=pdf_name
            )

            manual.chunks.all().delete()
            db_chunks = [
                DocumentChunk(
                    machine=machine,
                    manual=manual,
                    chunk_text=c["chunk_text"],
                    page_number=c["page_number"],
                    chunk_index=c["chunk_index"],
                    embedding_id=c["embedding_id"]
                )
                for c in chunks
            ]
            DocumentChunk.objects.bulk_create(db_chunks)

            collection.delete(where={"document_id": doc_id})
            docs = [c["chunk_text"] for c in chunks]
            ids = [c["embedding_id"] for c in chunks]
            metas = [
                {
                    "machine_id": m_code,
                    "document_id": doc_id,
                    "revision": rev,
                    "page_number": c["page_number"],
                    "manual_id": manual.id,
                    "filename": pdf_name,
                }
                for c in chunks
            ]
            vectors = embedder.embed_texts(docs)
            collection.upsert(ids=ids, documents=docs, metadatas=metas, embeddings=vectors)

            manual.ingestion_status = Manual.IngestionStatus.COMPLETED
            manual.save()
            print(f"Indexed {doc_id}: {len(chunks)} passages across {len(pages)} pages.")
            count += 1

    if temp_dir_obj:
        temp_dir_obj.cleanup()

    print(f"Ingestion complete: {count} manuals processed.")

if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else (BASE_DIR / "data")
    ingest(target)

