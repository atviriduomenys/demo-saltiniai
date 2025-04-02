from spyne import Array, ComplexModel
from spyne.util.django import DjangoComplexModel

from apps.address_registry.models import (
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
from apps.utils.spyne_utils import DjangoAttributes

# Spyne calls it models. Basically defines response schemas


class SalisModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = Salis
        django_exclude = ["pavadinimas"]


class GyvenvieteModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = Gyvenviete


class PavadinimasModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = Pavadinimas


class DokumentasModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = Dokumentas


class DokumentoAutoriusModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = DokumentoAutorius


class ApskritisModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = Apskritis


class SavivaldybeModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = Savivaldybe


class SeniunijaModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = Seniunija


class OrganizacijaModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = Organizacija


class JuridinisAsmuoModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = JuridinisAsmuo


class NejuridinisAsmuoModel(DjangoComplexModel):
    class Attributes(DjangoAttributes):
        django_model = NejuridinisAsmuo


class AddressRegistryResponseModel(ComplexModel):
    salys = Array(SalisModel)
    gyvenvietes = Array(GyvenvieteModel)
    pavadinimai = Array(PavadinimasModel)
    dokumentai = Array(DokumentasModel)
    dokumentu_autoriai = Array(DokumentoAutoriusModel)
    apskritys = Array(ApskritisModel)
    savivaldybes = Array(SavivaldybeModel)
    seniunijos = Array(SeniunijaModel)
    organizacijos = Array(OrganizacijaModel)
    juridiniai_asmenys = Array(JuridinisAsmuoModel)
    nejuridiniai_asmenys = Array(NejuridinisAsmuoModel)
