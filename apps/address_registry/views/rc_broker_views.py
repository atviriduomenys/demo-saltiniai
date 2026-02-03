import base64
import binascii
import xml.etree.ElementTree as ET
from enum import Enum

from django.views.decorators.csrf import csrf_exempt
from spyne import Application, ComplexModel, Iterable, Mandatory, String, rpc
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from spyne.service import Service

from apps.address_registry.helpers import construct_countries_xml, construct_country_xml
from apps.address_registry.models import Country


class Actions(Enum):
    AUTHENTICATED_RESPONSE_ACTION = "60"
    NO_BASE64_ACTION = "64"


ALLOWED_SIGNATURES = ["MTAwMQ==", "MTAwMg==", "MTAwMw=="]


class Input(ComplexModel):
    ActionType = String(min_occurs=1, nillable=False)
    CallerCode = String(min_occurs=1, nillable=False)
    EndUserInfo = String(min_occurs=0)
    Parameters = String(min_occurs=1, nillable=False)
    Time = String(min_occurs=1, nillable=False)
    Signature = String(min_occurs=1, nillable=False)
    CallerSignature = String(min_occurs=0)


class Output(ComplexModel):
    ResponseCode = String()
    ResponseData = String()
    DecodedParameters = String()


def _get_decoded_params(parameter: str) -> str:
    try:
        decoded_params = base64.b64decode(parameter, validate=True).decode("utf-8")
    except (binascii.Error, ValueError) as e:
        decoded_params = f"Decoding base64 failed: {e}"

    return decoded_params


def _get_response_data(action_type: str, xml_data: ET.Element) -> str | bytes:
    if action_type == Actions.NO_BASE64_ACTION.value:  # Returns ResponseData without base64 encoding
        countries_data = ET.tostring(xml_data, encoding="unicode")
    else:
        countries_data = base64.b64encode(ET.tostring(xml_data))

    return countries_data


def _fake_authenticate(action_type: str, signature: str) -> bool:
    if action_type == Actions.AUTHENTICATED_RESPONSE_ACTION.value:
        return signature in ALLOWED_SIGNATURES
    return True


class Get(Service):
    __service_name__ = "Get"
    __port_types__ = ("GetPort",)

    @rpc(Mandatory(Input), _returns=Output, _port_type="GetPort")
    def GetData(self, input: Input) -> dict:  # noqa: N802, A002
        decoded_params = _get_decoded_params(input.Parameters)

        if not _fake_authenticate(input.ActionType, input.Signature):
            return {
                "ResponseCode": "-1",
                "ResponseData": "Incorrect signature. Authorization failed.",
                "DecodedParameters": decoded_params,
            }

        countries_xml = construct_countries_xml()
        countries_str = _get_response_data(input.ActionType, countries_xml)

        return {"ResponseCode": "1", "ResponseData": countries_str, "DecodedParameters": decoded_params}

    @rpc(Mandatory(Input), _returns=Iterable(Output), _port_type="GetPort")
    def GetDataMultiple(self, input: Input) -> list[dict]:  # noqa: N802, A002
        decoded_params = _get_decoded_params(input.Parameters)

        if not _fake_authenticate(input.ActionType, input.Signature):
            return [
                {
                    "ResponseCode": "-1",
                    "ResponseData": "Incorrect signature. Authorization failed.",
                    "DecodedParameters": decoded_params,
                }
            ]

        response_data = []

        for country in Country.objects.all().select_related("continent"):
            country_xml = ET.Element("countries")
            country_xml.append(construct_country_xml(country))
            country_str = _get_response_data(input.ActionType, country_xml)

            response_data.append(
                {"ResponseCode": "1", "ResponseData": country_str, "DecodedParameters": decoded_params}
            )

        return response_data


get_data = csrf_exempt(
    DjangoApplication(
        Application(
            [Get],
            tns="Get",
            name="Get",
            in_protocol=Soap11(validator="lxml"),
            out_protocol=Soap11(validator="soft"),
        )
    )
)
