from django.contrib import admin

from apps.address_registry.models import Gyvenviete, Pavadinimas

admin.site.register(Gyvenviete)
admin.site.register(Pavadinimas)
