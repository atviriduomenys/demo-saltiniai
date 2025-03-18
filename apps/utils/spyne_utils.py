from spyne import Integer64
from spyne.util.django import DEFAULT_FIELD_MAP, DjangoComplexModel, DjangoModelMapper

# Add missing field maps
FIELD_MAP = DEFAULT_FIELD_MAP + (("BigAutoField", Integer64),)


class DjangoAttributes(DjangoComplexModel.Attributes):
    django_mapper = DjangoModelMapper(FIELD_MAP)
