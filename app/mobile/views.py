from django.contrib.auth import get_user_model
from django.db import IntegrityError
from rest_framework import generics, permissions, viewsets, status
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.serializers import ModelSerializer

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
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from core.utils import Gis, get_client_ip

from mobile.serializers import (
    MobileResultsSerializer,
    NtcMobileResultsSerializer,
    MobileDeviceSerializer,
    MobileResultsListSerializer,
    MobileDeviceUsersSerializer, MobileDeviceActivationSerializer, LinkedMobileDeviceSerializer
)

from core.models import (
    MobileResult,
    MobileDevice,
    PublicSpeedTest,
    NTCSpeedTest, LinkedMobileDevice
)
from . import permissions as custom_permission
from django.utils import timezone


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
            ).token_client

            device = get_object_or_404(MobileDevice, client=client)
            user = get_object_or_404(
                models.User,
                email=self.request.user)
            try:
                obj = serializer.save()
            except IntegrityError:
                raise ValidationError("Data already exists.")
            lat = float(self.request.data.get('lat'))
            lon = float(self.request.data.get('lon'))
            if lat is None or lon is None:
                raise ValidationError("lat and lon are required.")
            loc = Gis.find_location(lat, lon)
            if loc is None:
                raise NotFound("No Location found!")
            loc = models.Location.objects.create(**loc)
            ip = get_client_ip(self.request)
            NTCSpeedTest.objects.create(
                result_id=obj.id,
                tester=user,
                test_device=device,
                location=loc,
                client_ip=ip)


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
        return NTCSpeedTest.objects.filter(
            tester__agency=self.request.user.agent.office)

    def retrieve(self, request, *args, **kwargs):
        """List results from field tester"""
        try:
            instance = NTCSpeedTest.objects.get(
                    tester_id=int(self.kwargs['pk']))
        except NTCSpeedTest.DoesNotExist:
            raise NotFound("No test was found.")
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
        if self.action == "list":
            if self.request.user.is_superuser:
                return NTCSpeedTest.objects.all()
            elif self.request.user.is_staff:
                return NTCSpeedTest.objects.filter(
                    tester__agency=self.request.user.employee_set.office)
            return self.request.user.agent.ntcspeedtest_set.all().order_by("-date_created")

    def retrieve(self, request, *args, **kwargs):
        """List results from field tester"""
        lookup_field = self.kwargs["test_id"]
        try:
            instance = NTCSpeedTest.objects.get(
                    test_id=lookup_field)
        except NTCSpeedTest.DoesNotExist:
            raise NotFound("No result was found.")

        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# class RetrieveUserMobileResultDetail(generics.RetrieveAPIView):
#     serializer_class = NtcMobileResultsSerializer
#     authentication_classes = (TokenAuthentication,)
#     permission_classes = [permissions.IsAuthenticated, ]
#
#     def get_object(self):
#         lookup_field = self.kwargs["test_id"]
#         return get_object_or_404(NTCSpeedTest, test_id=lookup_field)


class MobileDeviceView(viewsets.ModelViewSet):
    """
    Create, List, Retrieve, Update Mobile Devices
    Admin: Full
    authenticated: ReadOnly

    """""
    permission_classes = (custom_permission.IsAdminFull,)
    authentication_classes = (TokenAuthentication, )

    def get_queryset(self):
        if self.action == "create":
            return MobileDevice.objects.all()

        elif self.action == "list":
            if self.request.user.is_superuser:
                return MobileDevice.objects.all().order_by('name')
            elif self.request.user.is_staff:
                return MobileDevice.objects.filter(
                    users__office__exact=self.request.user.agent.office)
            return self.request.user.agent.mobiledevice_set.all().order_by(
                'name')

        elif self.action == "link":
            return MobileDevice.objects.all()

        # For retrieve, partial_update, add-user, remove-user, activation
        return MobileDevice.objects.filter(pk=self.kwargs['pk'])

    def get_serializer_class(self):
        if self.action == "add_user":
            return MobileDeviceUsersSerializer
        elif self.action == "activation":
            return MobileDeviceActivationSerializer
        elif self.action == "link":
            return LinkedMobileDeviceSerializer
        return MobileDeviceSerializer

    def perform_create(self, serializer):
        """Reg Client """
        # Create a client from mobile device name
        device_imei = self.request.data['imei']
        try:
            client = Client.objects.create(name=device_imei)
            AuthToken.objects.create(user=self.request.user, client=client)
        except IntegrityError:
            return ValidationError("Device already exists.")
        serializer.save(client=client)

    @action(methods=['POST'], detail=True, url_path='add-user')
    def add_user(self, request, pk=None):
        device = self.get_object()
        users = get_user_model().objects.filter(
            id__in=request.data.getlist("user_id"))
        agent_ids = [user.agent.id for user in users]
        serializer: ModelSerializer = self.get_serializer(device, data={
            "users": agent_ids,
        }, partial=True)
        if serializer.is_valid(raise_exception=serializer.error_messages):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=True, url_path='remove-user')
    def remove_user(self, request, pk=None):
        device: MobileDevice = self.get_object()
        user_pk = request.data['user']
        agent = get_user_model().objects.get(pk=user_pk).agent
        device.users.remove(agent)
        return Response(status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=True, url_path='activation')
    def activation(self, request, pk=None):
        device = self.get_object()
        serializer = self.get_serializer(device, data=request.data)
        if serializer.is_valid(raise_exception=serializer.error_messages):
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)

    @action(methods=["POST"], detail=False, url_path='link')
    def link(self, request, pk=None):
        owner = self.request.user.agent
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=serializer.error_messages):
            imei = self.request.data['imei']
            try:
                LinkedMobileDevice.objects.get(device__imei=imei)
                raise IntegrityError("Device Already Linked.")
            except LinkedMobileDevice.DoesNotExist:
                device: MobileDevice = MobileDevice.objects.get(imei=imei)
                serializer.save(device=device, owner=owner)
                return Response(data=serializer.data, status=status.HTTP_200_OK)


class ListUserMobileDevices(generics.ListAPIView):
    serializer_class = MobileDeviceSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )

    def get_queryset(self):
        user = self.request.user
        return MobileDevice.objects.filter(owner=user)


class RetrieveUserMobileDeviceDetail(generics.RetrieveAPIView):
    serializer_class = MobileDeviceSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticated, ]

    def get_object(self):
        lookup_field = self.kwargs["id"]
        return get_object_or_404(MobileDevice, id=lookup_field)


search_csv = ''


@extend_schema_view(
    get=extend_schema(description='Mobile Datatable (Ignore)',
                      responses=MobileResultsListSerializer),
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def MobileResultsList(request):
    if request.method == 'GET':
        global search_csv, column_order, dir_order, starttable, lengthtable
        mobileresults = NTCSpeedTest.objects.filter(tester__agency=request.user.employee.office)
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
    header = ['date_created',  'test_id', 'tester_email', 'tester_first_name', 'tester_last_name',
              'ntc_region', 'td_android_version',
              'td_imei', 'td_phone_model', 'download', 'upload', 'ping',
              'jitter', 'mcc', 'mnc', 'tac', 'network_type', 'operator',
              'rssi', 'signal_quality',  'ssid', 'bssid', 'lat', 'lon', 'province',
              'municipality', 'barangay']


class MobileResultCSV(APIView):
    serializer_class = NtcMobileResultsSerializer
    renderer_classes = (MyUserRenderer,)
    header = ['date_created', 'test_id', 'tester_email']

    def get(self, request):
        global search_csv
        isp = request.query_params.get('isp')
        province = request.query_params.get('province')
        municipality = request.query_params.get('municipality')
        minDate = parse_date(request.query_params.get('mindate'))
        maxDate = parse_date(request.query_params.get('maxdate'))
        barangay = request.query_params.get('barangay')
        region = request.query_params.get('region')
        response = NTCSpeedTest.objects.filter(tester__agency=region).order_by('-date_created')
        # if column_order == '0':
        #     column_order = "date_created"
        # if dir_order == 'asc':
        #     column_order = '-' + column_order

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

        # response = response.order_by(column_order)[starttable:starttable+lengthtable]

        content = [{'date_created': timezone.localtime(response.date_created).strftime('%Y-%m-%d %I:%M%p '),
                    'test_id': response.test_id,
                    'tester_email': response.tester.email,
                    'tester_first_name': response.tester.first_name,
                    'tester_last_name': response.tester.last_name,
                    'ntc_region': response.tester.office.region,
                    'lat': response.location.lat,
                    'lon': response.location.lon,
                    'province': response.location.province,
                    'municipality': response.location.municipality,
                    'barangay': response.location.barangay,
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
                    }
                   for response in response]
        return Response(content)
