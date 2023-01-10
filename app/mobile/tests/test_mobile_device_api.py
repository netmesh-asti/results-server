from rest_framework.test import APIClient
from django.urls import reverse

import pytest
from pytest_drf import(
    ViewSetTest,
    UsesPostMethod,
    UsesGetMethod,
    UsesPatchMethod,
    UsesDeleteMethod,
    UsesListEndpoint,
    UsesDetailEndpoint,
    Returns200,
    Returns201,
    AsUser
)

from pytest_drf.util import url_for
from pytest_lambda import lambda_fixture, static_fixture


@pytest.mark.django_db(transaction=True)
class TestMobileDeviceAPI(ViewSetTest):

    list_url = lambda_fixture(
        lambda:
            reverse("mobile:mobile-device-list"))

    detail_url = lambda_fixture(
        lambda mobile_device:
            url_for("mobile:mobile-device-detail", mobile_device.pk))

    class TestCreate(
        UsesPostMethod,
        UsesListEndpoint,
        Returns201,
        AsUser('admin_user')
    ):
        @pytest.fixture
        def data(self, api_mobile_device_details):
            return api_mobile_device_details

    class TestList(
        UsesGetMethod,
        UsesListEndpoint,
        Returns200,
        AsUser("user")
    ):
        @pytest.fixture
        def client(self, unauthed_client, authenticated_user, agent):
            return authenticated_user
        """
        Test that a user can list assigned mobile devices
        """

    class TestRetrieve(
        UsesGetMethod,
        UsesDetailEndpoint,
        Returns200,
        AsUser("user")
    ):

        def test_device_retrieved_success(self,mobile_device, json):
            expected = mobile_device.id
            outcome = json.get('id')
            assert expected == outcome

    class TestUpdate(
        UsesPatchMethod,
        UsesDetailEndpoint,
        Returns200,
        AsUser("admin_user")
    ):
        data = static_fixture({"name": "updated_name"})

        def test_device_is_updated(self, data, json):
            print(json)
            expected = data["name"]
            outcome = json['name']
            assert expected == outcome














