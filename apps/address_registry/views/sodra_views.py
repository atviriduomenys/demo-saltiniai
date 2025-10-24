import base64
import binascii
from datetime import datetime

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import get_authorization_header
from spyne import Application, ComplexModel, Date, DateTime, Fault, Integer, Iterable, String, XmlAttribute, rpc
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


class SkolasodraiResponse(ComplexModel):
    asmuo = Iterable(Asmuo)
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


class SkolasodraiService(Service):
    __service_name__ = "skolasodrai"
    __port_types__ = ("skolasodraiPortType",)

    @rpc(Skolasodrai, _returns=SkolasodraiResponse, _throws=[SkolasodraiError], _port_type="skolasodraiPortType")
    def skolasodrai(self, SkolaSodrai: Skolasodrai) -> SkolasodraiResponse:  # noqa: N803
        if SkolaSodrai.asm_kodas and len(str(SkolaSodrai.asm_kodas)) != 11:
            details = {
                "asm_kodas": SkolaSodrai.asm_kodas,
                "vardas": SkolaSodrai.vardas,
                "pavarde": SkolaSodrai.pavarde,
                "gim_data": SkolaSodrai.gim_data,
                "sds": SkolaSodrai.sds,
                "sdn": SkolaSodrai.sdn,
                "klaida": '"asm_kodas" turi būti sudarytas iš 11 skaičių',
                "laikas": datetime.now(),
            }

            raise Fault(faultcode="Client", faultstring="Invalid input data", detail=details)

        # Mock logic: debtor if asm_kodas is even
        debtor = (SkolaSodrai.asm_kodas or 0) % 2 == 0

        return SkolasodraiResponse(
            asmuo=[
                Asmuo(
                    asm_kodas=SkolaSodrai.asm_kodas,
                    vardas=SkolaSodrai.vardas,
                    pavarde=SkolaSodrai.pavarde,
                    gim_data=SkolaSodrai.gim_data,
                    sds=SkolaSodrai.sds,
                    sdn=SkolaSodrai.sdn,
                    pavadinimas="",
                    skola=Skola(rezultatas="Taip" if debtor else "Ne"),
                ),
            ],
            laikas=datetime.now(),
        )


skola_sodrai = csrf_exempt(
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
