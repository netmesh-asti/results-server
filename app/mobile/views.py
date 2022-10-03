from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import NotFound
from rest_framework.status import HTTP_404_NOT_FOUND
from rest_framework.response import Response

from durin.models import AuthToken
from durin.auth import TokenAuthentication

from core import utils, models


from mobile.serializers import (
    MobileResultsSerializer,
    NtcMobileResultsSerializer,
)

from core.models import (
    MobileResult,
    MobileDevice,
    PublicSpeedTest,
    NTCSpeedTest
)
from . import permissions as CustomPermission


class AndroidResultsView(generics.ListCreateAPIView):
    """View for Android Speed Test Results"""

    queryset = MobileResult.objects.all()
    serializer_class = MobileResultsSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = [CustomPermission.IsAuthenticatedOrPostOnly]

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
            user = get_object_or_404(models.User, email=self.request.user)
            obj = serializer.save(tester=user, test_device=device)
            lat = float(self.request.data.get('lat'))
            lon = float(self.request.data.get('lon'))
            loc = utils.get_location(lat, lon)
            loc = models.Location.objects.create(**loc)
            NTCSpeedTest.objects.create(result_id=obj.id, location=loc)


class ListNtcMobileTestsView(viewsets.ReadOnlyModelViewSet):

    serializer_class = NtcMobileResultsSerializer
    permission_classes = (permissions.IsAuthenticated, )
    authentication_classes = (TokenAuthentication, )

    def get_queryset(self):
        queryset = NTCSpeedTest.objects.filter(
            result__tester=self.request.user)
        return queryset

    def list(self, request):
        queryset = NTCSpeedTest.objects.filter(
            result__tester=self.request.user)
        serializer = NtcMobileResultsSerializer(queryset, many=True)
        return Response(serializer.data)
