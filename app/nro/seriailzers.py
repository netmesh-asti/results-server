from rest_framework import serializers
from core.models import (
    NtcRegionalOffice,
    NtcOfficeEmails,
    NtcOfficeMob,
    NtcOfficeTele,
)


class NroEmailSerializer(serializers.ModelSerializer):
    """Serializer for NRO email addresses"""

    class Meta:
        model = NtcOfficeEmails
        exclude = ('id',)


class NroTeleSerializer(serializers.ModelSerializer):
    """Serializer for the NRO Telephone Serializers"""

    class Meta:
        model = NtcOfficeTele
        exclude = ('id',)


class NroMobSerializer(serializers.ModelSerializer):
    """Serializer for the NRO Mobile Numbers"""

    class Meta:
        model = NtcOfficeMob
        exclude = ('id',)


class NroSerializer(serializers.ModelSerializer):
    """Serializer for regional offices"""

    class Meta:
        model = NtcRegionalOffice
        exclude = ('id',)