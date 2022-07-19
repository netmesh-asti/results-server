from rest_framework import serializers

from core.models import RfcResult


class Rfc6349ResultSerializer(serializers.ModelSerializer):
    """Serializer for RFC 6349 test results"""
    class Meta:
        model = RfcResult
        exclude = ("id", "tester", "server")
        read_only_fields = ("date_tested",)
