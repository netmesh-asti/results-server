from datetime import datetime
import pytz

import pytest
from durin.models import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from durin.models import AuthToken

from core import models
from rfc6349.views import ResultLocation


@pytest.fixture
def user_info():
    return {
        "email": 'test@example.com',
        "password": 'testpassword123',
        "first_name": 'NTC',
        "last_name": 'Netmesh',
    }


@pytest.fixture
def admin_info():
    return {
        "email": 'admin@example.com',
        "password": 'testpassword123',
        "first_name": 'ADMIN',
        "last_name": 'USER',
    }


@pytest.mark.django_db
@pytest.fixture
def user(user_info, office):
    user = get_user_model().objects.create_user(
        **user_info
    )
    return user


@pytest.mark.django_db
@pytest.fixture
def agent(user, office):
    return models.Agent.objects.create(
        agent=user,
        office=office
    )


@pytest.mark.django_db
@pytest.fixture
def admin_agent(admin_user, office):
    return models.Agent.objects.create(
        agent=admin_user,
        office=office
    )


@pytest.fixture
def nro_info():
    return {
        "address": "test address",
        "region": "1",
    }


@pytest.mark.django_db
@pytest.fixture
def nro(nro_info):
    return models.RegionalOffice.objects.create(**nro_info)


@pytest.mark.django_db
@pytest.fixture
def server(user):
    return models.Server.objects.create(
        **{
            "ip_address": "192.168.1.1",
            "server_type": "unknown",
            "lat": 14,
            "lon": 120,
            "contributor_id": user.id
        }
    )


@pytest.fixture
def server_info(user):
    return {
            "ip_address": "192.168.1.1",
            "server_type": "unknown",
            "lat": 14,
            "lon": 120,
            "contributor_id": user.id
        }




@pytest.mark.django_db
@pytest.fixture
def token_client():
    return Client.objects.create(name="TestClient")


# This suses server_id since we are accessing the model directly
@pytest.mark.django_db
@pytest.fixture
def mobile_result(server):
    return {
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
        "server_id": server.id,
    }


@pytest.fixture
def user_mobile_result(server):
    return {
        "android_version": "8",
        "ssid": "WIFI-1",
        "bssid": "C2sre23",
        "rssi": 3.1,
        "network_type": "LTE",
        "imei": "2566",
        "cell_id": "22",
        "mcc": "5",
        "mnc": "15",
        "tac": "1",
        "signal_quality": "Strong",
        "operator": "Smart",
        "lat": 14.02,
        "lon": 120.16,
        "download": 100.0,
        "upload": 100.0,
        "jitter": 1.0,
        "ping": 1.0,
        "timestamp": "2022-11-08 02:35:23.300Z",
        "success": True,
        "server": server.id,
    }


@pytest.fixture
def rfc_result(server):
    return {
        "direction": "forward",
        "mtu": 0,
        "rtt": 0,
        "bb": 0,
        "bdp": 0,
        "rwnd": 0,
        "thpt_avg": 0,
        "thpt_ideal": 0,
        "transfer_avg": 0,
        "transfer_ideal": 0,
        "tcp_ttr": 0,
        "tx_bytes": 0,
        "retx_bytes": 3.434,
        "tcp_eff": 100.0,
        "ave_rtt": 2.1,
        "buf_delay": 5.0,
        "lat": 14.0,
        "lon": 121.0,
        "location": "building",
        "server": server.id,
    }


@pytest.mark.django_db
@pytest.fixture
def mobile_device_details(mobile_client):
    return {
        "serial_number": "123456",
        "imei": "43432423432",
        "phone_model": "Samsung S22",
        "android_version": "8",
        "ram": "8",
        "storage": "10000",
        "client": mobile_client,
    }


@pytest.mark.django_db
@pytest.fixture
def api_mobile_device_details(mobile_client):
    return {
        "name": "Example_Name",
        "serial_number": "1234567",
        "imei": "434324234321",
        "phone_model": "Samsung S22",
        "android_version": "8",
        "ram": "8",
        "storage": "10000",
    }


@pytest.fixture
def rfc_device_details(agent, durin_client):
    return {
        "serial_number": "123456",
        "name": durin_client.name,
        "manufacturer": "ACER",
        "product": "Samsung S22",
        "version": "1",
        "os": "Ubuntu 22.04",
        "kernel": "5.15",
        "ram": "8",
        "disk": "10000",
        "client": durin_client
    }


@pytest.fixture
def api_rfc_device_details(agent, durin_client ):
    return {
        "serial_number": "123456",
        "name": "TestDevice",
        "manufacturer": "ACER",
        "product": "Samsung S22",
        "version": "1",
        "os": "Ubuntu 22.04",
        "kernel": "5.15",
        "ram": "8",
        "disk": "10000",
        "client": durin_client
    }


@pytest.mark.django_db
@pytest.fixture
def durin_client():
    return Client.objects.create(name="TestClient0")


@pytest.mark.django_db
@pytest.fixture
def mobile_client():
    return Client.objects.create(name="43432423432")


@pytest.mark.django_db
@pytest.fixture
def user_token(user, durin_client):
    token = AuthToken.objects.create(user=user, client=durin_client)
    return token


@pytest.mark.django_db
@pytest.fixture
def admin_token(admin, durin_client):
    token = AuthToken.objects.create(user=admin, client=durin_client)
    return token


@pytest.fixture
def mock_get_location(monkeypatch):
    monkeypatch.setattr(ResultLocation, "reverse_geo", lambda _: {
            "lat": 15.1240083,
            "lon": 120.6120233,
            "region": "NCR",
            "province": "Metro Manila",
            "municipality": "Quezon City",
            "barangay": "Krus Na Ligas"
        })


@pytest.fixture
def location():
    return {
            "lat": 15.1240083,
            "lon": 120.6120233,
            "region": "NCR",
            "province": "Metro Manila",
            "municipality": "Quezon City",
            "barangay": "Krus Na Ligas"
    }


@pytest.fixture
def authenticated_user(user, user_token):
    client = APIClient()
    client.credentials(**{
            "Authorization": "Token {}".format(user_token)
    })
    client.force_authenticate(user=user, token=user_token)
    return client


@pytest.fixture
def authenticated_staff(admin, admin_token):
    client = APIClient()
    client.credentials(**{
            "Authorization": "Token {}".format(admin_token)
    })
    client.force_authenticate(user=admin, token=admin_token)
    return client


@pytest.fixture
def office(nro):
    return models.Office.objects.create(
        name="Example_Agency",
        region=nro)


@pytest.fixture
@pytest.mark.django_db
def rfc_device(rfc_device_details):
    return models.RfcDevice.objects.create(
        **rfc_device_details
    )


@pytest.mark.django_db
@pytest.fixture
def mobile_device(mobile_client) -> models.MobileDevice:
    return models.MobileDevice.objects.create(**{
        "name": "Example Name",
        "serial_number": "123456",
        "imei": "43432423432",
        "phone_model": "Samsung S22",
        "android_version": "8",
        "ram": "8",
        "storage": "10000",
        "client": mobile_client,
    })


@pytest.mark.django_db
@pytest.fixture
def user_mobile_device(mobile_device, agent):
    mobile_device.users.add(agent)
    return mobile_device
