from datetime import datetime, timedelta

import pytest
import pytz
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from pytest_drf import (
    APIViewTest,
    ViewSetTest,
    UsesListEndpoint,
    Returns201,
    Returns200,
    UsesGetMethod,
    UsesPostMethod,
    AsUser
)

from pytest_lambda import lambda_fixture

from durin.models import AuthToken, Client

from core.models import (
    MobileDevice,
    MobileResult,
    Location,
    NTCSpeedTest,
    Server,
    NTCSpeedTest,
    NtcRegionalOffice
)

from core.utils import Gis

SPEEDTEST_LIST_CREATE_RESULT_URL = reverse("mobile:result")
SPEEDTEST_LIST_RESULT_URL = reverse("mobile:speedtest-list")
USER_LIST_RESULT_URL = reverse("mobile:user-tests-list")
DEVICE_CREATE_URL = reverse("mobile:mobile-device-list")
DEVICE_LIST_URL = reverse("mobile:mobile-device-list")


@pytest.mark.django_db
def create_user(is_admin=False, **params):
    if is_admin:
        params['email'] = 'super@gmail.com'
        params['is_staff'] = True
    return get_user_model().objects.create_user(**params)


@pytest.mark.django_db
class TestMobileResultAPI(
    APIViewTest,
    Returns201,
    UsesPostMethod,
    AsUser('user')
):

    url = lambda_fixture(lambda: reverse("mobile:result"))

    @pytest.fixture
    def data(self, user_mobile_result):
        return user_mobile_result

    @pytest.fixture
    def client(self, unauthed_client, user, user_token, mobile_device_details):
        MobileDevice.objects.create(**mobile_device_details)
        client = APIClient()
        client.credentials(**{"Authorization": "Token {}".format(user_token)})
        client.force_authenticate(user=user)
        return client

    def test_user_create_result_success(self, json, user_mobile_result, monkeypatch):
        """Test user create results success"""
        def mockreturn():
            return {
                "lat": 15.1240083,
                "lon": 120.6120233,
                "region": "NCR",
                "province": "Metro Manila",
                "municipality": "Quezon City",
                "barangay": "Krus Na Ligas"
            }
        # mock get_location to that we don't query the api everytime
        monkeypatch.setattr(Gis, "get_location", mockreturn)
        ph_offset = timedelta(hours=8)
        result_ts = user_mobile_result['timestamp']
        result_dt = datetime.strptime(result_ts, '%Y-%m-%d %H:%M:%S.%fZ')
        result_dt = result_dt + ph_offset
        result_ts = result_dt.astimezone(pytz.timezone("Asia/Manila")).isoformat()
        user_mobile_result['timestamp'] = result_ts
        expected = user_mobile_result
        outcome = json

        assert expected == outcome

        # self.assertEqual(res.status_code, status.HTTP_201_CREATED)


@pytest.mark.django_db
class TestFTResultsViewset(ViewSetTest,):
    list_url = lambda_fixture(lambda: reverse("mobile:user-tests-list"))

    class TestList(
        UsesListEndpoint,
        UsesGetMethod,
        Returns200,
        AsUser('user'),
    ):
        @pytest.fixture
        def client(self,
                   unauthed_client,
                   user,
                   user_token,
                   mobile_result,
                   mobile_device_details,
                   location,
                   ):
            mobile_result = MobileResult.objects.create(**mobile_result)
            test_loc = Location.objects.create(**location)
            mob_device = MobileDevice.objects.create(
                **mobile_device_details)
            res = NTCSpeedTest.objects.create(
                tester=user,
                result=mobile_result,
                location=test_loc,
                test_device=mob_device,
                client_ip="127.0.0.1"
            )
            client = APIClient()
            client.credentials(**{
                "Authorization": "Token {}".format(user_token)
            })
            client.force_authenticate(user=user)
            return client

        def test_list_result_has_test_result(self, json):
            """Test that listing results has actual result"""
            outcome = len(json)
            expected = 1
            assert expected == outcome

    # def test_list_result_has_device(self):
    #     """test that individual result has device id"""
    #     obj = AuthToken.objects.create(user=self.user, client=self.test_client)
    #     self.client.credentials(Authorization='Token ' + obj.token)
    #     self.client.force_authenticate(user=self.user, token=obj.token)
    #     res = self.client.post(
    #         SPEEDTEST_LIST_CREATE_RESULT_URL,
    #         self.android_result)
    #     res = self.client.get(reverse("mobile:user-tests-list"), {})
    #     self.assertIn('test_device', res.data[0].keys())
    #
    # def test_list_results_no_auth_fail(self):
    #     """Test that listing NTC mobile results requires authentication"""
    #     res = self.client.get(SPEEDTEST_LIST_CREATE_RESULT_URL, {})
    #     self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    #
    # def test_list_results_auth_ok(self):
    #     self.client.force_authenticate(self.user)
    #     res = self.client.get(USER_LIST_RESULT_URL, {})
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #
    # @patch("core.utils.get_location")
    # def test_retrieve_user_results_success(self, patched_check):
    #     patched_check.return_value = {
    #         "lat": 15.1240083,
    #         "lon": 120.6120233,
    #         "region": "NCR",
    #         "province": "Metro Manila",
    #         "municipality": "Quezon City",
    #         "barangay": "Krus Na Ligas"
    #     }
    #     obj = AuthToken.objects.create(user=self.user, client=self.test_client)
    #     self.client.credentials(Authorization='Token ' + obj.token)
    #     self.client.force_authenticate(user=self.user, token=obj.token)
    #     res = self.client.post(
    #         SPEEDTEST_LIST_CREATE_RESULT_URL,
    #         self.android_result)
    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    #     test_obj = NTCSpeedTest.objects.get(tester_id=self.user.id)
    #
    #     retrieve_url = reverse(
    #         "mobile:user-tests-detail",
    #         args=[test_obj.test_id])
    #     res = self.client.get(retrieve_url, {})
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #
    # def test_staff_reg_device_success(self):
    #     device_details = {
    #         "name": "test_device",
    #         "serial_number": "1234567",
    #         "imei": "43432423432",
    #         "phone_model": "Samsung S22",
    #         "android_version": "8",
    #         "ram": "8",
    #         "storage": "10000",
    #         "owner": self.user2.id,
    #     }
    #     self.client.force_authenticate(user=self.admin)
    #     res = self.client.post(DEVICE_CREATE_URL, device_details)
    #     self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    #
    # def test_staff_list_device_success(self):
    #     self.client.force_authenticate(user=self.admin)
    #     res = self.client.get(DEVICE_LIST_URL, {})
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #
    # def test_staff_retrieve_device_success(self):
    #     self.client.force_authenticate(user=self.admin)
    #     device_details = {
    #         "name": "test_device",
    #         "serial_number": "1234567",
    #         "imei": "43432423432",
    #         "phone_model": "Samsung S22",
    #         "android_version": "8",
    #         "ram": "8",
    #         "storage": "10000",
    #         "owner": self.user2.id,
    #     }
    #     res = self.client.post(DEVICE_CREATE_URL, device_details)
    #     res = self.client.get(reverse("mobile:mobile-device-detail",
    #                                   args=[self.user2.id]), {})
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
