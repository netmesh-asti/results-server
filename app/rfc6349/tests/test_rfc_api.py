from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core import models

LIST_CREATE_RFCRESULT_URL = reverse("rfc6349:result")


class TestRfcApi(TestCase):
    """Test RFC6349 Endpoints"""

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            **{
                "email": "test@example.com",
                "first_name": "TestFN",
                "last_name": "TestLN",
                "password": "testpassword123"
            }
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
        self.client = APIClient()

    def test_create_result_success(self):
        """Test that authenticated user can create results"""
        data = {
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
            "gps_lat": 14.0,
            "gps_lon": 122.0,
            "location": "building",
            "server_id": self.server.id,
            "tester_id": self.user.id
            }
        self.client.force_authenticate(user=self.user)
        res = self.client.post(LIST_CREATE_RFCRESULT_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
