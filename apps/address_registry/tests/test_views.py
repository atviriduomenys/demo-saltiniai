import base64

import pytest
from model_bakery.baker import make
from spyne.client.django import DjangoTestClient

from apps.address_registry.models import (
    Continent,
    Country,
    Document,
    DocumentAuthor,
    Settlement,
    Title,
)
from apps.address_registry.views import (
    cities_application_soap,
    countries_application_soap,
    document_application_soap,
)
from apps.utils.tests_query_counter import APIClientWithQueryCounter


class TestCitiesApplicationSoap:
    @pytest.fixture
    def client(self) -> DjangoTestClient:
        return DjangoTestClient("/api/v1/cities-app/soap/", cities_application_soap.app)

    def test_city_response(self, client: DjangoTestClient) -> None:
        settlement = make(Settlement)
        title1 = make(Title, grammatical_case="GENITIVE", settlement=settlement)
        title2 = make(Title, grammatical_case="NOMINATIVE", settlement=settlement)

        response = client.service.cities.get_django_response()
        assert response.status_code == 200

        response_data = list(client.service.cities())
        assert len(response_data) == 1

        data = response_data[0]
        assert data.id == settlement.id
        assert len(data.title_forms) == 2
        assert {data.title_forms[0].id, data.title_forms[1].id} == {title1.id, title2.id}

    def test_city_name_response(self, client: DjangoTestClient) -> None:
        settlement = make(Settlement)
        title = make(Title, settlement=settlement)

        response = client.service.city_names.get_django_response()
        assert response.status_code == 200

        response_data = list(client.service.city_names())
        assert len(response_data) == 1

        data = response_data[0]
        assert data.id == title.id
        assert data.settlement.id == settlement.id

    def test_city_name_response_with_request_body(self, client: DjangoTestClient) -> None:
        settlement = make(Settlement, title_lt="TestName")
        title1 = make(Title, settlement=settlement, grammatical_case="NOMINATIVE", title="name1")
        make(Title, settlement=settlement, grammatical_case="GENITIVE", title="name2")

        request_data = {
            "city_name_filter": {
                "title": "name1",
                "grammatical_case": "NOMINATIVE",
                "settlement": {
                    "title": "TestName",
                },
            }
        }
        response = client.service.city_names.get_django_response(**request_data)
        assert response.status_code == 200

        response_data = list(client.service.city_names(**request_data))
        assert len(response_data) == 1

        data = response_data[0]
        assert data.id == title1.id
        assert data.settlement.id == settlement.id


class TestCitiesApplicationJson:
    def test_city_response(self, client: APIClientWithQueryCounter) -> None:
        settlement = make(Settlement)
        title1 = make(Title, grammatical_case="GENITIVE", settlement=settlement)
        title2 = make(Title, grammatical_case="NOMINATIVE", settlement=settlement)

        response = client.get("/api/v1/cities-app/json/cities")
        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data) == 1

        data = response_data[0]
        assert data["id"] == settlement.id
        assert len(data["title_forms"]) == 2
        assert {data["title_forms"][0]["id"], data["title_forms"][1]["id"]} == {
            title1.id,
            title2.id,
        }

    def test_city_name_response(self, client: APIClientWithQueryCounter) -> None:
        settlement = make(Settlement)
        title = make(Title, grammatical_case="GENITIVE", settlement=settlement)

        response = client.get("/api/v1/cities-app/json/city_names")
        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data) == 1

        data = response_data[0]
        assert data["id"] == title.id
        assert data["settlement"]["id"] == settlement.id


class TestGenerateTestData:
    @staticmethod
    def get_url(model_name: str) -> str:
        return f"/api/v1/address_registry/{model_name}/generate/"

    def test_return_403_when_not_authenticated(self, client: APIClientWithQueryCounter) -> None:
        response = client.post(self.get_url("country"))
        assert response.status_code == 401

    def test_return_404_when_model_does_not_exist(self, authorized_client: APIClientWithQueryCounter) -> None:
        response = authorized_client.post(self.get_url("foo"), data={"quantity": 1})
        assert response.status_code == 404

    def test_return_400_when_serializer_not_valid(self, authorized_client: APIClientWithQueryCounter) -> None:
        response = authorized_client.post(self.get_url("country"), data={"quantity": "foo"})
        assert response.status_code == 400

    def test_return_404_when_model_has_no_generate_data_method(
        self, authorized_client: APIClientWithQueryCounter
    ) -> None:
        response = authorized_client.post(self.get_url("documentauthor"), data={"quantity": 1})
        assert response.status_code == 404

    def test_return_201_when_data_is_generated(self, authorized_client: APIClientWithQueryCounter) -> None:
        assert Country.objects.all().count() == 0

        response = authorized_client.post(self.get_url("country"), data={"quantity": 1})
        assert response.status_code == 201
        assert Country.objects.all().count() == 1

    def test_generate_multiple_objects(self, authorized_client: APIClientWithQueryCounter) -> None:
        assert Country.objects.all().count() == 0

        response = authorized_client.post(self.get_url("country"), data={"quantity": 2})
        assert response.status_code == 201
        assert Country.objects.all().count() == 2

    @pytest.mark.parametrize("client", [100], indirect=True)
    def test_related_objects_generated_using_same_country_instance(
        self, authorized_client: APIClientWithQueryCounter
    ) -> None:
        response = authorized_client.post(self.get_url("eldership"), data={"quantity": 1})

        assert response.status_code == 201
        assert Country.objects.all().count() == 1


class TestDocumentsApplicationSoap:
    @pytest.fixture
    def client(self) -> DjangoTestClient:
        return DjangoTestClient("/api/v1/documents-app/soap/", document_application_soap.app)

    def test_document_response(self, client: DjangoTestClient) -> None:
        document = make(Document)
        response = client.service.documents.get_django_response()
        assert response.status_code == 200

        response_data = list(client.service.documents())
        assert len(response_data) == 1

        data = response_data[0]
        assert data.id == document.id
        assert data.document_author is None

    def test_document_author_response(self, client: DjangoTestClient) -> None:
        document_author = make(DocumentAuthor)
        response = client.service.document_authors.get_django_response()
        assert response.status_code == 200

        response_data = list(client.service.document_authors())
        assert len(response_data) == 1

        data = response_data[0]
        assert data.id == document_author.id
        assert data.document_id == document_author.document_id

    def test_document_response_with_request_body(self, client: DjangoTestClient) -> None:
        needed_document = make(Document, type="ORDER", status="REGISTERED", _quantity=3)
        make(Document, type="ORDER", status="CANCELLED", _quantity=2)

        request_data = {
            "document_filter": {
                "type": "ORDER",
                "status": "REGISTERED",
            }
        }

        response = client.service.documents.get_django_response(**request_data)
        assert response.status_code == 200

        response_data = list(client.service.documents(**request_data))
        assert len(response_data) == 3

        data = response_data[0]
        assert data.id == needed_document[0].id
        assert data.document_author is None


class TestCountryApplicationSoap:
    @pytest.fixture
    def client(self) -> DjangoTestClient:
        return DjangoTestClient("/api/v1/countries-app/soap/", countries_application_soap.app)

    def test_country_response(self, client: DjangoTestClient) -> None:
        country = make(Country)
        response = client.service.countries.get_django_response()
        assert response.status_code == 200

        response_data = list(client.service.countries())
        assert len(response_data) == 1

        data = response_data[0]
        assert data.id == country.id
        assert data.continent_id == country.continent_id

    def test_continent_response(self, client: DjangoTestClient) -> None:
        continent = make(Continent)
        response = client.service.continents.get_django_response()
        assert response.status_code == 200

        response_data = list(client.service.continents())
        assert len(response_data) == 1

        data = response_data[0]
        assert data.code == continent.code
        assert data.name == continent.name

    def test_country_response_with_request_body(self, client: DjangoTestClient) -> None:
        needed_country = make(Country, code=1, title_lt="title1", _quantity=3)
        make(Country, code="LT", _quantity=2)

        request_data = {
            "country_filter": {
                "code": "1",
                "title": "title1",
            }
        }

        response = client.service.countries.get_django_response(**request_data)
        assert response.status_code == 200

        response_data = list(client.service.countries(**request_data))
        assert len(response_data) == 3

        data = response_data[0]
        assert data.id == needed_country[0].id
        assert data.continent_id == needed_country[0].continent_id


class TestDocumentsApplicationJson:
    def test_document_response(self, client: APIClientWithQueryCounter) -> None:
        document = make(Document)
        response = client.get("/api/v1/documents-app/json/documents")
        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data) == 1

        data = response_data[0]
        assert data.get("id") == document.id
        assert data.get("document_author") is None

    def test_document_author_response(self, client: APIClientWithQueryCounter) -> None:
        document_author = make(DocumentAuthor)

        response = client.get("/api/v1/documents-app/json/document_authors")
        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data) == 1

        data = response_data[0]
        assert data.get("id") == document_author.id
        assert data.get("document_id") == document_author.document_id


class TestCountryApplicationJson:
    def test_country_response(self, client: APIClientWithQueryCounter) -> None:
        country = make(Country)
        response = client.get("/api/v1/countries-app/json/countries")
        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data) == 1

        data = response_data[0]
        assert data.get("id") == country.id
        assert data.get("continent_id") == country.continent_id

    def test_continent_response(self, client: APIClientWithQueryCounter) -> None:
        continent = make(Continent)

        response = client.get("/api/v1/countries-app/json/continents")
        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data) == 1

        data = response_data[0]
        assert data.get("code") == continent.code
        assert data.get("name") == continent.name


class TestGetDataEndpoints:
    @staticmethod
    def get_url(model_name: str) -> str:
        return f"/api/v1/{model_name}/"

    @pytest.mark.parametrize("endpoint_name", ["documents", "settlements"])
    def test_return_401_when_not_authenticated(self, client: APIClientWithQueryCounter, endpoint_name: str) -> None:
        response = client.get(self.get_url(endpoint_name))
        assert response.status_code == 401

    @pytest.mark.parametrize("endpoint_name", ["documents", "settlements"])
    def test_no_data_exists_in_db(self, authorized_client: APIClientWithQueryCounter, endpoint_name: str) -> None:
        response = authorized_client.get(self.get_url(endpoint_name))
        assert response.data == []

    def test_document_author_data_returned(self, authorized_client: APIClientWithQueryCounter) -> None:
        document = make(Document)
        document_author = make(DocumentAuthor, document=document)
        response = authorized_client.get(self.get_url("documents"))
        assert response.data == [
            {
                "id": document.id,
                "number": document.number,
                "received": document.received.isoformat(),
                "content": base64.b64encode(document.content).decode(),
                "status": document.status,
                "type": document.type,
                "creation_date": document.creation_date.isoformat(),
                "creation_time": document.creation_time.isoformat(),
                "document_author": {
                    "id": document_author.id,
                    "name": document_author.name,
                    "surname": document_author.surname,
                    "passport": None,
                    "document": document.id,
                },
            }
        ]

    def test_settlement_data_returned(self, authorized_client: APIClientWithQueryCounter) -> None:
        continent = make(Continent)
        country = make(Country, continent=continent)
        settlement = make(Settlement, country=country)
        title = make(Title, settlement=settlement)
        response = authorized_client.get(self.get_url("settlements"))
        assert response.data == [
            {
                "code": continent.code,
                "name": continent.name,
                "countries": [
                    {
                        "id": country.id,
                        "code": country.code,
                        "title": country.title,
                        "title_lt": country.title_lt,
                        "title_en": country.title_en,
                        "continent": country.continent_id,
                        "settlements": [
                            {
                                "id": settlement.id,
                                "registered": settlement.registered,
                                "deregistered": settlement.deregistered,
                                "title_lt": settlement.title_lt,
                                "area": settlement.area,
                                "type": settlement.type,
                                "country_code": settlement.country.code,
                                "country": settlement.country.id,
                                "title_forms": [
                                    {
                                        "id": title.id,
                                        "title": title.title,
                                        "accented": title.accented,
                                        "grammatical_case": title.grammatical_case,
                                        "settlement": title.settlement.id,
                                    }
                                ],
                            }
                        ],
                    }
                ],
            }
        ]
