from spyne import Array, ComplexModel

from apps.address_registry.models import Apskritis, Dokumentas, Gyvenviete, Pavadinimas, Savivaldybe, Seniunija
from apps.address_registry.schema import (
    ApskritisModel,
    DokumentasModel,
    DokumentoAutoriusModel,
    GyvenvieteModel,
    JuridinisAsmuoModel,
    NejuridinisAsmuoModel,
    PavadinimasModel,
    SalisModel,
    SavivaldybeModel,
    SeniunijaModel,
)
from apps.utils.spyne_utils import DjangoAttributes


class GyvenvieteNestedResponseModel(GyvenvieteModel):
    salis = SalisModel
    pavadinimu_formos = Array(PavadinimasModel)

    class Attributes(DjangoAttributes):
        django_model = Gyvenviete


class DokumentasNestedResponseModel(DokumentasModel):
    dokumento_autorius = DokumentoAutoriusModel

    class Attributes(DjangoAttributes):
        django_model = Dokumentas


class AdministracinisVienetasMixin(ComplexModel):
    __mixin__ = True

    centras = GyvenvieteNestedResponseModel
    dokumentai = Array(DokumentasNestedResponseModel)
    salis = SalisModel


class ApskritisNestedResponseModel(ApskritisModel, AdministracinisVienetasMixin):
    class Attributes(DjangoAttributes):
        django_model = Apskritis


class SavivaldybeNestedResponseModel(SavivaldybeModel, AdministracinisVienetasMixin):
    apskritis = ApskritisNestedResponseModel

    class Attributes(DjangoAttributes):
        django_model = Savivaldybe


class SeniunijosNestedResponseModel(SeniunijaModel, AdministracinisVienetasMixin):
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


class GyvenvietePavadinimasNestedModel(GyvenvieteModel):
    pavadinimo_formos = Array(PavadinimasModel)

    class Attributes(DjangoAttributes):
        django_model = Gyvenviete


class PavadinimasGyvenvieteNestedModel(PavadinimasModel):
    gyvenviete = GyvenvieteModel

    class Attributes(DjangoAttributes):
        django_model = Pavadinimas


class GyvenvietePavadinimasResponseModel(ComplexModel):
    gyvenvietes = Array(GyvenvietePavadinimasNestedModel)
    pavadinimai = Array(PavadinimasGyvenvieteNestedModel)
