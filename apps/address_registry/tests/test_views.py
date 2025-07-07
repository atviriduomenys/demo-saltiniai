import datetime

import pytest
from model_bakery.baker import make
from spyne.client.django import DjangoTestClient

from apps.address_registry.models import (
    Country,
    County,
    Document,
    DocumentAuthor,
    Eldership,
    Municipality,
    Settlement,
    Title,
)
from apps.address_registry.views import cities_application_soap
from apps.utils.tests_query_counter import APIClientWithQueryCounter


class TestSettlement:
    def test_empty(self, client: APIClientWithQueryCounter) -> None:
        response = client.get("/api/v1/demo/json/settlement")

        assert response.status_code == 200
        assert response.json() == []

    def test_json(self, client: APIClientWithQueryCounter) -> None:
        settlement = make(Settlement)

        response = client.get("/api/v1/demo/json/settlement")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert response.json() == [
            {
                "id": settlement.id,
                "registered": settlement.registered,
                "deregistered": settlement.deregistered,
                "title_lt": settlement.title_lt,
                "area": settlement.area,
                "type": settlement.type,
                "country_id": settlement.country_id,
                "country_code": settlement.country_code,
            }
        ]

    def test_xml(self, client: APIClientWithQueryCounter) -> None:
        country: Country = make("Country", code="LT")
        settlement = make(
            Settlement,
            id=1,
            registered=datetime.date(2025, 7, 8),
            deregistered=datetime.date(2025, 7, 8),
            title_lt="Vilnius",
            area=1234.56,
            type="SMALL TOWN",
            country=country,
            country_code=country.code,
        )

        response = client.get("/api/v1/demo/xml/settlement")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/xml"
        response_content = response.content.decode("utf-8")
        assert response_content == (
            f"<?xml version='1.0' encoding='UTF-8'?>\n"
            f'<ns0:settlementResponse xmlns:ns0="demo_service_xml">'
            f'<ns1:settlementResult xmlns:ns1="demo_service_json">'
            f'<ns2:SettlementModel xmlns:ns2="apps.address_registry.schema">'
            f"<ns2:id>{settlement.id}</ns2:id>"
            f"<ns2:registered>{settlement.registered}</ns2:registered>"
            f"<ns2:deregistered>{settlement.deregistered}</ns2:deregistered>"
            f"<ns2:title_lt>{settlement.title_lt}</ns2:title_lt>"
            f"<ns2:area>{settlement.area}</ns2:area>"
            f"<ns2:type>{settlement.type}</ns2:type>"
            f"<ns2:country_id>{settlement.country_id}</ns2:country_id>"
            f"<ns2:country_code>{settlement.country_code}</ns2:country_code>"
            f"</ns2:SettlementModel></ns1:settlementResult></ns0:settlementResponse>"
        )

    def test_soap(self, client: APIClientWithQueryCounter) -> None:
        country: Country = make("Country", code="LT")
        settlement = make(
            Settlement,
            id=1,
            registered=datetime.date(2025, 7, 8),
            deregistered=datetime.date(2025, 7, 8),
            title_lt="Vilnius",
            area=1234.56,
            type="SMALL TOWN",
            country=country,
            country_code=country.code,
        )

        response = client.get("/api/v1/demo/soap/settlement")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/xml; charset=utf-8"
        response_content = response.content.decode("utf-8")
        assert response_content == (
            f"<?xml version='1.0' encoding='UTF-8'?>\n"
            f'<soap11env:Envelope xmlns:soap11env="http://schemas.xmlsoap.org/soap/envelope/">'
            f"<soap11env:Body>"
            f'<ns1:settlementResponse xmlns:ns1="demo_service_json">'
            f"<ns1:settlementResult>"
            f'<ns2:SettlementModel xmlns:ns2="apps.address_registry.schema">'
            f"<ns2:id>{settlement.id}</ns2:id>"
            f"<ns2:registered>{settlement.registered.isoformat()}</ns2:registered>"
            f"<ns2:deregistered>{settlement.deregistered.isoformat()}</ns2:deregistered>"
            f"<ns2:title_lt>{settlement.title_lt}</ns2:title_lt>"
            f"<ns2:area>{settlement.area}</ns2:area>"
            f"<ns2:type>{settlement.type}</ns2:type>"
            f"<ns2:country_id>{settlement.country_id}</ns2:country_id>"
            f"<ns2:country_code>{settlement.country_code}</ns2:country_code>"
            f"</ns2:SettlementModel>"
            f"</ns1:settlementResult>"
            f"</ns1:settlementResponse>"
            f"</soap11env:Body>"
            f"</soap11env:Envelope>"
        )

    def test_search(self, client: APIClientWithQueryCounter) -> None:
        make(Settlement, title_lt="foo")
        make(Settlement, title_lt="bar")

        response = client.get("/api/v1/demo/json/settlement?title_lt=foo")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestAddressRegistry:
    def test_json_response(self, client: APIClientWithQueryCounter) -> None:
        country = make(Country)
        settlement = make(
            Settlement, country=country, registered=datetime.date(2025, 7, 8), deregistered=datetime.date(2025, 7, 8)
        )
        title = make(Title, settlement=settlement)
        document1 = make(Document)
        document_author = make(DocumentAuthor, document=document1)
        document2 = make(Document)
        county = make(County, centre=settlement, country=country)
        municipality = make(Municipality, centre=settlement, country=country, county=county)
        eldership = make(Eldership, centre=settlement, country=country, municipality=municipality)

        response = client.get("/api/v1/demo/json/address_registry")

        assert response.status_code == 200
        assert response.json() == {
            "countries": [
                {
                    "id": country.id,
                    "code": country.code,
                    "title_lt": country.title_lt,
                    "title_en": country.title_en,
                    "title": country.title,
                    "continent_id": country.continent_id,
                },
            ],
            "settlements": [
                {
                    "id": settlement.id,
                    "registered": settlement.registered.isoformat(),
                    "deregistered": settlement.deregistered.isoformat(),
                    "title_lt": settlement.title_lt,
                    "area": settlement.area,
                    "type": settlement.type,
                    "country_id": country.id,
                    "country_code": settlement.country_code,
                },
            ],
            "titles": [
                {
                    "id": title.id,
                    "title": title.title,
                    "grammatical_case": title.grammatical_case,
                    "accented": title.accented,
                    "settlement_id": settlement.id,
                }
            ],
            "documents": [
                {
                    "id": document1.id,
                    "number": document1.number,
                    "received": document1.received.isoformat(),
                    "status": document1.status,
                    "type": document1.type,
                    "creation_date": document1.creation_date.isoformat(),
                    "creation_time": document1.creation_time.isoformat(),
                },
                {
                    "id": document2.id,
                    "number": document2.number,
                    "received": document2.received.isoformat(),
                    "status": document2.status,
                    "type": document2.type,
                    "creation_date": document2.creation_date.isoformat(),
                    "creation_time": document2.creation_time.isoformat(),
                },
            ],
            "document_authors": [
                {
                    "id": document_author.id,
                    "document_id": document1.id,
                    "name": document_author.name,
                    "surname": document_author.surname,
                }
            ],
            "counties": [
                {
                    "id": county.id,
                    "type": county.type,
                    "code": county.code,
                    "registered": county.registered,
                    "deregistered": county.deregistered,
                    "title": county.title,
                    "area": county.area,
                    "centre_id": settlement.id,
                    "country_id": county.country_id,
                    "country_code": county.country_code,
                }
            ],
            "municipalities": [
                {
                    "id": municipality.id,
                    "type": municipality.type,
                    "code": municipality.code,
                    "registered": municipality.registered,
                    "deregistered": municipality.deregistered,
                    "title": municipality.title,
                    "area": municipality.area,
                    "centre_id": settlement.id,
                    "country_id": municipality.country_id,
                    "country_code": municipality.country_code,
                    "county_id": county.id,
                }
            ],
            "elderships": [
                {
                    "id": eldership.id,
                    "type": eldership.type,
                    "code": eldership.code,
                    "registered": eldership.registered,
                    "deregistered": eldership.deregistered,
                    "title": eldership.title,
                    "area": eldership.area,
                    "centre_id": settlement.id,
                    "country_id": eldership.country_id,
                    "country_code": eldership.country_code,
                    "municipality_id": municipality.id,
                }
            ],
            "administrations": [],
        }


class TestAddressRegistryNested:
    def test_json_response(self, client: APIClientWithQueryCounter) -> None:
        country = make(Country)
        settlement = make(
            Settlement,
            registered=datetime.date(2025, 7, 8),
            deregistered=datetime.date(2025, 7, 8),
            country=country,
            country_code=country.code,
        )
        title = make(Title, settlement=settlement)
        county = make(County, centre=settlement, country=country)
        municipality = make(Municipality, country=country, county=county, centre=settlement)
        eldership = make(Eldership, centre=settlement, country=country, municipality=municipality)

        response = client.get("/api/v1/demo/json/address_registry_nested")
        assert response.status_code == 200

        expected_country = {
            "id": country.id,
            "code": country.code,
            "title_lt": country.title_lt,
            "title_en": country.title_en,
            "title": country.title,
            "continent_id": country.continent_id,
        }
        expected_settlement = {
            "id": settlement.id,
            "registered": settlement.registered.isoformat(),
            "deregistered": settlement.deregistered.isoformat(),
            "title_lt": settlement.title_lt,
            "area": settlement.area,
            "type": settlement.type,
            "country_id": country.id,
            "country_code": settlement.country_code,
            "country": expected_country,
            "title_forms": [
                {
                    "id": title.id,
                    "title": title.title,
                    "grammatical_case": title.grammatical_case,
                    "settlement_id": settlement.id,
                    "accented": title.accented,
                }
            ],
        }
        expected_county = {
            "id": county.id,
            "type": county.type,
            "code": county.code,
            "registered": county.registered,
            "deregistered": county.deregistered,
            "title": county.title,
            "area": county.area,
            "centre_id": settlement.id,
            "country_id": country.id,
            "country_code": county.country_code,
            "centre": expected_settlement,
            "country": expected_country,
        }
        expected_municipality = {
            "id": municipality.id,
            "type": municipality.type,
            "code": municipality.code,
            "registered": municipality.registered,
            "deregistered": municipality.deregistered,
            "title": municipality.title,
            "area": municipality.area,
            "centre_id": county.centre.id,
            "country_id": country.id,
            "country_code": municipality.country_code,
            "centre": expected_settlement,
            "country": expected_country,
            "county": expected_county,
            "county_id": county.id,
        }
        expected_eldership = {
            "id": eldership.id,
            "type": eldership.type,
            "code": eldership.code,
            "registered": eldership.registered,
            "deregistered": eldership.deregistered,
            "title": eldership.title,
            "area": eldership.area,
            "centre_id": municipality.county.centre.id,
            "country_id": country.id,
            "country_code": eldership.country_code,
            "centre": expected_settlement,
            "country": expected_country,
            "municipality": expected_municipality,
            "municipality_id": municipality.id,
        }
        assert response.json() == {
            "settlements": [expected_settlement],
            "counties": [expected_county],
            "municipalities": [expected_municipality],
            "elderships": [expected_eldership],
        }


@pytest.mark.parametrize(
    "endpoint", ["settlement", "title", "settlement_title", "address_registry", "address_registry_nested"]
)
@pytest.mark.parametrize(
    ("frmt", "content_type"), [("json", "application/json"), ("xml", "text/xml"), ("soap", "text/xml; charset=utf-8")]
)
def test_content_types(client: APIClientWithQueryCounter, endpoint: str, frmt: str, content_type: str) -> None:
    response = client.get(f"/api/v1/demo/{frmt}/{endpoint}")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == content_type


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
