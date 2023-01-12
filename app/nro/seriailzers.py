from rest_framework import serializers
from core.models import (
    RegionalOffice,
)


class NroSerializer(serializers.ModelSerializer):
    """Serializer for regional offices"""

    class Meta:
        model = RegionalOffice
        fields = "__all__"
