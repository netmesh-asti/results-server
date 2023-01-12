from datetime import datetime
import pytz

import pytest

from django.contrib.auth import get_user_model

from durin.models import Client

from core import models
from core.models import RfcDevice


@pytest.mark.django_db
class TestUserModel:

    def test_create_user_success(self, user_info, user):
        """Test that normal user is created"""

        assert user.email == user_info.get("email")

    def test_create_superuser_success(self, user_info):
        """Test that superuser is created"""
        user = get_user_model().objects.create_superuser(
            **user_info
        )
        assert user.is_staff == True

    def test_user_email_serialized(self, nro):
        """Test that the new user email is normalize (lowercase afer @)"""
        email = 'test@gmaIl.coM'
        user = get_user_model().objects.create_user(
            email,
            'test123'
        )
        assert user.email == email.lower()

    def test_invalid_email_failed(self):
        """Test creating user with no email raises error"""
        with pytest.raises(ValueError):
            get_user_model().objects.create_user(None, 'testpassword123')


@pytest.mark.django_db
class TestRfcDeviceModel:

    def test_rfc_device_create_success(self, agent, token_client):
        """Test that rfc device is created successfully"""
        rfc_device_info = {
            "manufacturer": 'MSI',
            "product": 'GF63',
            "version": '1.0',
            "client": token_client
        }
        device: RfcDevice = models.RfcDevice.objects.create(
            **rfc_device_info
        )

        assert rfc_device_info.get("manufacturer") == device.manufacturer


@pytest.mark.django_db
class TestMobileModel:
    def test_mobile_device_create_success(self, mobile_device_details):
        device = models.MobileDevice.objects.create(**mobile_device_details)
        assert device.serial_number == mobile_device_details['serial_number']

    def test_create_result_success(self, mobile_result):
        obj = models.MobileResult.objects.create(**mobile_result)
        expected = mobile_result.get('rssi')
        actual = obj.rssi
        assert expected == actual


@pytest.mark.django_db
class TestServerModel():
    """Test Server Model creation"""

    def test_create_server_success(self, user):
        server_details = {
                "ip_address": "192.168.1.1",
                "server_type": "local",
                "lat": 14,
                "lon": 120,
                "contributor": user
        }
        server = models.Server.objects.create(**server_details)
        expected = server_details['ip_address']
        outcome = server.ip_address
        assert expected == outcome
