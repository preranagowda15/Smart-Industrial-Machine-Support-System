from rest_framework import serializers
from .models import QuestionHistory, SourceReference

class SourceReferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SourceReference
        fields = [
            "id",
            "document_name",
            "revision",
            "pdf_page",
            "passage_text",
            "pdf_url",
        ]

class QuestionHistorySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)
    user_role = serializers.CharField(source="user.role", read_only=True)
    machine_code = serializers.CharField(source="machine.machine_code", read_only=True)
    machine_name = serializers.CharField(source="machine.machine_name", read_only=True)
    source_references = SourceReferenceSerializer(many=True, read_only=True)

    class Meta:
        model = QuestionHistory
        fields = [
            "id",
            "user",
            "username",
            "user_role",
            "machine",
            "machine_code",
            "machine_name",
            "question",
            "answer",
            "status",
            "timestamp",
            "retrieved_sources",
            "source_references",
        ]
        read_only_fields = ["id", "timestamp"]

