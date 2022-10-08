from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.response import Response

from durin.models import AuthToken
from durin.auth import TokenAuthentication

from core import utils, models


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


class AndroidResultsView(generics.ListCreateAPIView):
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
            if not device:
                return NotFound(
                    detail="Device not registered to client.",
                    code=HTTP_404_NOT_FOUND)
            user = get_object_or_404(models.User, email=self.request.user)
            obj = serializer.save()
            lat = float(self.request.data.get('lat'))
            lon = float(self.request.data.get('lon'))
            loc = utils.get_location(lat, lon)
            loc = models.Location.objects.create(**loc)
            NTCSpeedTest.objects.create(
                result_id=obj.id,
                tester=user,
                test_device=device,
                location=loc)


class ListNtcMobileTestsView(viewsets.ReadOnlyModelViewSet):
    queryset = NTCSpeedTest.objects.all()
    serializer_class = NtcMobileResultsSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )

    def get_queryset(self):
        queryset = NTCSpeedTest.objects.filter(
            result__tester=self.request.user)
        return queryset

    def list(self, request, *args, **kwargs):
        device_obj = get_object_or_404(
            models.MobileDevice,
            user=self.request.user)
        queryset = NTCSpeedTest.objects.filter(test_device=device_obj)
        serializer = NtcMobileResultsSerializer(queryset, many=True)
        return Response(serializer.data)


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
    permission_classes = [permissions.IsAuthenticated, ]

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
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self):
        lookup_field = self.kwargs["serial_number"]
        return get_object_or_404(MobileDevice, serial_number=lookup_field)
