from rest_framework import serializers
from .models import Inspection
from services.image_validator import validate_image_file, ImageValidationError
from services.model_service import predict_plate


class InspectionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    predicted_label = serializers.CharField(read_only=True)
    limitations_notice = serializers.SerializerMethodField()
    reviews = serializers.SerializerMethodField()
    latest_review = serializers.SerializerMethodField()

    class Meta:
        model = Inspection
        fields = [
            'id',
            'username',
            'user_role',
            'image',
            'original_filename',
            'predicted_class',
            'predicted_label',
            'confidence',
            'defect_probability',
            'model_version',
            'status',
            'error_message',
            'parent_inspection',
            'reviews',
            'latest_review',
            'limitations_notice',
            'created_at',
            'updated_at',
        ]
        read_only_fields = fields

    def get_limitations_notice(self, obj):
        return Inspection.LIMITATIONS_NOTICE

    def get_reviews(self, obj):
        # We will import ReviewSerializer dynamically or serialize reviews
        reviews = obj.reviews.all().order_by('created_at')
        return [
            {
                'id': r.id,
                'reviewer': r.reviewer.username,
                'reviewer_role': r.reviewer.role,
                'decision': r.decision,
                'comment': r.comment,
                'created_at': r.created_at
            }
            for r in reviews
        ]

    def get_latest_review(self, obj):
        latest = obj.reviews.order_by('-created_at').first()
        if not latest:
            return None
        return {
            'id': latest.id,
            'reviewer': latest.reviewer.username,
            'decision': latest.decision,
            'comment': latest.comment,
            'created_at': latest.created_at
        }


class InspectionUploadSerializer(serializers.Serializer):
    image = serializers.FileField(required=True)
    parent_inspection_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_image(self, file_obj):
        try:
            validate_image_file(file_obj, filename=file_obj.name)
        except ImageValidationError as e:
            raise serializers.ValidationError({
                'error_code': e.error_code,
                'detail': e.message
            })
        return file_obj

