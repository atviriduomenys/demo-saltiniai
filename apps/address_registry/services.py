from django.db.models import QuerySet
from spyne import ComplexModel, Iterable, String, rpc
from spyne.service import Service

from apps.address_registry.builders import (
    build_address_registry,
    build_address_registry_nested,
    build_gyvenviete_pavadinimai,
)
from apps.address_registry.models import Gyvenviete, Pavadinimas
from apps.address_registry.schema import AddressRegistryResponseModel, GyvenvieteModel, PavadinimasModel
from apps.address_registry.schema_nested import (
    AddressRegistryNestedResponseModel,
    GyvenvietePavadinimasNestedModel,
    GyvenvietePavadinimasResponseModel,
    PavadinimasGyvenvieteNestedModel,
)


class DemoService(Service):
    @rpc(String, _returns=Iterable(GyvenvieteModel))
    def gyvenviete(self, pavadinimas: str | None) -> QuerySet:
        queryset = Gyvenviete.objects.all()
        if pavadinimas:
            queryset = queryset.filter(pavadinimas__icontains=pavadinimas)
        return queryset

    @rpc(String, _returns=Iterable(PavadinimasModel))
    def pavadinimas(self, pavadinimas: str | None) -> QuerySet:
        queryset = Pavadinimas.objects.all()
        if pavadinimas:
            queryset = queryset.filter(pavadinimas__icontains=pavadinimas)
        return queryset

    @rpc(_returns=AddressRegistryResponseModel)
    def address_registry(self) -> dict:
        return build_address_registry()

    @rpc(_returns=AddressRegistryNestedResponseModel)
    def address_registry_nested(self) -> dict:
        return build_address_registry_nested()

    @rpc(String, _returns=GyvenvietePavadinimasResponseModel)
    def gyvenviete_pavadinimai(self, pavadinimas: str | None) -> dict:
        return build_gyvenviete_pavadinimai(pavadinimas)


class TownFilter(ComplexModel):
    pavadinimas = String(min_occurs=0, nillable=True)


class CityNameFilter(ComplexModel):
    pavadinimas = String(min_occurs=0, nillable=True)
    linksnis = String(min_occurs=0, nillable=True)
    gyvenviete = TownFilter


class CityNameService(Service):
    @rpc(CityNameFilter, _returns=Iterable(PavadinimasGyvenvieteNestedModel))
    def city_names(self, city_name_filter: CityNameFilter | None = None) -> QuerySet:
        queryset = Pavadinimas.objects.all().select_related("gyvenviete")

        if not city_name_filter:
            return queryset

        if name := city_name_filter.pavadinimas:
            queryset = queryset.filter(pavadinimas__icontains=name)
        if case := city_name_filter.linksnis:
            queryset = queryset.filter(linksnis=case)
        if city_name_filter.gyvenviete and (town_name := city_name_filter.gyvenviete.pavadinimas):
            queryset = queryset.filter(gyvenviete__pavadinimas__icontains=town_name)

        return queryset


class CityService(Service):
    @rpc(_returns=Iterable(GyvenvietePavadinimasNestedModel))
    def cities(self) -> list[dict]:
        queryset = Gyvenviete.objects.all().prefetch_related("pavadinimo_formos")
        return [
            {
                **gyvenviete.to_dict(),
                "pavadinimo_formos": [{**pavadinimas.to_dict()} for pavadinimas in gyvenviete.pavadinimo_formos.all()],
            }
            for gyvenviete in queryset
        ]
