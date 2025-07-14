from typing import Any

import pytest
from model_bakery.baker import make

from apps.address_registry.builders import (
    _get_administrative_unit_dict,
    _get_one_by_dict,
    _get_settlement_dict,
    build_address_registry_nested,
)
from apps.address_registry.models import (
    AdministrativeUnit,
    Country,
    County,
    Eldership,
    Municipality,
    Settlement,
    Title,
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


class TestGetSettlementDict:
    def test_get_settlement_dict(self) -> None:
        country = make(Country)
        settlement = make(Settlement, country=country)

        assert _get_settlement_dict(settlement) == {
            "id": settlement.id,
            "registered": settlement.registered,
            "deregistered": settlement.deregistered,
            "title_lt": settlement.title_lt,
            "area": settlement.area,
            "type": settlement.type,
            "country_id": settlement.country_id,
            "country_code": settlement.country_code,
            "country": {
                "id": country.id,
                "code": country.code,
                "title_lt": country.title_lt,
                "title_en": country.title_en,
                "continent_id": country.continent_id,
                "title": country.title,
            },
            "title_forms": [],
        }

    def test_settlement_title(self) -> None:
        settlement = make(Settlement, country=make(Country))
        title1 = make(Title, grammatical_case="NOMINATIVE", settlement=settlement)
        title2 = make(Title, grammatical_case="GENITIVE", settlement=settlement)

        assert _get_settlement_dict(settlement)["title_forms"] == [
            {
                "id": title1.id,
                "title": title1.title,
                "accented": title1.accented,
                "grammatical_case": title1.grammatical_case,
                "settlement_id": title1.settlement_id,
            },
            {
                "id": title2.id,
                "title": title2.title,
                "accented": title2.accented,
                "grammatical_case": title2.grammatical_case,
                "settlement_id": title2.settlement_id,
            },
        ]


class TestGetAdministrativeUnitDict:
    def test_get_administrative_unit_dict(self) -> None:
        county = make(County)

        assert _get_administrative_unit_dict(county.admin_unit, [county.admin_unit.centre.to_dict()]) == {
            "uuid": county.admin_unit.uuid,
            "type": county.admin_unit.type,
            "code": county.admin_unit.code,
            "registered": county.admin_unit.registered,
            "deregistered": county.admin_unit.deregistered,
            "title": county.admin_unit.title,
            "area": county.admin_unit.area,
            "centre_id": county.admin_unit.centre.id,
            "country_id": county.admin_unit.country.id,
            "country_code": county.admin_unit.country_code,
            "centre": county.admin_unit.centre.to_dict(),
            "country": {
                "id": county.admin_unit.country.id,
                "code": county.admin_unit.country.code,
                "title_lt": county.admin_unit.country.title_lt,
                "title_en": county.admin_unit.country.title_en,
                "title": county.admin_unit.country.title,
                "continent_id": county.admin_unit.country.continent_id,
            },
        }

    def test_centre_takes_dict_from_settlement_attribute_that_matches_centre_id(self) -> None:
        country = make(Country)
        settlement = make(Settlement, country=country)
        admin_unit = make(AdministrativeUnit, centre=settlement, country=country)
        county = make(County, admin_unit=admin_unit)

        test_list = [{"id": county.admin_unit.centre_id, "foo": "bar"}]
        result = _get_administrative_unit_dict(county.admin_unit, settlements=test_list)

        assert result["centre"] == {"id": county.admin_unit.centre_id, "foo": "bar"}

    def test_centre_returns_none_if_empty_list_given(self) -> None:
        country = make(Country)
        settlement = make(Settlement, country=country)
        admin_unit = make(AdministrativeUnit, centre=settlement, country=country)
        county = make(County, admin_unit=admin_unit)

        result = _get_administrative_unit_dict(county.admin_unit, [])

        assert result["centre"] is None


class TestBuildAddressRegistryNested:
    def test_empty(self) -> None:
        result = build_address_registry_nested()

        assert result["settlements"] == []
        assert result["counties"] == []
        assert result["municipalities"] == []
        assert result["elderships"] == []

    def test_settlements(self) -> None:
        country = make(Country)
        settlement1 = make(Settlement, country=country)
        settlement2 = make(Settlement, country=country)

        result = build_address_registry_nested()
        assert result["settlements"] == [
            _get_settlement_dict(settlement1),
            _get_settlement_dict(settlement2),
        ]

    def test_county(self) -> None:
        admin_unit = make(AdministrativeUnit)
        county = make(County, admin_unit=admin_unit)

        result = build_address_registry_nested()

        assert result["counties"] == [
            {
                "id": county.id,
                "admin_unit_id": county.admin_unit_id,
                "uuid": county.admin_unit.uuid,
                "type": county.admin_unit.type,
                "code": county.admin_unit.code,
                "registered": county.admin_unit.registered,
                "deregistered": county.admin_unit.deregistered,
                "title": county.admin_unit.title,
                "area": county.admin_unit.area,
                "centre_id": county.admin_unit.centre_id,
                "country_id": county.admin_unit.country_id,
                "country_code": county.admin_unit.country_code,
                "country": {
                    "id": county.admin_unit.country.id,
                    "code": county.admin_unit.country.code,
                    "title_lt": county.admin_unit.country.title_lt,
                    "title_en": county.admin_unit.country.title_en,
                    "title": county.admin_unit.country.title,
                    "continent_id": county.admin_unit.country.continent_id,
                },
                "centre": _get_settlement_dict(county.admin_unit.centre),
            }
        ]

    def test_municipality(self) -> None:
        municipality = make(Municipality)

        result = build_address_registry_nested()
        assert result["municipalities"] == [
            {
                "id": municipality.id,
                "admin_unit_id": municipality.admin_unit_id,
                "county_id": municipality.county_id,
                "uuid": municipality.admin_unit.uuid,
                "type": municipality.admin_unit.type,
                "code": municipality.admin_unit.code,
                "registered": municipality.admin_unit.registered,
                "deregistered": municipality.admin_unit.deregistered,
                "title": municipality.admin_unit.title,
                "area": municipality.admin_unit.area,
                "centre_id": municipality.admin_unit.centre_id,
                "country_id": municipality.admin_unit.country_id,
                "country_code": municipality.admin_unit.country_code,
                "country": {
                    "id": municipality.admin_unit.country.id,
                    "code": municipality.admin_unit.country.code,
                    "title_lt": municipality.admin_unit.country.title_lt,
                    "title_en": municipality.admin_unit.country.title_en,
                    "title": municipality.admin_unit.country.title,
                    "continent_id": municipality.admin_unit.country.continent_id,
                },
                "centre": _get_settlement_dict(municipality.admin_unit.centre),
                "county": result["counties"][0],
            }
        ]

    def test_eldership(self) -> None:
        eldership = make(Eldership)

        result = build_address_registry_nested()
        assert result["elderships"] == [
            {
                "id": eldership.id,
                "admin_unit_id": eldership.admin_unit_id,
                "municipality_id": eldership.municipality_id,
                "uuid": eldership.admin_unit.uuid,
                "type": eldership.admin_unit.type,
                "code": eldership.admin_unit.code,
                "registered": eldership.admin_unit.registered,
                "deregistered": eldership.admin_unit.deregistered,
                "title": eldership.admin_unit.title,
                "area": eldership.admin_unit.area,
                "centre_id": eldership.admin_unit.centre_id,
                "country_id": eldership.admin_unit.country_id,
                "country_code": eldership.admin_unit.country_code,
                "centre": _get_settlement_dict(eldership.admin_unit.centre),
                "country": {
                    "id": eldership.admin_unit.country.id,
                    "code": eldership.admin_unit.country.code,
                    "title_lt": eldership.admin_unit.country.title_lt,
                    "title_en": eldership.admin_unit.country.title_en,
                    "title": eldership.admin_unit.country.title,
                    "continent_id": eldership.admin_unit.country.continent_id,
                },
                "municipality": result["municipalities"][0],
            }
        ]
