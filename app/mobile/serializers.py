from core.models import MobileResult, MobileDevice
from rest_framework import serializers


class MobileDeviceSerializer(serializers.ModelSerializer):
    """Serializer for the Mobile Results Object"""
    class Meta:
        model = MobileDevice
        exclude = ('id', 'client', 'user', 'ram', 'storage')


class MobileResultsSerializer(serializers.ModelSerializer):
    """Serializer for the Mobile Results Object"""
    device = MobileDeviceSerializer(read_only=True)

    class Meta:
        model = MobileResult
        exclude = ('id', 'test_device',)
        read_only_fields = ('created_on', 'test_id',)
