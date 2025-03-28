from typing import Any

from apps.address_registry.models import (
    AdministracinisVienetas,
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


def build_address_registry() -> dict:
    return {
        "salys": Salis.objects.all(),
        "gyvenvietes": Gyvenviete.objects.all(),
        "pavadinimai": Pavadinimas.objects.all(),
        "dokumentai": Dokumentas.objects.all(),
        "dokumentu_autoriai": DokumentoAutorius.objects.all(),
        "apskritys": Apskritis.objects.all(),
        "savivaldybes": Savivaldybe.objects.all(),
        "seniunijos": Seniunija.objects.all(),
        "organizacijos": Organizacija.objects.all(),
        "juridiniai_asmenys": JuridinisAsmuo.objects.all(),
        "nejuridiniai_asmenys": NejuridinisAsmuo.objects.all(),
    }


def _get_one_by_dict(source: list[dict], filter_key: str, filter_value: Any) -> dict:
    return next(
        (obj_dict for obj_dict in source if obj_dict.get(filter_key) == filter_value),
        None,
    )


def _get_gyvenviete_dict(gyvenviete: Gyvenviete) -> dict:
    return {
        **gyvenviete.to_dict(),
        "salis": gyvenviete.salis.to_dict(),
        "pavadinimu_formos": [pavadinimas.to_dict() for pavadinimas in gyvenviete.pavadinimo_formos.all()],
    }


def _get_administracinis_vienetas_dict(
    obj: AdministracinisVienetas,
    gyvenvietes: list[dict],
) -> dict:
    return {
        **obj.to_dict(),
        "centras": _get_one_by_dict(gyvenvietes, filter_key="id", filter_value=obj.centras_id),
        "dokumentai": [
            {
                **dokumentas.to_dict(),
                "dokumento_autorius": (
                    dokumentas.dokumentoautorius.to_dict() if hasattr(dokumentas, "dokumentoautorius") else {}
                ),
            }
            for dokumentas in obj.dokumentai.all()
        ],
        "salis": obj.salis.to_dict(),
    }


def build_address_registry_nested() -> dict:
    gyvenvietes = Gyvenviete.objects.all().select_related("salis").prefetch_related("pavadinimo_formos")
    apskritys = Apskritis.objects.all().select_related("salis").prefetch_related("dokumentai__dokumentoautorius")
    savivaldybes = Savivaldybe.objects.all().select_related("salis").prefetch_related("dokumentai__dokumentoautorius")
    seniunijos = Seniunija.objects.all().select_related("salis").prefetch_related("dokumentai__dokumentoautorius")

    gyvenvietes_dict = [_get_gyvenviete_dict(gyvenviete) for gyvenviete in gyvenvietes]
    apskritys_dict = [
        {
            **_get_administracinis_vienetas_dict(apskritis, gyvenvietes_dict),
        }
        for apskritis in apskritys
    ]
    savivaldybes_dict = [
        {
            **_get_administracinis_vienetas_dict(savivaldybe, gyvenvietes_dict),
            "apskritis": _get_one_by_dict(apskritys_dict, filter_key="id", filter_value=savivaldybe.apskritis_id),
        }
        for savivaldybe in savivaldybes
    ]
    seniunijos_dict = [
        {
            **_get_administracinis_vienetas_dict(seniunija, gyvenvietes_dict),
            "savivaldybe": _get_one_by_dict(savivaldybes_dict, filter_key="id", filter_value=seniunija.savivaldybe_id),
        }
        for seniunija in seniunijos
    ]

    return {
        "gyvenvietes": gyvenvietes_dict,
        "apskritys": apskritys_dict,
        "savivaldybes": savivaldybes_dict,
        "seniunijos": seniunijos_dict,
        "juridiniai_asmenys": JuridinisAsmuo.objects.all(),
        "nejuridiniai_asmenys": NejuridinisAsmuo.objects.all(),
    }


def build_gyvenviete_pavadinimai(pavadinimas: str | None) -> dict:
    gyvenviete_queryset = Gyvenviete.objects.all().prefetch_related("pavadinimo_formos")
    pavadinimai_queryset = Pavadinimas.objects.all().select_related("gyvenviete")
    if pavadinimas:
        gyvenviete_queryset = gyvenviete_queryset.filter(pavadinimas__icontains=pavadinimas)
        pavadinimai_queryset = pavadinimai_queryset.filter(pavadinimas__icontains=pavadinimas)

    return {
        "gyvenvietes": [
            {
                **gyvenviete.to_dict(),
                "pavadinimo_formos": [{**pavadinimas.to_dict()} for pavadinimas in gyvenviete.pavadinimo_formos.all()],
            }
            for gyvenviete in gyvenviete_queryset
        ],
        "pavadinimai": [
            {
                **pavadinimas.to_dict(),
                "gyvenviete": pavadinimas.gyvenviete.to_dict(),
            }
            for pavadinimas in pavadinimai_queryset
        ],
    }
