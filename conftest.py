import logging
from pathlib import Path

import pytest
from model_bakery import generators
from model_bakery.baker import make

from apps.utils.tests_query_counter import APIClientWithQueryCounter
from apps.utils.token_helpers import get_token


@pytest.fixture(autouse=True)
def enable_db_access(db):
    """Global DB access to all tests."""
    pass


@pytest.fixture(autouse=True)
def add_richtextfield():
    generators.add("ckeditor.fields.RichTextField", generators.random_gen.gen_text)


@pytest.fixture(autouse=True, scope="session")
def disable_logging():
    logging.disable(logging.INFO)
    yield
    logging.disable(logging.NOTSET)


@pytest.fixture
def client(request) -> APIClientWithQueryCounter:
    """Using rest framework's api client instead of built-in django test client since we'll be working with APIs"""
    return APIClientWithQueryCounter(count=getattr(request, "param", 20))


@pytest.fixture(scope="session")
def user_credentials():
    return {
        "username": "test@test.lt",
        "email": "test@test.lt",
        "password": "Testtest5$",
    }


@pytest.fixture(scope="session")
def user_data(user_credentials):
    return {
        **user_credentials,
        "first_name": "First",
        "last_name": "Last",
        "phone_number": "+1234567890",
    }


@pytest.fixture
def user(user_credentials, django_user_model):
    user = make(django_user_model, **user_credentials)
    user.set_password(user_credentials["password"])
    user.save(update_fields=["password"])
    return user


@pytest.fixture
def superuser(user):
    user.is_staff = True
    user.is_superuser = True
    user.save(update_fields=["is_staff", "is_superuser"])
    return user


@pytest.fixture
def authorized_client(client: APIClientWithQueryCounter, user):
    refresh = get_token(user)
    client.credentials(HTTP_AUTHORIZATION=f"Token {str(refresh.access_token)}")
    return client


@pytest.fixture
def temp_media(settings, tmp_path: Path) -> Path:
    media = tmp_path / "media"
    media.mkdir()
    settings.MEDIA_ROOT = media
    return media
