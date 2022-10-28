from datetime import datetime
import pytz
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from durin.models import AuthToken, Client

from core.models import (
    MobileDevice,
    Server,
    NTCSpeedTest,
    NtcRegionalOffice
)

SPEEDTEST_LIST_CREATE_RESULT_URL = reverse("mobile:result")
SPEEDTEST_LIST_RESULT_URL = reverse("mobile:speedtest-list")
USER_LIST_RESULT_URL = reverse("mobile:user-tests-list")
DEVICE_CREATE_URL = reverse("mobile:mobile-device-list")
DEVICE_LIST_URL = reverse("mobile:mobile-device-list")


def create_user(is_admin=False, **params):
    if is_admin:
        params['email'] = 'super@gmail.com'
        params['is_staff'] = True
    return get_user_model().objects.create_user(**params)


class PrivateAndroidApiTests(TestCase):
    def setUp(self):
        self.nro_info = {
            "address": "test address",
            "region": "1",
        }
        self.nro = NtcRegionalOffice.objects.create(**self.nro_info)
        self.info = {
            "email": "netmesh@example.com",
            "password": "test123",
            "first_name": "netmesh",
            "last_name": "tester",
            "nro": self.nro
        }
        self.user = create_user(**self.info)
        self.admin = create_user(**self.info, is_admin=True)
        user2_info = self.info
        user2_info["email"] = "user2@example.com"
        self.user2 = create_user(**user2_info)
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
            "owner": self.user,
        }
        MobileDevice.objects.create(**device_details)

    @patch("core.utils.get_location")
    def test_user_create_result_success(self, patched_check):
        """Test user create results success"""
        patched_check.return_value = {
            "lat": 15.1240083,
            "lon": 120.6120233,
            "region": "NCR",
            "province": "Metro Manila",
            "municipality": "Quezon City",
            "barangay": "Krus Na Ligas"
        }

        obj = AuthToken.objects.create(user=self.user, client=self.test_client)
        self.client.credentials(Authorization='Token ' + obj.token)
        self.client.force_authenticate(user=self.user, token=obj.token)
        res = self.client.post(
            SPEEDTEST_LIST_CREATE_RESULT_URL,
            self.android_result)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_result_has_test_result(self):
        """Test that listing results has actual result"""
        obj = AuthToken.objects.create(user=self.user, client=self.test_client)
        self.client.credentials(Authorization='Token ' + obj.token)
        self.client.force_authenticate(user=self.user, token=obj.token)
        res = self.client.post(
            SPEEDTEST_LIST_CREATE_RESULT_URL,
            self.android_result)
        res = self.client.get(USER_LIST_RESULT_URL, {})
        self.assertIn('result', res.data[0].keys())

    def test_list_result_has_device(self):
        """test that individual result has device id"""
        obj = AuthToken.objects.create(user=self.user, client=self.test_client)
        self.client.credentials(Authorization='Token ' + obj.token)
        self.client.force_authenticate(user=self.user, token=obj.token)
        res = self.client.post(
            SPEEDTEST_LIST_CREATE_RESULT_URL,
            self.android_result)
        res = self.client.get(reverse("mobile:user-tests-list"), {})
        self.assertIn('test_device', res.data[0].keys())

    def test_list_results_no_auth_fail(self):
        """Test that listing NTC mobile results requires authentication"""
        res = self.client.get(SPEEDTEST_LIST_CREATE_RESULT_URL, {})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_results_auth_ok(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(USER_LIST_RESULT_URL, {})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    @patch("core.utils.get_location")
    def test_retrieve_user_results_success(self, patched_check):
        patched_check.return_value = {
            "lat": 15.1240083,
            "lon": 120.6120233,
            "region": "NCR",
            "province": "Metro Manila",
            "municipality": "Quezon City",
            "barangay": "Krus Na Ligas"
        }
        obj = AuthToken.objects.create(user=self.user, client=self.test_client)
        self.client.credentials(Authorization='Token ' + obj.token)
        self.client.force_authenticate(user=self.user, token=obj.token)
        res = self.client.post(
            SPEEDTEST_LIST_CREATE_RESULT_URL,
            self.android_result)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        test_obj = NTCSpeedTest.objects.get(tester_id=self.user.id)

        retrieve_url = reverse(
            "mobile:user-tests-detail",
            args=[test_obj.test_id])
        res = self.client.get(retrieve_url, {})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_staff_reg_device_success(self):
        device_details = {
            "name": "test_device",
            "serial_number": "1234567",
            "imei": "43432423432",
            "phone_model": "Samsung S22",
            "android_version": "8",
            "ram": "8",
            "storage": "10000",
            "owner": self.user2.id,
        }
        self.client.force_authenticate(user=self.admin)
        res = self.client.post(DEVICE_CREATE_URL, device_details)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_staff_list_device_success(self):
        self.client.force_authenticate(user=self.admin)
        res = self.client.get(DEVICE_LIST_URL, {})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_staff_retrieve_device_success(self):
        self.client.force_authenticate(user=self.admin)
        device_details = {
            "name": "test_device",
            "serial_number": "1234567",
            "imei": "43432423432",
            "phone_model": "Samsung S22",
            "android_version": "8",
            "ram": "8",
            "storage": "10000",
            "owner": self.user2.id,
        }
        res = self.client.post(DEVICE_CREATE_URL, device_details)
        res = self.client.get(reverse("mobile:mobile-device-detail",
                                      args=[self.user2.id]), {})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
