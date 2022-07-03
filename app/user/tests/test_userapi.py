from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse("user:create")
RETRIEVE_USER_URL = reverse("user:me")
RETRIEVE_FIELD_TESTER_URL = reverse("user:account")


def create_user(is_admin=False, **params):
    if is_admin:
        params['email'] = 'super@gmail.com'
        params['is_staff'] = True
    return get_user_model().objects.create_user(**params)


class PrivateUserApiTests(TestCase):
    """Test Create User API (NTC)"""

    def setUp(self):
        self.user_info = {
                    "email": "test@gmail.com",
                    "password": "test123",
                    "first_name": "netmesh",
                    "last_name": "tester"
                }
        self.normal_user = create_user(**self.user_info)
        self.admin_user = create_user(is_admin=True, **self.user_info)
        self.client = APIClient()

    def test_create_not_authenticated_forbidden(self):
        res = self.client.post(CREATE_USER_URL, {})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_not_admin_create_account_forbidden(self):
        self.client.force_authenticate(user=self.normal_user)
        res = self.client.post(CREATE_USER_URL, {})
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_create_valid_user_success(self):
        """test admin can create valid user successfully"""
        payload = {
            "email": "fieldtester@gmail.com",
            "password": "test123",
            "first_name": "netmesh",
            "last_name": "tester",
            }

        # only admins are allowed to create/update field testers
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_retrieve_update_user_success(self):
        """test that admin can fetch fieldtester and update"""
        # only admin are allowed to update
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get(RETRIEVE_FIELD_TESTER_URL, {'email':
                                                          'test@gmail.com'})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data,
                         {"email": "test@gmail.com",
                          "first_name": "netmesh",
                          "last_name": "tester"})

        # Update User Profile
        res = self.client.patch(RETRIEVE_USER_URL,
                                {"first_name": "asti"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        user = get_user_model().objects.get(**res.data)
        self.assertEqual('asti', user.first_name)

    def test_retrieve_not_found_404(self):
        """test that retrieving not found user return 404"""
        self.client.force_authenticate(user=self.admin_user)
        res = self.client.get(RETRIEVE_FIELD_TESTER_URL,
                              {'email': 'none@gmail.com'})
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
