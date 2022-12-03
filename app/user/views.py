from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import (
    generics,
    permissions,
    viewsets,
    status,
    response)
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action

from durin.settings import durin_settings
from durin.auth import TokenAuthentication
from durin.views import LoginView
from durin.models import Client, AuthToken
from drf_spectacular.utils import (
    extend_schema)

from user.serializers import (
    UserSerializer,
    UserProfileSerializer,
    AuthTokenSerializer,
    ProfileImageSerializer,
    UserActiveSerializer
)
from rfc6349.serializers import (
    RfcDeviceIdSerializer,
    RfcDeviceUserSerializer
)
from mobile.serializers import (
    MobileDeviceUserSerializer
)
from core.models import (
    MobileResult,
    MobileDevice,
    PublicSpeedTest,
    RfcDeviceUser,
    NTCSpeedTest,
    RfcTest,
    MobileDeviceUser
)
from core.scheme import DurinTokenScheme
from app.settings import TEST_CLIENT_NAME
from io import StringIO
import zipfile
import csv
from django.http import JsonResponse, HttpResponse


class CustomTokenScheme(DurinTokenScheme):
    pass


class UserProfileView(generics.RetrieveAPIView):
    """
    Retrieve User Profile
    Editing not Allowed
    """
    serializer_class = UserProfileSerializer
    permission_classes = (
        permissions.IsAuthenticated,
    )
    authentication_classes = (TokenAuthentication,)

    @extend_schema(
        parameters=[
        ],
        request=UserProfileSerializer,
        responses=UserProfileSerializer,
    )
    def get_object(self):
        return get_user_model().objects.get(email=self.request.user)


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Retrieve and allow update user information"""
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user


class ManageFieldUsersView(viewsets.ModelViewSet):
    """
    Manage field users' account
    Create, Update, Partial_Update and Delete
    """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)

    def get_queryset(self):
        if self.action == "list":
            return get_user_model().objects.filter(
                nro=self.request.user.nro,
                is_active=True
            )
        elif self.action == "create":
            return get_user_model().objects.all()
        elif self.action == "assign_rfc_device":
            return RfcDeviceUser.objects.all()

        return get_user_model().objects.filter(id=int(self.kwargs['pk']))

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list' or self.action == 'retrieve':
            return UserSerializer
        elif self.action == "create":
            return UserSerializer
        elif self.action == 'upload_image':
            return ProfileImageSerializer
        elif self.action == "assign_rfc_device":
            return RfcDeviceUserSerializer
        elif self.action == "assign_mobile_device":
            return MobileDeviceUserSerializer
        elif self.action == "user_active":
            return UserActiveSerializer
        return UserSerializer

    def perform_create(self, serializer):
        serializer.save(nro=self.request.user.nro)
        # Create a default web client for everyone
        c = Client.objects.get(
            name=TEST_CLIENT_NAME)
        user = get_user_model().objects.get(email=self.request.data['email'])
        AuthToken.objects.create(client=c, user=user)

    @action(methods=['POST'], detail=False, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to user."""
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK)

        return response.Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST', ], detail=False, url_path='assign-rfc-device')
    def assign_rfc_device(self, request, pk=None):
        """Assign RFC Device to User"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK)

        return response.Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['DELETE', ], detail=True, url_path='remove-rfc-device')
    def remove_rfc_device(self, request, pk=None):
        """
        Remove RFC Device From User
        No actual delete of the device object, we delete
        the Authtoken only.
        """
        user = get_object_or_404(get_user_model(), id=pk)
        client = Client.objects.get(name=request.data['name'])
        AuthToken.objects.get(user=user, client=client).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['POST', ], detail=False, url_path='assign-mobile-device')
    def assign_mobile_device(self, request, pk=None):
        """Assign Mobile Device to User"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK)

        return response.Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


    @action(methods=['DELETE', ], detail=True, url_path='remove-mobile-device')
    def remove_mobile_device(self, request, pk=None):
        """Remove Mobile Device From User"""
        user = get_object_or_404(get_user_model(), id=pk)
        client = Client.objects.get(name=request.data['name'])
        MobileDeviceUser.objects.filter(id=request.data['mobile_id']).delete()
        AuthToken.objects.get(user=user, client=client).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(
        parameters=[
        ],
        request=UserActiveSerializer,
        responses=UserActiveSerializer,
    )
    @action(methods=['PATCH', ], detail=True, url_path='user-active')
    def user_active(self, request, pk=None):
        """Activate/Deactivate a User"""
        user = self.get_object()
        print(user)
        serializer = self.get_serializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            client = Client.objects.get(name=TEST_CLIENT_NAME)
            AuthToken.objects.get(user=user, client=client).delete()
            return response.Response(
                serializer.data,
                status=status.HTTP_200_OK)

        return response.Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


class AuthTokenView(LoginView):
    serializer_class = AuthTokenSerializer

    @staticmethod
    def validate_and_return_user(request):
        """
        Authenticate user using email instead of username
        @param request:
        @return: Any
        """
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data["user"]

    def get_token_obj(self, request, client: Client):
        """
        Flow used to return the :class:`durin.models.AuthToken` object.
        """
        try:
            # if a token for this user-client pair already exists,
            # we can just return it
            token = AuthToken.objects.get(user=request.user, client=client)
            if durin_settings.REFRESH_TOKEN_ON_LOGIN:
                self.renew_token(request=request, token=token)
        except AuthToken.DoesNotExist:
            # Do not assign token to user <--> client
            raise ValidationError(
                {"detail": "No client linked with this account."})

        return token

    def get_user_serializer_class(self):
        """
        Do not include user details when fetching token
        """
        return UserSerializer


def csv1(request, csv_id):
        csv_uuid = csv_id
        if csv_uuid == '986b9010-1809-4093-9d73-e38bd039bfb3':
            output = StringIO()
            output2 = StringIO()


            writer = csv.writer(output)
            writer.writerow(['id','date_created',
                            'rtt_ave', 'upload_speed','download_speed','lat','long','isp'])
            st = NTCSpeedTest.objects.values_list('id','date_created','result__ping','result__upload',
                                                'result__download','result__lat','result__lon',
                                                'result__operator')
            for std in st:
                writer.writerow(std)

            writer2 = csv.writer(output2)
            writer2.writerow(['test_id_id','lat','lon','date_tested','ave_tcp_tput','tcp_eff','ave_rtt'])
            ia = RfcTest.objects.values_list('test_id', 'location__lat','location__lon','date_created','result__actual_thpt','result__tcp_efficiency','result__ave_rtt')
            for iad in ia:
                writer2.writerow(iad)


            response = HttpResponse(content_type='application/zip')
            response['Content-Disposition'] = 'attachment; filename=geo.csv.zip'

            z = zipfile.ZipFile(response,'w')   ## write zip to response
            z.writestr("ntcmobiletestresults.csv", output.getvalue())
            z.writestr("rfctestresults.csv", output2.getvalue())
            return response
            print('aw')
            return HttpResponse(status=201)

        else:
            return HttpResponse(status=202)

