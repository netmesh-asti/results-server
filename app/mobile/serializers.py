from rest_framework import serializers
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import ValidationError

from core.models import (
    MobileResult,
    MobileDevice,
    NTCSpeedTest,
    MobileDeviceUser,
    ActivatedMobDevice,
)

from durin.models import (
    Client,
    AuthToken,
)

from location.serializers import LocationSerializer
from user.serializers import UserSerializer 


class ListMobileSerializer(serializers.ModelSerializer):
    owner = UserSerializer()

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
            "owner",
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
            "owner",
          
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


class MobileDeviceUsersSerializer(serializers.ModelSerializer):
    """Serializers for the list of mobile device users"""

    class Meta:
        model = MobileDevice
        fields = "__all__"


class MobileDeviceUserSerializer(serializers.ModelSerializer):
    """Serializer for assigning mobile device to user"""
    class Meta:
        model = MobileDeviceUser
        fields = ('id', 'user', 'device')
        read_only_fields = ('id',)

    def create(self, validated_data):
        instance = MobileDeviceUser.objects.create(**validated_data)
        mobile_device_instance = MobileDeviceUser.objects.get(id=instance.id)
        device_name = mobile_device_instance.device.imei
        client = Client.objects.get(name=device_name)
        AuthToken.objects.create(user=mobile_device_instance.user, client=client)
        return instance


class MobileDeviceImeiSerializer(serializers.ModelSerializer):
    """Serializer for the mobile device imei"""

    class Meta:
        model = MobileDevice
        fields = ("imei", )
        read_only_fields = ("id",)


class ActivateMobileDeviceSerializer(serializers.ModelSerializer):
    """Serializer for the Activation of mobile devices"""
    # device = MobileDeviceImeiSerializer()
    imei = serializers.CharField()

    class Meta:
        model = ActivatedMobDevice
        fields = ("imei", )

    def create(self, validated_data):
        imei = validated_data['imei']
        registered_device = get_object_or_404(MobileDevice, imei=imei)
        try:
            ActivatedMobDevice.objects.get(imei=imei)
            raise ValidationError(detail="Device Already Activated")
        except ActivatedMobDevice.DoesNotExist:
            obj = ActivatedMobDevice.objects.create(imei=registered_device)
            return obj
