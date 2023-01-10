from rest_framework import serializers

from durin.models import (
    Client,
    AuthToken
)
from core.models import (
    RfcResult,
    RfcDevice,
    RfcTest,
    RfcDeviceUser
)
from user.serializers import UserSerializer
from location.serializers import LocationSerializer


class Rfc6349ResultSerializer(serializers.ModelSerializer):
    """Serializer for RFC 6349 test results"""
    class Meta:
        model = RfcResult
        exclude = ("id",)
        read_only_fields = ("created_on",)


class RfcDeviceSerializer(serializers.ModelSerializer):
    """Serializer from RFC Test Devices"""
    class Meta:
        model = RfcDevice
        exclude = ("id", "client", "users")
        read_only_fields = ("date_created",)


class RfcTestSerializer(serializers.ModelSerializer):
    """Serializer for RFC Tests"""
    tester = UserSerializer(read_only=True)
    test_device = RfcDeviceSerializer(read_only=True)
    result = Rfc6349ResultSerializer(read_only=True)
    location = LocationSerializer(read_only=True)

    class Meta:
        model = RfcTest
        fields = ["id", "date_created",
                  "tester", "test_id",
                  "result", "location",
                  "test_device", "client_ip"]
        read_only_fields = (
            'id',
            'date_created',
            'test_id',
            "client_ip"
        )


class RfcDeviceNameSerializer(serializers.ModelSerializer):
    """Serializer for RFC Device Check Name"""
    check_name = serializers.CharField(allow_blank=True, allow_null=True)

    class Meta:
        model = RfcDevice
        fields = ('check_name', )


class RfcDeviceIdSerializer(serializers.ModelSerializer):
    """Serializer for RFC Device Check Name"""

    class Meta:
        model = RfcDevice
        fields = ('name', )


class RfcDeviceUserSerializer(serializers.ModelSerializer):
    """Serializer for RFC device lists"""

    class Meta:
        model = RfcDeviceUser
        fields = ("id", "user", "device")
        read_only_fields = ('id',)

    def create(self, validated_data):
        instance = RfcDeviceUser.objects.create(**validated_data)
        rfc_device_instance = RfcDeviceUser.objects.get(id=instance.id)
        device_name = rfc_device_instance.device.name
        client = Client.objects.get(name=device_name)
        AuthToken.objects.create(user=rfc_device_instance.user, client=client)
        return instance
