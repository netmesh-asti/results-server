import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from durin.models import Client, AuthToken

from app.settings import TEST_CLIENT_NAME
from core.choices import ntc_region_choices

USER_MANAGE_URL = reverse("user:user-list")  # create and list
GET_TOKEN_URL = reverse("user:token")

LIST_USERS_URL = reverse("user:user-list")
RETRIEVE_FIELD_TESTER_URL = reverse("user:user-list")
USER_PROFILE_URL = reverse("user:my-profile")


def create_user(is_admin=False, **params):
    if is_admin:
        params['email'] = 'super@gmail.com'
        params['is_staff'] = True
    return get_user_model().objects.create_user(**params)


class AdminUserAPITests(TestCase):
    """Test Create User API (NTC)"""

    def setUp(self):
        self.user_info = {
                    "email": "test@example.com",
                    "password": "test123",
                    "first_name": "netmesh",
                    "last_name": "tester",
                    "ntc_region": "unknown"
                }
        self.user = create_user(**self.user_info)
        self.admin_user = create_user(is_admin=True, **self.user_info)
        self.regions = [region[0] for region in ntc_region_choices]
        emails = ('user1', 'user2', 'user3', 'user4', 'user5')
        for region, name in zip(self.regions, emails):
            self.user_info['email'] = f'{name}@example.com'
            self.user_info['ntc_region'] = region
            self.new_user = get_user_model().objects.create_user(
                **self.user_info)
        self.client = APIClient()
        Client.objects.create(name=TEST_CLIENT_NAME)

    def test_not_authenticated_create_account_fail(self):
        """Test that create user returns unauthorized if not authenticated"""
        res = self.client.post(USER_MANAGE_URL, {})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_not_admin_create_account_forbidden(self):
        self.client.force_authenticate(user=self.user)
        res = self.client.post(USER_MANAGE_URL, {})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_create_valid_user_success(self):
        """test admin can create valid user successfully"""
        payload = {
            "email": "fieldtester@example.com",
            "password": "test123",
            "first_name": "netmesh",
            "last_name": "tester",
            "ntc_region": "1"
        }

        # only admins are allowed to create/update field testers
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.post(USER_MANAGE_URL, data=payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=res.data['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_list_users_success(self):
        """test that only users from selected region is returned"""

        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get(USER_MANAGE_URL,
                              data={'ntc_region': self.regions[1]})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        items_str = json.dumps(res.data)
        items = json.loads(items_str)
        self.assertIn('id', items[0])

    def test_retrieve_update_user_success(self):
        """test that admin can fetch field tester and update"""
        # only staffs are allowed to update
        self.client.force_authenticate(user=self.admin_user)

        res = self.client.get(reverse('user:user-detail', args=[self.user.id]),
                              {})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("email", res.data)

        # Update User Profile
        user_id = res.data['id']
        res = self.client.patch(reverse(
            "user:user-detail",
            args=[user_id]),
            {"first_name": "asti"}
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user = get_user_model().objects.get(id=user_id)
        self.assertEqual('asti', user.first_name)

    def test_retrieve_not_found_404(self):
        """test that retrieving not found user return 404"""
        retrieve_user_url = reverse("user:user-detail", args=[1])  # retrieve
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get(retrieve_user_url, {})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_token_no_credentials_fail(self):
        """test login without credentials raises 400 Bad Request"""
        res = self.client.post(GET_TOKEN_URL, {})
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_token_bad_credentials_400(self):
        """test login with wrong credentials raises 400 Bad Request"""
        res = self.client.post(GET_TOKEN_URL, {
            "email": self,
            "password": "wrong_pass",
            })
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_token_valid_user_ok(self):
        """test that token is returned"""
        client = Client.objects.create(name="test_client")
        AuthToken.objects.create(client=client, user=self.user)
        res = self.client.post(GET_TOKEN_URL, {
                    "email": "test@example.com",
                    "client": "test_client",
                    "password": "test123",
            })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("token", res.data)

    def test_get_users_from_region_success(self):
        """test that only users from selected region is returned"""

        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get(USER_MANAGE_URL,
                              data={'ntc_region': self.regions[1]})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        items_str = json.dumps(res.data)
        items = json.loads(items_str)
        ntc_regions = [region['ntc_region'] for region in items]
        self.assertIn(self.admin_user.ntc_region, ntc_regions)
        self.assertNotIn(self.regions[2], ntc_regions)

    def test_get_users_no_admin_in_list(self):
        """test that no admin in the list"""
        emails = ('admin1', 'admin2', 'admin3', 'admin4', 'admin5')
        for region, name in zip(self.regions, emails):
            self.user_info['email'] = f'{name}@example.com'
            self.user_info['is_staff'] = True
            self.user_info['ntc_region'] = region
            self.new_user = get_user_model().objects.create_user(
                **self.user_info)
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get(USER_MANAGE_URL,
                              data={'ntc_region': self.regions[1]})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        items_str = json.dumps(res.data)
        items = json.loads(items_str)
        ntc_users = [region['email'] for region in items]
        for email in ntc_users:
            user = get_user_model().objects.get(email=email)
            self.assertFalse(user.is_staff)

    def test_delete_user_success(self):
        self.client.force_authenticate(self.admin_user)
        res = self.client.delete(reverse(
            "user:user-detail",
            args=[self.user.id]), {})
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_assign_rfc_device_to_user_success(self):
        device_client1 = Client.objects.create(name="device1")
        self.client.force_authenticate(self.admin_user)
        assign_rfc_url = reverse("user:user-assign-rfc-device",
                                 args=[self.user.id])
        res = self.client.post(assign_rfc_url, {
            "name": device_client1.name
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_assign_multiple_rfc_device_to_user_success(self):
        device_client1 = Client.objects.create(name="device1")
        device_client2 = Client.objects.create(name="device2")
        self.client.force_authenticate(self.admin_user)
        assign_rfc_url = reverse("user:user-assign-rfc-device",
                                 args=[self.user.id])
        res = self.client.post(assign_rfc_url, {
            "name": device_client1.name
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        res = self.client.post(assign_rfc_url, {
            "name": device_client2.name
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_remove_device_from_user(self):
        device_client1 = Client.objects.create(name="device1")
        self.client.force_authenticate(self.admin_user)
        assign_rfc_url = reverse("user:user-assign-rfc-device",
                                 args=[self.user.id])
        res = self.client.post(assign_rfc_url, {
            "name": device_client1.name
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # Delete Device Token From user
        delete_rfc_url = reverse("user:user-remove-rfc-device",
                                 args=[self.user.id])
        res = self.client.delete(delete_rfc_url, {
            "name": device_client1.name
        })
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


class TestFieldUserAPITests(TestCase):

    def setUp(self):
        self.user_info = {
            "email": "test@example.com",
            "password": "test123",
            "first_name": "netmesh",
            "last_name": "tester",
            "ntc_region": "unknown"
        }
        self.user = create_user(**self.user_info)
        self.client = APIClient()
        Client.objects.create(name=TEST_CLIENT_NAME)

    def test_retrieve_profile_success(self):
        """Test that field user can retrieve profile."""

        client = Client.objects.create(name="test_client")
        # AuthToken.objects.create(client=client, user=self.user)
        # token = AuthToken.objects.get(user=self.user).token
        obj = AuthToken.objects.create(user=self.user, client=client)
        self.client.credentials(Authorization='Token ' + obj.token)
        self.client.force_authenticate(user=self.user)
        res = self.client.get(USER_PROFILE_URL, {
        })
        self.assertEqual(res.status_code, status.HTTP_200_OK)
