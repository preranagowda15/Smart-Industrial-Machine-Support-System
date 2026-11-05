from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import QuestionHistory
from .serializers import QuestionHistorySerializer
from apps.accounts.permissions import role_of

class QuestionHistoryListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = role_of(request.user)
        machine_code = request.query_params.get("machine_code")
        status_filter = request.query_params.get("status")

        # Engineers see only their own history; Supervisors and Admins see team history
        if role == "ENGINEER":
            qs = QuestionHistory.objects.filter(user=request.user)
        else:
            qs = QuestionHistory.objects.all()

        if machine_code:
            qs = qs.filter(machine__machine_code=machine_code)
        if status_filter:
            qs = qs.filter(status=status_filter)

        qs = qs.select_related("user", "machine").prefetch_related("source_references")[:150]
        serializer = QuestionHistorySerializer(qs, many=True)
        return Response(serializer.data)

class QuestionHistoryDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        role = role_of(request.user)
        qs = QuestionHistory.objects.select_related("user", "machine").prefetch_related("source_references")
        
        if role == "ENGINEER":
            history_item = get_object_or_404(qs, pk=pk, user=request.user)
        else:
            history_item = get_object_or_404(qs, pk=pk)

        return Response(QuestionHistorySerializer(history_item).data)

