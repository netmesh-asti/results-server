import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core import models
from pytest_drf import(
    APIViewTest,
    Returns403,
    Returns201,
    Returns200,
    AsUser,
    AsAnonymousUser,
    UsesPostMethod,
    UsesGetMethod
)
from pytest_lambda import lambda_fixture, static_fixture

LIST_CREATE_SERVER_URL = reverse("server:servers")


pytestmark = pytest.mark.django_db


@pytest.fixture
def agent(user):
    return user


class TestServerAPI(
    APIViewTest,
    UsesPostMethod,
    Returns403,
    AsUser('agent')
):
    """Tests for the servers endpoint"""
    url = lambda_fixture(lambda: reverse("server:servers"))

    @pytest.fixture
    def data(self, server_info):
        return server_info


class TestAdminCreateSuccess(
    APIViewTest,
    Returns201,
    UsesPostMethod,
    AsUser('admin_user')
):

    url = lambda_fixture(lambda: reverse("server:servers"))

    @pytest.fixture
    def data(self, server_info):
        return server_info


class TestUserReadSuccess(
    APIViewTest,
    UsesGetMethod,
    Returns200,
    AsUser('user')
):
    url = lambda_fixture(lambda: reverse("server:servers"))


class TestAnonymousReadSuccess(
    APIViewTest,
    UsesGetMethod,
    Returns200,
    AsAnonymousUser
):
    url = lambda_fixture(lambda: reverse("server:servers"))
