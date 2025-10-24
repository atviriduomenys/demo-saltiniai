from datetime import date

import pytest
from spyne import Fault
from spyne.client.django import DjangoTestClient

from apps.address_registry.views.sodra_views import skola_sodrai


@pytest.fixture
def client() -> DjangoTestClient:
    return DjangoTestClient("/api/v1/sodra/skola-sodrai/", skola_sodrai.app)


def _get_request_data(asm_kodas: int = 11111111111) -> dict:
    return {
        "SkolaSodrai": {
            "asm_kodas": asm_kodas,
            "vardas": "Vardenis",
            "pavarde": "Pavardenis",
            "gim_data": date(2023, 1, 1),
            "sds": "1",
            "sdn": 1,
            "klausejo_kodas": 1,
            "tikslas": 1,
        }
    }


@pytest.mark.parametrize(("asm_kodas", "skola"), [(11111111111, "Ne"), (11111111112, "Taip")])
def test_returns_data_if_asm_kodas_has_11_digits(client: DjangoTestClient, asm_kodas: int, skola: str) -> None:
    request_data = _get_request_data(asm_kodas)
    response = client.service.skolasodrai.get_django_response(**request_data)
    assert response.status_code == 200

    response_data = client.service.skolasodrai(**request_data)
    asmuo = list(response_data.asmuo)[0]
    assert asmuo.asm_kodas == asm_kodas
    assert asmuo.vardas == "Vardenis"
    assert asmuo.pavarde == "Pavardenis"
    assert asmuo.gim_data == date(2023, 1, 1)
    assert asmuo.sds == "1"
    assert asmuo.sdn == 1
    assert asmuo.pavadinimas == ""
    assert asmuo.skola.rezultatas == skola


def test_raise_fault_if_asm_kodas_not_11_digits(client: DjangoTestClient) -> None:
    request_data = _get_request_data(1)
    response = client.service.skolasodrai.get_django_response(**request_data)
    assert response.status_code == 500

    with pytest.raises(Fault) as e:
        client.service.skolasodrai(**request_data)
    assert e.value.faultstring == "Invalid input data"
