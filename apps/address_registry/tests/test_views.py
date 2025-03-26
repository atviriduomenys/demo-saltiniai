import pytest

from apps.address_registry.tests.utils import (
    create_apskritis,
    create_dokumentas,
    create_dokumento_autorius,
    create_gyvenviete,
    create_juridinis_asmuo,
    create_nejuridinis_asmuo,
    create_pavadinimas,
    create_salis,
    create_savivaldybe,
    create_seniunija,
)
from apps.utils.tests_query_counter import APIClientWithQueryCounter


class TestGyvenviete:
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
                "plotas": 1123.12,
                "tipas": "MIESTELIS",
                "salis_id": gyvenviete.salis_id,
                "salies_kodas": "test",
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
            f'<ns2:GyvenvieteModel xmlns:ns2="apps.address_registry.schema">'
            f"<ns2:id>{gyvenviete.id}</ns2:id>"
            f"<ns2:isregistruota>2024-03-03</ns2:isregistruota>"
            f"<ns2:registruota>2024-03-03</ns2:registruota>"
            f"<ns2:pavadinimas>test_name</ns2:pavadinimas>"
            f"<ns2:kurortas>true</ns2:kurortas>"
            f"<ns2:plotas>1123.12</ns2:plotas>"
            f"<ns2:tipas>MIESTELIS</ns2:tipas>"
            f"<ns2:salis_id>{gyvenviete.salis_id}</ns2:salis_id>"
            f"<ns2:salies_kodas>test</ns2:salies_kodas>"
            f"</ns2:GyvenvieteModel></ns1:gyvenvieteResult></ns0:gyvenvieteResponse>"
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
            f'<ns2:GyvenvieteModel xmlns:ns2="apps.address_registry.schema">'
            f"<ns2:id>{gyvenviete.id}</ns2:id>"
            f"<ns2:isregistruota>2024-03-03</ns2:isregistruota>"
            f"<ns2:registruota>2024-03-03</ns2:registruota>"
            f"<ns2:pavadinimas>test_name</ns2:pavadinimas>"
            f"<ns2:kurortas>true</ns2:kurortas>"
            f"<ns2:plotas>1123.12</ns2:plotas>"
            f"<ns2:tipas>MIESTELIS</ns2:tipas>"
            f"<ns2:salis_id>{gyvenviete.salis_id}</ns2:salis_id>"
            f"<ns2:salies_kodas>test</ns2:salies_kodas>"
            f"</ns2:GyvenvieteModel>"
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


class TestAddressRegistry:
    def test_json_response(self, client: APIClientWithQueryCounter) -> None:
        salis = create_salis()
        gyvenviete = create_gyvenviete(salis=salis)
        pavadinimas = create_pavadinimas(gyvenviete=gyvenviete)
        dokumentas1 = create_dokumentas()
        dokumento_autorius = create_dokumento_autorius(dokumentas=dokumentas1)
        dokumentas2 = create_dokumentas()
        apskritis = create_apskritis(gyvenviete=gyvenviete, salis=salis)
        savivaldybe = create_savivaldybe(gyvenviete=gyvenviete, salis=salis, apskritis=apskritis)
        seniunija = create_seniunija(
            gyvenviete=gyvenviete, salis=salis, dokumentai=[dokumentas1, dokumentas2], savivaldybe=savivaldybe
        )
        juridinis_asmuo = create_juridinis_asmuo()
        nejuridinis_asmuo = create_nejuridinis_asmuo()

        response = client.get("/api/v1/demo/json/address_registry")

        assert response.status_code == 200
        assert response.json() == {
            "salys": [
                {
                    "id": salis.id,
                    "kodas": "test",
                    "pavadinimas_lt": "TestMiestas",
                    "pavadinimas_en": "TestMiestasEN",
                },
            ],
            "gyvenvietes": [
                {
                    "id": gyvenviete.id,
                    "isregistruota": "2024-03-03",
                    "registruota": "2024-03-03",
                    "pavadinimas": "test_name",
                    "kurortas": True,
                    "plotas": 1123.12,
                    "tipas": "MIESTELIS",
                    "salis_id": salis.id,
                    "salies_kodas": "test",
                },
            ],
            "pavadinimai": [
                {
                    "id": pavadinimas.id,
                    "pavadinimas": "TestPavadinimas",
                    "kirciuotas": "TestPavadinimas",
                    "linksnis": "VARDININKAS",
                    "gyvenviete_id": gyvenviete.id,
                }
            ],
            "dokumentai": [
                {
                    "id": dokumentas1.id,
                    "numeris": "TEST-123-DOK",
                    "priimta": "2024-03-05",
                    "rusis": "ISAKYMAS",
                    "pozymis": "IREGISTRUOTA",
                    "sukurimo_data": "2024-01-05",
                    "sukurimo_laikas": "12:03:00",
                },
                {
                    "id": dokumentas2.id,
                    "numeris": "TEST-123-DOK",
                    "priimta": "2024-03-05",
                    "rusis": "ISAKYMAS",
                    "pozymis": "IREGISTRUOTA",
                    "sukurimo_data": "2024-01-05",
                    "sukurimo_laikas": "12:03:00",
                },
            ],
            "dokumentu_autoriai": [
                {
                    "id": dokumento_autorius.id,
                    "dokumentas_id": dokumentas1.id,
                    "vardas": "Vardenis",
                    "pavarde": "Pavardenis",
                }
            ],
            "apskritys": [
                {
                    "id": apskritis.id,
                    "tipas": "APSKRITIS",
                    "kodas": 123,
                    "iregistruota": "2024-05-06T14:30:00+00:00",
                    "isregistruota": "2024-05-07T14:30:00+00:00",
                    "pavadinimas": "TestApskritis",
                    "plotas": 20,
                    "centras_id": gyvenviete.id,
                    "salis_id": salis.id,
                    "salies_kodas": "test",
                }
            ],
            "savivaldybes": [
                {
                    "id": savivaldybe.id,
                    "tipas": "SAVIVALDYBE",
                    "kodas": 123,
                    "iregistruota": "2024-05-06T14:30:00+00:00",
                    "isregistruota": "2024-05-07T14:30:00+00:00",
                    "pavadinimas": "TestSavivaldybe",
                    "plotas": 20,
                    "centras_id": gyvenviete.id,
                    "salis_id": salis.id,
                    "salies_kodas": "test",
                    "apskritis_id": apskritis.id,
                }
            ],
            "seniunijos": [
                {
                    "id": seniunija.id,
                    "tipas": "SENIUNIJA",
                    "kodas": 123,
                    "iregistruota": "2024-05-06T14:30:00+00:00",
                    "isregistruota": "2024-05-07T14:30:00+00:00",
                    "pavadinimas": "TestSeniunija",
                    "plotas": 20,
                    "centras_id": gyvenviete.id,
                    "salis_id": salis.id,
                    "salies_kodas": "test",
                    "savivaldybe_id": savivaldybe.id,
                }
            ],
            "organizacijos": [{"id": juridinis_asmuo.id}, {"id": nejuridinis_asmuo.id}],
            "juridiniai_asmenys": [
                {
                    "id": juridinis_asmuo.id,
                    "organizacija_ptr_id": juridinis_asmuo.id,
                    "pavadinimas": "TestJuridinis",
                }
            ],
            "ne_juridiniai_asmenys": [
                {
                    "id": nejuridinis_asmuo.id,
                    "organizacija_ptr_id": nejuridinis_asmuo.id,
                    "pavadinimas": "TestNeJuridinis",
                }
            ],
        }


class TestAddressRegistryNested:
    def test_json_response(self, client: APIClientWithQueryCounter) -> None:
        salis = create_salis()
        gyvenviete = create_gyvenviete(salis=salis)
        pavadinimas = create_pavadinimas(gyvenviete=gyvenviete)
        dokumentas1 = create_dokumentas()
        dokumento_autorius = create_dokumento_autorius(dokumentas=dokumentas1)
        dokumentas2 = create_dokumentas()
        apskritis = create_apskritis(gyvenviete=gyvenviete, salis=salis)
        savivaldybe = create_savivaldybe(gyvenviete=gyvenviete, salis=salis, apskritis=apskritis)
        seniunija = create_seniunija(
            gyvenviete=gyvenviete, salis=salis, dokumentai=[dokumentas1, dokumentas2], savivaldybe=savivaldybe
        )
        juridinis_asmuo = create_juridinis_asmuo()
        nejuridinis_asmuo = create_nejuridinis_asmuo()

        response = client.get("/api/v1/demo/json/address_registry_nested")
        assert response.status_code == 200

        expected_salis = {
            "id": salis.id,
            "kodas": "test",
            "pavadinimas_lt": "TestMiestas",
            "pavadinimas_en": "TestMiestasEN",
        }
        expected_gyvenviete = {
            "id": gyvenviete.id,
            "isregistruota": "2024-03-03",
            "registruota": "2024-03-03",
            "pavadinimas": "test_name",
            "kurortas": True,
            "plotas": 1123.12,
            "tipas": "MIESTELIS",
            "salis_id": salis.id,
            "salies_kodas": "test",
            "salis": expected_salis,
            "pavadinimu_formos": [
                {
                    "id": pavadinimas.id,
                    "pavadinimas": "TestPavadinimas",
                    "kirciuotas": "TestPavadinimas",
                    "linksnis": "VARDININKAS",
                }
            ],
        }
        expected_apskritis = {
            "id": apskritis.id,
            "tipas": "APSKRITIS",
            "kodas": 123,
            "iregistruota": "2024-05-06T14:30:00+00:00",
            "isregistruota": "2024-05-07T14:30:00+00:00",
            "pavadinimas": "TestApskritis",
            "plotas": 20,
            "centras_id": gyvenviete.id,
            "salis_id": salis.id,
            "salies_kodas": "test",
            "centras": expected_gyvenviete,
            "dokumentai": [],
            "salis": expected_salis,
        }
        expected_savivaldybe = {
            "id": savivaldybe.id,
            "tipas": "SAVIVALDYBE",
            "kodas": 123,
            "iregistruota": "2024-05-06T14:30:00+00:00",
            "isregistruota": "2024-05-07T14:30:00+00:00",
            "pavadinimas": "TestSavivaldybe",
            "plotas": 20,
            "centras_id": gyvenviete.id,
            "salis_id": salis.id,
            "salies_kodas": "test",
            "apskritis_id": apskritis.id,
            "centras": expected_gyvenviete,
            "dokumentai": [],
            "salis": expected_salis,
            "apskritis": expected_apskritis,
        }
        expected_seniunija = {
            "id": seniunija.id,
            "tipas": "SENIUNIJA",
            "kodas": 123,
            "iregistruota": "2024-05-06T14:30:00+00:00",
            "isregistruota": "2024-05-07T14:30:00+00:00",
            "pavadinimas": "TestSeniunija",
            "plotas": 20,
            "centras_id": gyvenviete.id,
            "salis_id": salis.id,
            "salies_kodas": "test",
            "savivaldybe_id": savivaldybe.id,
            "centras": expected_gyvenviete,
            "dokumentai": [
                {
                    "id": dokumentas1.id,
                    "numeris": "TEST-123-DOK",
                    "priimta": "2024-03-05",
                    "rusis": "ISAKYMAS",
                    "pozymis": "IREGISTRUOTA",
                    "sukurimo_data": "2024-01-05",
                    "sukurimo_laikas": "12:03:00",
                    "dokumento_autorius": {
                        "id": dokumento_autorius.id,
                        "dokumentas_id": dokumentas1.id,
                        "vardas": "Vardenis",
                        "pavarde": "Pavardenis",
                    },
                },
                {
                    "id": dokumentas2.id,
                    "numeris": "TEST-123-DOK",
                    "priimta": "2024-03-05",
                    "rusis": "ISAKYMAS",
                    "pozymis": "IREGISTRUOTA",
                    "sukurimo_data": "2024-01-05",
                    "sukurimo_laikas": "12:03:00",
                    "dokumento_autorius": {
                        "dokumentas_id": None,
                        "vardas": None,
                        "pavarde": None,
                    },
                },
            ],
            "salis": expected_salis,
            "savivaldybe": expected_savivaldybe,
        }
        assert response.json() == {
            "gyvenvietes": [expected_gyvenviete],
            "apskritys": [expected_apskritis],
            "savivaldybes": [expected_savivaldybe],
            "seniunijos": [expected_seniunija],
            "juridiniai_asmenys": [
                {"id": juridinis_asmuo.id, "organizacija_ptr_id": juridinis_asmuo.id, "pavadinimas": "TestJuridinis"},
            ],
            "ne_juridiniai_asmenys": [
                {
                    "id": nejuridinis_asmuo.id,
                    "organizacija_ptr_id": nejuridinis_asmuo.id,
                    "pavadinimas": "TestNeJuridinis",
                }
            ],
        }


@pytest.mark.parametrize(
    "endpoint", ["gyvenviete", "pavadinimas", "gyvenviete_pavadinimai", "address_registry", "address_registry_nested"]
)
@pytest.mark.parametrize(
    ("frmt", "content_type"), [("json", "application/json"), ("xml", "text/xml"), ("soap", "text/xml; charset=utf-8")]
)
def test_content_types(client: APIClientWithQueryCounter, endpoint: str, frmt: str, content_type: str) -> None:
    response = client.get(f"/api/v1/demo/{frmt}/{endpoint}")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == content_type
