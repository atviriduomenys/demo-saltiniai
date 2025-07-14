import pytest
from model_bakery.baker import make
from spyne.client.django import DjangoTestClient

from apps.address_registry.models import (
    Country,
    Settlement,
    Title,
)
from apps.address_registry.views import cities_application_soap
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
