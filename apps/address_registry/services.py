from django.db.models import QuerySet
from spyne import ComplexModel, Iterable, String, rpc
from spyne.service import Service

from apps.address_registry.builders import (
    build_address_registry,
    build_address_registry_nested,
    build_settlement_title,
)
from apps.address_registry.models import Settlement, Title
from apps.address_registry.schema import AddressRegistryResponseModel, SettlementModel, TitleModel
from apps.address_registry.schema_nested import (
    AddressRegistryNestedResponseModel,
    SettlementTitleNestedModel,
    SettlementTitleResponseModel,
    TitleSettlementNestedModel,
)


class DemoService(Service):
    @rpc(String, _returns=Iterable(SettlementModel))
    def settlement(self, title_lt: str | None) -> QuerySet:
        queryset = Settlement.objects.all()
        if title_lt:
            queryset = queryset.filter(title_lt__icontains=title_lt)
        return queryset

    @rpc(String, _returns=Iterable(TitleModel))
    def title(self, title: str | None) -> QuerySet:
        queryset = Title.objects.all()
        if title:
            queryset = queryset.filter(title__icontains=title)
        return queryset

    @rpc(_returns=AddressRegistryResponseModel)
    def address_registry(self) -> dict:
        return build_address_registry()

    @rpc(_returns=AddressRegistryNestedResponseModel)
    def address_registry_nested(self) -> dict:
        return build_address_registry_nested()

    @rpc(String, _returns=SettlementTitleResponseModel)
    def settlement_title(self, title: str | None) -> dict:
        return build_settlement_title(title)


class TownFilter(ComplexModel):
    title = String(min_occurs=0, nillable=True)


class CityNameFilter(ComplexModel):
    title = String(min_occurs=0, nillable=True)
    grammatical_case = String(min_occurs=0, nillable=True)
    settlement = TownFilter


class CityNameService(Service):
    @rpc(CityNameFilter, _returns=Iterable(TitleSettlementNestedModel))
    def city_names(self, city_name_filter: CityNameFilter | None = None) -> QuerySet:
        queryset = Title.objects.all().select_related("settlement")

        if not city_name_filter:
            return queryset

        if name := city_name_filter.title:
            queryset = queryset.filter(title__icontains=name)
        if case := city_name_filter.grammatical_case:
            queryset = queryset.filter(grammatical_case=case)
        if city_name_filter.settlement and (town_name := city_name_filter.settlement.title):
            queryset = queryset.filter(settlement__title_lt__icontains=town_name)

        return queryset


class CityService(Service):
    @rpc(_returns=Iterable(SettlementTitleNestedModel))
    def cities(self) -> list[dict]:
        queryset = Settlement.objects.all().prefetch_related("title_forms")
        return [
            {
                **settlement.to_dict(),
                "title_forms": [{**title.to_dict()} for title in settlement.title_forms.all()],
            }
            for settlement in queryset
        ]
