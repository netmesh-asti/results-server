from core.models import MobileResult
from rest_framework import serializers


class MobileResultsSerializer(serializers.ModelSerializer):
    """Serializer for the Mobile Results Object"""
    server_id = serializers.IntegerField()

    class Meta:
        model = MobileResult
        exclude = ('id', 'test_device',)
        read_only_fields = ('created_on', 'test_id',)
        depth = 1
