from datetime import date, datetime, time, timezone
from uuid import uuid4

from apps.address_registry.models import (
    Apskritis,
    Dokumentas,
    DokumentoAutorius,
    Gyvenviete,
    JuridinisAsmuo,
    NeJuridinisAsmuo,
    Pavadinimas,
    Salis,
    Savivaldybe,
    Seniunija,
)


def create_salis() -> Salis:
    return Salis.objects.create(
        kodas="test",
        pavadinimas="TestMiestas",
        pavadinimas_lt="TestMiestas",
        pavadinimas_en="TestMiestasEN",
    )


def create_gyvenviete(salis: Salis | None = None, pavadinimas: str = "test_name") -> Gyvenviete:
    if salis is None:
        salis = create_salis()

    return Gyvenviete.objects.create(
        isregistruota=date(2024, 3, 3),
        registruota=date(2024, 3, 3),
        pavadinimas=pavadinimas,
        kurortas=True,
        plotas=1123.12,
        tipas="MIESTELIS",
        salis=salis,
        salies_kodas=salis.kodas,
    )


def create_pavadinimas(
    pavadinimas: str = "TestPavadinimas", linksnis: str = "VARDININKAS", gyvenviete: Gyvenviete | None = None
) -> Pavadinimas:
    if gyvenviete is None:
        gyvenviete = create_gyvenviete()

    return Pavadinimas.objects.create(
        pavadinimas=pavadinimas,
        kirciuotas="TestPavadinimas",
        linksnis=linksnis,
        gyvenviete=gyvenviete,
    )


def create_dokumentas() -> Dokumentas:
    return Dokumentas.objects.create(
        numeris="TEST-123-DOK",
        priimta=date(2024, 3, 5),
        rusis="ISAKYMAS",
        pozymis="IREGISTRUOTA",
        sukurimo_data=date(2024, 1, 5),
        sukurimo_laikas=time(12, 3),
    )


def create_dokumento_autorius(dokumentas: Dokumentas | None = None) -> DokumentoAutorius:
    if dokumentas is None:
        dokumentas = create_dokumentas()

    return DokumentoAutorius.objects.create(
        dokumentas=dokumentas,
        vardas="Vardenis",
        pavarde="Pavardenis",
    )


def create_apskritis(
    gyvenviete: Gyvenviete | None = None,
    salis: Salis | None = None,
    dokumentai: list[Dokumentas] | None = None,
) -> Apskritis:
    if gyvenviete is None:
        gyvenviete = create_gyvenviete()
    if salis is None:
        salis = create_salis()
    if dokumentai is None:
        dokumentai = []

    apskritis = Apskritis.objects.create(
        uuid=uuid4(),
        tipas="APSKRITIS",
        kodas=123,
        iregistruota=datetime(2024, 5, 6, 14, 30, tzinfo=timezone.utc),
        isregistruota=datetime(2024, 5, 7, 14, 30, tzinfo=timezone.utc),
        pavadinimas="TestApskritis",
        plotas=20,
        centras=gyvenviete,
        salis=salis,
        salies_kodas=salis.kodas,
    )
    apskritis.dokumentai.add(*dokumentai)

    return apskritis


def create_savivaldybe(
    gyvenviete: Gyvenviete | None = None,
    salis: Salis | None = None,
    dokumentai: list[Dokumentas] | None = None,
    apskritis: Apskritis | None = None,
) -> Savivaldybe:
    if gyvenviete is None:
        gyvenviete = create_gyvenviete()
    if salis is None:
        salis = create_salis()
    if dokumentai is None:
        dokumentai = []
    if apskritis is None:
        apskritis = create_apskritis()

    savivaldybe = Savivaldybe.objects.create(
        uuid=uuid4(),
        tipas="SAVIVALDYBE",
        kodas=123,
        iregistruota=datetime(2024, 5, 6, 14, 30, tzinfo=timezone.utc),
        isregistruota=datetime(2024, 5, 7, 14, 30, tzinfo=timezone.utc),
        pavadinimas="TestSavivaldybe",
        plotas=20,
        centras=gyvenviete,
        salis=salis,
        salies_kodas=salis.kodas,
        apskritis=apskritis,
    )
    savivaldybe.dokumentai.add(*dokumentai)

    return savivaldybe


def create_seniunija(
    gyvenviete: Gyvenviete | None = None,
    salis: Salis | None = None,
    dokumentai: list[Dokumentas] | None = None,
    savivaldybe: Savivaldybe | None = None,
) -> Seniunija:
    if gyvenviete is None:
        gyvenviete = create_gyvenviete()
    if salis is None:
        salis = create_salis()
    if dokumentai is None:
        dokumentai = []
    if savivaldybe is None:
        savivaldybe = create_savivaldybe()

    seniunija = Seniunija.objects.create(
        uuid=uuid4(),
        tipas="SENIUNIJA",
        kodas=123,
        iregistruota=datetime(2024, 5, 6, 14, 30, tzinfo=timezone.utc),
        isregistruota=datetime(2024, 5, 7, 14, 30, tzinfo=timezone.utc),
        pavadinimas="TestSeniunija",
        plotas=20,
        centras=gyvenviete,
        salis=salis,
        salies_kodas=salis.kodas,
        savivaldybe=savivaldybe,
    )
    seniunija.dokumentai.add(*dokumentai)

    return seniunija


def create_juridinis_asmuo() -> JuridinisAsmuo:
    return JuridinisAsmuo.objects.create(
        pavadinimas="TestJuridinis",
    )


def create_nejuridinis_asmuo() -> NeJuridinisAsmuo:
    return NeJuridinisAsmuo.objects.create(
        pavadinimas="TestNeJuridinis",
    )
