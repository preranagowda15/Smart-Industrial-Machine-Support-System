from rest_framework import serializers
from .models import Manual, DocumentChunk

class ManualSerializer(serializers.ModelSerializer):
    machine_code = serializers.CharField(source="machine.machine_code", read_only=True)
    machine_name = serializers.CharField(source="machine.machine_name", read_only=True)
    pdf_url = serializers.SerializerMethodField()
    chunk_count = serializers.IntegerField(source="chunks.count", read_only=True)

    class Meta:
        model = Manual
        fields = [
            "id",
            "machine",
            "machine_code",
            "machine_name",
            "document_name",
            "revision",
            "pdf_file",
            "pdf_url",
            "total_pages",
            "uploaded_by",
            "uploaded_at",
            "ingestion_status",
            "error_message",
            "chunk_count",
        ]
        read_only_fields = ["id", "uploaded_at", "total_pages", "ingestion_status", "error_message", "chunk_count"]

    def get_pdf_url(self, obj):
        if obj.pdf_file:
            return obj.pdf_file.url
        return None

class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = [
            "id",
            "machine",
            "manual",
            "chunk_text",
            "page_number",
            "chunk_index",
            "embedding_id",
            "created_at",
        ]
