from core.models import (
    MobileResult,
    MobileDevice,
    NTCSpeedTest,
)

from rest_framework import serializers


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

    class Meta:
        model = NTCSpeedTest
        fields = "__all__"
        read_only_fields = (
            'date_created', 'result', 'test_device', 'id', 'test_id')
