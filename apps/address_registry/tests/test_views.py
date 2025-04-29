import pytest
from model_bakery.baker import make
from spyne.client.django import DjangoTestClient

from apps.address_registry.models import (
    Apskritis,
    Dokumentas,
    DokumentoAutorius,
    Gyvenviete,
    JuridinisAsmuo,
    NejuridinisAsmuo,
    Pavadinimas,
    Salis,
    Savivaldybe,
    Seniunija,
)
from apps.address_registry.views import cities_application_soap
from apps.utils.tests_query_counter import APIClientWithQueryCounter


class TestGyvenviete:
    def test_empty(self, client: APIClientWithQueryCounter) -> None:
        response = client.get("/api/v1/demo/json/gyvenviete")

        assert response.status_code == 200
        assert response.json() == []

    def test_json(self, client: APIClientWithQueryCounter) -> None:
        gyvenviete = make(Gyvenviete)

        response = client.get("/api/v1/demo/json/gyvenviete")
        assert response.status_code == 200
        assert response.headers["Content-Type"] == "application/json"
        assert response.json() == [
            {
                "id": gyvenviete.id,
                "isregistruota": gyvenviete.isregistruota.isoformat(),
                "registruota": gyvenviete.registruota.isoformat(),
                "pavadinimas": gyvenviete.pavadinimas,
                "kurortas": gyvenviete.kurortas,
                "plotas": gyvenviete.plotas,
                "tipas": gyvenviete.tipas,
                "salis_id": gyvenviete.salis_id,
                "salies_kodas": gyvenviete.salies_kodas,
            }
        ]

    def test_xml(self, client: APIClientWithQueryCounter) -> None:
        gyvenviete = make(Gyvenviete)

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
            f"<ns2:isregistruota>{gyvenviete.isregistruota}</ns2:isregistruota>"
            f"<ns2:registruota>{gyvenviete.registruota}</ns2:registruota>"
            f"<ns2:pavadinimas>{gyvenviete.pavadinimas}</ns2:pavadinimas>"
            f"<ns2:kurortas>{str(gyvenviete.kurortas).lower()}</ns2:kurortas>"
            f"<ns2:plotas>{gyvenviete.plotas}</ns2:plotas>"
            f"<ns2:tipas>{gyvenviete.tipas}</ns2:tipas>"
            f"<ns2:salis_id>{gyvenviete.salis_id}</ns2:salis_id>"
            f"<ns2:salies_kodas>{gyvenviete.salies_kodas}</ns2:salies_kodas>"
            f"</ns2:GyvenvieteModel></ns1:gyvenvieteResult></ns0:gyvenvieteResponse>"
        )

    def test_soap(self, client: APIClientWithQueryCounter) -> None:
        gyvenviete = make(Gyvenviete)

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
            f"<ns2:isregistruota>{gyvenviete.isregistruota.isoformat()}</ns2:isregistruota>"
            f"<ns2:registruota>{gyvenviete.registruota.isoformat()}</ns2:registruota>"
            f"<ns2:pavadinimas>{gyvenviete.pavadinimas}</ns2:pavadinimas>"
            f"<ns2:kurortas>{str(gyvenviete.kurortas).lower()}</ns2:kurortas>"
            f"<ns2:plotas>{gyvenviete.plotas}</ns2:plotas>"
            f"<ns2:tipas>{gyvenviete.tipas}</ns2:tipas>"
            f"<ns2:salis_id>{gyvenviete.salis_id}</ns2:salis_id>"
            f"<ns2:salies_kodas>{gyvenviete.salies_kodas}</ns2:salies_kodas>"
            f"</ns2:GyvenvieteModel>"
            f"</ns1:gyvenvieteResult>"
            f"</ns1:gyvenvieteResponse>"
            f"</soap11env:Body>"
            f"</soap11env:Envelope>"
        )

    def test_search(self, client: APIClientWithQueryCounter) -> None:
        make(Gyvenviete, pavadinimas="foo")
        make(Gyvenviete, pavadinimas="bar")

        response = client.get("/api/v1/demo/json/gyvenviete?pavadinimas=foo")
        assert response.status_code == 200
        assert len(response.json()) == 1


class TestAddressRegistry:
    def test_json_response(self, client: APIClientWithQueryCounter) -> None:
        salis = make(Salis)
        gyvenviete = make(Gyvenviete, salis=salis)
        pavadinimas = make(Pavadinimas, gyvenviete=gyvenviete)
        dokumentas1 = make(Dokumentas)
        dokumento_autorius = make(DokumentoAutorius, dokumentas=dokumentas1)
        dokumentas2 = make(Dokumentas)
        apskritis = make(Apskritis, centras=gyvenviete, salis=salis)
        savivaldybe = make(Savivaldybe, centras=gyvenviete, salis=salis, apskritis=apskritis)
        seniunija = make(
            Seniunija, centras=gyvenviete, salis=salis, dokumentai=[dokumentas1, dokumentas2], savivaldybe=savivaldybe
        )
        juridinis_asmuo = make(JuridinisAsmuo)
        nejuridinis_asmuo = make(NejuridinisAsmuo)

        response = client.get("/api/v1/demo/json/address_registry")

        assert response.status_code == 200
        assert response.json() == {
            "salys": [
                {
                    "id": salis.id,
                    "kodas": salis.kodas,
                    "pavadinimas_lt": salis.pavadinimas_lt,
                    "pavadinimas_en": salis.pavadinimas_en,
                },
            ],
            "gyvenvietes": [
                {
                    "id": gyvenviete.id,
                    "isregistruota": gyvenviete.isregistruota.isoformat(),
                    "registruota": gyvenviete.registruota.isoformat(),
                    "pavadinimas": gyvenviete.pavadinimas,
                    "kurortas": gyvenviete.kurortas,
                    "plotas": gyvenviete.plotas,
                    "tipas": gyvenviete.tipas,
                    "salis_id": salis.id,
                    "salies_kodas": gyvenviete.salies_kodas,
                },
            ],
            "pavadinimai": [
                {
                    "id": pavadinimas.id,
                    "pavadinimas": pavadinimas.pavadinimas,
                    "kirciuotas": pavadinimas.kirciuotas,
                    "linksnis": pavadinimas.linksnis,
                    "gyvenviete_id": gyvenviete.id,
                }
            ],
            "dokumentai": [
                {
                    "id": dokumentas1.id,
                    "numeris": dokumentas1.numeris,
                    "priimta": dokumentas1.priimta.isoformat(),
                    "rusis": dokumentas1.rusis,
                    "pozymis": dokumentas1.pozymis,
                    "sukurimo_data": dokumentas1.sukurimo_data.isoformat(),
                    "sukurimo_laikas": dokumentas1.sukurimo_laikas.isoformat(),
                },
                {
                    "id": dokumentas2.id,
                    "numeris": dokumentas2.numeris,
                    "priimta": dokumentas2.priimta.isoformat(),
                    "rusis": dokumentas2.rusis,
                    "pozymis": dokumentas2.pozymis,
                    "sukurimo_data": dokumentas2.sukurimo_data.isoformat(),
                    "sukurimo_laikas": dokumentas2.sukurimo_laikas.isoformat(),
                },
            ],
            "dokumentu_autoriai": [
                {
                    "id": dokumento_autorius.id,
                    "dokumentas_id": dokumentas1.id,
                    "vardas": dokumento_autorius.vardas,
                    "pavarde": dokumento_autorius.pavarde,
                }
            ],
            "apskritys": [
                {
                    "id": apskritis.id,
                    "tipas": apskritis.tipas,
                    "kodas": apskritis.kodas,
                    "iregistruota": apskritis.iregistruota,
                    "isregistruota": apskritis.isregistruota,
                    "pavadinimas": apskritis.pavadinimas,
                    "plotas": apskritis.plotas,
                    "centras_id": gyvenviete.id,
                    "salis_id": apskritis.salis_id,
                    "salies_kodas": apskritis.salies_kodas,
                }
            ],
            "savivaldybes": [
                {
                    "id": savivaldybe.id,
                    "tipas": savivaldybe.tipas,
                    "kodas": savivaldybe.kodas,
                    "iregistruota": savivaldybe.iregistruota,
                    "isregistruota": savivaldybe.isregistruota,
                    "pavadinimas": savivaldybe.pavadinimas,
                    "plotas": savivaldybe.plotas,
                    "centras_id": gyvenviete.id,
                    "salis_id": salis.id,
                    "salies_kodas": savivaldybe.salies_kodas,
                    "apskritis_id": apskritis.id,
                }
            ],
            "seniunijos": [
                {
                    "id": seniunija.id,
                    "tipas": seniunija.tipas,
                    "kodas": seniunija.kodas,
                    "iregistruota": seniunija.iregistruota,
                    "isregistruota": seniunija.isregistruota,
                    "pavadinimas": seniunija.pavadinimas,
                    "plotas": seniunija.plotas,
                    "centras_id": gyvenviete.id,
                    "salis_id": salis.id,
                    "salies_kodas": seniunija.salies_kodas,
                    "savivaldybe_id": savivaldybe.id,
                }
            ],
            "organizacijos": [{"id": juridinis_asmuo.id}, {"id": nejuridinis_asmuo.id}],
            "juridiniai_asmenys": [
                {
                    "id": juridinis_asmuo.id,
                    "organizacija_ptr_id": juridinis_asmuo.id,
                    "pavadinimas": juridinis_asmuo.pavadinimas,
                }
            ],
            "nejuridiniai_asmenys": [
                {
                    "id": nejuridinis_asmuo.id,
                    "organizacija_ptr_id": nejuridinis_asmuo.id,
                    "pavadinimas": nejuridinis_asmuo.pavadinimas,
                }
            ],
        }


class TestAddressRegistryNested:
    def test_json_response(self, client: APIClientWithQueryCounter) -> None:
        salis = make(Salis)
        gyvenviete = make(Gyvenviete, salis=salis)
        pavadinimas = make(Pavadinimas, gyvenviete=gyvenviete)
        dokumentas1 = make(Dokumentas)
        dokumento_autorius = make(DokumentoAutorius, dokumentas=dokumentas1)
        dokumentas2 = make(Dokumentas)
        apskritis = make(Apskritis, centras=gyvenviete, salis=salis)
        savivaldybe = make(Savivaldybe, centras=gyvenviete, salis=salis, apskritis=apskritis)
        seniunija = make(
            Seniunija, centras=gyvenviete, salis=salis, dokumentai=[dokumentas1, dokumentas2], savivaldybe=savivaldybe
        )
        juridinis_asmuo = make(JuridinisAsmuo)
        nejuridinis_asmuo = make(NejuridinisAsmuo)

        response = client.get("/api/v1/demo/json/address_registry_nested")
        assert response.status_code == 200

        expected_salis = {
            "id": salis.id,
            "kodas": salis.kodas,
            "pavadinimas_lt": salis.pavadinimas_lt,
            "pavadinimas_en": salis.pavadinimas_en,
        }
        expected_gyvenviete = {
            "id": gyvenviete.id,
            "isregistruota": gyvenviete.isregistruota.isoformat(),
            "registruota": gyvenviete.registruota.isoformat(),
            "pavadinimas": gyvenviete.pavadinimas,
            "kurortas": gyvenviete.kurortas,
            "plotas": gyvenviete.plotas,
            "tipas": gyvenviete.tipas,
            "salis_id": salis.id,
            "salies_kodas": gyvenviete.salies_kodas,
            "salis": expected_salis,
            "pavadinimu_formos": [
                {
                    "id": pavadinimas.id,
                    "pavadinimas": pavadinimas.pavadinimas,
                    "kirciuotas": pavadinimas.kirciuotas,
                    "linksnis": pavadinimas.linksnis,
                }
            ],
        }
        expected_apskritis = {
            "id": apskritis.id,
            "tipas": apskritis.tipas,
            "kodas": apskritis.kodas,
            "iregistruota": apskritis.iregistruota,
            "isregistruota": apskritis.isregistruota,
            "pavadinimas": apskritis.pavadinimas,
            "plotas": apskritis.plotas,
            "centras_id": gyvenviete.id,
            "salis_id": salis.id,
            "salies_kodas": apskritis.salies_kodas,
            "centras": expected_gyvenviete,
            "dokumentai": [],
            "salis": expected_salis,
        }
        expected_savivaldybe = {
            "id": savivaldybe.id,
            "tipas": savivaldybe.tipas,
            "kodas": savivaldybe.kodas,
            "iregistruota": savivaldybe.iregistruota,
            "isregistruota": savivaldybe.isregistruota,
            "pavadinimas": savivaldybe.pavadinimas,
            "plotas": savivaldybe.plotas,
            "centras_id": gyvenviete.id,
            "salis_id": salis.id,
            "salies_kodas": savivaldybe.salies_kodas,
            "apskritis_id": apskritis.id,
            "centras": expected_gyvenviete,
            "dokumentai": [],
            "salis": expected_salis,
            "apskritis": expected_apskritis,
        }
        expected_seniunija = {
            "id": seniunija.id,
            "tipas": seniunija.tipas,
            "kodas": seniunija.kodas,
            "iregistruota": seniunija.iregistruota,
            "isregistruota": seniunija.isregistruota,
            "pavadinimas": seniunija.pavadinimas,
            "plotas": seniunija.plotas,
            "centras_id": gyvenviete.id,
            "salis_id": salis.id,
            "salies_kodas": seniunija.salies_kodas,
            "savivaldybe_id": savivaldybe.id,
            "centras": expected_gyvenviete,
            "dokumentai": [
                {
                    "id": dokumentas1.id,
                    "numeris": dokumentas1.numeris,
                    "priimta": dokumentas1.priimta.isoformat(),
                    "rusis": dokumentas1.rusis,
                    "pozymis": dokumentas1.pozymis,
                    "sukurimo_data": dokumentas1.sukurimo_data.isoformat(),
                    "sukurimo_laikas": dokumentas1.sukurimo_laikas.isoformat(),
                    "dokumento_autorius": {
                        "id": dokumento_autorius.id,
                        "dokumentas_id": dokumentas1.id,
                        "vardas": dokumento_autorius.vardas,
                        "pavarde": dokumento_autorius.pavarde,
                    },
                },
                {
                    "id": dokumentas2.id,
                    "numeris": dokumentas2.numeris,
                    "priimta": dokumentas2.priimta.isoformat(),
                    "rusis": dokumentas2.rusis,
                    "pozymis": dokumentas2.pozymis,
                    "sukurimo_data": dokumentas2.sukurimo_data.isoformat(),
                    "sukurimo_laikas": dokumentas2.sukurimo_laikas.isoformat(),
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
                {
                    "id": juridinis_asmuo.id,
                    "organizacija_ptr_id": juridinis_asmuo.id,
                    "pavadinimas": juridinis_asmuo.pavadinimas,
                },
            ],
            "nejuridiniai_asmenys": [
                {
                    "id": nejuridinis_asmuo.id,
                    "organizacija_ptr_id": nejuridinis_asmuo.id,
                    "pavadinimas": nejuridinis_asmuo.pavadinimas,
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


class TestCitiesApplicationSoap:
    @pytest.fixture
    def client(self) -> DjangoTestClient:
        return DjangoTestClient("/api/v1/cities-app/soap/", cities_application_soap.app)

    def test_city_response(self, client: DjangoTestClient) -> None:
        gyvenviete = make(Gyvenviete)
        pavadinimas1 = make(Pavadinimas, linksnis="VARDININKAS", gyvenviete=gyvenviete)
        pavadinimas2 = make(Pavadinimas, linksnis="KILMININKAS", gyvenviete=gyvenviete)

        response = client.service.cities.get_django_response()
        assert response.status_code == 200

        response_data = list(client.service.cities())
        assert len(response_data) == 1

        data = response_data[0]
        assert data.id == gyvenviete.id
        assert len(data.pavadinimo_formos) == 2
        assert {data.pavadinimo_formos[0].id, data.pavadinimo_formos[1].id} == {pavadinimas1.id, pavadinimas2.id}

    def test_city_name_response(self, client: DjangoTestClient) -> None:
        gyvenviete = make(Gyvenviete)
        pavadinimas = make(Pavadinimas, gyvenviete=gyvenviete)

        response = client.service.city_names.get_django_response()
        assert response.status_code == 200

        response_data = list(client.service.city_names())
        assert len(response_data) == 1

        data = response_data[0]
        assert data.id == pavadinimas.id
        assert data.gyvenviete.id == gyvenviete.id


class TestCitiesApplicationJson:
    def test_city_response(self, client: APIClientWithQueryCounter) -> None:
        gyvenviete = make(Gyvenviete)
        pavadinimas1 = make(Pavadinimas, linksnis="VARDININKAS", gyvenviete=gyvenviete)
        pavadinimas2 = make(Pavadinimas, linksnis="KILMININKAS", gyvenviete=gyvenviete)

        response = client.get("/api/v1/cities-app/json/cities")
        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data) == 1

        data = response_data[0]
        assert data["id"] == gyvenviete.id
        assert len(data["pavadinimo_formos"]) == 2
        assert {data["pavadinimo_formos"][0]["id"], data["pavadinimo_formos"][1]["id"]} == {
            pavadinimas1.id,
            pavadinimas2.id,
        }

    def test_city_name_response(self, client: APIClientWithQueryCounter) -> None:
        gyvenviete = make(Gyvenviete)
        pavadinimas = make(Pavadinimas, gyvenviete=gyvenviete)

        response = client.get("/api/v1/cities-app/json/city_names")
        assert response.status_code == 200

        response_data = response.json()
        assert len(response_data) == 1

        data = response_data[0]
        assert data["id"] == pavadinimas.id
        assert data["gyvenviete"]["id"] == gyvenviete.id


class TestGenerateTestData:
    @staticmethod
    def get_url(model_name: str) -> str:
        return f"/api/v1/address_registry/{model_name}/generate/"

    def test_return_403_when_not_authenticated(self, client: APIClientWithQueryCounter) -> None:
        response = client.post(self.get_url("salis"))
        assert response.status_code == 401

    def test_return_404_when_model_does_not_exist(self, authorized_client: APIClientWithQueryCounter) -> None:
        response = authorized_client.post(self.get_url("foo"), data={"quantity": 1})
        assert response.status_code == 404

    def test_return_400_when_serializer_not_valid(self, authorized_client: APIClientWithQueryCounter) -> None:
        response = authorized_client.post(self.get_url("salis"), data={"quantity": "foo"})
        assert response.status_code == 400

    def test_return_404_when_model_has_no_generate_data_method(
        self, authorized_client: APIClientWithQueryCounter
    ) -> None:
        response = authorized_client.post(self.get_url("pavadinimas"), data={"quantity": 1})
        assert response.status_code == 404

    def test_return_201_when_data_is_generated(self, authorized_client: APIClientWithQueryCounter) -> None:
        assert Salis.objects.all().count() == 0

        response = authorized_client.post(self.get_url("salis"), data={"quantity": 1})
        assert response.status_code == 201
        assert Salis.objects.all().count() == 1

    def test_generate_multiple_objects(self, authorized_client: APIClientWithQueryCounter) -> None:
        assert Salis.objects.all().count() == 0

        response = authorized_client.post(self.get_url("salis"), data={"quantity": 2})
        assert response.status_code == 201
        assert Salis.objects.all().count() == 2

    @pytest.mark.parametrize("client", [100], indirect=True)
    def test_related_objects_generated_using_same_salis_instance(
        self, authorized_client: APIClientWithQueryCounter
    ) -> None:
        response = authorized_client.post(self.get_url("seniunija"), data={"quantity": 1})

        assert response.status_code == 201
        assert Salis.objects.all().count() == 1
