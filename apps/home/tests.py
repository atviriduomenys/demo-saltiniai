import re

import pytest
from django.conf import settings
from django.contrib.admin import site
from django.contrib.admindocs.views import simplify_regex
from django.db.models import Model
from django.urls import reverse
from django_extensions.management.commands.show_urls import Command
from model_bakery.baker import make
from rest_framework import status

from apps.utils.tests_query_counter import APIClientWithQueryCounter


def get_model_name(value):
    admin = value  # because [site._registry[model]] is a model name inside a list
    return f"{admin.model._meta.model_name}"


class TestAdminSmokerCase:
    exclude = [
        "home_siteconfiguration_add",
        "home_siteconfiguration_delete",
        "admin_logentry_add",
        "admin_logentry_delete",
        "admin_logentry_list",
    ]

    @pytest.fixture
    def authorized_admin_client(self, client: APIClientWithQueryCounter, superuser, user_credentials):
        client.login(**user_credentials)
        return client

    def test_admin_index(self, authorized_admin_client):
        response = authorized_admin_client.get(reverse("admin:index"))
        assert response.status_code == status.HTTP_200_OK, response.request

    @pytest.mark.parametrize("site_admin", [site._registry[model] for model in site._registry], ids=get_model_name)
    def test_admin(self, site_admin, authorized_admin_client: APIClientWithQueryCounter):
        obj: Model = make(site_admin.model)
        for url in site_admin.urls:
            args = []
            if not url.name or url.name.endswith("autocomplete") or url.name in self.exclude:
                continue

            if getattr(url.pattern, "_route", "").startswith(("<path:object_id>", "<id>")):
                args = [obj.pk]

            response = authorized_admin_client.get(reverse(f"admin:{url.name}", args=args), query_limit=9)
            assert response.status_code == status.HTTP_200_OK, url.name


class TestUrlPathPatterns:
    """Ensure that all URL paths comply with the best practices.

    It is possible to face hard to debug issues, when URL paths do not comply with
    the best practices. For example, when a URL path is missing trailing / Django
    usually redirects the request to another URL, which has trailing /.
    The body of PUT/POST request is being lost during this redirection.
    This test suite makes sure that such cases are avoided by forcing
    each registered URL path to comply with these rules:
    - ends with a slash,
    - does not contain upper-cased letters,
    - does not contain underscores;
    """

    @staticmethod
    def get_url_paths_and_names():
        urlconf = __import__(settings.ROOT_URLCONF, {}, {}, [""])  # Taken from django_extensions source
        extracted_views_paths_and_names = Command().extract_views_from_urlpatterns(urlconf.urlpatterns)
        url_paths_and_names = [(simplify_regex(e[1]), e[2]) for e in extracted_views_paths_and_names]
        return url_paths_and_names

    url_paths_and_names = get_url_paths_and_names()
    url_paths_and_names_excluding_admin = [
        (path, name) for path, name in url_paths_and_names if not path.startswith("/admin/")
    ]

    @pytest.mark.parametrize(("path", "path_name"), url_paths_and_names)
    def test_url_path_ends_with_underscores(self, path, path_name):
        if not (path.endswith("/") or path.endswith("<path>") or path.endswith("<url>")):
            raise AssertionError(f"Path {path} <{path_name}> does not end with /")

    @pytest.mark.parametrize(("path", "path_name"), url_paths_and_names)
    def test_url_paths_do_not_contain_upper_letters(self, path, path_name):
        path_without_params = re.sub("<.*?>", "", path)
        if path_without_params.lower() != path_without_params:
            raise AssertionError(f"Path {path} <{path_name}> contains upper letters")

    # Allowing underscores in admin URL paths, since they are autogenerated and use package name inside URLs.
    # BE team has agreed that we should allow using underscores in the package names, since they improve readability.
    @pytest.mark.parametrize(("path", "path_name"), url_paths_and_names_excluding_admin)
    def test_url_paths_do_not_contain_underscores(self, path, path_name):
        path_without_params = re.sub("<.*?>", "", path)

        if "_" in path_without_params:
            raise AssertionError(f"Path {path} <{path_name}> contains underscores, use dashes instead")
