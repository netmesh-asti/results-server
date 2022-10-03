from datetime import datetime
import pytz

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from durin.models import AuthToken, Client

from core.models import (
    MobileDevice,
    Server,
    Location
)


LIST_CREATE_RESULT_URL = reverse("mobile:result")
LIST_NTC_RESULTS_URL = reverse("mobile:ntc-list")


def create_user(is_admin=False, **params):
    if is_admin:
        params['email'] = 'super@gmail.com'
        params['is_staff'] = True
    return get_user_model().objects.create_user(**params)


class PublicAndroidApiTests(TestCase):
    def setUp(self):
        self.info = {
            "email": "netmesh@example.com",
            "password": "test123",
            "first_name": "netmesh",
            "last_name": "tester"
            }
        self.user = create_user(**self.info)
        self.server = Server.objects.create(
            **{
                "ip_address": "192.168.1.1",
                "server_type": "unknown",
                "lat": 14,
                "lon": 120,
                "contributor_id": self.user.id
            }
        )
        self.client = APIClient()

        self.android_result = {
            "phone_model": "Samsung S22",
            "android_version": "8",
            "ssid": "WIFI-1",
            "bssid": "C2sre23",
            "rssi": 3.1,
            "network_type": "LTE",
            "imei": 2566,
            "cellid": 22,
            "mcc": 5,
            "mnc": 15,
            "tac": 1,
            "signal_quality": "Strong",
            "operator": "Smart",
            "lat": 15.02,
            "lon": 120.16,
            "upload": 100000000,
            "download": 200000000,
            "jitter": 0.0001,
            "ping": 0.03,
            "timestamp": datetime.now(tz=pytz.UTC),
            "success": True,
            "server": self.server.id
            }
        client_name = "TestClient"
        self.test_client = Client.objects.create(name=client_name)
        device_details = {
            "serial_number": "123456",
            "imei": "43432423432",
            "phone_model": "Samsung S22",
            "android_version": "8",
            "ram": "8",
            "storage": "10000",
            "client": self.test_client,
            "user": self.user,
        }
        MobileDevice.objects.create(**device_details)

    def test_user_create_result_success(self):
        """Test user create results success"""
        loc = {
            "lat": 15.1240083,
            "lon": 120.6120233,
            "region": "NCR",
            "province": "Metro Manila",
            "municipality": "Quezon City",
            "barangay": "Krus Na Ligas"
        }
        Location.objects.create(**loc)
        obj = AuthToken.objects.create(user=self.user, client=self.test_client)
        self.client.credentials(Authorization='Token ' + obj.token)
        self.client.force_authenticate(user=self.user, token=obj.token)
        res = self.client.post(LIST_CREATE_RESULT_URL, self.android_result)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_result_has_test_result(self):
        """Test that listing results has actual result"""
        obj = AuthToken.objects.create(user=self.user, client=self.test_client)
        self.client.credentials(Authorization='Token ' + obj.token)
        self.client.force_authenticate(user=self.user, token=obj.token)
        res = self.client.post(LIST_CREATE_RESULT_URL, self.android_result)
        res = self.client.get(LIST_CREATE_RESULT_URL, {})
        self.assertIn('timestamp', res.data[0])

    def test_list_result_has_device(self):
        """test that individual result has device id"""
        obj = AuthToken.objects.create(user=self.user, client=self.test_client)
        self.client.credentials(Authorization='Token ' + obj.token)
        self.client.force_authenticate(user=self.user, token=obj.token)
        res = self.client.post(LIST_CREATE_RESULT_URL, self.android_result)
        res = self.client.get(LIST_NTC_RESULTS_URL, {})
        self.assertIn('test_device', res.data[0].keys())

    def test_list_results_no_auth_fail(self):
        """Test that listing NTC mobile results requires authentication"""
        res = self.client.get(LIST_CREATE_RESULT_URL, {})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_results_auth_ok(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(LIST_CREATE_RESULT_URL, {})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
