from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

LIST_CREATE_RESULT_URL = reverse("android:result")


def create_user(is_admin=False, **params):
    if is_admin:
        params['email'] = 'super@gmail.com'
        params['is_staff'] = True
    return get_user_model().objects.create_user(**params)


class PublicAndroidApiTests(TestCase):
    def setUp(self):
        self.info = {
            "email": "netmesh@gmail.com",
            "password": "test123",
            "first_name": "netmesh",
            "last_name": "tester"
            }
        self.user = create_user(**self.info)
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
            "lat": 14.02,
            "lon": 120.16,
            }

    def test_user_create_result(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(LIST_CREATE_RESULT_URL, self.android_result)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_list_results_no_auth_ok(self):
        res = self.client.get(LIST_CREATE_RESULT_URL, {})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_results_auth_ok(self):
        self.client.force_authenticate(self.user)
        res = self.client.get(LIST_CREATE_RESULT_URL, {})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
