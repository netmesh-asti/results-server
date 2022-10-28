from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import NtcRegionalOffice

USER_MOB_LIST_URL = reverse("mobile:mobiledevicelist")


class DeviceManageTest(TestCase):

    def setUp(self):
        nro = NtcRegionalOffice.objects.create(**{
            "region": 1
        })
        user_info = {
            "first_name": "Test",
            "last_name": "Test",
            "email": "user@example.com",
            "password": "netmesh1234",
            "nro_id": nro.id,
        }
        self.client = APIClient()
        self.user = get_user_model().objects.create(**user_info)

    def test_user_lists_devices_success(self):

        self.client.force_authenticate(user=self.user)
        res = self.client.get(USER_MOB_LIST_URL, {})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
