from rest_framework import serializers
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from core.models import (
    MobileResult,
    MobileDevice,
    NTCSpeedTest, LinkedMobileDevice,
)

from durin.models import (
    Client,
    AuthToken,
)

from location.serializers import LocationSerializer
from user.serializers import UserSerializer, AgentSerializer


class ListMobileSerializer(serializers.ModelSerializer):
    owner = UserSerializer()


class MobileDeviceSerializer(serializers.ModelSerializer):
    """Serializer for the Mobile Results Object"""

    class Meta:
        model = MobileDevice

        fields = (
            "id",
            "name",
            "serial_number",
            "imei",
            "phone_model",
            "android_version",
            "ram",
            "storage",
         )

        read_only_fields = ("id",)


class MobileDeviceUsersSerializer(serializers.ModelSerializer):
    """Serializer for adding Users of a Mobile Device"""
    class Meta:
        model = MobileDevice
        fields = ("users",)


class MobileDeviceActivationSerializer(serializers.ModelSerializer):
    """Serializer for adding Users of a Mobile Device"""
    class Meta:
        model = MobileDevice
        fields = ("is_active",)


class MobileResultsSerializer(serializers.ModelSerializer):
    """Serializer for the Mobile Results Object"""

    class Meta:
        model = MobileResult
        exclude = ('id',)
        read_only_fields = ('created_on', 'test_id', )


class NtcMobileResultsSerializer(serializers.ModelSerializer):
    """SerializeR for NTC Field Tester Test Results"""
    tester = AgentSerializer(read_only=True)
    test_device = MobileDeviceSerializer(read_only=True)
    result = MobileResultsSerializer(read_only=True)
    location = LocationSerializer(read_only=True)

    class Meta:
        model = NTCSpeedTest
        fields = ["id", "date_created",
                  "tester", "test_id",
                  "result", "location",
                  "test_device",
                  "client_ip"]
        read_only_fields = (
            'id',
            'date_created',
            'test_id',
            "client_ip"
        )


class MobileResultsListSerializer(serializers.ModelSerializer):
    """Serializer for Listing the Mobile Results Object"""
    test_device = MobileDeviceSerializer(read_only=True)
    result = MobileResultsSerializer(read_only=True)
    location = LocationSerializer(read_only=True)

    class Meta:
        model = NTCSpeedTest
        fields = ["id", "date_created",
                  "tester", "test_id",
                  "result", "location",
                  "test_device"]
        read_only_fields = (
            'id',
            'date_created',
            'test_id',
            "location")


class MobileDeviceImeiSerializer(serializers.ModelSerializer):
    """Serializer for the mobile device imei"""

    class Meta:
        model = MobileDevice
        fields = ("imei", )
        read_only_fields = ("id",)


class LinkedMobileDeviceSerializer(serializers.ModelSerializer):
    """Serializer for linked mobile devices to owner"""
    imei = serializers.CharField(max_length=250, read_only=True)

    class Meta:
        model = LinkedMobileDevice
        fields = ("imei", )
        read_only_fields = ("id", "owner")

