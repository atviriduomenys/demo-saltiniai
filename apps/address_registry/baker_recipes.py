from random import random

from model_bakery import seq
from model_bakery.recipe import Recipe, foreign_key

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

continent = Recipe(
    Continent,
    name=seq("Europe - "),
)

country = Recipe(
    Country,
    title=seq("Lietuva - %s", random()),
    title_lt=seq("Lietuva - "),
    title_en=seq("Lithuania - "),
)


document = Recipe(Document, number=seq("DOK-NUMERIS-"))


document_author = Recipe(
    DocumentAuthor, name=seq("Vardas - "), surname=seq("Pavarde - "), document=foreign_key(document, one_to_one=True)
)

settlement = Recipe(Settlement, title_lt=seq("Settlement title - "), area=seq(1), country=foreign_key(country))

administrative_unit = Recipe(
    AdministrativeUnit,
    code=seq(1),
    title=seq("Administrative Unit title - "),
    area=seq(1),
    country=foreign_key(country),
    centre=foreign_key(settlement),
)

title = Recipe(Title, title=seq("Title - "), settlement=foreign_key(settlement))

county = Recipe(
    County,
)

municipality = Recipe(
    Municipality,
)

eldership = Recipe(
    Eldership,
)

administration = Recipe(
    Administration,
    country=foreign_key(country),
    admin_unit=foreign_key(administrative_unit),
)
