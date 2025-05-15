from django.urls import include, path, re_path

from apps.address_registry.views import (
    GenerateTestData,
    cities_application_json,
    cities_application_soap,
    demo_application_json,
    demo_application_soap,
    demo_application_xml,
)

urlpatterns = [
    path(
        "demo/",
        include(
            [
                re_path(r"^json/", demo_application_json),
                re_path(r"^soap/", demo_application_soap),
                re_path(r"^xml/", demo_application_xml),
            ]
        ),
    ),
    path(
        "cities-app/",
        include(
            [
                re_path(r"^soap/", cities_application_soap),
                re_path(r"^json/", cities_application_json),
            ]
        ),
    ),
    path("<str:app_label>/<str:model_name>/generate/", GenerateTestData.as_view()),
]
