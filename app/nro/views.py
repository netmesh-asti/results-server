from django.contrib.auth import get_user_model

from rest_framework import (
    generics,
    permissions
)

from durin.auth import TokenAuthentication

from nro import seriailzers
from core.models import NtcRegionalOffice


class NroOfficeView(generics.ListCreateAPIView):
    """View for NRO"""
    queryset = NtcRegionalOffice.objects.all()
    serializer_class = seriailzers.NroSerializer
    permission_classes = (permissions.IsAdminUser, )
    authentication_classes = (TokenAuthentication, )

    def get_object(self):
        admin = get_user_model().objects.get(
            email=self.request.user)
        office_obj = NtcRegionalOffice.objects.get(
            region=admin.ntc_region)
        return office_obj

