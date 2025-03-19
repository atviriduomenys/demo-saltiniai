from model_bakery.baker import make

from apps.address_registry.models import (
    Apskritis,
    Dokumentas,
    DokumentoAutorius,
    Gyvenviete,
    JuridinisAsmuo,
    NejuridinisAsmuo,
    Organizacija,
    Pavadinimas,
    Salis,
    Savivaldybe,
    Seniunija,
)


class TestSalis:
    def test_to_dict(self) -> None:
        salis = make(Salis)
        assert salis.to_dict() == {
            "id": salis.id,
            "kodas": salis.kodas,
            "pavadinimas_lt": salis.pavadinimas_lt,
            "pavadinimas_en": salis.pavadinimas_en,
        }

    def test_generate_test_data(self) -> None:
        Salis.generate_test_data(quantity=2)
        assert Salis.objects.count() == 2


class TestGyvenviete:
    def test_to_dict(self) -> None:
        gyvenviete = make(Gyvenviete)
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

    def test_generate_test_data(self) -> None:
        Gyvenviete.generate_test_data(quantity=2)
        assert Gyvenviete.objects.count() == 2
        assert Pavadinimas.objects.count() == 4


class TestPavadinimas:
    def test_to_dict(self) -> None:
        pavadinimas = make(Pavadinimas)
        assert pavadinimas.to_dict() == {
            "id": pavadinimas.id,
            "pavadinimas": pavadinimas.pavadinimas,
            "kirciuotas": pavadinimas.kirciuotas,
            "linksnis": pavadinimas.linksnis,
            "gyvenviete": pavadinimas.gyvenviete_id,
        }


class TestDokumentas:
    def test_to_dict(self) -> None:
        dokumentas = make(Dokumentas)
        assert dokumentas.to_dict() == {
            "id": dokumentas.id,
            "numeris": dokumentas.numeris,
            "priimta": dokumentas.priimta,
            "rusis": dokumentas.rusis,
            "pozymis": dokumentas.pozymis,
            "sukurimo_data": dokumentas.sukurimo_data,
            "sukurimo_laikas": dokumentas.sukurimo_laikas,
        }

    def test_generate_test_data(self) -> None:
        Dokumentas.generate_test_data(quantity=2)
        assert Dokumentas.objects.count() == 2
        assert DokumentoAutorius.objects.count() == 2


class TestDokumentoAutorius:
    def test_to_dict_without_dokumentas(self) -> None:
        dokumento_autorius = make(DokumentoAutorius, dokumentas=None)
        assert dokumento_autorius.to_dict() == {
            "id": dokumento_autorius.id,
            "vardas": dokumento_autorius.vardas,
            "pavarde": dokumento_autorius.pavarde,
            "dokumentas_id": None,
        }

    def test_to_dict_with_dokumentas(self) -> None:
        dokumento_autorius = make(DokumentoAutorius)
        assert dokumento_autorius.to_dict() == {
            "id": dokumento_autorius.id,
            "vardas": dokumento_autorius.vardas,
            "pavarde": dokumento_autorius.pavarde,
            "dokumentas_id": dokumento_autorius.dokumentas_id,
        }


class TestApskritis:
    def test_to_dict(self) -> None:
        apskritis = make(Apskritis)
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

    def test_generate_test_dataa(self) -> None:
        Apskritis.generate_test_data(quantity=2)
        assert Apskritis.objects.count() == 2
        assert Salis.objects.count() == 2


class TestSavivaldybe:
    def test_to_dict(self) -> None:
        savivaldybe = make(Savivaldybe)
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

    def test_generate_test_data(self) -> None:
        Savivaldybe.generate_test_data(quantity=2)
        assert Savivaldybe.objects.count() == 2
        assert Salis.objects.count() == 2


class TestSeniunija:
    def test_to_dict(self) -> None:
        seniunija = make(Seniunija)
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

    def test_generate_test_data(self) -> None:
        Seniunija.generate_test_data(quantity=2)
        assert Seniunija.objects.count() == 2
        assert Salis.objects.count() == 2


class TestOrganizacija:
    def test_to_dict(self) -> None:
        make(JuridinisAsmuo)
        organizacija = Organizacija.objects.first()

        assert organizacija.to_dict() == {
            "id": organizacija.id,
        }


class TestJuridinisAsmuo:
    def test_to_dict(self) -> None:
        juridinis_asmuo = make(JuridinisAsmuo)
        assert juridinis_asmuo.to_dict() == {
            "id": juridinis_asmuo.id,
            "pavadinimas": juridinis_asmuo.pavadinimas,
        }

    def test_generate_test_data(self) -> None:
        JuridinisAsmuo.generate_test_data(quantity=2)
        assert JuridinisAsmuo.objects.count() == 2


class TestNejuridinisAsmuo:
    def test_to_dict(self) -> None:
        nejuridinis_asmuo = make(NejuridinisAsmuo)
        assert nejuridinis_asmuo.to_dict() == {
            "id": nejuridinis_asmuo.id,
            "pavadinimas": nejuridinis_asmuo.pavadinimas,
        }

    def test_generate_test_data(self) -> None:
        NejuridinisAsmuo.generate_test_data(quantity=2)
        assert NejuridinisAsmuo.objects.count() == 2
