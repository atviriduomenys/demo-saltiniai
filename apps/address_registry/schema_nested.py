from spyne import Array, ComplexModel
from spyne.util.django import DjangoComplexModel

from apps.address_registry.models import County, Document, Eldership, Municipality, Settlement, Title
from apps.address_registry.schema import CountryModel, DocumentAuthorModel, SettlementModel, TitleModel
from apps.utils.spyne_utils import DjangoAttributes


class SettlementNestedResponseModel(DjangoComplexModel):
    country = CountryModel
    title_forms = Array(TitleModel)

    class Attributes(DjangoAttributes):
        django_model = Settlement


class DocumentsNestedResponseModel(DjangoComplexModel):
    document_author = DocumentAuthorModel

    class Attributes(DjangoAttributes):
        django_model = Document
        django_exclude = ("content",)


class AdministrativeUnitMixin(ComplexModel):
    __mixin__ = True

    centre = SettlementNestedResponseModel
    documents = Array(DocumentsNestedResponseModel)
    country = CountryModel


class CountyNestedResponseModel(DjangoComplexModel, AdministrativeUnitMixin):
    class Attributes(DjangoAttributes):
        django_model = County


class MunicipalityNestedResponseModel(DjangoComplexModel, AdministrativeUnitMixin):
    county = CountyNestedResponseModel

    class Attributes(DjangoAttributes):
        django_model = Municipality


class EldershipNestedResponseModel(DjangoComplexModel, AdministrativeUnitMixin):
    municipality = MunicipalityNestedResponseModel

    class Attributes(DjangoAttributes):
        django_model = Eldership


class AddressRegistryNestedResponseModel(ComplexModel):
    settlements = Array(SettlementNestedResponseModel)
    counties = Array(CountyNestedResponseModel)
    municipalities = Array(MunicipalityNestedResponseModel)
    elderships = Array(EldershipNestedResponseModel)


class SettlementTitleNestedModel(DjangoComplexModel):
    title_forms = Array(TitleModel)

    class Attributes(DjangoAttributes):
        django_model = Settlement


class TitleSettlementNestedModel(DjangoComplexModel):
    settlement = SettlementModel

    class Attributes(DjangoAttributes):
        django_model = Title


class SettlementTitleResponseModel(ComplexModel):
    settlements = Array(SettlementTitleNestedModel)
    titles = Array(TitleSettlementNestedModel)
