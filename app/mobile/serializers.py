from core.models import RfcResult, MobileResult
from rest_framework import serializers


class MobileResultsSerializer(serializers.ModelSerializer):
    """Serializer for the Mobile Results Object"""

    class Meta:
        model = MobileResult
        exclude = ("id", "user",)
        read_only_fields=('created_on',)
