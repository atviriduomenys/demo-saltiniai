from spyne import Array, ComplexModel
from spyne.util.django import DjangoComplexModel

from apps.address_registry.models import Apskritis, Dokumentas, Gyvenviete, Pavadinimas, Savivaldybe, Seniunija
from apps.address_registry.schema import (
    DokumentoAutoriusModel,
    GyvenvieteModel,
    JuridinisAsmuoModel,
    NejuridinisAsmuoModel,
    PavadinimasModel,
    SalisModel,
)
from apps.utils.spyne_utils import DjangoAttributes


class GyvenvieteNestedResponseModel(DjangoComplexModel):
    salis = SalisModel
    pavadinimu_formos = Array(PavadinimasModel)

    class Attributes(DjangoAttributes):
        django_model = Gyvenviete


class DokumentasNestedResponseModel(DjangoComplexModel):
    dokumento_autorius = DokumentoAutoriusModel

    class Attributes(DjangoAttributes):
        django_model = Dokumentas


class AdministracinisVienetasMixin(ComplexModel):
    __mixin__ = True

    centras = GyvenvieteNestedResponseModel
    dokumentai = Array(DokumentasNestedResponseModel)
    salis = SalisModel


class ApskritisNestedResponseModel(DjangoComplexModel, AdministracinisVienetasMixin):
    class Attributes(DjangoAttributes):
        django_model = Apskritis


class SavivaldybeNestedResponseModel(DjangoComplexModel, AdministracinisVienetasMixin):
    apskritis = ApskritisNestedResponseModel

    class Attributes(DjangoAttributes):
        django_model = Savivaldybe


class SeniunijosNestedResponseModel(DjangoComplexModel, AdministracinisVienetasMixin):
    savivaldybe = SavivaldybeNestedResponseModel

    class Attributes(DjangoAttributes):
        django_model = Seniunija


class AddressRegistryNestedResponseModel(ComplexModel):
    gyvenvietes = Array(GyvenvieteNestedResponseModel)
    apskritys = Array(ApskritisNestedResponseModel)
    savivaldybes = Array(SavivaldybeNestedResponseModel)
    seniunijos = Array(SeniunijosNestedResponseModel)
    juridiniai_asmenys = Array(JuridinisAsmuoModel)
    nejuridiniai_asmenys = Array(NejuridinisAsmuoModel)


class GyvenvietePavadinimasNestedModel(DjangoComplexModel):
    pavadinimo_formos = Array(PavadinimasModel)

    class Attributes(DjangoAttributes):
        django_model = Gyvenviete


class PavadinimasGyvenvieteNestedModel(DjangoComplexModel):
    gyvenviete = GyvenvieteModel

    class Attributes(DjangoAttributes):
        django_model = Pavadinimas


class GyvenvietePavadinimasResponseModel(ComplexModel):
    gyvenvietes = Array(GyvenvietePavadinimasNestedModel)
    pavadinimai = Array(PavadinimasGyvenvieteNestedModel)
