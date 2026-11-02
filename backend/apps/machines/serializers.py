from rest_framework import serializers
from .models import Machine

class MachineSerializer(serializers.ModelSerializer):
    manual_count = serializers.IntegerField(source="manuals.count", read_only=True)

    class Meta:
        model = Machine
        fields = [
            "id",
            "machine_code",
            "machine_name",
            "manufacturer",
            "description",
            "is_active",
            "created_at",
            "manual_count",
        ]
        read_only_fields = ["id", "created_at", "manual_count"]
