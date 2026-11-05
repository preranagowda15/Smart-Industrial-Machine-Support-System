import os
from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, NotFound
from django.shortcuts import get_object_or_404
from .models import Inspection
from .serializers import InspectionSerializer, InspectionUploadSerializer
from apps.accounts.models import User
from services.model_service import predict_plate
from services.image_validator import validate_image_file, ImageValidationError


class InspectionListCreateView(APIView):
    """
    POST /api/inspections/
    Uploads plate image, validates, runs model inference, and stores completed result.
    
    GET /api/inspections/
    Lists inspections:
    - Operator: sees own inspections only.
    - Supervisor / Admin: sees all inspections.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role == User.Role.OPERATOR:
            queryset = Inspection.objects.filter(user=user)
        else:
            queryset = Inspection.objects.all()

        # Query filters
        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param.upper())

        predicted_class = request.query_params.get('predicted_class')
        if predicted_class is not None and predicted_class != '':
            queryset = queryset.filter(predicted_class=int(predicted_class))

        unreviewed = request.query_params.get('unreviewed')
        if unreviewed is not None and unreviewed.lower() in ('true', '1'):
            queryset = queryset.filter(reviews__isnull=True)

        queryset = queryset.select_related('user').prefetch_related('reviews__reviewer').order_by('-created_at')
        serializer = InspectionSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        upload_serializer = InspectionUploadSerializer(data=request.data)
        if not upload_serializer.is_valid():
            errors = upload_serializer.errors
            err_code = 'VALIDATION_FAILED'
            detail_msg = 'Validation error'

            if 'image' in errors:
                err_data = errors['image']
                # Handle list of dicts, single dict, or list of strings
                if isinstance(err_data, list) and len(err_data) > 0:
                    first = err_data[0]
                    if isinstance(first, dict):
                        err_code = str(first.get('error_code', 'VALIDATION_FAILED'))
                        detail_msg = str(first.get('detail', 'Image validation failed'))
                    else:
                        detail_msg = str(first)
                elif isinstance(err_data, dict):
                    err_code = str(err_data.get('error_code', 'VALIDATION_FAILED'))
                    detail_msg = str(err_data.get('detail', 'Image validation failed'))
                else:
                    detail_msg = str(err_data)

            return Response({
                'error_code': err_code,
                'detail': detail_msg
            }, status=status.HTTP_400_BAD_REQUEST)

        image_file = upload_serializer.validated_data['image']
        parent_id = upload_serializer.validated_data.get('parent_inspection_id')
        parent_inspection = None
        if parent_id:
            parent_inspection = Inspection.objects.filter(id=parent_id).first()

        # Create initial inspection record
        inspection = Inspection(
            user=request.user,
            image=image_file,
            original_filename=image_file.name,
            parent_inspection=parent_inspection,
            status=Inspection.Status.COMPLETED
        )
        inspection.save()

        # Execute model inference
        try:
            prediction_res = predict_plate(inspection.image.path)
            # Update prediction fields directly
            Inspection.objects.filter(id=inspection.id).update(
                predicted_class=prediction_res['predicted_class'],
                confidence=prediction_res['confidence'],
                defect_probability=prediction_res['defect_probability'],
                model_version=prediction_res['model_version'],
                status=Inspection.Status.COMPLETED,
                error_message=''
            )
            inspection.refresh_from_db()
        except Exception as e:
            Inspection.objects.filter(id=inspection.id).update(
                status=Inspection.Status.FAILED,
                error_message=str(e)
            )
            inspection.refresh_from_db()

        return Response(InspectionSerializer(inspection).data, status=status.HTTP_201_CREATED)


class InspectionDetailView(APIView):
    """
    GET /api/inspections/{id}/
    - Operator: 403 Forbidden if not their inspection.
    - Supervisor / Admin: Can view any inspection.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        inspection = get_object_or_404(
            Inspection.objects.select_related('user').prefetch_related('reviews__reviewer'),
            pk=pk
        )
        # Role check
        if request.user.role == User.Role.OPERATOR and inspection.user_id != request.user.id:
            raise PermissionDenied("You do not have permission to view inspections belonging to other operators.")

        return Response(InspectionSerializer(inspection).data, status=status.HTTP_200_OK)
