from django.db.models import QuerySet
from spyne import ComplexModel, Integer, Iterable, String, rpc
from spyne.service import Service

from apps.address_registry.models import Continent, Country, Document, DocumentAuthor, Settlement, Title
from apps.address_registry.schema import ContinentModel, CountryModel, DocumentAuthorModel
from apps.address_registry.schema_nested import (
    DocumentsNestedResponseModel,
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


class DocumentFilter(ComplexModel):
    type = String(min_occurs=0, nillable=True)
    status = String(min_occurs=0, nillable=True)


class DocumentService(Service):
    @rpc(DocumentFilter, _returns=Iterable(DocumentsNestedResponseModel))
    def documents(self, document_filter: DocumentFilter) -> list[dict]:
        queryset = Document.objects.all().select_related("documentauthor")
        if document_filter:
            if doc_type := document_filter.type:
                queryset = queryset.filter(type__icontains=doc_type)

            if status := document_filter.status:
                queryset = queryset.filter(status=status)

        return [
            {
                **document.to_dict(),
                "document_author": document.documentauthor.to_dict() if hasattr(document, "documentauthor") else None,
            }
            for document in queryset
        ]


class DocumentAuthorFilter(ComplexModel):
    name = String(min_occurs=0, nillable=True)
    surname = String(min_occurs=0, nillable=True)
    document_id = Integer(min_occurs=0, nillable=True)


class DocumentAuthorService(Service):
    @rpc(DocumentAuthorFilter, _returns=Iterable(DocumentAuthorModel))
    def document_authors(self, document_author_filter: DocumentAuthorFilter) -> QuerySet:
        queryset = DocumentAuthor.objects.all().select_related("document")

        if document_author_filter:
            if name := document_author_filter.name:
                queryset = queryset.filter(name__icontains=name)

            if surname := document_author_filter.surname:
                queryset = queryset.filter(surname__icontains=surname)

            if document_id := document_author_filter.document_id:
                queryset = queryset.filter(document_id=document_id)

        return queryset


class ContinentService(Service):
    @rpc(_returns=Iterable(ContinentModel))
    def continents(self) -> QuerySet:
        queryset = Continent.objects.all()
        return queryset


class CountryFilter(ComplexModel):
    code = String(min_occurs=0, nillable=True)
    title = String(min_occurs=0, nillable=True)


class CountryService(Service):
    @rpc(CountryFilter, _returns=Iterable(CountryModel))
    def countries(self, country_filter: CountryFilter) -> QuerySet:
        queryset = Country.objects.all()

        if country_filter:
            if code := country_filter.code:
                queryset = queryset.filter(code=code)

            if title := country_filter.title:
                queryset = queryset.filter(title_lt__icontains=title)

        return queryset
