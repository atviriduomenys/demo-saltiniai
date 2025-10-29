import pytest
from django.test import Client
from lxml import etree


@pytest.fixture
def client() -> Client:
    return Client()


def _get_element_text(root_node, element_name: str, namespaces: dict) -> str | None:
    element = root_node.find(element_name, namespaces=namespaces)
    return element.text if element is not None else None


@pytest.mark.parametrize(("asm_kodas", "skola"), [(11111111111, "Ne"), (11111111112, "Taip")])
def test_returns_data_if_asm_kodas_has_11_digits(client: Client, asm_kodas: int, skola: str) -> None:
    request = f"""
    <soap-env:Envelope
        xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:ns0="SkolaSodraiService"
        xmlns:ns1="apps.address_registry.views.sodra_views"
        >
        <soap-env:Body>
            <ns0:SkolaSodrai>
                <ns1:asm_kodas>{asm_kodas}</ns1:asm_kodas>
                <ns1:vardas>1</ns1:vardas>
                <ns1:pavarde>1</ns1:pavarde>
                <ns1:gim_data>2023-01-01</ns1:gim_data>
                <ns1:sds>1</ns1:sds>
                <ns1:sdn>1</ns1:sdn>
                <ns1:klausejo_kodas>123</ns1:klausejo_kodas>
                <ns1:tikslas>213</ns1:tikslas>
            </ns0:SkolaSodrai>
        </soap-env:Body>
    </soap-env:Envelope>
    """

    response = client.post(
        "/api/v1/sodra/skola-sodrai/",
        data=request,
        content_type="text/xml; charset=utf-8",
        HTTP_AUTHORIZATION="Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ=",
    )
    assert response.status_code == 200

    root = etree.fromstring(response.content)
    namespaces = root.nsmap
    asmuo_element = root.find(".//s0:asmuo", namespaces=namespaces)
    assert asmuo_element is not None

    assert _get_element_text(asmuo_element, "s0:asm_kodas", namespaces) == str(asm_kodas)
    assert _get_element_text(asmuo_element, "s0:vardas", namespaces) == "1"
    assert _get_element_text(asmuo_element, "s0:pavarde", namespaces) == "1"
    assert _get_element_text(asmuo_element, "s0:gim_data", namespaces) == "2023-01-01"
    assert _get_element_text(asmuo_element, "s0:sds", namespaces) == "1"
    assert _get_element_text(asmuo_element, "s0:sdn", namespaces) == "1"
    assert _get_element_text(asmuo_element, "s0:pavadinimas", namespaces) is None
    assert _get_element_text(asmuo_element, "s0:skola/s0:rezultatas", namespaces) == skola


def test_raise_fault_if_asm_kodas_not_11_digits(client: Client) -> None:
    request = """
    <soap-env:Envelope
        xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:ns0="SkolaSodraiService"
        xmlns:ns1="apps.address_registry.views.sodra_views"
        >
        <soap-env:Body>
                <ns0:SkolaSodrai>
                    <ns1:asm_kodas>1</ns1:asm_kodas>
                    <ns1:klausejo_kodas>123</ns1:klausejo_kodas>
                    <ns1:tikslas>213</ns1:tikslas>
                </ns0:SkolaSodrai>
        </soap-env:Body>
    </soap-env:Envelope>
    """

    response = client.post(
        "/api/v1/sodra/skola-sodrai/",
        data=request,
        content_type="text/xml; charset=utf-8",
        HTTP_AUTHORIZATION="Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ=",
    )

    assert response.status_code == 500

    root = etree.fromstring(response.content)
    faultstring = root.find(".//soap11env:Fault/faultstring", namespaces=root.nsmap).text
    assert faultstring == "Invalid input data"


def test_http_200_if_request_has_correct_credentials(client: Client) -> None:
    request = """
    <soap-env:Envelope
        xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:ns0="SkolaSodraiService"
        xmlns:ns1="apps.address_registry.views.sodra_views"
        >
        <soap-env:Body>
                <ns0:SkolaSodrai>
                    <ns1:klausejo_kodas>123</ns1:klausejo_kodas>
                    <ns1:tikslas>213</ns1:tikslas>
                </ns0:SkolaSodrai>
        </soap-env:Body>
    </soap-env:Envelope>
    """

    response = client.post(
        "/api/v1/sodra/skola-sodrai/",
        data=request,
        content_type="text/xml; charset=utf-8",
        HTTP_AUTHORIZATION="Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ=",
    )

    assert response.status_code == 200


@pytest.mark.parametrize(
    ("header", "error_message"),
    [
        # Bad header
        ({"HTTP_foo": "Basic dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ="}, "Invalid auth header"),
        # Missing "Basic "
        ({"HTTP_AUTHORIZATION": "dGVzdF91c2VyOnRlc3RfcGFzc3dvcmQ="}, "Invalid auth header"),
        # Base64 encoded test_user test_password, not test_user:test_password
        (
            {"HTTP_AUTHORIZATION": "Basic dGVzdF91c2VyIHRlc3RfcGFzc3dvcmQ="},
            "Invalid basic header. Credentials not correctly base64 encoded",
        ),
        # Base64 encoded user:test_password, bad username
        ({"HTTP_AUTHORIZATION": "Basic dXNlcjp0ZXN0X3Bhc3N3b3Jk"}, "Invalid credentials"),
        # Base64 encoded test_user:password, bad password
        ({"HTTP_AUTHORIZATION": "Basic dGVzdF91c2VyOnBhc3N3b3Jk"}, "Invalid credentials"),
    ],
)
def test_http_500_if_request_has_incorrect_credentials(client: Client, header: dict, error_message: str) -> None:
    request = """
    <soap-env:Envelope
        xmlns:soap-env="http://schemas.xmlsoap.org/soap/envelope/"
        xmlns:ns0="SkolaSodraiService"
        xmlns:ns1="apps.address_registry.views.sodra_views"
        >
        <soap-env:Body>
                <ns0:SkolaSodrai>
                    <ns1:klausejo_kodas>123</ns1:klausejo_kodas>
                    <ns1:tikslas>213</ns1:tikslas>
                </ns0:SkolaSodrai>
        </soap-env:Body>
    </soap-env:Envelope>
    """

    response = client.post(
        "/api/v1/sodra/skola-sodrai/",
        data=request,
        content_type="text/xml; charset=utf-8",
        **header,
    )

    assert response.status_code == 500
    root = etree.fromstring(response.content)
    faultstring = root.find(
        ".//soap11env:Fault/faultstring", namespaces={"soap11env": "http://schemas.xmlsoap.org/soap/envelope/"}
    ).text

    assert faultstring == error_message
