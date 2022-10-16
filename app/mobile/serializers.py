from rest_framework import serializers

from core.models import (
    MobileResult,
    MobileDevice,
    NTCSpeedTest,
    User,
)

from location.serializers import LocationSerializer
from user.serializers import UserSerializer 


class ListMobileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
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
            "user",
         )



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
            "user",
          
         )

   

class MobileResultsSerializer(serializers.ModelSerializer):
    """Serializer for the Mobile Results Object"""

    class Meta:
        model = MobileResult
        exclude = ('id',)
        read_only_fields = ('created_on', 'test_id', )


class NtcMobileResultsSerializer(serializers.ModelSerializer):
    """SerializeR for NTC Field Tester Test Results"""
    tester = UserSerializer(read_only=True)
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
    """Serializer for the Mobile Results Object"""
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
