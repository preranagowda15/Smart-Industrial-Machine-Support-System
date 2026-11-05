from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Review
from .serializers import ReviewSerializer, ReviewCreateSerializer
from apps.inspections.models import Inspection
from apps.accounts.permissions import CanReviewInspection
from apps.accounts.models import User


class ReviewListCreateView(APIView):
    """
    GET  /api/inspections/{id}/reviews/ - List all reviews on this inspection
    POST /api/inspections/{id}/reviews/ - Append a review (Supervisor / Admin only)
    """
    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), CanReviewInspection()]
        return [permissions.IsAuthenticated()]

    def get(self, request, pk):
        inspection = get_object_or_404(Inspection, pk=pk)
        # Operators can only see reviews for their own inspection
        if request.user.role == User.Role.OPERATOR and inspection.user_id != request.user.id:
            raise PermissionDenied("You do not have permission to view reviews for other operators' inspections.")

        reviews = inspection.reviews.all().select_related('reviewer').order_by('created_at')
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        inspection = get_object_or_404(Inspection, pk=pk)
        serializer = ReviewCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        review = Review.objects.create(
            inspection=inspection,
            reviewer=request.user,
            decision=serializer.validated_data['decision'],
            comment=serializer.validated_data.get('comment', '')
        )

        return Response(ReviewSerializer(review).data, status=status.HTTP_201_CREATED)

