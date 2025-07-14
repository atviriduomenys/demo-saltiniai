from django.db.models import QuerySet
from spyne import ComplexModel, Iterable, String, rpc
from spyne.service import Service

from apps.address_registry.models import Settlement, Title
from apps.address_registry.schema_nested import (
    SettlementTitleNestedModel,
    TitleSettlementNestedModel,
)


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
