"""
Seed script: creates demo users, registers machines from machine_manual_index.csv,
and ingests/indexes the 3 official PDF manuals.
"""
import os
import sys
import csv
from pathlib import Path

# Add project root to sys.path
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

def create_demo_users():
    print("--- Creating Demo Users ---")
    users_data = [
        ("admin_demo", "admin@manufacturing.local", "AdminDemo!2026", User.Role.ADMIN, True, True),
        ("engineer_demo", "engineer@manufacturing.local", "EngineerDemo!2026", User.Role.ENGINEER, False, False),
        ("supervisor_demo", "supervisor@manufacturing.local", "SupervisorDemo!2026", User.Role.SUPERVISOR, False, False),
    ]

    created_users = {}
    for username, email, pwd, role, is_staff, is_super in users_data:
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                "email": email,
                "role": role,
                "is_staff": is_staff,
                "is_superuser": is_super,
            }
        )
        user.set_password(pwd)
        user.role = role
        user.is_staff = is_staff
        user.is_superuser = is_super
        user.save()
        created_users[role] = user
        action = "Created" if created else "Updated"
        print(f"[{action}] User: {username} | Role: {role} | Password: {pwd}")

    return created_users

def ingest_manuals_from_csv(admin_user):
    print("\n--- Registering Machines and Ingesting Manuals from CSV ---")
    csv_path = BASE_DIR / "data" / "machine_manual_index.csv"
    if not csv_path.exists():
        raise FileNotFoundError(f"Index CSV not found at {csv_path}")

    chunker = ChunkingService(chunk_size=850, overlap=120)
    embedder = EmbeddingService()
    vector_store = VectorStoreService()
    collection = vector_store.get_collection()

    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            machine_code = row["machine_id"]
            model = row["model"]
            machine_name = row["machine_name"]
            doc_id = row["document_id"]
            rev = row["revision"]
            pdf_filename = row["pdf_filename"]

            # 1. Register or update Machine
            machine, m_created = Machine.objects.get_or_create(
                machine_code=machine_code,
                defaults={
                    "machine_name": machine_name,
                    "manufacturer": "Apex Machining Systems",
                    "description": f"{model} industrial unit.",
                    "is_active": True,
                }
            )
            if not m_created:
                machine.machine_name = machine_name
                machine.save()
            print(f"Machine: {machine.machine_code} ({machine.machine_name})")

            # 2. Locate PDF
            pdf_source_path = BASE_DIR / "data" / "Manuals" / pdf_filename
            if not pdf_source_path.exists():
                print(f"Warning: PDF file {pdf_source_path} not found, skipping ingestion.")
                continue

            # 3. Create or update Manual record
            manual, man_created = Manual.objects.get_or_create(
                document_name=doc_id,
                defaults={
                    "machine": machine,
                    "revision": rev,
                    "uploaded_by": admin_user,
                    "ingestion_status": Manual.IngestionStatus.PROCESSING,
                }
            )
            manual.machine = machine
            manual.revision = rev
            manual.uploaded_by = admin_user
            manual.ingestion_status = Manual.IngestionStatus.PROCESSING

            with open(pdf_source_path, "rb") as pdf_fh:
                manual.pdf_file.save(pdf_filename, File(pdf_fh), save=False)
            manual.save()

            # 4. Extract pages with PyMuPDF
            pages = PDFProcessor.extract_pages(manual.pdf_file.path)
            manual.total_pages = len(pages)

            # 5. Chunk pages
            chunks = chunker.process_pages(
                pages=pages,
                machine_code=machine.machine_code,
                document_name=doc_id,
                revision=rev,
                manual_id=manual.id,
                filename=pdf_filename
            )

            # 6. Idempotently update DocumentChunk records
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

            # 7. Update Vector Store
            collection.delete(where={"document_id": doc_id})
            docs = [c["chunk_text"] for c in chunks]
            ids = [c["embedding_id"] for c in chunks]
            metas = [
                {
                    "machine_id": machine.machine_code,
                    "document_id": doc_id,
                    "revision": rev,
                    "page_number": c["page_number"],
                    "manual_id": manual.id,
                    "filename": pdf_filename,
                }
                for c in chunks
            ]
            vectors = embedder.embed_texts(docs)
            collection.upsert(ids=ids, documents=docs, metadatas=metas, embeddings=vectors)

            manual.ingestion_status = Manual.IngestionStatus.COMPLETED
            manual.error_message = ""
            manual.save()
            print(f"  -> Ingested {doc_id} Rev {rev}: {len(pages)} pages, {len(chunks)} chunks indexed in vector store.")

    print(f"\nVector Store collection count: {collection.count()} passages.")

def main():
    users = create_demo_users()
    admin_user = users.get(User.Role.ADMIN)
    ingest_manuals_from_csv(admin_user)
    print("\n=== SEED DATA COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    main()
