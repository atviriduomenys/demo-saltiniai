import base64
import binascii
import xml.etree.ElementTree as ET

from django.views.decorators.csrf import csrf_exempt
from spyne import Application, ComplexModel, String, rpc
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from spyne.service import Service

from apps.address_registry.models import Country


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


def _construct_countries_xml() -> ET.Element:
    countries = ET.Element("countries")
    for country in Country.objects.all().select_related("continent"):
        country_data = ET.SubElement(countries, "countryData")
        ET.SubElement(country_data, "id").text = str(country.id)
        ET.SubElement(country_data, "title").text = country.title
        ET.SubElement(country_data, "continent_id").text = str(country.continent_id)

        continent_data = ET.SubElement(country_data, "continent")
        ET.SubElement(continent_data, "code").text = str(country.continent.code)
        ET.SubElement(continent_data, "name").text = country.continent.name

    return countries


class Get(Service):
    __service_name__ = "Get"
    __port_types__ = ("GetPort",)

    @rpc(Input, _returns=Output, _port_type="GetPort")
    def GetData(self, input: Input) -> dict:  # noqa: N802, A002
        try:
            decoded_params = base64.b64decode(input.Parameters, validate=True).decode("utf-8")
        except (binascii.Error, ValueError) as e:
            decoded_params = f"Decoding base64 failed: {e}"

        countries_xml = _construct_countries_xml()
        if input.ActionType == "64":  # ActionType="64" returns ResponseData without base64 encoding
            countries_str = ET.tostring(countries_xml, encoding="unicode")
        else:
            countries_str = base64.b64encode(ET.tostring(countries_xml))

        return {"ResponseCode": "1", "ResponseData": countries_str, "DecodedParameters": decoded_params}


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
