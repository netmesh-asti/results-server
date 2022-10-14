from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication

from core.models import Server
from server.serializers import ServerSerializer


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff


class ServerAPIView(generics.ListCreateAPIView):
    queryset = Server.objects.all()
    serializer_class = ServerSerializer
    authenticaion_classes = (TokenAuthentication,)
    permission_classes = (IsAdminOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(contributor=self.request.user)
