from datetime import datetime
import pytz

import pytest
from durin.models import Client
from django.contrib.auth import get_user_model

from durin.models import AuthToken

from core import models
from rfc6349.views import ResultLocation


@pytest.fixture
def user_info(nro):
    return {
        "email": 'test@example.com',
        "password": 'testpassword123',
        "first_name": 'NTC',
        "last_name": 'Netmesh',
        "nro": nro
    }


@pytest.fixture
def admin_info(nro):
    return {
        "email": 'admin@example.com',
        "password": 'testpassword123',
        "first_name": 'ADMIN',
        "last_name": 'USER',
        "nro": nro
    }


@pytest.mark.django_db
@pytest.fixture
def user(user_info):
    return get_user_model().objects.create_user(
        **user_info
    )


@pytest.mark.django_db
@pytest.fixture
def admin(admin_info):
    return get_user_model().objects.create_superuser(
        **admin_info
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
    return models.NtcRegionalOffice.objects.create(**nro_info)


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
def client():
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
def mobile_device_details(mobile_client, user):
    return {
        "serial_number": "123456",
        "imei": "43432423432",
        "phone_model": "Samsung S22",
        "android_version": "8",
        "ram": "8",
        "storage": "10000",
        "client": mobile_client,
        "owner": user
    }


@pytest.fixture
def rfc_device_details(user, durin_client ):
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
        "client": durin_client,
        "owner": user
    }

@pytest.fixture
def api_rfc_device_details(user, durin_client ):
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
        "client": durin_client,
        "owner": user.id
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
