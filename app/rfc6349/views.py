from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import (
    generics,
    permissions,
    viewsets,
    status,
    response
)
from rest_framework.exceptions import NotFound
from durin.models import AuthToken, Client
from durin.auth import TokenAuthentication

from core.models import (
    RfcResult,
    RfcDevice,
    RfcTest,
    User,
    Location)
from rfc6349.serializers import (
    Rfc6349ResultSerializer,
    RfcDeviceSerializer,
    RfcTestSerializer
)

from core import utils


class Rfc6349ResView(generics.ListCreateAPIView):
    serializer_class = Rfc6349ResultSerializer
    queryset = RfcResult.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        token = self.request.auth
        client = AuthToken.objects.select_related('client').get(
            token=token).client
        device = RfcDevice.objects.get(client=client)
        if not device:
            return NotFound(
                detail="Device not registered to client.",
                code=status.HTTP_404_NOT_FOUND)
        user = get_object_or_404(
            User,
            email=self.request.user)
        obj = serializer.save()
        lat = float(self.request.data.get('lat'))
        lon = float(self.request.data.get('lon'))
        loc = utils.get_location(lat, lon)
        loc = Location.objects.create(**loc)
        RfcTest.objects.create(
            result_id=obj.id,
            tester=user,
            test_device=device,
            location=loc
        )


class RfcDeviceView(viewsets.ModelViewSet):
    serializer_class = RfcDeviceSerializer
    queryset = RfcDevice.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        if self.action == "list":
            email = self.request.user
            admin = get_user_model().objects.get(email=email)
            device_query = RfcDevice.objects.filter(
                owner__ntc_region=admin.ntc_region)
            return device_query

        return self.queryset

    def perform_create(self, serializer):
        name = self.request.data['name']
        device_user = self.request.data['owner']
        user = get_user_model().objects.get(id=device_user)
        client = Client.objects.create(name=name)
        AuthToken.objects.create(client=client, user=user)
        serializer.save(client=client, owner=user)


class AdminRfcTestsView(viewsets.ReadOnlyModelViewSet):
    """
    View for Staff User
    Staffs can only list results from his/her region
    Staffs can retrieve results from individual testers
    Staffs can't change or delete results
    """
    serializer_class = RfcTestSerializer
    permission_classes = (permissions.IsAdminUser, )
    authentication_classes = (TokenAuthentication, )

    def get_queryset(self):
        user = get_user_model().objects.get(email=self.request.user)
        return RfcTest.objects.filter(
            tester__ntc_region=user.ntc_region)

    def retrieve(self, request, *args, **kwargs):
        """List results from field tester"""
        instance = RfcTest.objects.filter(
                tester_id=self.kwargs['pk'])
        serializer = self.get_serializer(instance)
        return response.Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """List all results from staff's regions"""
        queryset = self.get_queryset()
        serializer = RfcTestSerializer(
            queryset, many=True)
        return response.Response(serializer.data)
        serializer.save(client=client, user=user)




# class RetrieveRfc6349ResDetail(generics.RetrieveAPIView):
#     serializer_class = NtcMobileResultsSerializer
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = [permissions.IsAuthenticated, ]

#     def get_object(self):
#         lookup_field = self.kwargs["test_id"]
#         return get_object_or_404(NTCSpeedTest, test_id=lookup_field)


# class ListUserMobileDevices(generics.ListAPIView):
#     serializer_class = MobileDeviceSerializer
#     permission_classes = (permissions.IsAuthenticated, )
#     authentication_classes = (TokenAuthentication, )

#     def get_queryset(self):
#         user = self.request.user
#         print(user)
#         return MobileDevice.objects.filter(user=user)


# class RetrieveUserMobileDeviceDetail(generics.RetrieveAPIView):
#     serializer_class = MobileDeviceSerializer
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = [permissions.IsAuthenticated, ]

#     def get_object(self):
#         lookup_field = self.kwargs["serial_number"]
#         return get_object_or_404(MobileDevice, serial_number=lookup_field)

