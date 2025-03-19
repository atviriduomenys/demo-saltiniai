from model_bakery import seq
from model_bakery.recipe import Recipe, foreign_key, related

from apps.address_registry.models import (
    Apskritis,
    Dokumentas,
    DokumentoAutorius,
    Gyvenviete,
    JuridinisAsmuo,
    NejuridinisAsmuo,
    Pavadinimas,
    Salis,
    Savivaldybe,
    Seniunija,
)

salis = Recipe(
    Salis,
    kodas=seq(1),
    pavadinimas=seq("Salies pavadinimas - "),
    pavadinimas_lt=seq("Salies pavadinimas LT - "),
    pavadinimas_en=seq("Salies pavadinimas EN - "),
)

gyvenviete = Recipe(
    Gyvenviete,
    pavadinimas=seq("Gyvenvietes pavadinimas - "),
    salis=foreign_key(salis),
)

pavadinimas = Recipe(
    Pavadinimas,
    pavadinimas=seq("Pavadinimas - "),
    kirciuotas=seq("Pavadinimo kirtis - "),
    gyvenviete=foreign_key(gyvenviete),
)

dokumentas = Recipe(
    Dokumentas,
    numeris=seq("DOK-NUMERIS-"),
)

dokumento_autorius = Recipe(
    DokumentoAutorius,
    dokumentas=foreign_key(dokumentas, one_to_one=True),
    vardas=seq("Vardas - "),
    pavarde=seq("Pavarde - "),
)

apskritis = Recipe(
    Apskritis,
    tipas="APSKRITIS",
    pavadinimas=seq("Apskrities pavadinimas - "),
    centras=foreign_key(gyvenviete),
    dokumentai=related(dokumentas, dokumentas),
    salis=foreign_key(salis),
)

savivaldybe = Recipe(
    Savivaldybe,
    tipas="SAVIVALDYBE",
    pavadinimas=seq("Savivaldybes pavadinimas - "),
    centras=foreign_key(gyvenviete),
    dokumentai=related(dokumentas, dokumentas),
    salis=foreign_key(salis),
    apskritis=foreign_key(apskritis),
)

seniunija = Recipe(
    Seniunija,
    tipas="SENIUNIJA",
    pavadinimas=seq("Seniunijos pavadinimas - "),
    centras=foreign_key(gyvenviete),
    dokumentai=related(dokumentas, dokumentas),
    salis=foreign_key(salis),
    savivaldybe=foreign_key(savivaldybe),
)

juridinis_asmuo = Recipe(
    JuridinisAsmuo,
    pavadinimas=seq("Juridinis pavadinimas - "),
)

nejuridinis_asmuo = Recipe(
    NejuridinisAsmuo,
    pavadinimas=seq("Nejuridinis pavadinimas - "),
)
