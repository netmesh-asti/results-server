from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.authtoken.serializers import AuthTokenSerializer

from durin.views import APIAccessTokenView, LoginView
from durin.auth import TokenAuthentication
from durin import serializers as durin_serializer

from user.serializers import UserSerializer, UserTokenSerializer


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer
    permission_classes = (
        permissions.IsAdminUser,
    )
    authentication_classes = (TokenAuthentication,)


class ManageUserView(generics.RetrieveUpdateAPIView):
    """list and allow update user information"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user


class ManageFieldUsersView(generics.RetrieveUpdateAPIView):
    """list and allow update field tester information"""
    serializer_class = UserSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,
                          permissions.IsAdminUser,)

    def get_object(self):
        queryset = get_user_model().objects.all()
        email = self.request.query_params.get('email')
        obj = get_object_or_404(queryset, email=email)
        return obj

class AuthTokenView(LoginView):
    serializer_class = UserTokenSerializer

    @staticmethod
    def validate_and_return_user(request):
        request.data._mutable = True
        try:
            request.data['username'] = request.data['email']
        except KeyError:
            pass
        request.data._mutable = False
        serializer = AuthTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return serializer.validated_data["user"]

    def get_user_serializer_class(self, *args, **kwargs):
        """
        Do not include user details when fetching token
        """
        return None
