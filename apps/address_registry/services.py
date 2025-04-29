from django.db.models import QuerySet
from spyne import Iterable, String, rpc
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


class CityNameService(Service):
    @rpc(_returns=Iterable(PavadinimasGyvenvieteNestedModel))
    def city_names(self) -> QuerySet:
        return Pavadinimas.objects.all().select_related("gyvenviete")


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
