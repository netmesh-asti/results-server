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
    ProfileImageSerializer)
from core.scheme import DurinTokenScheme
from app.settings import TEST_CLIENT_NAME


class CustomTokenScheme(DurinTokenScheme):
    pass


# class CreateUserView(generics.CreateAPIView):
#     """Create a new user in the system"""
#     serializer_class = UserSerializer
#     permission_classes = (
#         permissions.IsAdminUser,
#     )
#     authentication_classes = (TokenAuthentication,)
#
#     def perform_create(self, serializer):
#         serializer.save()
#         c = Client.objects.get(name=TEST_CLIENT_NAME)
#         user = get_user_model().objects.get(email=self.request.data['email'])
#         AuthToken.objects.create(client=c, user=user)


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
    queryset = get_user_model().objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAdminUser,)

    def get_queryset(self):
        if self.action == "list":
            user = get_user_model().objects.get(email=self.request.user)
            return get_user_model().objects.filter(
                ntc_region=user.ntc_region, is_staff=False)
        elif self.action == "create":
            return get_user_model().objects.all()
        return get_user_model().objects.filter(id=int(self.kwargs['pk']))

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list' or self.action == 'retrieve':
            return UserSerializer
        elif self.action == "create":
            return UserSerializer
        elif self.action == 'upload_image':
            return ProfileImageSerializer
        return UserSerializer

    def perform_create(self, serializer):
        serializer.save()
        # Create a default web client for everyone
        c = Client.objects.get(
            name=TEST_CLIENT_NAME)
        user = get_user_model().objects.get(email=self.request.data['email'])
        AuthToken.objects.create(client=c, user=user)

    @extend_schema(
        parameters=[
        ],
        request=UserSerializer,
        responses=UserSerializer,
        # more customizations
    )
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

    @action(methods=['POST', ], detail=True, url_path='assign-rfc-device')
    def assign_rfc_device(self, request, pk=None):
        """Assign RFC Device to User"""
        user = get_object_or_404(get_user_model(), id=pk)
        client = Client.objects.get(name=request.data['name'])
        AuthToken.objects.create(user=user, client=client)
        return response.Response(status=status.HTTP_200_OK)

    @action(methods=['DELETE', ], detail=True, url_path='remove-rfc-device')
    def remove_rfc_device(self, request, pk=None):
        """Remove RFC Device From User"""
        user = get_object_or_404(get_user_model(), id=pk)
        client = Client.objects.get(name=request.data['name'])
        AuthToken.objects.get(user=user, client=client).delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


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
