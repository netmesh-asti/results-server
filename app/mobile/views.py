from rest_framework import generics, permissions
from django.shortcuts import get_object_or_404
from durin.models import AuthToken
from durin.auth import TokenAuthentication

from mobile.serializers import (
    MobileResultsSerializer,
    NtcMobileResultsSerializer,
    MobileDeviceSerializer
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




class SelfListNtcMobileTestsView(generics.ListAPIView):
    serializer_class = NtcMobileResultsSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )

    def get_queryset(self):
        user = self.request.user
        print(user)
        return NTCSpeedTest.objects.filter(test_device__user=user)

class RetrieveUserMobileResultDetail(generics.RetrieveAPIView):
    serializer_class = NtcMobileResultsSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated,]

    def get_object(self):
        lookup_field = self.kwargs["test_id"]
        return get_object_or_404(NTCSpeedTest, test_id=lookup_field)    



class ListUserMobileDevices(generics.ListAPIView):
    serializer_class = MobileDeviceSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )

    def get_queryset(self):
        user = self.request.user
        print(user)
        return MobileDevice.objects.filter(user=user)


class RetrieveUserMobileDeviceDetail(generics.RetrieveAPIView):
    serializer_class = MobileDeviceSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated,]

    def get_object(self):
        lookup_field = self.kwargs["serial_number"]
        return get_object_or_404(MobileDevice, serial_number=lookup_field)    
        

