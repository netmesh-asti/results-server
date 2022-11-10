from datetime import date
import datetime

from django.utils.dateparse import parse_date
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import (
    generics,
    permissions,
    viewsets,
    status,
)
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework_csv import renderers as r
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from durin.models import AuthToken, Client
from durin.auth import TokenAuthentication

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    extend_schema_view
)

from core.utils import get_client_ip

from core.models import (
    RfcResult,
    RfcDevice,
    RfcTest,
    User,
    Location)
from rfc6349.serializers import (
    Rfc6349ResultSerializer,
    RfcDeviceSerializer,
    RfcTestSerializer,
    RfcDeviceNameSerializer,
)

from core.utils import Gis


class ResultLocation(Gis):

    def __init__(self, lat, lon):
        super(ResultLocation, self).__init__(lat, lon)

    def reverse_geo(self):
        return self.get_location()


class Rfc6349ResView(generics.ListCreateAPIView):
    serializer_class = Rfc6349ResultSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = RfcResult.objects.all().order_by('-timestamp')
        return queryset

    def perform_create(self, serializer):
        token = self.request.auth
        client = AuthToken.objects.select_related('client').get(
            token=token).client
        try:
            device = RfcDevice.objects.get(client=client)
        except RfcDevice.DoesNotExist as e:
            raise Http404(e)
        user = get_object_or_404(
            User,
            email=self.request.user)
        obj = serializer.save()
        lat = float(self.request.data.get('lat'))
        lon = float(self.request.data.get('lon'))
        if lat is None or lon is None:
            raise ValidationError("lat and lon are required.")
        loc = Gis.find_location(lat, lon)
        if loc is None:
            raise ValidationError("No Location found!")
        loc = Location.objects.create(**loc)
        ip = get_client_ip(self.request)
        RfcTest.objects.create(
            result_id=obj.id,
            tester=user,
            test_device=device,
            location=loc,
            client_ip=ip
        )


class RfcDeviceView(viewsets.ModelViewSet):
    queryset = RfcDevice.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.request.query_params.get('check_name'):
            return RfcDeviceNameSerializer
        return RfcDeviceSerializer

    def get_queryset(self):
        if self.action == "list":
            name = self.request.query_params.get('check_name')
            if name:
                device_query = RfcDevice.objects.filter(
                    client__name=name
                )
                if device_query.exists():
                    raise ValidationError("The client name is already taken. ")
            email = self.request.user
            admin = get_user_model().objects.get(email=email)
            device_query = RfcDevice.objects.filter(
                owner__nro=admin.nro)
            return device_query

        return self.queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='check_name',
                description='Client Name',
                type=str),
        ],
    )
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        parameters=[
        ],
        request=RfcDeviceSerializer,
        responses=RfcDeviceSerializer
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def perform_create(self, serializer):
        name = self.request.data['name']
        device_user = self.request.data['owner']
        user = get_user_model().objects.get(id=device_user)
        if Client.objects.filter(name=name).exists():
            raise ValidationError("The name already exists.")
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
    lookup_field = "test_id"
    serializer_class = RfcTestSerializer
    permission_classes = (permissions.IsAdminUser, )
    authentication_classes = (TokenAuthentication, )

    def get_queryset(self):
        user = get_user_model().objects.get(email=self.request.user)
        return RfcTest.objects.filter(
            tester__ntc_region=user.nro.region)

    def retrieve(self, request, *args, **kwargs):
        """List results from field tester"""
        lookup_field = self.kwargs["test_id"]
        print(lookup_field)
        user = get_object_or_404(RfcTest, test_id=lookup_field)
        serializer = RfcTestSerializer(user)
        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        """List all results from staff's regions"""
        queryset = self.get_queryset().order_by("-timestamp")
        serializer = RfcTestSerializer(
            queryset, many=True)
        return Response(serializer.data)


class UserRFC6349TestsView(viewsets.ReadOnlyModelViewSet):
    """
    View for Field Tester aka User
    FT can only retrieve his/her tests
    FT can't change/delete his/her tests
    """
    lookup_field = "test_id"
    serializer_class = RfcTestSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )

    def get_queryset(self):
        return RfcTest.objects.filter(
            tester__email=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        lookup_field = self.kwargs["test_id"]
        print(lookup_field)
        user = get_object_or_404(RfcTest, test_id=lookup_field)
        serializer = RfcTestSerializer(user)
        return Response(serializer.data)


class UserRFC6349DeviceView(viewsets.ReadOnlyModelViewSet):
    """
    View for Field Tester aka User
    FT can only retrieve his/her tests
    FT can't change/delete his/her tests
    """
    lookup_field = "id"
    serializer_class = RfcDeviceSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )

    def get_queryset(self):
        return RfcDevice.objects.filter(
            owner=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        lookup_field = self.kwargs["id"]
        print(lookup_field)
        device = get_object_or_404(RfcDevice, id=lookup_field)
        serializer = RfcDeviceSerializer(device)
        return Response(serializer.data)


search_csv = ''

@extend_schema_view(
    get=extend_schema(description='Fetch All RFC6349 Results for Staff Region Datatable ONLY (Ignore)'),
)
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def RFC6349ResultsList(request):
    if request.method == 'GET':
        rfcresults = RfcTest.objects.filter(
            tester__nro__region=request.user.nro.region).order_by("-date_created")
        global search_csv 
        total = RfcTest.objects.all().count()
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
            rfcresults = rfcresults.filter(Q(test_id__icontains=search_query))

        if minDate:
            rfcresults = rfcresults.filter(date_created__range=(minDate, date.today() + datetime.timedelta(days=1)))

        if minDate and maxDate:
            rfcresults = rfcresults.filter(date_created__range=(minDate, maxDate + datetime.timedelta(days=1)))

        if isp:
            rfcresults = rfcresults.filter(Q(result__operator__icontains=isp))

        if province:
            rfcresults = rfcresults.filter(Q(location__province__icontains=province))

        if municipality:
            rfcresults = rfcresults.filter(Q(location__municipality__icontains=municipality))

        if barangay:
            rfcresults = rfcresults.filter(Q(location__barangay__icontains=barangay))
        total = rfcresults.count()
        rfcresults = rfcresults.order_by(order_column)[start:start+length]
        serializer = RfcTestSerializer(rfcresults, many=True)
        response = {
            'draw': draw,
            'recordsTotal': total,
            'recordsFiltered': total,
            'data': serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK)


class MyUserRenderer (r.CSVRenderer):
    header = ['date_created', 'test_id', 'tester_first_name', 'tester_last_name', 'ntc_region', 'lat', 'lon', 'province', 'municipality',
              'barangay', 'mtu', 'rtt', 'bb', 'bdp', 'rwnd', 'actual_thpt', 'max_achievable_thpt', 'tx_bytes', 'ave_rtt',
              'rwnd', 'retransmit_bytes', 'ideal_transfer_time', 'transfer_time_ratio', 'tcp_efficiency', 'buffer_delay']


class RFC6349ResultCSV(APIView):
    serializer_class = RfcTestSerializer
    renderer_classes = (MyUserRenderer,)
    header = ['date_created', 'test_id', 'tester_email']

    def get(self, request):
        global search_csv
        isp = request.query_params.get('isp')
        search_query = request.GET.get('search[value]')
        province = request.query_params.get('province')
        municipality = request.query_params.get('municipality')
        minDate = parse_date(request.query_params.get('mindate'))
        maxDate = parse_date(request.query_params.get('maxdate'))
        barangay = request.query_params.get('barangay')
        region = request.query_params.get('region')

        # if column_order == '0':
        #     column_order = "date_created"
        # if dir_order == 'asc':
        #     column_order = '-' + column_order

        res = RfcTest.objects.filter(tester__nro__region=region).filter().order_by('-date_created')
        if isp:
            res = res.filter(Q(result__operator__icontains=isp))
        if minDate:
            res = res.filter(date_created__range=(minDate, date.today() + datetime.timedelta(days=1)))
        if minDate and maxDate:
            res = res.filter(date_created__range=(minDate, maxDate + datetime.timedelta(days=1)))

        if isp:
            res = res.filter(Q(result__operator__icontains=isp))
        if province:
            res = res.filter(Q(location__province__icontains=province))
        if municipality:
            res = res.filter(Q(location__municipality__icontains=municipality))
        if barangay:
            res = res.filter(Q(location__barangay__icontains=barangay))
        if search_csv:
            res = res.filter(Q(test_id__icontains=search_csv))

        # res = res.order_by(column_order)[starttable:starttable+lengthtable]

        content = [{'date_created': response.date_created.strftime("%Y-%m-%d %-I:%M %p"),
                    'test_id': response.test_id,
                    'tester_email': response.tester.email,
                    'tester_first_name': response.tester.first_name,
                    'tester_last_name': response.tester.last_name,
                    'ntc_region': response.tester.nro.region,
                    'lat': response.location.lat,
                    'lon': response.location.lon,
                    'province': response.location.province,
                    'municipality': response.location.municipality,
                    'barangay': response.location.barangay,
                    'direction': response.result.direction,
                    'mtu': response.result.mtu,
                    'rtt': response.result.rtt,
                    'bb': response.result.bb,
                    'bdp': response.result.bdp,
                    'rwnd': response.result.rwnd,
                    'actual_thpt': response.result.actual_thpt,
                    'max_achievable_thpt': response.result.max_achievable_thpt,
                    'tx_bytes': response.result.tx_bytes,
                    'ave_rtt': response.result.ave_rtt,
                    'retransmit_bytes': response.result.retransmit_bytes,
                    'acutal_transfer_time': response.result.acutal_transfer_time,
                    'ideal_transfer_time': response.result.ideal_transfer_time,
                    'transfer_time_ratio': response.result.transfer_time_ratio,
                    'tcp_efficiency': response.result.tcp_efficiency,
                    'buffer_delay': response.result.buffer_delay,
                    }
                   for response in res]
        return Response(content)
