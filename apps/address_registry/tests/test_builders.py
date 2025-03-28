from typing import Any

import pytest
from model_bakery.baker import make

from apps.address_registry.builders import (
    _get_administracinis_vienetas_dict,
    _get_gyvenviete_dict,
    _get_one_by_dict,
    build_address_registry_nested,
)
from apps.address_registry.models import (
    Apskritis,
    Dokumentas,
    DokumentoAutorius,
    Gyvenviete,
    JuridinisAsmuo,
    NejuridinisAsmuo,
    Pavadinimas,
    Salis,
    Savivaldybe,
    Seniunija,
)


class TestGetOneByDict:
    @pytest.mark.parametrize(
        ("key", "value", "expected"),
        [
            ("type", "Apple", {"id": 1, "type": "Apple"}),
            ("id", 2, {"id": 2, "type": "Pear"}),
            ("type", "foo", None),
            ("foo", "Apple", None),
            ("foo", "bar", None),
        ],
    )
    def test_get_dict_by_key_value_pair(self, key: str, value: Any, expected: dict) -> None:
        initial_data = [
            {"id": 1, "type": "Apple"},
            {"id": 2, "type": "Pear"},
            {"id": 3, "type": "Cherry"},
        ]
        assert _get_one_by_dict(initial_data, key, value) == expected

    def test_return_first_match_if_multiple_exists(self) -> None:
        initial_data = [
            {"id": 1, "type": "Apple"},
            {"id": 2, "type": "Apple"},
        ]
        assert _get_one_by_dict(initial_data, "type", "Apple") == {"id": 1, "type": "Apple"}


class TestGetGyvenvieteDict:
    def test_get_gyvenviete_dict(self) -> None:
        salis = make(Salis)
        gyvenviete = make(Gyvenviete, salis=salis)

        assert _get_gyvenviete_dict(gyvenviete) == {
            "id": gyvenviete.id,
            "isregistruota": gyvenviete.isregistruota,
            "registruota": gyvenviete.registruota,
            "pavadinimas": gyvenviete.pavadinimas,
            "kurortas": gyvenviete.kurortas,
            "plotas": gyvenviete.plotas,
            "tipas": gyvenviete.tipas,
            "salis_id": gyvenviete.salis_id,
            "salies_kodas": gyvenviete.salies_kodas,
            "salis": {
                "id": salis.id,
                "kodas": salis.kodas,
                "pavadinimas_lt": salis.pavadinimas_lt,
                "pavadinimas_en": salis.pavadinimas_en,
            },
            "pavadinimu_formos": [],
        }

    def test_gyvenviete_pavadinimai(self) -> None:
        gyvenviete = make(Gyvenviete)
        pavadinimas1 = make(Pavadinimas, linksnis="VARDININKAS", gyvenviete=gyvenviete)
        pavadinimas2 = make(Pavadinimas, linksnis="KILMININKAS", gyvenviete=gyvenviete)

        assert _get_gyvenviete_dict(gyvenviete)["pavadinimu_formos"] == [
            {
                "id": pavadinimas1.id,
                "pavadinimas": pavadinimas1.pavadinimas,
                "kirciuotas": pavadinimas1.kirciuotas,
                "linksnis": pavadinimas1.linksnis,
                "gyvenviete": pavadinimas1.gyvenviete_id,
            },
            {
                "id": pavadinimas2.id,
                "pavadinimas": pavadinimas2.pavadinimas,
                "kirciuotas": pavadinimas2.kirciuotas,
                "linksnis": pavadinimas2.linksnis,
                "gyvenviete": pavadinimas2.gyvenviete_id,
            },
        ]


class TestGetAdministracinisVienetasDict:
    def test_get_administracinis_vienetas_dict(self) -> None:
        salis = make(Salis)
        gyvenviete = make(Gyvenviete, salis=salis)
        apskritis = make(Apskritis, centras=gyvenviete, salis=salis)

        assert _get_administracinis_vienetas_dict(apskritis, [gyvenviete.to_dict()]) == {
            "id": apskritis.id,
            "uuid": apskritis.uuid,
            "tipas": apskritis.tipas,
            "kodas": apskritis.kodas,
            "iregistruota": apskritis.iregistruota,
            "isregistruota": apskritis.isregistruota,
            "pavadinimas": apskritis.pavadinimas,
            "plotas": apskritis.plotas,
            "centras_id": gyvenviete.id,
            "salis_id": salis.id,
            "salies_kodas": apskritis.salies_kodas,
            "centras": gyvenviete.to_dict(),
            "dokumentai": [],
            "salis": {
                "id": salis.id,
                "kodas": salis.kodas,
                "pavadinimas_lt": salis.pavadinimas_lt,
                "pavadinimas_en": salis.pavadinimas_en,
            },
        }

    def test_centras_takes_dict_from_gyvenvietes_attribute_that_matches_centras_id(self) -> None:
        apskritis = make(Apskritis)

        test_list = [{"id": apskritis.centras_id, "foo": "bar"}]
        result = _get_administracinis_vienetas_dict(apskritis, gyvenvietes=test_list)

        assert result["centras"] == {"id": apskritis.centras_id, "foo": "bar"}

    def test_centras_returns_none_if_empty_list_given(self) -> None:
        apskritis = make(Apskritis)

        result = _get_administracinis_vienetas_dict(apskritis, [])

        assert result["centras"] is None

    def test_only_related_dokumentai_returned_with_or_without_autorius(self) -> None:
        dokumentas1 = make(Dokumentas)
        dokumento_autorius1 = make(DokumentoAutorius, dokumentas=dokumentas1)
        dokumentas2 = make(Dokumentas)
        make(Dokumentas)
        apskritis = make(Apskritis, dokumentai=[dokumentas1, dokumentas2])

        result = _get_administracinis_vienetas_dict(apskritis, [])

        assert result["dokumentai"] == [
            {
                "id": dokumentas1.id,
                "numeris": dokumentas1.numeris,
                "priimta": dokumentas1.priimta,
                "rusis": dokumentas1.rusis,
                "pozymis": dokumentas1.pozymis,
                "sukurimo_data": dokumentas1.sukurimo_data,
                "sukurimo_laikas": dokumentas1.sukurimo_laikas,
                "dokumento_autorius": {
                    "id": dokumento_autorius1.id,
                    "vardas": dokumento_autorius1.vardas,
                    "pavarde": dokumento_autorius1.pavarde,
                    "dokumentas_id": dokumentas1.id,
                },
            },
            {
                "id": dokumentas2.id,
                "numeris": dokumentas2.numeris,
                "priimta": dokumentas2.priimta,
                "rusis": dokumentas2.rusis,
                "pozymis": dokumentas2.pozymis,
                "sukurimo_data": dokumentas2.sukurimo_data,
                "sukurimo_laikas": dokumentas2.sukurimo_laikas,
                "dokumento_autorius": {},
            },
        ]


class TestBuildAddressRegistryNested:
    def test_empty(self) -> None:
        result = build_address_registry_nested()

        assert result["gyvenvietes"] == []
        assert result["apskritys"] == []
        assert result["savivaldybes"] == []
        assert result["seniunijos"] == []
        assert list(result["juridiniai_asmenys"]) == []
        assert list(result["nejuridiniai_asmenys"]) == []

    def test_gyvenvietes(self) -> None:
        gyvenviete1 = make(Gyvenviete)
        gyvenviete2 = make(Gyvenviete)

        result = build_address_registry_nested()
        assert result["gyvenvietes"] == [
            _get_gyvenviete_dict(gyvenviete1),
            _get_gyvenviete_dict(gyvenviete2),
        ]

    def test_apskritys(self) -> None:
        gyvenviete = make(Gyvenviete)
        apskritis = make(Apskritis, centras=gyvenviete)

        result = build_address_registry_nested()
        assert result["apskritys"] == [
            {
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
                "centras": _get_gyvenviete_dict(gyvenviete),
                "dokumentai": [],
                "salis": {
                    "id": apskritis.salis.id,
                    "kodas": apskritis.salis.kodas,
                    "pavadinimas_lt": apskritis.salis.pavadinimas_lt,
                    "pavadinimas_en": apskritis.salis.pavadinimas_en,
                },
            }
        ]

    def test_savivaldybes(self) -> None:
        apskritis = make(Apskritis)
        savivaldybe = make(Savivaldybe, apskritis=apskritis)

        result = build_address_registry_nested()
        assert result["savivaldybes"] == [
            {
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
                "centras": _get_gyvenviete_dict(savivaldybe.centras),
                "dokumentai": [],
                "salis": {
                    "id": savivaldybe.salis.id,
                    "kodas": savivaldybe.salis.kodas,
                    "pavadinimas_lt": savivaldybe.salis.pavadinimas_lt,
                    "pavadinimas_en": savivaldybe.salis.pavadinimas_en,
                },
                "apskritis_id": savivaldybe.apskritis_id,
                "apskritis": result["apskritys"][0],
            }
        ]

    def test_seniunijos(self) -> None:
        savivaldybe = make(Savivaldybe)
        seniunija = make(Seniunija, savivaldybe=savivaldybe)

        result = build_address_registry_nested()
        assert result["seniunijos"] == [
            {
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
                "centras": _get_gyvenviete_dict(seniunija.centras),
                "dokumentai": [],
                "salis": {
                    "id": seniunija.salis.id,
                    "kodas": seniunija.salis.kodas,
                    "pavadinimas_lt": seniunija.salis.pavadinimas_lt,
                    "pavadinimas_en": seniunija.salis.pavadinimas_en,
                },
                "savivaldybe_id": seniunija.savivaldybe_id,
                "savivaldybe": result["savivaldybes"][0],
            }
        ]

    def test_juridiniai_asmenys_nejuridiniai_asmenys(self) -> None:
        juridinis_asmuo1 = make(JuridinisAsmuo)
        juridinis_asmuo2 = make(JuridinisAsmuo)
        nejuridinis_asmuo1 = make(NejuridinisAsmuo)
        nejuridinis_asmuo2 = make(NejuridinisAsmuo)

        result = build_address_registry_nested()

        assert set(result["juridiniai_asmenys"]) == {juridinis_asmuo1, juridinis_asmuo2}
        assert set(result["nejuridiniai_asmenys"]) == {nejuridinis_asmuo1, nejuridinis_asmuo2}
