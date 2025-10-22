from spyne import Array, String
from spyne.util.django import DjangoComplexModel

from apps.address_registry.models import (
    AdministrativeUnit,
    County,
    Document,
    Eldership,
    Municipality,
    Settlement,
    Title,
)
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


class AdministrativeUnitNestedModel(DjangoComplexModel):
    centre = SettlementNestedResponseModel
    country = CountryModel

    class Attributes(DjangoAttributes):
        django_model = AdministrativeUnit


class CountyNestedResponseModel(DjangoComplexModel):
    admin_unit = AdministrativeUnitNestedModel

    class Attributes(DjangoAttributes):
        django_model = County


class MunicipalityNestedResponseModel(DjangoComplexModel):
    admin_unit = AdministrativeUnitNestedModel
    county = CountyNestedResponseModel

    class Attributes(DjangoAttributes):
        django_model = Municipality


class EldershipNestedResponseModel(
    DjangoComplexModel,
):
    municipality = MunicipalityNestedResponseModel

    class Attributes(DjangoAttributes):
        django_model = Eldership


class SettlementTitleNestedModel(DjangoComplexModel):
    title_forms = Array(TitleModel)
    json_settlement_data = String()
    xml_country_data = String()

    class Attributes(DjangoAttributes):
        django_model = Settlement


class TitleSettlementNestedModel(DjangoComplexModel):
    settlement = SettlementModel

    class Attributes(DjangoAttributes):
        django_model = Title
