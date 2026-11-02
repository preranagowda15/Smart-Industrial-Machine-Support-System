import os
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

from .models import Manual, DocumentChunk
from .serializers import ManualSerializer, DocumentChunkSerializer
from backend.apps.machines.models import Machine
from backend.apps.accounts.permissions import IsAdministrator
from backend.services.pdf_processor import PDFProcessor
from backend.services.chunking_service import ChunkingService
from backend.services.embedding_service import EmbeddingService
from backend.services.vector_store import VectorStoreService

class ManualListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        machine_code = request.query_params.get("machine_code")
        qs = Manual.objects.all().select_related("machine")
        if machine_code:
            qs = qs.filter(machine__machine_code=machine_code)
        return Response(ManualSerializer(qs, many=True).data)

class ManualDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        manual = get_object_or_404(Manual.objects.select_related("machine"), pk=pk)
        return Response(ManualSerializer(manual).data)

class ManualStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        manual = get_object_or_404(Manual, pk=pk)
        return Response({
            "id": manual.id,
            "document_name": manual.document_name,
            "ingestion_status": manual.ingestion_status,
            "total_pages": manual.total_pages,
            "chunk_count": manual.chunks.count(),
            "error_message": manual.error_message,
        })

class ManualUploadAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdministrator]

    def post(self, request):
        machine_id = request.data.get("machine_id") or request.data.get("machine")
        document_name = str(request.data.get("document_name", "")).strip()
        revision = str(request.data.get("revision", "1.0")).strip()
        pdf_file = request.FILES.get("pdf_file") or request.FILES.get("pdf")

        if not machine_id:
            return Response({"detail": "machine_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not document_name:
            return Response({"detail": "document_name is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not pdf_file:
            return Response({"detail": "pdf_file is required."}, status=status.HTTP_400_BAD_REQUEST)

        # File validation
        filename = pdf_file.name.lower()
        if not filename.endswith(".pdf"):
            return Response({"detail": "Only PDF files are accepted."}, status=status.HTTP_400_BAD_REQUEST)
        if pdf_file.size > 25 * 1024 * 1024:
            return Response({"detail": "File size exceeds 25 MB limit."}, status=status.HTTP_400_BAD_REQUEST)

        # Resolve machine by pk or machine_code
        try:
            if str(machine_id).isdigit():
                machine = Machine.objects.get(pk=int(machine_id))
            else:
                machine = Machine.objects.get(machine_code=str(machine_id))
        except Machine.DoesNotExist:
            return Response({"detail": f"Machine not found for ID: {machine_id}"}, status=status.HTTP_404_NOT_FOUND)

        # Create or update manual record
        manual, created = Manual.objects.get_or_create(
            document_name=document_name,
            defaults={
                "machine": machine,
                "revision": revision,
                "pdf_file": pdf_file,
                "uploaded_by": request.user,
                "ingestion_status": Manual.IngestionStatus.PROCESSING,
            }
        )

        if not created:
            manual.machine = machine
            manual.revision = revision
            manual.pdf_file = pdf_file
            manual.uploaded_by = request.user
            manual.ingestion_status = Manual.IngestionStatus.PROCESSING
            manual.error_message = ""
            manual.save()

        # Ingestion Pipeline
        try:
            pdf_path = manual.pdf_file.path
            pages = PDFProcessor.extract_pages(pdf_path)
            if not pages:
                raise ValueError("No extractable pages found in the uploaded PDF.")

            chunker = ChunkingService(chunk_size=850, overlap=120)
            chunks = chunker.process_pages(
                pages=pages,
                machine_code=machine.machine_code,
                document_name=manual.document_name,
                revision=manual.revision,
                manual_id=manual.id,
                filename=os.path.basename(manual.pdf_file.name)
            )

            # Idempotent DB update: clear previous chunks for this manual
            with transaction.atomic():
                manual.chunks.all().delete()
                db_chunk_objs = [
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
                DocumentChunk.objects.bulk_create(db_chunk_objs)

            # Vector Store Ingestion
            vector_store = VectorStoreService()
            collection = vector_store.get_collection()
            # Clear old vectors for this document
            collection.delete(where={"document_id": manual.document_name})

            embedder = EmbeddingService()
            docs = [c["chunk_text"] for c in chunks]
            ids = [c["embedding_id"] for c in chunks]
            metas = [
                {
                    "machine_id": machine.machine_code,
                    "document_id": manual.document_name,
                    "revision": manual.revision,
                    "page_number": c["page_number"],
                    "manual_id": manual.id,
                    "filename": os.path.basename(manual.pdf_file.name),
                }
                for c in chunks
            ]
            embeddings = embedder.embed_texts(docs)
            collection.upsert(ids=ids, documents=docs, metadatas=metas, embeddings=embeddings)

            # Mark COMPLETED
            manual.total_pages = len(pages)
            manual.ingestion_status = Manual.IngestionStatus.COMPLETED
            manual.error_message = ""
            manual.save()

            return Response({
                "message": "Manual successfully uploaded and indexed.",
                "manual": ManualSerializer(manual).data,
                "total_pages": len(pages),
                "chunks_indexed": len(chunks),
            }, status=status.HTTP_201_CREATED)

        except Exception as exc:
            manual.ingestion_status = Manual.IngestionStatus.FAILED
            manual.error_message = str(exc)
            manual.save()
            return Response({
                "detail": f"Manual ingestion failed: {exc}",
                "ingestion_status": "FAILED"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
