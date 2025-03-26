from apps.address_registry.models import DokumentoAutorius, Organizacija
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


class TestSalis:
    def test_to_dict(self) -> None:
        salis = create_salis()
        assert salis.to_dict() == {
            "id": salis.id,
            "kodas": salis.kodas,
            "pavadinimas_lt": salis.pavadinimas_lt,
            "pavadinimas_en": salis.pavadinimas_en,
        }


class TestGyvenviete:
    def test_to_dict(self) -> None:
        gyvenviete = create_gyvenviete()
        assert gyvenviete.to_dict() == {
            "id": gyvenviete.id,
            "isregistruota": gyvenviete.isregistruota,
            "registruota": gyvenviete.registruota,
            "pavadinimas": gyvenviete.pavadinimas,
            "kurortas": gyvenviete.kurortas,
            "plotas": gyvenviete.plotas,
            "tipas": gyvenviete.tipas,
            "salis_id": gyvenviete.salis_id,
            "salies_kodas": gyvenviete.salies_kodas,
        }


class TestPavadinimas:
    def test_to_dict(self) -> None:
        pavadinimas = create_pavadinimas()
        assert pavadinimas.to_dict() == {
            "id": pavadinimas.id,
            "pavadinimas": pavadinimas.pavadinimas,
            "kirciuotas": pavadinimas.kirciuotas,
            "linksnis": pavadinimas.linksnis,
            "gyvenviete": pavadinimas.gyvenviete_id,
        }


class TestDokumentas:
    def test_to_dict(self) -> None:
        dokumentas = create_dokumentas()
        assert dokumentas.to_dict() == {
            "id": dokumentas.id,
            "numeris": dokumentas.numeris,
            "priimta": dokumentas.priimta,
            "rusis": dokumentas.rusis,
            "pozymis": dokumentas.pozymis,
            "sukurimo_data": dokumentas.sukurimo_data,
            "sukurimo_laikas": dokumentas.sukurimo_laikas,
        }


class TestDokumentoAutorius:
    def test_to_dict_without_dokumentas(self) -> None:
        dokumento_autorius = DokumentoAutorius.objects.create(vardas="Vardenis", pavarde="Pavardenis")
        assert dokumento_autorius.to_dict() == {
            "id": dokumento_autorius.id,
            "vardas": dokumento_autorius.vardas,
            "pavarde": dokumento_autorius.pavarde,
            "dokumentas_id": None,
        }

    def test_to_dict_with_dokumentas(self) -> None:
        dokumento_autorius = create_dokumento_autorius(dokumentas=create_dokumentas())
        assert dokumento_autorius.to_dict() == {
            "id": dokumento_autorius.id,
            "vardas": dokumento_autorius.vardas,
            "pavarde": dokumento_autorius.pavarde,
            "dokumentas_id": dokumento_autorius.dokumentas_id,
        }


class TestApskritis:
    def test_to_dict(self) -> None:
        apskritis = create_apskritis()
        assert apskritis.to_dict() == {
            "id": apskritis.id,
            "uuid": apskritis.uuid,
            "tipas": apskritis.tipas,
            "kodas": apskritis.kodas,
            "iregistruota": apskritis.iregistruota,
            "isregistruota": apskritis.isregistruota,
            "pavadinimas": apskritis.pavadinimas,
            "plotas": apskritis.plotas,
            "centras_id": apskritis.centras_id,
            "salis_id": apskritis.salis_id,
            "salies_kodas": apskritis.salies_kodas,
        }


class TestSavivaldybe:
    def test_to_dict(self) -> None:
        savivaldybe = create_savivaldybe()
        assert savivaldybe.to_dict() == {
            "id": savivaldybe.id,
            "uuid": savivaldybe.uuid,
            "tipas": savivaldybe.tipas,
            "kodas": savivaldybe.kodas,
            "iregistruota": savivaldybe.iregistruota,
            "isregistruota": savivaldybe.isregistruota,
            "pavadinimas": savivaldybe.pavadinimas,
            "plotas": savivaldybe.plotas,
            "centras_id": savivaldybe.centras_id,
            "salis_id": savivaldybe.salis_id,
            "salies_kodas": savivaldybe.salies_kodas,
            "apskritis_id": savivaldybe.apskritis_id,
        }


class TestSeniunija:
    def test_to_dict(self) -> None:
        seniunija = create_seniunija()
        assert seniunija.to_dict() == {
            "id": seniunija.id,
            "uuid": seniunija.uuid,
            "tipas": seniunija.tipas,
            "kodas": seniunija.kodas,
            "iregistruota": seniunija.iregistruota,
            "isregistruota": seniunija.isregistruota,
            "pavadinimas": seniunija.pavadinimas,
            "plotas": seniunija.plotas,
            "centras_id": seniunija.centras_id,
            "salis_id": seniunija.salis_id,
            "salies_kodas": seniunija.salies_kodas,
            "savivaldybe_id": seniunija.savivaldybe_id,
        }


class TestOrganizacija:
    def test_to_dict(self) -> None:
        create_juridinis_asmuo()
        organizacija = Organizacija.objects.first()

        assert organizacija.to_dict() == {
            "id": organizacija.id,
        }


class TestJuridinisAsmuo:
    def test_to_dict(self) -> None:
        juridinis_asmuo = create_juridinis_asmuo()
        assert juridinis_asmuo.to_dict() == {
            "id": juridinis_asmuo.id,
            "pavadinimas": juridinis_asmuo.pavadinimas,
        }


class TestNejuridinisAsmuo:
    def test_to_dict(self) -> None:
        nejuridinis_asmuo = create_nejuridinis_asmuo()
        assert nejuridinis_asmuo.to_dict() == {
            "id": nejuridinis_asmuo.id,
            "pavadinimas": nejuridinis_asmuo.pavadinimas,
        }
