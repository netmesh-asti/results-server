from datetime import datetime
import pytz

from django.test import TestCase
from django.contrib.auth import get_user_model

from durin.models import Client

from core import models


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
        self.client = Client.objects.create(name="DjangoTest")

    def test_rfc_device(self):
        """Test rfcdevice is created successfuly"""
        device = models.RfcDevice.objects.create(
            manufacturer='MSI',
            product='GF63',
            version='1.0',
            client=self.client,
            user=self.user
        )

        self.assertEqual(device.manufacturer, 'MSI')
        self.assertEqual(device.product, 'GF63')
        self.assertEqual(device.version, '1.0')
        self.assertEqual(device.client, self.client)


class TestMobileModel(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@example.com',
            first_name='ntc',
            last_name='netmesh',
            password='testpass123'
        )
        self.server = models.Server.objects.create(
            **{
                "ip_address": "192.168.1.1",
                "server_type": "unknown",
                "lat": 14,
                "lon": 120,
                "contributor_id": self.user.id
            }
        )
        self.client = Client.objects.create(name="DjangoTest")

    def test_create_mobiledevice(self):
        device_details = {
            "serial_number": "123456",
            "imei": "43432423432",
            "phone_model": "Samsung S22",
            "android_version": "8",
            "ram": "8",
            "storage": "10000",
            "client": self.client,
            "user": self.user
        }
        device = models.MobileDevice.objects.create(**device_details)
        self.assertEqual(device.serial_number, device_details['serial_number'])

    def test_create_result_success(self):
        android_result = {
            "android_version": "8",
            "ssid": "WIFI-1",
            "bssid": "C2sre23",
            "rssi": 3.1,
            "network_type": "LTE",
            "imei": 2566,
            "cell_id": 22,
            "mcc": 5,
            "mnc": 15,
            "tac": 1,
            "signal_quality": "Strong",
            "operator": "Smart",
            "lat": 14.02,
            "lon": 120.16,
            "timestamp": datetime.now(tz=pytz.UTC),
            "success": True,
            "server_id": self.server.id
            }
        obj = models.MobileResult.objects.create(**android_result)
        self.assertEqual(obj.rssi, 3.1)


class ServerModelTests(TestCase):
    """Test Server Model creation"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email='test@gmail.com',
            first_name='ntc',
            last_name='netmesh',
            password='testpass123'
        )

    def test_create_server_success(self):
        data = {
                "ip_address": "192.168.1.1",
                "server_type": "local",
                "lat": 14,
                "lon": 120,
                "contributor": self.user
        }
        server = models.Server.objects.create(**data)
        self.assertEqual(server.ip_address, data['ip_address'])
