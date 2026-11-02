from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction

from backend.apps.machines.models import Machine
from backend.apps.manuals.models import Manual
from backend.apps.history.models import QuestionHistory, SourceReference
from backend.apps.history.serializers import QuestionHistorySerializer
from backend.apps.accounts.permissions import role_of
from backend.services.rag_service import RAGService

class AskAssistantAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        role = role_of(request.user)
        # Supervisors have a dedicated read-only oversight role
        if role not in ("ENGINEER", "ADMIN"):
            return Response(
                {"detail": "Access restricted: Only Engineers (and Admins) can submit maintenance questions."},
                status=status.HTTP_403_FORBIDDEN
            )

        machine_param = request.data.get("machine_id") or request.data.get("machine")
        question = str(request.data.get("question", "")).strip()

        if not machine_param:
            return Response({"detail": "machine_id is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not question:
            return Response({"detail": "question is required."}, status=status.HTTP_400_BAD_REQUEST)
        if len(question) > 2000:
            return Response({"detail": "Question exceeds 2,000 characters limit."}, status=status.HTTP_400_BAD_REQUEST)

        # Lookup machine by code or pk
        try:
            if str(machine_param).isdigit():
                machine = Machine.objects.get(pk=int(machine_param), is_active=True)
            else:
                machine = Machine.objects.get(machine_code=str(machine_param), is_active=True)
        except Machine.DoesNotExist:
            return Response({"detail": f"Machine not found for: {machine_param}"}, status=status.HTTP_404_NOT_FOUND)

        # Initialize QuestionHistory record
        question_log = QuestionHistory.objects.create(
            user=request.user,
            machine=machine,
            question=question,
            status=QuestionHistory.Status.PROCESSING
        )

        try:
            rag_service = RAGService()
            rag_output = rag_service.ask(
                question=question,
                machine_code=machine.machine_code,
                machine_name=machine.machine_name
            )

            status_val = (
                QuestionHistory.Status.ANSWERED
                if rag_output["evidence_status"] == "ANSWERED"
                else QuestionHistory.Status.INSUFFICIENT_EVIDENCE
            )

            with transaction.atomic():
                question_log.answer = rag_output["answer"]
                question_log.status = status_val
                question_log.retrieved_sources = [
                    {
                        "document_id": c.get("document_id"),
                        "revision": c.get("revision"),
                        "pdf_page": c.get("pdf_page"),
                        "pdf_url": c.get("pdf_url"),
                    }
                    for c in rag_output.get("citations", [])
                ]
                question_log.save()

                # Persist verified source references
                for cit in rag_output.get("citations", []):
                    # Link to actual Manual record if exists
                    manual_match = Manual.objects.filter(
                        document_name=cit.get("document_id"),
                        machine=machine
                    ).first()

                    SourceReference.objects.create(
                        question_history=question_log,
                        manual=manual_match,
                        document_name=cit.get("document_name") or cit.get("document_id"),
                        revision=cit.get("revision", "1.0"),
                        pdf_page=cit.get("pdf_page", 1),
                        passage_text=cit.get("supporting_passage", ""),
                        pdf_url=cit.get("pdf_url", "")
                    )

            # Return serialized response
            serializer = QuestionHistorySerializer(question_log)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as exc:
            question_log.status = QuestionHistory.Status.ERROR
            question_log.answer = "An internal error occurred during RAG pipeline execution."
            question_log.save()
            return Response(
                {"detail": f"Assistant execution error: {exc}", "question_id": question_log.id},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

