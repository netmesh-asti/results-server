from core.models import RfcResult, AndroidResult
from rest_framework import serializers


class RfcResultsSerializer(serializers.ModelSerializer):
    """Serializer for the Results Object"""
    class Meta:
        model = RfcResult
        exclude = (id,)


class AndroidResultsSerializer(serializers.ModelSerializer):
    """Serializer for the Android Results Object"""

    class Meta:
        model = AndroidResult
        exclude = ("id", "user",)
