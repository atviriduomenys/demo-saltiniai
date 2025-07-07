from typing import Any

from apps.address_registry.models import (
    Administration,
    AdministrativeUnit,
    Continent,
    Country,
    County,
    Document,
    DocumentAuthor,
    Eldership,
    Municipality,
    Settlement,
    Title,
)


def build_address_registry() -> dict:
    return {
        "countries": Country.objects.all(),
        "settlements": Settlement.objects.all(),
        "titles": Title.objects.all(),
        "documents": Document.objects.all(),
        "document_authors": DocumentAuthor.objects.all(),
        "continents": Continent.objects.all(),
        "elderships": Eldership.objects.all(),
        "municipalities": Municipality.objects.all(),
        "counties": County.objects.all(),
        "administrations": Administration.objects.all(),
    }


def _get_one_by_dict(source: list[dict], filter_key: str, filter_value: Any) -> dict:
    return next(
        (obj_dict for obj_dict in source if obj_dict.get(filter_key) == filter_value),
        None,
    )


def _get_settlement_dict(settlement: Settlement) -> dict:
    return {
        **settlement.to_dict(),
        "country": settlement.country.to_dict(),
        "title_forms": [title.to_dict() for title in settlement.title_forms.all()],  # ?
    }


def _get_administrative_unit_dict(
    obj: AdministrativeUnit,
    settlements: list[dict],
) -> dict:
    return {
        **obj.to_dict(),
        "centre": _get_one_by_dict(settlements, filter_key="id", filter_value=obj.centre_id),
        "country": obj.country.to_dict(),
    }


def build_address_registry_nested() -> dict:
    settlements = Settlement.objects.all().select_related("country").prefetch_related("title_forms")
    counties = County.objects.select_related("admin_unit__country").prefetch_related("admin_unit")
    municipalities = Municipality.objects.select_related("admin_unit__country").prefetch_related("admin_unit")
    elderships = Eldership.objects.select_related("admin_unit__country").prefetch_related("admin_unit")

    settlements_dict = [_get_settlement_dict(settlement) for settlement in settlements]
    counties_dict = [
        {
            "admin_unit_id": county.admin_unit_id,
            **_get_administrative_unit_dict(county.admin_unit, settlements_dict),
        }
        for county in counties
    ]
    municipalities_dict = [
        {
            "admin_unit_id": municipality.admin_unit_id,
            **_get_administrative_unit_dict(municipality.admin_unit, settlements_dict),
            "county": _get_one_by_dict(counties_dict, filter_key="id", filter_value=municipality.county_id),
        }
        for municipality in municipalities
    ]
    elderships_dict = [
        {
            **_get_administrative_unit_dict(eldership.admin_unit, settlements_dict),
            "municipality": _get_one_by_dict(
                municipalities_dict, filter_key="id", filter_value=eldership.municipality_id
            ),
        }
        for eldership in elderships
    ]

    return {
        "settlements": settlements_dict,
        "counties": counties_dict,
        "municipalities": municipalities_dict,
        "elderships": elderships_dict,
    }


def build_settlement_title(title: str | None) -> dict:
    settlement_queryset = Settlement.objects.all().prefetch_related("title_forms")
    title_queryset = Title.objects.all().select_related("settlement")
    if title:
        settlement_queryset = settlement_queryset.filter(title_lt__icontains=title)
        title_queryset = title_queryset.filter(title__icontains=title)

    return {
        "settlements": [
            {
                **settlement.to_dict(),
                "title_forms": [{**title.to_dict()} for title in settlement.title_forms.all()],
            }
            for settlement in settlement_queryset
        ],
        "titles": [
            {
                **title.to_dict(),
                "settlement": title.settlement.to_dict(),
            }
            for title in title_queryset
        ],
    }
