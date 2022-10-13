from django.contrib.auth import get_user_model

from rest_framework import (
    generics,
)

from durin.auth import TokenAuthentication

from nro import seriailzers, permissions
from core.models import NtcRegionalOffice


class NroOfficeView(generics.ListCreateAPIView):
    """View for NRO"""

    serializer_class = seriailzers.NroSerializer
    permission_classes = (permissions.IsAdminOrReadOnly, )
    authentication_classes = (TokenAuthentication, )

    def get_queryset(self):
        queryset = NtcRegionalOffice.objects.all().order_by(
            'id'
        )
        return queryset

    def get_object(self):
        user = get_user_model().objects.get(
            email=self.request.user)
        office_obj = NtcRegionalOffice.objects.get(
            region=user.ntc_region)
        return office_obj
