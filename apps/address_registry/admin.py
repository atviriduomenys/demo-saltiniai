from django.contrib import admin

from apps.address_registry.models import (
    Administration,
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

admin.site.register(Administration)
admin.site.register(Country)
admin.site.register(County)
admin.site.register(Document)
admin.site.register(DocumentAuthor)
admin.site.register(Eldership)
admin.site.register(Municipality)
admin.site.register(Settlement)
admin.site.register(Title)
admin.site.register(Continent)
