from core.models import Server
from rest_framework import serializers


class ServerSerializer(serializers.ModelSerializer):
    """Server model serializer"""
    class Meta:
        model = Server
        exclude = ('contributor',)
        read_only_fields = ['id']
