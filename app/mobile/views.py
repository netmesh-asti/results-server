from rest_framework import generics, permissions

from durin.models import AuthToken
from durin.auth import TokenAuthentication

from mobile.serializers import MobileResultsSerializer
from core.models import MobileResult, MobileDevice


class CreateAndroidResView(generics.ListCreateAPIView):
    """View for Android Speed Test Results"""
    queryset = MobileResult.objects.all()
    serializer_class = MobileResultsSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        client = AuthToken.objects.select_related('client').get(
            token=self.request.auth).client
        device = MobileDevice.objects.get(client=client)
        serializer.save(test_device=device)
