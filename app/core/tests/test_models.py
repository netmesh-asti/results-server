from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from core import models

from rest_framework.test import APIClient
from rest_framework import status


class testUserModel(TestCase):

    def test_create_user_success(self):
        """Test that normal user is created"""
        email = 'test@gmail.com'
        password = 'testpassword123'
        first_name = 'NTC',
        last_name = 'Netmesh'
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertTrue(user.check_password(password))

    def test_create_superuser_success(self):
        """Test that super user is created"""
        email = 'test@gmail.com'
        password = 'testpassword123'
        first_name = 'NTC',
        last_name = 'Netmesh'
        user = get_user_model().objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )

        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_serialized(self):
        """Test that the new user email is normalize (lowercase afer @)"""
        email = 'test@gmaIl.coM'
        user = get_user_model().objects.create_user(email, 'test123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'testpassword123')

class NtcObjectsTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            first_name='ntc',
            last_name='netmesh',
            password='testpass123'
        )

    def test_rfc_device(self):
        """Test rfcdevice is created successfuly"""
        #staff = get_user_model().objects.create_superuser(
        #    email='admin@gmail.com',
        #    first_name='admin',
        #    last_name='netmesh',
        #    password='testpass123'

        #)
        device = models.RfcDevice.objects.create(
            manufacturer='MSI',
            product='GF63',
            version='1.0',
            user = self.user,
        )

        self.assertEqual(device.manufacturer, 'MSI')
        self.assertEqual(device.product, 'GF63')
        self.assertEqual(device.version, '1.0')
        self.assertEqual(device.user, self.user)

    def test_field_tester(self):
        """Test Field Tester Created successfully"""

        device = models.RfcDevice.objects.create(
            manufacturer='MSI',
            product='GF63',
            version='1.0',
            user = self.user,
        )

        fieldtester = models.FieldTester.objects.create(
            user = self.user,
            device_kind='computer',
            device=device,

        )
        self.assertEqual(fieldtester.user, self.user)
        self.assertEqual(fieldtester.ntc_region, 'unknown')
        self.assertEqual(fieldtester.device_kind, 'computer')
        self.assertEqual(fieldtester.device, device)
