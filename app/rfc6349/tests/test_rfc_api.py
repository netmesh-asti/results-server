from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from durin.models import AuthToken, Client

from core import models

LIST_CREATE_RFCRESULT_URL = reverse("rfc6349:result")
LIST_CREATE_RFCDEVICE_URL = reverse("rfc6349:device")


class TestRfcApi(TestCase):
    """Test RFC6349 Endpoints"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            **{
                "email": "admin@example.com",
                "first_name": "TestFN",
                "last_name": "TestLN",
                "password": "testpassword123"
            }
        )
        self.admin = get_user_model().objects.create_superuser(
            **{
                "email": "test@example.com",
                "first_name": "TestFN",
                "last_name": "TestLN",
                "password": "testpassword123"
            }
        )

        self.server = models.Server.objects.create(
            **{
                "ip_address": "192.168.1.1",
                "server_type": "unknown",
                "lat": 14,
                "lon": 120,
                "contributor_id": self.user.id
            }
        )
        self.data = {
            "direction": "forward",
            "mtu": 0,
            "rtt": 0,
            "bb": 0,
            "bdp": 0,
            "rwnd": 0,
            "thpt_avg": 0,
            "thpt_ideal": 0,
            "transfer_avg": 0,
            "transfer_ideal": 0,
            "tcp_ttr": 0,
            "tx_bytes": 0,
            "retx_bytes": 3.434,
            "tcp_eff": 100.0,
            "ave_rtt": 2.1,
            "buf_delay": 5.0,
            "gps_lat": 14.0,
            "gps_lon": 121.0,
            "location": "building",
            "server": self.server.id,
            }
        self.durin_client = Client.objects.create(name="TestClient")
        self.device_details = {
            "serial_number": "123456",
            "name": "TestDevice",
            "manufacturer": "ACER",
            "product": "Samsung S22",
            "version": "1",
            "os": "Ubuntu 22.04",
            "kernel": "5.15",
            "ram": "8",
            "disk": "10000",
            "client": self.durin_client,
            "user": self.user
            }
        self.client = APIClient()

    def test_create_result_success(self):
        """Test that authenticated user can post results"""
        obj = AuthToken.objects.create(
            client=self.durin_client,
            user=self.user)
        models.RfcDevice.objects.create(**self.device_details)
        self.client.force_authenticate(user=self.user, token=obj.token)
        res = self.client.post(LIST_CREATE_RFCRESULT_URL, self.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_result_anonymous_failure(self):
        """Test that unauthenticated user can't post results"""
        res = self.client.post(LIST_CREATE_RFCRESULT_URL, self.data)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_device_success(self):
        """Test that admin can create device for user"""
        device = {
            "serial_number": "123456",
            "name": "TestUserDevice",
            "manufacturer": "ACER",
            "product": "Samsung S22",
            "version": "1",
            "os": "Ubuntu 22.04",
            "kernel": "5.15",
            "ram": "8",
            "disk": "10000",
            "user": self.user.id
            }
        self.client.force_authenticate(user=self.admin)
        res = self.client.post(LIST_CREATE_RFCDEVICE_URL, device)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        client = Client.objects.get(name=device['name'])
        self.assertTrue(client)
