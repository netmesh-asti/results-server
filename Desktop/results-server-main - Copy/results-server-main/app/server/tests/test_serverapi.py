from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core import models

LIST_CREATE_SERVER_URL = reverse("server:servers")


class ServerAPITest(TestCase):
    """Tests for the servers endpoint"""

    def setUp(self):
        self.nro_info = {
            "address": "test address",
            "region": "1",
        }
        self.nro = models.NtcRegionalOffice.objects.create(**self.nro_info)
        self.user_admin = get_user_model().objects.create_superuser(
            **{
                "email": "admin@example.com",
                "first_name": "testadmin",
                "last_name": "testadmin",
                "password": "testpassword123",
                "nro": self.nro.id
            }
        )
        self.data = {
            "ip_address": "192.168.1.1",
            "server_type": "local",
            "lat": 14,
            "lon": 120,
        }
        self.user = get_user_model().objects.create_user(
            **{
                "email": "user@example.com",
                "first_name": "testuser",
                "last_name": "testuser",
                "password": "testpassword123",
                "nro": self.nro
            }
        )
        self.client = APIClient()

    def test_notadmin_create_fail(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(LIST_CREATE_SERVER_URL, self.data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_create_success(self):
        self.client.force_authenticate(user=self.user_admin)
        res = self.client.post(LIST_CREATE_SERVER_URL, self.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_user_list_success(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.get(LIST_CREATE_SERVER_URL, {})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_notuser_list_success(self):
        res = self.client.get(LIST_CREATE_SERVER_URL, {})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
