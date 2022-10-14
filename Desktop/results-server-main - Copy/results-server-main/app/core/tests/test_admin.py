from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from core import models


class AdminSiteTests(TestCase):

    def setUp(self):
        self.nro_info = {
            "address": "test address",
            "region": "1",
        }
        self.nro = models.NtcRegionalOffice.objects.create(**self.nro_info)
        self.client = Client()
        email = 'admin@gmail.com'
        password = 'password123'
        first_name = 'NTC'
        last_name = 'Netmesh'

        self.admin_user = get_user_model().objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            nro=self.nro.id
        )

        self.client.force_login(self.admin_user)
        self.user = get_user_model().objects.create_user(
            email='tester@gmail.com',
            password='password123',
            first_name='Test', last_name='User',
            nro=self.nro
        )

    def test_users_listed(self):
        """Test that users are listed on user page"""
        url = reverse('admin:core_user_changelist')
        res = self.client.get(url)

        self.assertContains(res, self.user.first_name)
        self.assertContains(res, self.user.last_name)
        self.assertContains(res, self.user.email)
