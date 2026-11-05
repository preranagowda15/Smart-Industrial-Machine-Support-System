from rest_framework import serializers
from .models import Review


class ReviewSerializer(serializers.ModelSerializer):
    reviewer_username = serializers.CharField(source='reviewer.username', read_only=True)
    reviewer_role = serializers.CharField(source='reviewer.role', read_only=True)

    class Meta:
        model = Review
        fields = [
            'id',
            'inspection',
            'reviewer',
            'reviewer_username',
            'reviewer_role',
            'decision',
            'comment',
            'created_at'
        ]
        read_only_fields = ['id', 'reviewer', 'inspection', 'created_at']


class ReviewCreateSerializer(serializers.ModelSerializer):
    decision = serializers.ChoiceField(choices=Review.Decision.choices)
    comment = serializers.CharField(required=False, allow_blank=True, default='')

    class Meta:
        model = Review
        fields = ['decision', 'comment']

