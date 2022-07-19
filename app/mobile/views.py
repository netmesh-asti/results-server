from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication

from mobile.serializers import MobileResultsSerializer
from core.models import MobileResult


class CreateAndroidResView(generics.ListCreateAPIView):
    """View for Android Speed Test Results"""
    queryset = MobileResult.objects.all()
    serializer_class = MobileResultsSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(tester=self.request.user)
