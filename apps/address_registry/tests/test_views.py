from datetime import date

import pytest

from apps.address_registry.models import Gyvenviete
from apps.utils.tests_query_counter import APIClientWithQueryCounter


def create_gyvenviete(pavadinimas="test_name") -> Gyvenviete:
    return Gyvenviete.objects.create(
        isregistruota=date(2024, 3, 3),
        registruota=date(2024, 3, 3),
        pavadinimas=pavadinimas,
        kurortas=True,
        plotas=1123,
        tipas="MIESTELIS",
    )


class TestListGyvenviete:
    def test_empty(self, client: APIClientWithQueryCounter) -> None:
        response = client.get("/api/v1/demo/json/gyvenviete")

        assert response.status_code == 200
        assert response.json() == []

    def test_json(self, client: APIClientWithQueryCounter) -> None:
        gyvenviete = create_gyvenviete()

        response = client.get("/api/v1/demo/json/gyvenviete")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert response.json() == [
            {
                "id": gyvenviete.id,
                "isregistruota": "2024-03-03",
                "registruota": "2024-03-03",
                "pavadinimas": "test_name",
                "kurortas": True,
                "plotas": 1123.0,
                "tipas": "MIESTELIS",
            }
        ]

    def test_xml(self, client: APIClientWithQueryCounter) -> None:
        gyvenviete = create_gyvenviete()

        response = client.get("/api/v1/demo/xml/gyvenviete")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/xml"
        response_content = response.content.decode("utf-8")
        assert response_content == (
            f"<?xml version='1.0' encoding='UTF-8'?>\n"
            f'<ns0:gyvenvieteResponse xmlns:ns0="demo_service_xml">'
            f'<ns1:gyvenvieteResult xmlns:ns1="demo_service_json">'
            f'<ns2:GyvenvieteBaseModel xmlns:ns2="apps.address_registry.schema">'
            f"<ns2:id>{gyvenviete.id}</ns2:id>"
            f"<ns2:isregistruota>2024-03-03</ns2:isregistruota>"
            f"<ns2:registruota>2024-03-03</ns2:registruota>"
            f"<ns2:pavadinimas>test_name</ns2:pavadinimas>"
            f"<ns2:kurortas>true</ns2:kurortas>"
            f"<ns2:plotas>1123.0</ns2:plotas>"
            f"<ns2:tipas>MIESTELIS</ns2:tipas>"
            f"</ns2:GyvenvieteBaseModel></ns1:gyvenvieteResult></ns0:gyvenvieteResponse>"
        )

    def test_soap(self, client: APIClientWithQueryCounter) -> None:
        gyvenviete = create_gyvenviete()

        response = client.get("/api/v1/demo/soap/gyvenviete")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "text/xml; charset=utf-8"
        response_content = response.content.decode("utf-8")
        assert response_content == (
            f"<?xml version='1.0' encoding='UTF-8'?>\n"
            f'<soap11env:Envelope xmlns:soap11env="http://schemas.xmlsoap.org/soap/envelope/">'
            f"<soap11env:Body>"
            f'<ns1:gyvenvieteResponse xmlns:ns1="demo_service_json">'
            f"<ns1:gyvenvieteResult>"
            f'<ns2:GyvenvieteBaseModel xmlns:ns2="apps.address_registry.schema">'
            f"<ns2:id>{gyvenviete.id}</ns2:id>"
            f"<ns2:isregistruota>2024-03-03</ns2:isregistruota>"
            f"<ns2:registruota>2024-03-03</ns2:registruota>"
            f"<ns2:pavadinimas>test_name</ns2:pavadinimas>"
            f"<ns2:kurortas>true</ns2:kurortas>"
            f"<ns2:plotas>1123.0</ns2:plotas>"
            f"<ns2:tipas>MIESTELIS</ns2:tipas>"
            f"</ns2:GyvenvieteBaseModel>"
            f"</ns1:gyvenvieteResult>"
            f"</ns1:gyvenvieteResponse>"
            f"</soap11env:Body>"
            f"</soap11env:Envelope>"
        )

    def test_search(self, client: APIClientWithQueryCounter) -> None:
        create_gyvenviete(pavadinimas="foo")
        create_gyvenviete(pavadinimas="bar")

        response = client.get("/api/v1/demo/json/gyvenviete?pavadinimas=foo")
        assert response.status_code == 200
        assert len(response.json()) == 1


@pytest.mark.parametrize("endpoint", ["gyvenviete", "pavadinimas", "gyvenviete_pavadinimai"])
@pytest.mark.parametrize(
    ("frmt", "content_type"), [("json", "application/json"), ("xml", "text/xml"), ("soap", "text/xml; charset=utf-8")]
)
def test_content_types(client: APIClientWithQueryCounter, endpoint: str, frmt: str, content_type: str) -> None:
    response = client.get(f"/api/v1/demo/{frmt}/{endpoint}")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == content_type
