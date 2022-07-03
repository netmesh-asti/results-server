from rest_framework import generics, authentication, permissions
from user.serializers import UserSerializer, AuthTokenSerializer
from django.contrib.auth import get_user_model
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from django.shortcuts import get_object_or_404


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer
    permission_classes = (
        permissions.IsAuthenticated,
        permissions.IsAdminUser)


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


class CreateTokenView(ObtainAuthToken):
    """Create A new Authtoken for the user"""
    serializer_class = AuthTokenSerializer
    rederer_classes = api_settings.DEFAULT_RENDERER_CLASSES
