from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets, status
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.response import Response
from durin.models import AuthToken, Client
from durin.auth import TokenAuthentication
from drf_spectacular.utils import extend_schema_view, extend_schema
from django.utils.dateparse import parse_date
from datetime import date, timedelta
import datetime, calendar
from core import utils, models
from django.db.models import Q, Avg
from rest_framework.settings import api_settings
from rest_framework_csv import renderers as r
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.http import JsonResponse


from drf_spectacular.utils import (
    extend_schema)

from drf_spectacular.utils import (
    extend_schema)

from core import utils, models


from mobile.serializers import (
    MobileResultsSerializer,
    NtcMobileResultsSerializer,
    MobileDeviceSerializer,
    MobileResultsListSerializer
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
        lookup_field = self.kwargs["test_id"]
        print(lookup_field)
        user = get_object_or_404(NTCSpeedTest, test_id = lookup_field)
        serializer = NtcMobileResultsSerializer(user)
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



@extend_schema_view(
    get=extend_schema(description='Fetch All Mobile Results for Staff Region Datatable ONLY', responses=MobileResultsListSerializer),
)   
@api_view(['GET'])
@permission_classes([IsAuthenticated, IsAdminUser])
def MobileResultsList(request):
    if request.method == 'GET':
        mobileresults = NTCSpeedTest.objects.filter(tester__ntc_region=request.user.ntc_region)
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

        if order_column  == '0':
           order_column = "date_created"
        if order == 'asc':
           order_column = '-' + order_column
        print(draw)        

        if search_query:
            mobileresults = mobileresults.filter(Q(test_id__icontains=search_query))

        if minDate:
            mobileresults = mobileresults.filter(date_created__range=(minDate, date.today() + datetime.timedelta(days=1)))
       

        if minDate and maxDate:
            mobileresults = mobileresults.filter(date_created__range=(minDate, maxDate + datetime.timedelta(days=1)))
    
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
            'draw' : draw,
            'recordsTotal' : total,
            'recordsFiltered' : total,
            'data' : serializer.data,
        }
        return Response(response, status=status.HTTP_200_OK) 
    

class MyUserRenderer (r.CSVRenderer):
      header = ['date_created', 'test_id', 'tester_first_name', 'tester_last_name', 'ntc_region', 'td_android_version',
        'td_imei', 'td_phone_model', 'download', 'upload', 'ping', 'jitter', 'mcc', 'mnc', 'tac', 'network_type', 'operator',
        'rssi', 'signal_quality',  'ssid', 'bssid', 'province', 'municipality', 'barangay'  ]

class MobileResultCSV(APIView):
    
    serializer_class = NtcMobileResultsSerializer
    renderer_classes = (MyUserRenderer,)
    header = ['date_created', 'test_id', 'tester_email'] 


    def get(self, request):
        isp = request.query_params.get('isp')
        search_query = request.GET.get('search[value]')
        province = request.query_params.get('province')
        municipality = request.query_params.get('municipality')
        minDate = parse_date(request.query_params.get('mindate'))
        maxDate = parse_date(request.query_params.get('maxdate'))
        barangay = request.query_params.get('barangay')
        response = NTCSpeedTest.objects.filter(tester__ntc_region=3).order_by('-date_created')

        if isp:
            response = response.filter(Q(result__operator__icontains=isp))

        if minDate:
            response = response.filter(date_created__range=(minDate, date.today() + datetime.timedelta(days=1)))
       
        if minDate and maxDate:
            response = response.filter(date_created__range=(minDate, maxDate + datetime.timedelta(days=1)))
    
        if isp:
            response = response.filter(Q(result__operator__icontains=isp))

        if province:
            response = response.filter(Q(location__province__icontains=province))

        if municipality:
            response = response.filter(Q(location__municipality__icontains=municipality))  

        if barangay:
            
            response = response.filter(Q(location__barangay__icontains=barangay))    


        content = [{'date_created': response.date_created.strftime("%Y-%m-%d %-I:%M %p"),
                    'test_id': response.test_id,
                    'tester_email': response.tester.email,
                    'tester_first_name': response.tester.first_name,
                    'tester_last_name': response.tester.last_name,
                    'ntc_region': response.tester.ntc_region,
                    'td_android_version': response.test_device.android_version,
                    'td_imei': response.test_device.imei,
                    'td_phone_model': response.test_device.phone_model,
                    'download' : response.result.download,
                    'upload' : response.result.upload,
                    'ping' : response.result.ping,
                    'jitter' : response.result.jitter,
                    'mcc' : response.result.mcc,
                    'mnc' : response.result.mnc,
                    'tac' : response.result.tac,
                    'network_type' : response.result.network_type,
                    'operator' : response.result.operator,
                    'rssi' : response.result.rssi,
                    'signal_quality' : response.result.signal_quality,
                    'ssid' : response.result.ssid,
                    'bssid' : response.result.bssid,
                    'province' : response.location.province,
                    'municipality' : response.location.municipality,
                    'barangay' : response.location.barangay,
                    }
                for response in response]
        return Response(content)


@api_view(('GET',))
def speedtest_performance_detail(request, name):
    if request.method == 'GET':

        query = NTCSpeedTest.objects.filter(Q(location__municipality__icontains=name))
        lastyear = int((datetime.datetime.now()- timedelta(days=365)).strftime("%Y"))
        thisyear = int(datetime.datetime.now().strftime('%Y'))
        print(test2)
        
        
        start = date(lastyear, 6, 1)
        end = date(thisyear, 6, 30) +  datetime.timedelta(days=1)
      
        download = query.filter(date_created__range=[start, end]).aggregate(Avg('result__download'))
        upload =  query.filter(date_created__range=[start, end]).aggregate(Avg('result__upload'))
        ping =  query.filter(date_created__range=[start, end]).aggregate(Avg('result__ping'))
        lytest = query.filter(date_created__range=[start, end])

   
    # lyjune = query.filter(date__range=[start, end]).annotate(month=TruncMonth('date', output_field=DateField())).values('month').annotate(Avg('download_speed'))


        context = {
            'lytest' : lytest,
            'download': download,
            'upload': upload,
            'ping': ping,
            'name' : name,
            'globe' : query.filter(date_created__range=[start, end]).filter(Q(result__operator__icontains="globe")).aggregate(Avg('result__download')),
            'converge' : query.filter(date_created__range=[start, end]).filter(Q(result__operator__icontains="converge")).aggregate(Avg('result__download')),
            'pldt' : query.filter(date_created__range=[start, end]).filter(Q(result__operator__icontains="philippine long distance telephone")).aggregate(Avg('result__download')),
            'smart' : query.filter(date_created__range=[start, end]).filter(Q(result__operator__icontains="smart")).aggregate(Avg('result__download')),
            'lyjun' :   query.filter(date_created__range=[date(lastyear, 6, 1) , date(lastyear, 6, calendar.monthrange(lastyear , 6)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__download')),
        'lyjul' :    query.filter(date_created__range=[date(lastyear, 7, 1) , date(lastyear, 7, calendar.monthrange(lastyear , 7)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__download')),
            'lyaug' :  query.filter(date_created__range=[date(lastyear, 8, 1) , date(lastyear, 8, calendar.monthrange(lastyear , 8)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__download')),
            'lysep' :  query.filter(date_created__range=[date(lastyear, 9, 1) , date(lastyear, 9, calendar.monthrange(lastyear , 9)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__download')),
            'lyoct' :  query.filter(date_created__range=[date(lastyear, 10, 1) , date(lastyear, 10, calendar.monthrange(lastyear , 10)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__download')),
            'lynov' :   query.filter(date_created__range=[date(lastyear, 11, 1) , date(lastyear, 11, calendar.monthrange(lastyear , 11)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__download')),
            'lydec' :   query.filter(date_created__range=[date(lastyear, 12, 1) , date(lastyear, 12, calendar.monthrange(lastyear , 12)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__download')),
            'thjan' :    query.filter(date_created__range=[date(thisyear, 1, 1) , date(thisyear, 1, calendar.monthrange(thisyear , 1)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__download')),
            'thfeb' :   query.filter(date_created__range=[date(thisyear, 2, 1) , date(thisyear, 2, calendar.monthrange(thisyear , 2)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__download')),
            'thmar' :   query.filter(date_created__range=[date(thisyear, 3, 1) , date(thisyear, 3, calendar.monthrange(thisyear , 3)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__download')),
            'thapr' :  query.filter(date_created__range=[date(thisyear, 4, 1) , date(thisyear, 4, calendar.monthrange(thisyear , 4)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__download')),
                'thmay' :  query.filter(date_created__range=[date(thisyear, 5, 1) , date(thisyear, 5, calendar.monthrange(thisyear , 5)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__download')),
                'thjun' :   query.filter(date_created__range=[date(thisyear, 6, 1) , date(thisyear, 6, calendar.monthrange(thisyear , 6)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__download')),

                    'lyjunu' :  query.filter(date_created__range=[date(lastyear, 6, 1) , date(lastyear, 6, calendar.monthrange(lastyear , 6)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__upload')),
                    'lyjulu' : query.filter(date_created__range=[date(lastyear, 7, 1) , date(lastyear, 7, calendar.monthrange(lastyear , 7)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__upload')),
                    'lyaugu' : query.filter(date_created__range=[date(lastyear, 8, 1) , date(lastyear, 8, calendar.monthrange(lastyear , 8)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__upload')),
                    'lysepu' :  query.filter(date_created__range=[date(lastyear, 9, 1) , date(lastyear, 9, calendar.monthrange(lastyear , 9)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__upload')),
                    'lyoctu' :  query.filter(date_created__range=[date(lastyear, 10, 1) , date(lastyear, 10, calendar.monthrange(lastyear , 10)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__upload')),
                    'lynovu' :   query.filter(date_created__range=[date(lastyear, 11, 1) , date(lastyear, 11, calendar.monthrange(lastyear , 11)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__upload')),
                    'lydecu' :  query.filter(date_created__range=[date(lastyear, 12, 1) , date(lastyear, 12, calendar.monthrange(lastyear , 12)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__upload')),
                    'thjanu' : query.filter(date_created__range=[date(thisyear, 1, 1) , date(thisyear, 1, calendar.monthrange(thisyear , 1)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__upload')),
                    'thfebu' : query.filter(date_created__range=[date(thisyear, 2, 1) , date(thisyear, 2, calendar.monthrange(thisyear , 2)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__upload')),
                    'thmaru' : query.filter(date_created__range=[date(thisyear, 3, 1) , date(thisyear, 3, calendar.monthrange(thisyear , 3)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__upload')),
                    'thapru' : query.filter(date_created__range=[date(thisyear, 4, 1) , date(thisyear, 4, calendar.monthrange(thisyear , 4)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__upload')),
                    'thmayu' : query.filter(date_created__range=[date(thisyear, 5, 1) , date(thisyear, 5, calendar.monthrange(thisyear , 5)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__upload')),
                    'thjunu' : query.filter(date_created__range=[date(thisyear, 6, 1) , date(thisyear, 6, calendar.monthrange(thisyear , 6)[1]) + datetime.timedelta(days=1)]).aggregate(Avg('result__upload')),

        }
    return Response(context)    


