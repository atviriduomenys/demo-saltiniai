import base64
import binascii
from collections.abc import Callable
from datetime import datetime
from functools import wraps

from django.views.decorators.csrf import csrf_exempt
from spyne import Application, ComplexModel, Date, DateTime, Fault, Integer, String, XmlAttribute, rpc
from spyne.protocol.soap import Soap11
from spyne.server.django import DjangoApplication
from spyne.service import Service


class Skola(ComplexModel):
    rezultatas = String()


class Asmuo(ComplexModel):
    asm_kodas = Integer(min_occurs=0)
    vardas = String(min_occurs=0)
    pavarde = String(min_occurs=0)
    gim_data = Date(min_occurs=0)
    sds = String(min_occurs=0)
    sdn = Integer(min_occurs=0)
    pavadinimas = String(min_occurs=0)
    skola = Skola


class Skolasodrai(ComplexModel):
    __namespace__ = None
    asm_kodas = Integer(min_occurs=0)
    vardas = String(min_occurs=0)
    pavarde = String(min_occurs=0)
    gim_data = Date(min_occurs=0)
    sds = String(min_occurs=0)
    sdn = Integer(min_occurs=0)
    klausejo_kodas = Integer()
    tikslas = Integer()


class SkolaSodraiResponse(ComplexModel):
    asmuo = Asmuo
    laikas = XmlAttribute(DateTime)


class SkolasodraiError(ComplexModel):
    asm_kodas = Integer(min_occurs=0)
    vardas = String(min_occurs=0)
    pavarde = String(min_occurs=0)
    gim_data = Date(min_occurs=0)
    sds = String(min_occurs=0)
    sdn = Integer(min_occurs=0)
    klaida = String()
    laikas = XmlAttribute(DateTime)


def fake_auth_decorator(func: Callable) -> Callable:
    """This decorator imitates HTTP Basic Auth. Only allows username: test_user password: test_password"""

    @wraps(func)
    def wrapper(self, skola_sodrai: Skolasodrai, *args, **kwargs) -> Callable:
        auth = self.transport.headers.get("authorization", "")
        if isinstance(auth, list):
            auth = auth[0]

        if not auth or not auth.lower().startswith("basic"):
            raise Fault(faultcode="Client", faultstring="Invalid auth header")

        try:
            auth_decoded = base64.b64decode(auth.split()[1]).decode("utf-8")
            username, password = auth_decoded.split(":", 1)
        except (TypeError, ValueError, UnicodeDecodeError, binascii.Error, IndexError) as exception:
            raise Fault(
                faultcode="Client", faultstring="Invalid basic header. Credentials not correctly base64 encoded"
            ) from exception

        if username == "test_user" and password == "test_password":
            return func(self, skola_sodrai, *args, **kwargs)

        raise Fault(faultcode="Client", faultstring="Invalid credentials")

    return wrapper


class SkolasodraiService(Service):
    __service_name__ = "skolasodrai"
    __port_types__ = ("skolasodraiPortType",)

    @rpc(
        Skolasodrai,
        _returns=SkolaSodraiResponse,
        _throws=[SkolasodraiError],
        _port_type="skolasodraiPortType",
        _body_style="bare",
    )
    @fake_auth_decorator
    def SkolaSodrai(self, skola_sodrai: Skolasodrai) -> SkolaSodraiResponse:  # noqa: N802
        if skola_sodrai.asm_kodas and len(str(skola_sodrai.asm_kodas)) != 11:
            details = {
                "asm_kodas": skola_sodrai.asm_kodas,
                "vardas": skola_sodrai.vardas,
                "pavarde": skola_sodrai.pavarde,
                "gim_data": skola_sodrai.gim_data,
                "sds": skola_sodrai.sds,
                "sdn": skola_sodrai.sdn,
                "klaida": '"asm_kodas" turi būti sudarytas iš 11 skaičių',
                "laikas": datetime.now(),
            }

            raise Fault(faultcode="Client", faultstring="Invalid input data", detail=details)

        # Mock logic: debtor if asm_kodas is even
        debtor = (skola_sodrai.asm_kodas or 0) % 2 == 0

        return SkolaSodraiResponse(
            asmuo=Asmuo(
                asm_kodas=skola_sodrai.asm_kodas,
                vardas=skola_sodrai.vardas,
                pavarde=skola_sodrai.pavarde,
                gim_data=skola_sodrai.gim_data,
                sds=skola_sodrai.sds,
                sdn=skola_sodrai.sdn,
                pavadinimas="",
                skola=Skola(rezultatas="Taip" if debtor else "Ne"),
            ),
            laikas=datetime.now(),
        )


skola_sodrai_view = csrf_exempt(
    DjangoApplication(
        Application(
            [SkolasodraiService],
            tns="SkolaSodraiService",
            name="SkolaSodraiService",
            in_protocol=Soap11(validator="lxml"),
            out_protocol=Soap11(validator="soft"),
        )
    )
)
