from django.apps import apps as django_apps
from django.views.decorators.csrf import csrf_exempt
from drf_yasg.utils import swagger_auto_schema
from rest_framework import serializers, status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from spyne import Application
from spyne.protocol.http import HttpRpc
from spyne.protocol.json import JsonDocument
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication

from apps.address_registry.services import (
    CityNameService,
    CityService,
    ContinentService,
    CountryService,
    DocumentAuthorService,
    DocumentService,
)
from apps.address_registry.models import (
    Continent,
    Document,
)
from apps.address_registry.serializers import (
    ContinentCountrySettlementSerializer,
    DocumentSerializer,
)
from apps.address_registry.services import CityNameService, CityService

cities_application_soap = csrf_exempt(
    DjangoApplication(
        Application(
            [CityService, CityNameService],
            tns="cities_application_tns",
            name="CitiesApplication",
            in_protocol=Soap11(validator="lxml"),
            out_protocol=Soap11(validator="soft"),
        )
    )
)


cities_application_json = csrf_exempt(
    DjangoApplication(
        Application(
            [CityService, CityNameService],
            tns="cities_application_tns",
            name="CitiesApplication",
            in_protocol=HttpRpc(validator="soft"),
            out_protocol=JsonDocument(validator="soft"),
        )
    )
)


document_application_json = csrf_exempt(
    DjangoApplication(
        Application(
            [DocumentService, DocumentAuthorService],
            tns="document_application_tns",
            name="DocumentApplication",
            in_protocol=HttpRpc(validator="soft"),
            out_protocol=JsonDocument(validator="soft"),
        )
    )
)

document_application_soap = csrf_exempt(
    DjangoApplication(
        Application(
            [DocumentService, DocumentAuthorService],
            tns="document_application_tns",
            name="DocumentApplication",
            in_protocol=Soap11(validator="lxml"),
            out_protocol=Soap11(validator="soft"),
        )
    )
)

countries_application_json = csrf_exempt(
    DjangoApplication(
        Application(
            [ContinentService, CountryService],
            tns="countries_application_tns",
            name="CountryApplication",
            in_protocol=HttpRpc(validator="soft"),
            out_protocol=JsonDocument(validator="soft"),
        )
    )
)

countries_application_soap = csrf_exempt(
    DjangoApplication(
        Application(
            [ContinentService, CountryService],
            tns="countries_application_tns",
            name="CountryApplication",
            in_protocol=Soap11(validator="lxml"),
            out_protocol=Soap11(validator="soft"),
        )
    )
)


class GenerateTestDataSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1, max_value=1000, required=True)


class GenerateTestData(APIView):
    permission_classes = [
        IsAuthenticated,
    ]

    @swagger_auto_schema(request_body=GenerateTestDataSerializer)
    def post(self, request: Request, app_label: str, model_name: str) -> Response:
        try:
            model_class = django_apps.get_model(app_label, model_name)
        except LookupError:
            return Response(
                f"Django model '{model_name}' in app '{app_label}' does not exist", status=status.HTTP_404_NOT_FOUND
            )

        serializer = GenerateTestDataSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        if not callable(getattr(model_class, "generate_test_data", None)):
            return Response(
                f"Test data for model {model_class.__name__} cannot be generated", status=status.HTTP_404_NOT_FOUND
            )

        model_class.generate_test_data(quantity=serializer.validated_data["quantity"])

        return Response(status=status.HTTP_201_CREATED)


class DocumentViewSet(viewsets.ModelViewSet):
    queryset = Document.objects.all().prefetch_related("documentauthor")
    serializer_class = DocumentSerializer
    permission_classes = [
        IsAuthenticated,
    ]


class ContinentCountrySettlementViewSet(viewsets.ModelViewSet):
    queryset = Continent.objects.all().prefetch_related("countries__settlements")
    serializer_class = ContinentCountrySettlementSerializer
    permission_classes = [IsAuthenticated]
