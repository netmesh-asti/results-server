import pytest
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from durin.models import Client, AuthToken

from pytest_drf import (
    ViewSetTest,
    UsesListEndpoint,
    UsesPostMethod,
    UsesPatchMethod,
    Returns200,
    Returns201,
    AsUser
)
from pytest_lambda import lambda_fixture, static_fixture
from pytest_drf.util import url_for
from pytest_assert_utils import assert_model_attrs

from app.settings import TEST_CLIENT_NAME
from core.models import (
    RfcDevice,
    RfcDeviceUser,
    MobileDevice
)

USER_MANAGE_URL = reverse("user:ft-list")  # create and list
GET_TOKEN_URL = reverse("user:token")

LIST_USERS_URL = reverse("user:ft-list")
RETRIEVE_FIELD_TESTER_URL = reverse("user:ft-list")
USER_PROFILE_URL = reverse("user:my-profile")


# def create_user(is_admin=False, **params):
#     if is_admin:
#         params['email'] = 'super@gmail.com'
#         params['is_staff'] = True
#     return get_user_model().objects.create_user(**params)
#
#
# class AdminUserAPITests(TestCase):
#     """Test Create User API (NTC)"""
#
#     def setUp(self):
#         regions = [region[0] for region in ntc_region_choices]
#         emails = ('user1', 'user2', 'user3', 'user4', 'user5')
#         self.ft = list()
#         self.nros = list()
#         for region, name in zip(regions, emails):
#             nro = models.NtcRegionalOffice.objects.create(**{"region": region})
#             new_user = get_user_model().objects.create_user(
#                 **{
#                     'email': f'{name}@example.com',
#                     'nro': nro
#                 }
#             )
#             self.ft.append(new_user)
#             self.nros.append(nro)
#         self.user_info = {
#             "email": "test@example.com",
#             "password": "test123",
#             "first_name": "netmesh",
#             "last_name": "tester",
#             "nro": self.nros[0]
#         }
#         self.user = create_user(**self.user_info)
#         self.admin_user = create_user(is_admin=True, **self.user_info)
#
#         self.client = APIClient()
#         Client.objects.create(name=TEST_CLIENT_NAME)
#
#     def test_not_authenticated_create_account_fail(self):
#         """Test that create user returns unauthorized if not authenticated"""
#         res = self.client.post(USER_MANAGE_URL, {})
#         self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
#
#     def test_not_admin_create_account_forbidden(self):
#         self.client.force_authenticate(user=self.user)
#         res = self.client.post(USER_MANAGE_URL, {})
#         self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
#
#     def test_admin_create_valid_user_success(self):
#         """test admin can create valid user successfully"""
#         payload = {
#             "email": "fieldtester@example.com",
#             "password": "test123",
#             "first_name": "netmesh",
#             "last_name": "tester",
#             "nro": self.nros[1].id
#         }
#
#         # only admins are allowed to create/update field testers
#         self.client.force_authenticate(user=self.admin_user)
#         res = self.client.post(USER_MANAGE_URL, data=payload)
#         self.assertEqual(res.status_code, status.HTTP_201_CREATED)
#         user = get_user_model().objects.get(email=res.data['email'])
#         self.assertTrue(user.check_password(payload['password']))
#         self.assertNotIn('password', res.data)
#
#     def test_list_users_success(self):
#         """test that only users from selected region is returned"""
#
#         self.client.force_authenticate(user=self.admin_user)
#         res = self.client.get(USER_MANAGE_URL,
#                               data={'nro': self.nros[1]})
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
#         items_str = json.dumps(res.data)
#         items = json.loads(items_str)
#         self.assertIn('id', items[0])

@pytest.mark.django_db
class TestAssignRfcDeviceToUser(
    ViewSetTest
):
    @pytest.fixture
    def data(self, user, rfc_device_details, durin_client):
        device = RfcDevice.objects.create(
            **rfc_device_details
        )

        return {
            "user": user.id,
            "device": device.id,
        }

    class TestAssignRfcDevice(
        UsesPostMethod,
        Returns200,
        AsUser('admin_user')
    ):
        url = lambda_fixture(lambda: reverse("user:ft-assign-rfc-device"))

        def test_instance_created(self, user, json):
            instance = RfcDeviceUser.objects.get(id=json['id'])
            # print(instance.device, instance.user)
            assert instance.user == user


@pytest.mark.django_db
class TestAssignMobileDeviceToUser(
    ViewSetTest
):
    @pytest.fixture
    def data(self, user, mobile_device_details, durin_client):
        device = MobileDevice.objects.create(
            **mobile_device_details
        )

        return {
            "user": user.id,
            "device": device.id,
        }

    # class TestAssignMobileDevice(
    #     UsesPostMethod,
    #     Returns200,
    #     AsUser('admin_user')
    # ):
    #     url = lambda_fixture(lambda: reverse("user:ft-assign-mobile-device"))
    #
    #     def test_instance_created(self, user, json):
    #         instance = MobileDeviceUser.objects.get(id=json['id'])
    #         # print(instance.device, instance.user)
    #         assert instance.user == user


@pytest.mark.django_db
class TestUserActiveInDB(
    ViewSetTest
):

    data = static_fixture({
        "is_active": False
    })

    class TestSetActive(
        UsesPatchMethod,
        Returns200,
        AsUser('admin_user')
    ):
        url = lambda_fixture(lambda user: url_for("user:ft-user-active", user.pk))

        def test_user_db_active_set(self, json):
            print(json)
            user = get_user_model().objects.get(id=json['id'])
            expected = False
            outcome = user.is_active
            assert expected == outcome
    # def test_retrieve_update_user_success(self):
    #     """test that admin can fetch field tester and update"""
    #     # only staffs are allowed to update
    #     self.client.force_authenticate(user=self.admin_user)
    #
    #     res = self.client.get(reverse('user:user-detail',
    #                                   args=[self.user.id]),
    #                           {})
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertIn("email", res.data)
    #
    #     # Update User Profile
    #     user_id = res.data['id']
    #     res = self.client.patch(reverse(
    #         "user:user-detail",
    #         args=[user_id]),
    #         {"first_name": "asti"}
    #     )
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     user = get_user_model().objects.get(id=user_id)
    #     self.assertEqual('asti', user.first_name)
    #
    # def test_retrieve_not_found_404(self):
    #     """test that retrieving not found user return 404"""
    #     retrieve_user_url = reverse("user:user-detail", args=[1])  # retrieve
    #     self.client.force_authenticate(user=self.admin_user)
    #     res = self.client.get(retrieve_user_url, {})
    #     self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
    #
    # def test_get_token_no_credentials_fail(self):
    #     """test login without credentials raises 400 Bad Request"""
    #     res = self.client.post(GET_TOKEN_URL, {})
    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    #
    # def test_get_token_bad_credentials_400(self):
    #     """test login with wrong credentials raises 400 Bad Request"""
    #     res = self.client.post(GET_TOKEN_URL, {
    #         "email": self,
    #         "password": "wrong_pass",
    #         })
    #     self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
    #
    # def test_get_token_valid_user_ok(self):
    #     """test that token is returned"""
    #     client = Client.objects.create(name="test_client")
    #     AuthToken.objects.create(client=client, user=self.user)
    #     res = self.client.post(GET_TOKEN_URL, {
    #                 "email": "test@example.com",
    #                 "client": "test_client",
    #                 "password": "test123",
    #         })
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     self.assertIn("token", res.data)
    #
    # def test_get_users_from_region_success(self):
    #     """test that only users from selected region is returned"""
    #
    #     self.client.force_authenticate(user=self.admin_user)
    #     res = self.client.get(USER_MANAGE_URL, {})
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     items_str = json.dumps(res.data)
    #     items = json.loads(items_str)
    #     nros = [nro['nro'] for nro in items]
    #     self.assertIn(
    #         self.admin_user.nro.region,
    #         nros[0].values())
    #     self.assertNotIn(self.nros[2], nros)

    # def test_get_users_no_admin_in_list(self):
    #     """test that no admin in the list"""
    #     # Disabled, allow admin in list 14/10/2022
    #     emails = ('admin1', 'admin2', 'admin3', 'admin4', 'admin5')
    #     for nro, name in zip(self.nros, emails):
    #         self.user_info['email'] = f'{name}@example.com'
    #         self.user_info['is_staff'] = True
    #         self.user_info['nro'] = nro
    #         self.new_user = get_user_model().objects.create_user(
    #             **self.user_info)
    #     self.client.force_authenticate(user=self.admin_user)
    #     res = self.client.get(USER_MANAGE_URL,
    #                           data={'nro': self.nros[1].id})
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     items_str = json.dumps(res.data)
    #     items = json.loads(items_str)
    #     ntc_users = [region['email'] for region in items]
    #     for email in ntc_users:
    #         user = get_user_model().objects.get(email=email)
    #         self.assertFalse(user.is_staff)

    # def test_delete_user_success(self):
    #     self.client.force_authenticate(self.admin_user)
    #     res = self.client.delete(reverse(
    #         "user:user-detail",
    #         args=[self.user.id]), {})
    #     self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
    #

    #
    # def test_assign_multiple_rfc_device_to_user_success(self):
    #     device_client1 = Client.objects.create(name="device1")
    #     device_client2 = Client.objects.create(name="device2")
    #     self.client.force_authenticate(self.admin_user)
    #     assign_rfc_url = reverse("user:user-assign-rfc-device",
    #                              args=[self.user.id])
    #     res = self.client.post(assign_rfc_url, {
    #         "name": device_client1.name
    #     })
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #     res = self.client.post(assign_rfc_url, {
    #         "name": device_client2.name
    #     })
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #
    # def test_remove_device_from_user(self):
    #     device_client1 = Client.objects.create(name="device1")
    #     self.client.force_authenticate(self.admin_user)
    #     assign_rfc_url = reverse("user:user-assign-rfc-device",
    #                              args=[self.user.id])
    #     res = self.client.post(assign_rfc_url, {
    #         "name": device_client1.name
    #     })
    #     self.assertEqual(res.status_code, status.HTTP_200_OK)
    #
    #     # Delete Device Token From user
    #     delete_rfc_url = reverse("user:user-remove-rfc-device",
    #                              args=[self.user.id])
    #     res = self.client.delete(delete_rfc_url, {
    #         "name": device_client1.name
    #     })
    #     self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


# class TestFieldUserAPITests(TestCase):
#
#     def setUp(self):
#         self.nro_info = {
#             "address": "test address",
#             "region": "1",
#         }
#         self.nro = models.NtcRegionalOffice.objects.create(**self.nro_info)
#         self.user_info = {
#             "email": "test@example.com",
#             "password": "test123",
#             "first_name": "netmesh",
#             "last_name": "tester",
#             "nro": self.nro
#         }
#         self.user = create_user(**self.user_info)
#         self.client = APIClient()
#         Client.objects.create(name=TEST_CLIENT_NAME)
#
#     def test_retrieve_profile_success(self):
#         """Test that field user can retrieve profile."""
#
#         client = Client.objects.create(name="test_client")
#         # AuthToken.objects.create(client=client, user=self.user)
#         # token = AuthToken.objects.get(user=self.user).token
#         obj = AuthToken.objects.create(user=self.user, client=client)
#         self.client.credentials(Authorization='Token ' + obj.token)
#         self.client.force_authenticate(user=self.user)
#         res = self.client.get(USER_PROFILE_URL, {
#         })
#         self.assertEqual(res.status_code, status.HTTP_200_OK)
