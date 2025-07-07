from spyne import Array, ComplexModel
from spyne.util.django import DjangoComplexModel

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
from apps.utils.spyne_utils import DjangoAttributes

# Spyne calls it models. Basically defines response schemas


class CountryModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = Country


class SettlementModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = Settlement


class TitleModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = Title


class DocumentModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = Document
        django_exclude = ("content",)


class ContinentModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = Continent


class DocumentAuthorModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = DocumentAuthor


class MunicipalityModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = Municipality


class EldershipModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = Eldership


class AdministrationModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = Administration


class CountyModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = County


class AdministrativeUnitModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = AdministrativeUnit


class AddressRegistryResponseModel(ComplexModel):
    countries = Array(CountryModel)
    settlements = Array(SettlementModel)
    titles = Array(TitleModel)
    documents = Array(DocumentModel)
    document_authors = Array(DocumentAuthorModel)
    elderships = Array(EldershipModel)
    municipalities = Array(MunicipalityModel)
    counties = Array(CountyModel)
    administrations = Array(AdministrationModel)
    administrative_units = Array(AdministrativeUnitModel)
