from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import (
    generics,
    permissions,)
from rest_framework.exceptions import ValidationError

from durin.settings import durin_settings
from durin.auth import TokenAuthentication
from durin.views import LoginView
from durin.models import Client, AuthToken
from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,)

from user.serializers import (
    UserSerializer,
    ListUsersSerializer,
    ListUserRequestSerializer,
    AuthTokenSerializer)
from core.scheme import DurinTokenScheme
from app.settings import TEST_CLIENT_NAME


class CustomTokenScheme(DurinTokenScheme):
    pass


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer
    permission_classes = (
        permissions.IsAdminUser,
    )
    authentication_classes = (TokenAuthentication,)

    def perform_create(self, serializer):
        serializer.save()
        c = Client.objects.get(name=TEST_CLIENT_NAME)
        user = get_user_model().objects.get(email=self.request.data['email'])
        AuthToken.objects.create(client=c, user=user)


class ListUsersView(generics.ListAPIView):
    """List all users"""
    serializer_class = ListUsersSerializer
    permission_classes = (
        permissions.IsAdminUser,
    )
    authentication_classes = (TokenAuthentication,)

    @extend_schema(
        parameters=[
            ListUserRequestSerializer,
            OpenApiParameter("ntc_region", ListUserRequestSerializer),
        ],
        request=ListUserRequestSerializer,
        responses=ListUsersSerializer,
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def get_queryset(self):
        """return users from a region"""
        region = self.request.query_params['ntc_region']
        return get_user_model().objects.filter(
            ntc_region=region).filter(is_staff=False)


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Retrieve and allow update user information"""
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user


class ManageFieldUsersView(generics.RetrieveUpdateAPIView):
    """list and allow update field tester information"""
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,
                          permissions.IsAdminUser,)

    def get_object(self):
        queryset = get_user_model().objects.all()
        email = self.request.query_params.get('email')
        obj = get_object_or_404(queryset, email=email)
        return obj


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
