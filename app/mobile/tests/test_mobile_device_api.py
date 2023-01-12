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
class TestMobileDeviceAdminAPI(ViewSetTest):

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
        AsUser("admin_user")
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
        AsUser("admin_user")
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

    class TestAddUser(
        UsesPostMethod,
        Returns200,
        AsUser('admin_user')
    ):
        url = lambda_fixture(
            lambda mobile_device: url_for("mobile:mobile-device-add-user", mobile_device.pk)
        )
        data = lambda_fixture(
            lambda user, agent: {"user_id": [user.id]}
        )

    class TestRemoveUser(
        UsesPostMethod,
        UsesDetailEndpoint,
        Returns200,
        AsUser("admin_user")
    ):
        url = lambda_fixture(
            lambda user_mobile_device: url_for("mobile:mobile-device-remove-user", user_mobile_device.pk)
        )
        data = lambda_fixture(
            lambda user, agent: {"user": user.id},
            autouse=True
        )

    class TestActivate(
        UsesPostMethod,
        Returns200,
        AsUser('admin_user')
    ):
        url = lambda_fixture(
            lambda mobile_device: url_for("mobile:mobile-device-activation", mobile_device.pk)
        )
        data = lambda_fixture(
            lambda user, agent, mobile_device: {"is_active": False},
            autouse=True
        )

        def test_activation_is_performed(self, json):
            expected = False
            outcome = json['is_active']
            assert expected == outcome

    class TestLinkDevice(
        UsesPostMethod,
        Returns200,
        AsUser("user")
    ):


        url = lambda_fixture(
            lambda user, agent: url_for("mobile:mobile-device-link")
        )

        data = lambda_fixture(lambda user_mobile_device: {
            "imei": user_mobile_device.imei
        }, autouse=True)







