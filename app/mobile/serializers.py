from rest_framework import serializers

from core.models import (
    MobileResult,
    MobileDevice,
    NTCSpeedTest,
)


class MobileDeviceSerializer(serializers.ModelSerializer):
    """Serializer for the Mobile Results Object"""
    class Meta:
        model = MobileDevice
        exclude = ('id', 'client', 'user', 'ram', 'storage')


class MobileResultsSerializer(serializers.ModelSerializer):
    """Serializer for the Mobile Results Object"""
    test_device = MobileDeviceSerializer(read_only=True)

    class Meta:
        model = MobileResult
        exclude = ('id',)
        read_only_fields = ('created_on', 'test_id', )


class NtcMobileResultsSerializer(serializers.ModelSerializer):
    """SerializeR for NTC Field Tester Test Results"""

    class Meta:
        model = NTCSpeedTest
        fields = ["id", "date_created", "test_id", "result",
                  "location", "test_device"]
        read_only_fields = (
            'date_created',
            'result',
            'test_device',
            'id',
            'test_id',
            "location")
        depth = 1
