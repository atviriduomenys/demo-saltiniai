from django.urls import include, path, re_path
from rest_framework.routers import DefaultRouter

from apps.address_registry.views.rc_broker_views import get_data
from apps.address_registry.views.sodra_views import skola_sodrai
from apps.address_registry.views.views import (
    ContinentCountrySettlementViewSet,
    DocumentViewSet,
    GenerateTestData,
    cities_application_json,
    cities_application_soap,
    cities_application_xml,
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
        "cities/",
        include(
            [
                re_path(r"^soap/", cities_application_soap),
                re_path(r"^json/", cities_application_json),
                re_path(r"^xml/", cities_application_xml),
            ]
        ),
    ),
    path(
        "documents/",
        include(
            [
                re_path(r"^json/", document_application_json),
                re_path(r"^soap/", document_application_soap),
            ]
        ),
    ),
    path(
        "countries/",
        include(
            [
                re_path(r"^json/", countries_application_json),
                re_path(r"^soap/", countries_application_soap),
            ]
        ),
    ),
    re_path(r"^rc/get-data/", get_data),
    re_path(r"^sodra/skola-sodrai/", skola_sodrai),
    path("<str:app_label>/<str:model_name>/generate/", GenerateTestData.as_view()),
    path("", include(router.urls)),
]
