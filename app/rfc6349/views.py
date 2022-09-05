from django.contrib.auth import get_user_model
from rest_framework import generics, permissions

from durin.models import AuthToken, Client
from durin.auth import TokenAuthentication

from core.models import RfcResult, RfcDevice
from rfc6349.serializers import Rfc6349ResultSerializer, RfcDeviceSerializer


class Rfc6349ResView(generics.ListCreateAPIView):
    serializer_class = Rfc6349ResultSerializer
    queryset = RfcResult.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        http_auth_token = self.request.META.get('Authorization')
        token = http_auth_token.replace(" ", '').replace('Token', '')
        client = AuthToken.objects.select_related('client').get(
            token=token).client
        device = RfcDevice.objects.get(client=client)
        serializer.save(device=device)


class RfcDeviceView(generics.ListCreateAPIView):
    serializer_class = RfcDeviceSerializer
    queryset = RfcDevice.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAdminUser]

    def perform_create(self, serializer):
        name = self.request.data['name']
        device_user = self.request.data['user']
        user = get_user_model().objects.get(id=device_user)
        client = Client.objects.create(name=name)
        AuthToken.objects.create(client=client, user=user)
        serializer.save(client=client, user=user)
