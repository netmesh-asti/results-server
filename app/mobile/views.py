from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.response import Response

from durin.models import AuthToken, Client
from durin.auth import TokenAuthentication

from drf_spectacular.utils import (
    extend_schema)

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
from . import permissions as custom_permission


class MobileResultsView(generics.CreateAPIView):
    """View for Creating and Listing Mobile Speed Test Results"""
    queryset = MobileResult.objects.all()
    serializer_class = MobileResultsSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [
        custom_permission.IsAuthenticatedOrPostOnly]

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
            user = get_object_or_404(
                models.User,
                email=self.request.user)
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


class AdminMobileTestsView(viewsets.ReadOnlyModelViewSet):
    """
    View for Staff User
    Staffs can only list results from his/her region
    Staffs can retrieve results from individual testers
    Staffs can't change or delete results
    """
    serializer_class = NtcMobileResultsSerializer
    permission_classes = (permissions.IsAdminUser, )
    authentication_classes = (TokenAuthentication, )

    def get_queryset(self):
        user = get_user_model().objects.get(email=self.request.user)
        return NTCSpeedTest.objects.filter(
            tester__ntc_region=user.ntc_region)

    def retrieve(self, request, *args, **kwargs):
        """List results from field tester"""
        instance = NTCSpeedTest.objects.filter(
                tester_id=self.kwargs['pk'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """List all results from staff's regions"""
        queryset = self.get_queryset()
        serializer = NtcMobileResultsSerializer(
            queryset, many=True)
        return Response(serializer.data)


class UserMobileTestsView(viewsets.ReadOnlyModelViewSet):
    """
    View for Field Tester aka User
    FT can only retrieve his/her tests
    FT can't change/delete his/her tests
    """
    lookup_field = "test_id"
    serializer_class = NtcMobileResultsSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )

    def get_queryset(self):
        return NTCSpeedTest.objects.filter(
            tester__email=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        """List results from field tester"""
        instance = NTCSpeedTest.objects.filter(
                test_id=self.kwargs['test_id'])
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """List all results from staff's regions"""
        queryset = self.get_queryset()
        serializer = NtcMobileResultsSerializer(
            queryset, many=True)
        return Response(serializer.data)


# class RetrieveUserMobileResultDetail(generics.RetrieveAPIView):
#     serializer_class = NtcMobileResultsSerializer
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = [permissions.IsAuthenticated, ]
#
#     def get_object(self):
#         lookup_field = self.kwargs["test_id"]
#         return get_object_or_404(NTCSpeedTest, test_id=lookup_field)


class ManageMobileDeviceView(viewsets.ModelViewSet):
    """Manage Enrollment of Mobile Devices for Staffs"""
    serializer_class = MobileDeviceSerializer
    permission_classes = (permissions.IsAdminUser,)
    authentication_classes = (TokenAuthentication, )

    def get_queryset(self):
        if self.action == "create":
            return MobileDevice.objects.all()
        elif self.action == "list":
            staff = get_user_model().objects.get(
                email=self.request.user
            )
            return MobileDevice.objects.filter(
                user__ntc_region=staff.ntc_region
            )

    def retrieve(self, request, *args, **kwargs):
        instance = MobileDevice.objects.filter(
                user_id=self.kwargs['pk'],
            )
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        """Reg Client and User(owner)"""
        # Create a client from mobile device name
        device_name = self.request.data['name']
        client = Client.objects.create(name=device_name)
        serializer.save(client=client)


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
