from rest_framework import generics, permissions

from durin.models import AuthToken
from durin.auth import TokenAuthentication

from mobile.serializers import (
    MobileResultsSerializer,
    NtcMobileResultsSerializer,
)

from core.models import (
    MobileResult,
    MobileDevice,
    PublicSpeedTest,
    NTCSpeedTest
)
from . import permissions as CustomPermission


class CreateAndroidResView(generics.ListCreateAPIView):
    """View for Android Speed Test Results"""

    queryset = MobileResult.objects.all()
    serializer_class = MobileResultsSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [CustomPermission.IsAuthenticatedOrPostOnly]

    def perform_create(self, serializer):
        token = self.request.auth
        if not token:
            obj = serializer.save()
            PublicSpeedTest.objects.create(result_id=obj.id)
        else:
            client = AuthToken.objects.select_related('client').get(
                token=token).client
            device = MobileDevice.objects.get(client=client)
            obj = serializer.save()
            NTCSpeedTest.objects.create(result_id=obj.id, test_device=device)


class ListNtcMobileTestsView(generics.ListAPIView):
    queryset = NTCSpeedTest.objects.all()
    serializer_class = NtcMobileResultsSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )
