from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

CREATE_RESULT_URL = reverse("android:store")
LIST_RESULTS_URL = reverse("android:list")


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

    def test_user_create_result(self):
        pass

    def test_list_results_no_auth_ok(self):
        res = self.client.get(LIST_RESULTS_URL, {})
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_list_results_auth_ok(self):
        self.client.force_login(self.user)
        res = self.client.get(LIST_RESULTS_URL, {})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
