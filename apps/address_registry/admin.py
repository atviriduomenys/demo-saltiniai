from django.contrib import admin

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

admin.site.register(Salis)
admin.site.register(Gyvenviete)
admin.site.register(Pavadinimas)
admin.site.register(Dokumentas)
admin.site.register(DokumentoAutorius)
admin.site.register(Apskritis)
admin.site.register(Savivaldybe)
admin.site.register(Seniunija)
admin.site.register(Organizacija)
admin.site.register(JuridinisAsmuo)
admin.site.register(NejuridinisAsmuo)
