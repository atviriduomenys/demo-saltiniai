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
from apps.address_registry.schema_nested import AddressRegistryNestedResponseModel, GyvenvietePavadinimasResponseModel


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
