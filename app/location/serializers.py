from core import models
from rest_framework import serializers


class LocationSerializer(serializers.ModelSerializer):
    """Location Serialzier"""

    class Meta:
        model = models.Location
        fields = "__all__"
