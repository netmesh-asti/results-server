from rest_framework import generics, permissions
from rest_framework.authentication import TokenAuthentication

from core.models import RfcResult
from rfc6349.serializers import Rfc6349ResultSerializer


class Rfc6349ResView(generics.ListCreateAPIView):
    serializer_class = Rfc6349ResultSerializer
    queryset = RfcResult.objects.all()
    authentication_classes = (TokenAuthentication,)
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(tester=self.request.user)
