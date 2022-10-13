from rest_framework import serializers
from core.models import (
    NtcRegionalOffice,
)


class NroSerializer(serializers.ModelSerializer):
    """Serializer for regional offices"""

    class Meta:
        model = NtcRegionalOffice
        fields = "__all__"
