import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from durin.models import AuthToken, Client
from rfc6349.views import Gis

from pytest_drf import(
    APIViewTest,
    Returns201,
    Returns200,
    AsUser,
    UsesPostMethod,
    UsesGetMethod
)
from pytest_lambda import lambda_fixture, static_fixture

from core import models


pytestmark = pytest.mark.django_db


class TestUserCreateResultAPI(
    APIViewTest,
    UsesPostMethod,
    Returns201,
    AsUser('user')
):
    """Test RFC6349 Endpoints"""

    url = lambda_fixture(lambda: reverse("rfc6349:result"))

    # mock get_location so that we don't query the api everytime

    @pytest.fixture
    def data(self, rfc_result, mock_get_location, monkeypatch):
        def mockreturn(*args, **kwargs):
            return {
                "lat": 15.1240083,
                "lon": 120.6120233,
                "region": "NCR",
                "province": "Metro Manila",
                "municipality": "Quezon City",
                "barangay": "Krus Na Ligas"
            }
        # mock get_location to that we don't query the api everytime
        monkeypatch.setattr(Gis, "find_location", mockreturn)
        return rfc_result

    @pytest.fixture
    def client(self, unauthed_client, user, durin_client, rfc_device_details):
        models.RfcDevice.objects.create(**rfc_device_details)
        obj = AuthToken.objects.create(
            client=durin_client,
            user=user)
        client = APIClient()
        client.credentials(Authorization='Token ' + obj.token)
        client.force_authenticate(user=user, token=obj.token)
        return client

    def test_create_result_success(self, json, rfc_result):
        """Test that authenticated user can post results"""

        expected = "test_id"
        outcome = json.keys()
        assert expected in outcome

    # def test_create_result_anonymous_failure(self):
    #     """Test that unauthenticated user can't post results"""
    #     res = self.client.post(LIST_CREATE_RFCRESULT_URL, self.data)
    #     self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
    #

    @pytest.mark.django_db
    def test_user_has_multiple_tokens_success(self, json, user, durin_client):
        """Test that user can create result with correct client."""
        Client.objects.create(name="TestClient1")
        Client.objects.create(name="TestClient2")
        expected = "test_id"
        outcome = json.keys()
        assert expected in outcome


class TestAdminCreateRfcDeviceAPI(
    APIViewTest,
    Returns201,
    UsesPostMethod,
    AsUser('admin_user')
):

    url = lambda_fixture(lambda: reverse("rfc6349:rfc-device-list"))

    @pytest.fixture
    def data(self, api_rfc_device_details):
        return api_rfc_device_details

    def test_create_device_success(self, json, api_rfc_device_details):
        """Test that admin can create device for user"""
        device_name = api_rfc_device_details.get('name')
        client = Client.objects.get(name=json['name'])
        expected = device_name
        outcome = client.name
        assert expected == outcome


class TestAdminListDevices(
    APIViewTest,
    UsesGetMethod,
    Returns200,
    AsUser('admin_user')
):

    url = lambda_fixture(lambda: reverse("rfc6349:rfc-device-list") )

    def test_list_device_success(self, rfc_device, json):
        """Test that Admin can list all registered devices"""
        assert len(json) > 0
