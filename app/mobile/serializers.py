from core.models import RfcResult, MobileResult
from rest_framework import serializers


class RfcResultsSerializer(serializers.ModelSerializer):
    """Serializer for the Results Object"""
    class Meta:
        model = RfcResult
        exclude = (id,)


class MobileResultsSerializer(serializers.ModelSerializer):
    """Serializer for the Mobile Results Object"""

    class Meta:
        model = MobileResult
        exclude = ("id", "user",)
        read_only_fields=('created_on',)
