import base64

import pytest
from model_bakery.baker import make
from spyne.client.django import DjangoTestClient

from apps.address_registry.models import Continent, Country
from apps.address_registry.views.rc_broker_views import get_data


@pytest.fixture
def client() -> DjangoTestClient:
    return DjangoTestClient("/api/v1/rc/get-data/", get_data.app)


def _get_request_data(
    action_type="1",
    parameters="dGVzdA==",  # test in base64
) -> dict:
    return {
        "input": {
            "ActionType": action_type,
            "CallerCode": "1",
            "EndUserInfo": "",
            "Parameters": parameters,
            "Time": "1",
            "Signature": "1",
            "CallerSignature": "",
        }
    }


def test_get_data_returns_base64_encoded_empty_country_xml_in_responsedata(client: DjangoTestClient) -> None:
    request_data = _get_request_data()
    response = client.service.GetData.get_django_response(**request_data)
    assert response.status_code == 200

    response_data = client.service.GetData(**request_data)
    assert response_data.ResponseData == "PGNvdW50cmllcyAvPg=="  # <countries /> in base64


def test_get_data_returns_base64_encoded_country_xml_in_responsedata(client: DjangoTestClient) -> None:
    continent = make(Continent, name="Europe")
    country = make(Country, continent=continent, title="Lithuania")
    request_data = _get_request_data()

    xml = (
        f"<countries><countryData>"
        f"<id>{country.id}</id><title>{country.title}</title><continent_id>{country.continent_id}</continent_id>"
        f"<continent><code>{continent.code}</code><name>{continent.name}</name></continent>"
        f"</countryData></countries>"
    ).encode()
    result = base64.b64encode(xml).decode("utf-8")

    response = client.service.GetData.get_django_response(**request_data)
    assert response.status_code == 200

    response_data = client.service.GetData(**request_data)
    assert response_data.ResponseData == result


def test_get_data_returns_country_xml_if_action_type_64_in_responsedata(client: DjangoTestClient):
    continent = make(Continent, name="Europe")
    country = make(Country, continent=continent, title="Lithuania")
    request_data = _get_request_data(action_type="64")

    xml = (
        f"<countries><countryData>"
        f"<id>{country.id}</id><title>{country.title}</title><continent_id>{country.continent_id}</continent_id>"
        f"<continent><code>{continent.code}</code><name>{continent.name}</name></continent>"
        f"</countryData></countries>"
    )

    response = client.service.GetData.get_django_response(**request_data)
    assert response.status_code == 200

    response_data = client.service.GetData(**request_data)
    assert response_data.ResponseData == xml


def test_get_data_returns_base64_decoded_value_in_decodedparameters(client: DjangoTestClient):
    request_data = _get_request_data()

    response = client.service.GetData.get_django_response(**request_data)
    assert response.status_code == 200

    response_data = client.service.GetData(**request_data)
    assert response_data.DecodedParameters == "test"


def test_get_data_returns_error_message_in_decodedparameters_if_base64_fails(client: DjangoTestClient):
    request_data = _get_request_data(parameters="ą")

    response = client.service.GetData.get_django_response(**request_data)
    assert response.status_code == 200

    response_data = client.service.GetData(**request_data)
    assert response_data.DecodedParameters == (
        "Decoding base64 failed: string argument should contain only ASCII characters"
    )


def test_get_data_multiple_returns_multiple_objects(client: DjangoTestClient):
    continent = make(Continent, name="Europe")
    country1 = make(Country, continent=continent, title="Lithuania")
    country2 = make(Country, continent=continent, title="Latvia")
    request_data = _get_request_data()

    result = "".join(  # Makes string single line, without spaces
        f"""
        <countries>
            <countryData>
                <id>{country2.id}</id>
                <title>Latvia</title>
                <continent_id>{continent.code}</continent_id>
                <continent>
                    <code>{continent.code}</code>
                    <name>Europe</name>
                </continent>
            </countryData>
            <countryData>
                <id>{country1.id}</id>
                <title>Lithuania</title>
                <continent_id>{continent.code}</continent_id>
                <continent>
                    <code>{continent.code}</code>
                    <name>Europe</name>
                </continent>
            </countryData>
        </countries>
        """.split()
    )

    response = client.service.GetData.get_django_response(**request_data)
    assert response.status_code == 200
    response_data = client.service.GetData(**request_data)
    assert base64.b64decode(response_data.ResponseData).decode("utf-8") == result
