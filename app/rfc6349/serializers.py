from rest_framework import serializers

from core.models import RfcResult, RfcDevice


class Rfc6349ResultSerializer(serializers.ModelSerializer):
    """Serializer for RFC 6349 test results"""
    class Meta:
        model = RfcResult
        exclude = ("id", "device",)
        read_only_fields = ("created_on",)


class RfcDeviceSerializer(serializers.ModelSerializer):
    """Serializer from RFC Test Devices"""
    class Meta:
        model = RfcDevice
        exclude = ("client",)
        read_only_fields = ("date_created",)
