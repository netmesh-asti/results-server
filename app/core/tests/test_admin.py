import pytest

from rest_framework.test import APIClient

from django.contrib.auth import get_user_model
from django.urls import reverse

from pytest_drf import AsUser, UsesGetMethod, Returns200, APIViewTest
from pytest_lambda import lambda_fixture

pytestmark = pytest.mark.django_db


@pytest.fixture
def admin(user_info):
    user_info['email'] = "admin@example.com"
    admin = get_user_model().objects.create_superuser(
        **user_info
    )
    return admin


class TestAdminSiteListUsers(
    APIViewTest,
    UsesGetMethod,
    Returns200,
    AsUser("admin")
):
    url = lambda_fixture(lambda: reverse('admin:core_user_changelist'))

    @pytest.fixture
    def client(self, unauthed_client, admin):
        client = APIClient()
        client.force_login(user=admin)
        return client

    def test_user_listed(self, response, user_info):
        """Test that users are listed on user page"""
        first_name = user_info['first_name']
        outcome = response.render().content.decode()
        assert first_name in outcome

