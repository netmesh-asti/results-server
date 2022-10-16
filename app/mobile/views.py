from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import generics, permissions, viewsets, status
from rest_framework.exceptions import APIException

from rest_framework.response import Response

from durin.models import AuthToken, Client
from durin.auth import TokenAuthentication

from drf_spectacular.utils import extend_schema_view, extend_schema
from drf_spectacular.utils import OpenApiParameter
from django.utils.dateparse import parse_date
from datetime import date
import datetime

from django.shortcuts import get_object_or_404

from core import utils, models
from django.db.models import Q
from rest_framework_csv import renderers as r
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from core.utils import get_client_ip

from mobile.serializers import (
    MobileResultsSerializer,
    NtcMobileResultsSerializer,
    MobileDeviceSerializer,
    MobileResultsListSerializer,
    ListMobileSerializer
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
                token=token
            ).client

            device = get_object_or_404(MobileDevice, client=client)
            user = get_object_or_404(
                models.User,
                email=self.request.user)
            try:
                obj = serializer.save()
            except IntegrityError:
                raise APIException("Data already exists.")
            lat = float(self.request.data.get('lat'))
            lon = float(self.request.data.get('lon'))
            if lat is None or lon is None:
                raise APIException("lat and lon are require")
            loc = utils.get_location(lat, lon)
            if loc is None:
                raise APIException("No Location found!")
            loc = models.Location.objects.create(**loc)
            ip = get_client_ip(self.request)
            NTCSpeedTest.objects.create(
                result_id=obj.id,
                tester=user,
                test_device=device,
                location=loc,
                client_ip=ip)


@extend_schema(parameters=[OpenApiParameter("id", int, OpenApiParameter.PATH)])
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
        try:
            instance = NTCSpeedTest.objects.get(
                    tester_id=self.kwargs['pk'])
        except NTCSpeedTest.DoesNotExist:
            raise APIException("No test was found.")
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
        lookup_field = self.kwargs["test_id"]
        try:
            instance = NTCSpeedTest.objects.get(
                    test_id=lookup_field)
        except NTCSpeedTest.DoesNotExist:
            raise APIException("No result was found.")

        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """List all results from staff's regions"""
        queryset = NTCSpeedTest.objects.filter(tester__email=self.request.user).order_by("-date_created")
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

    def get_serializer_class(self):
        if self.action == "create":
            return MobileDeviceSerializer
        elif self.action == "list":
            return ListMobileSerializer

    def get_queryset(self):
        if self.action == "create":
            return MobileDevice.objects.all()
        elif self.action == "list":
            staff = get_user_model().objects.get(
                email=self.request.user
            )
            return MobileDevice.objects.filter(
                user__nro=staff.nro
            )

    def retrieve(self, request, *args, **kwargs):
        try:
            instance = MobileDevice.objects.get(
                    user_id=self.kwargs['pk'],
            )
        except MobileDevice.DoesNotExist:
            raise APIException("No device was found.")
        serializer = self.get_serializer(instance)
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


@extend_schema_view(
    get=extend_schema(description='Mobile Datatable (Ignore)',
                      responses=MobileResultsListSerializer),
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def MobileResultsList(request):
    if request.method == 'GET':
        global search_csv, column_order, dir_order, starttable, lengthtable
        mobileresults = NTCSpeedTest.objects.filter(tester__nro__region=request.user.nro.region)
        total = NTCSpeedTest.objects.all().count()
        draw = request.query_params.get('draw')
        start = int(request.query_params.get('start'))
        length = int(request.query_params.get('length'))
        isp = request.query_params.get('isp')
        search_query = request.GET.get('search[value]')
        province = request.query_params.get('province')
        municipality = request.query_params.get('municipality')
        barangay = request.query_params.get('barangay')
        order_column = request.GET.get('order[0][column]')
        order = request.GET.get('order[0][dir]')
        minDate = parse_date(request.query_params.get('minDate'))
        maxDate = parse_date(request.query_params.get('maxDate'))
        search_csv = search_query
        column_order = order_column
        dir_order = order
        starttable = start
        lengthtable = length

        if order_column == '0':
            order_column = "date_created"
        if order == 'asc':
            order_column = '-' + order_column
        print(draw)

        if search_query:
            mobileresults = mobileresults.filter(Q(test_id__icontains=search_query))

        if minDate:
            mobileresults = mobileresults.filter(date_created__range=(minDate,
                                                 date.today() + datetime.timedelta(days=1)))
        if minDate and maxDate:
            mobileresults = mobileresults.filter(date_created__range=(minDate,
                                                 maxDate + datetime.timedelta(days=1)))
        if isp:
            mobileresults = mobileresults.filter(Q(result__operator__icontains=isp))

        if province:
            mobileresults = mobileresults.filter(Q(location__province__icontains=province))

        if municipality:
            mobileresults = mobileresults.filter(Q(location__municipality__icontains=municipality))

        if barangay:
            mobileresults = mobileresults.filter(Q(location__barangay__icontains=barangay))
        total = mobileresults.count()
        mobileresults = mobileresults.order_by(order_column)[start:start+length]
        serializer = MobileResultsListSerializer(mobileresults, many=True)
        response = {
            'draw': draw,
            'recordsTotal': total,
            'recordsFiltered': total,
            'data': serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)


class MyUserRenderer (r.CSVRenderer):
    header = ['date_created', 'test_id', 'tester_first_name', 'tester_last_name',
              'ntc_region', 'td_android_version',
              'td_imei', 'td_phone_model', 'download', 'upload', 'ping',
              'jitter', 'mcc', 'mnc', 'tac', 'network_type', 'operator',
              'rssi', 'signal_quality',  'ssid', 'bssid', 'province',
              'municipality', 'barangay']


class MobileResultCSV(APIView):
    serializer_class = NtcMobileResultsSerializer
    renderer_classes = (MyUserRenderer,)
    header = ['date_created', 'test_id', 'tester_email']

    def get(self, request):
        global search_csv, column_order, dir_order, starttable, lengthtable
        isp = request.query_params.get('isp')
        province = request.query_params.get('province')
        municipality = request.query_params.get('municipality')
        minDate = parse_date(request.query_params.get('mindate'))
        maxDate = parse_date(request.query_params.get('maxdate'))
        barangay = request.query_params.get('barangay')
        region = request.query_params.get('region')
        response = NTCSpeedTest.objects.filter(tester__nro__region=region).order_by('-date_created')
        if column_order == '0':
            column_order = "date_created"
        if dir_order == 'asc':
            column_order = '-' + column_order

        if isp:
            response = response.filter(Q(result__operator__icontains=isp))

        if minDate:
            response = response.filter(date_created__range=(minDate,
                                       date.today() + datetime.timedelta(days=1)))
        if minDate and maxDate:
            response = response.filter(date_created__range=(minDate,
                                       maxDate + datetime.timedelta(days=1)))
        if isp:
            response = response.filter(Q(result__operator__icontains=isp))
        if province:
            response = response.filter(Q(location__province__icontains=province))

        if municipality:
            response = response.filter(Q(location__municipality__icontains=municipality))

        if barangay:
            response = response.filter(Q(location__barangay__icontains=barangay))

        if search_csv:
            response = response.filter(Q(test_id__icontains=search_csv))

        response = response.order_by(column_order)[starttable:starttable+lengthtable]

        content = [{'date_created': response.date_created.strftime("%Y-%m-%d %-I:%M %p"),
                    'test_id': response.test_id,
                    'tester_email': response.tester.email,
                    'tester_first_name': response.tester.first_name,
                    'tester_last_name': response.tester.last_name,
                    'ntc_region': response.tester.nro.region,
                    'td_android_version': response.test_device.android_version,
                    'td_imei': response.test_device.imei,
                    'td_phone_model': response.test_device.phone_model,
                    'download': response.result.download,
                    'upload': response.result.upload,
                    'ping': response.result.ping,
                    'jitter': response.result.jitter,
                    'mcc': response.result.mcc,
                    'mnc': response.result.mnc,
                    'tac': response.result.tac,
                    'network_type': response.result.network_type,
                    'operator': response.result.operator,
                    'rssi': response.result.rssi,
                    'signal_quality': response.result.signal_quality,
                    'ssid': response.result.ssid,
                    'bssid': response.result.bssid,
                    'province': response.location.province,
                    'municipality': response.location.municipality,
                    'barangay': response.location.barangay,
                    }
                   for response in response]
        return Response(content)
