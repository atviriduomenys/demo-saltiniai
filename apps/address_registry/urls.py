from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from apps.address_registry.views import (
    ContinentCountrySettlementViewSet,
    DocumentViewSet,
    GenerateTestData,
    cities_application_json,
    cities_application_soap,
    countries_application_json,
    countries_application_soap,
    document_application_json,
    document_application_soap,
)

router = DefaultRouter()
router.register(r"settlements", ContinentCountrySettlementViewSet, basename="settlements")
router.register(r"documents", DocumentViewSet, basename="documents")

urlpatterns = [
    path(
        "cities-app/",
        include(
            [
                re_path(r"^soap/", cities_application_soap),
                re_path(r"^json/", cities_application_json),
            ]
        ),
    ),
    path(
        "documents-app/",
        include(
            [
                re_path(r"^json/", document_application_json),
                re_path(r"^soap/", document_application_soap),
            ]
        ),
    ),
    path(
        "countries-app/",
        include(
            [
                re_path(r"^json/", countries_application_json),
                re_path(r"^soap/", countries_application_soap),
            ]
        ),
    ),
    path("<str:app_label>/<str:model_name>/generate/", GenerateTestData.as_view()),
    path("", include(router.urls)),
]
