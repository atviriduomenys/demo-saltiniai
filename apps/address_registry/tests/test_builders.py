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
        country = make(Country)
        settlement = make(Settlement, country=country)
        county = make(County, centre=settlement, country=country)

        assert _get_administrative_unit_dict(county, [settlement.to_dict()]) == {
            "id": county.id,
            "uuid": county.uuid,
            "type": county.type,
            "code": county.code,
            "registered": county.registered,
            "deregistered": county.deregistered,
            "title": county.title,
            "area": county.area,
            "centre_id": settlement.id,
            "country_id": country.id,
            "country_code": county.country_code,
            "centre": settlement.to_dict(),
            "country": {
                "id": country.id,
                "code": country.code,
                "title_lt": country.title_lt,
                "title_en": country.title_en,
                "title": country.title,
                "continent_id": country.continent_id,
            },
        }

    def test_centre_takes_dict_from_settlement_attribute_that_matches_centre_id(self) -> None:
        country = make(Country)
        settlement = make(Settlement, country=country)
        county = make(County, centre=settlement, country=country)

        test_list = [{"id": county.centre_id, "foo": "bar"}]
        result = _get_administrative_unit_dict(county, settlements=test_list)

        assert result["centre"] == {"id": county.centre_id, "foo": "bar"}

    def test_centre_returns_none_if_empty_list_given(self) -> None:
        country = make(Country)
        settlement = make(Settlement, country=country)
        county = make(County, centre=settlement, country=country)

        result = _get_administrative_unit_dict(county, [])

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
        country = make(Country)
        settlement = make(Settlement, country=country)
        county = make(County, centre=settlement, country=country)

        result = build_address_registry_nested()
        assert result["counties"] == [
            {
                "id": county.id,
                "uuid": county.uuid,
                "type": county.type,
                "code": county.code,
                "registered": county.registered,
                "deregistered": county.deregistered,
                "title": county.title,
                "area": county.area,
                "centre_id": county.centre_id,
                "country_id": county.country_id,
                "country_code": county.country_code,
                "centre": _get_settlement_dict(county.centre),
                "country": {
                    "id": county.country.id,
                    "code": county.country.code,
                    "title_lt": county.country.title_lt,
                    "title_en": county.country.title_en,
                    "title": county.country.title,
                    "continent_id": county.country.continent_id,
                },
            }
        ]

    def test_municipality(self) -> None:
        country = make(Country)
        settlement = make(Settlement, country=country)
        county = make(County, country=country, centre=settlement)
        municipality = make(Municipality, county=county, country=country, centre=settlement)

        result = build_address_registry_nested()
        assert result["municipalities"] == [
            {
                "id": municipality.id,
                "uuid": municipality.uuid,
                "type": municipality.type,
                "code": municipality.code,
                "registered": municipality.registered,
                "deregistered": municipality.deregistered,
                "title": municipality.title,
                "area": municipality.area,
                "centre_id": municipality.centre_id,
                "country_id": municipality.country_id,
                "country_code": municipality.country_code,
                "centre": _get_settlement_dict(municipality.centre),
                "county_id": municipality.county_id,
                "country": {
                    "id": municipality.country.id,
                    "code": municipality.country.code,
                    "title_lt": municipality.country.title_lt,
                    "title_en": municipality.country.title_en,
                    "title": municipality.country.title,
                    "continent_id": municipality.country.continent_id,
                },
                "county": {
                    "id": municipality.county.id,
                    "uuid": municipality.county.uuid,
                    "country_code": municipality.county.country_code,
                    "code": municipality.county.code,
                    "registered": municipality.county.registered,
                    "deregistered": municipality.county.deregistered,
                    "title": municipality.county.title,
                    "area": municipality.county.area,
                    "type": municipality.county.type,
                    "centre_id": municipality.county.centre_id,
                    "country_id": municipality.county.country_id,
                    "centre": _get_settlement_dict(county.centre),
                    "country": {
                        "id": municipality.country.id,
                        "code": municipality.country.code,
                        "title": municipality.country.title,
                        "title_lt": municipality.country.title_lt,
                        "title_en": municipality.country.title_en,
                        "continent_id": municipality.country.continent_id,
                    },
                },
            }
        ]

    def test_eldership(self) -> None:
        municipality = make(Municipality)

        eldership = make(Eldership, municipality=municipality)

        result = build_address_registry_nested()
        assert result["elderships"] == [
            {
                "id": eldership.id,
                "uuid": eldership.uuid,
                "type": eldership.type,
                "code": eldership.code,
                "registered": eldership.registered,
                "deregistered": eldership.deregistered,
                "title": eldership.title,
                "area": eldership.area,
                "centre_id": eldership.centre_id,
                "country_id": eldership.country_id,
                "country_code": eldership.country_code,
                "municipality_id": eldership.municipality_id,
                "centre": _get_settlement_dict(eldership.centre),
                "country": {
                    "id": eldership.country.id,
                    "code": eldership.country.code,
                    "title": eldership.country.title,
                    "title_lt": eldership.country.title_lt,
                    "title_en": eldership.country.title_en,
                    "continent_id": eldership.country.continent_id,
                },
                "municipality": {
                    "id": eldership.municipality.id,
                    "uuid": eldership.municipality.uuid,
                    "country_code": eldership.municipality.country_code,
                    "code": eldership.municipality.code,
                    "registered": eldership.municipality.registered,
                    "deregistered": eldership.municipality.deregistered,
                    "county_id": eldership.municipality.county_id,
                    "title": eldership.municipality.title,
                    "area": eldership.municipality.area,
                    "type": eldership.municipality.type,
                    "centre_id": eldership.municipality.centre_id,
                    "country_id": eldership.municipality.country_id,
                    "centre": _get_settlement_dict(eldership.municipality.centre),
                    "country": {
                        "id": eldership.municipality.country.id,
                        "code": eldership.municipality.country.code,
                        "title": eldership.municipality.country.title,
                        "title_lt": eldership.municipality.country.title_lt,
                        "title_en": eldership.municipality.country.title_en,
                        "continent_id": eldership.municipality.country.continent_id,
                    },
                    "county": None,
                },
            }
        ]
