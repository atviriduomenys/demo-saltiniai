from django.conf import settings
from django.contrib.admin import AdminSite as Site
from django.contrib.admin import apps


class AdminSite(Site):
    site_header = "Demo šaltiniai"
    site_title = "Demo šaltiniai"

    def each_context(self, request) -> dict:
        context = super().each_context(request)
        context["color"] = settings.ADMIN_COLOR
        return context


class AdminConfig(apps.AdminConfig):
    default_site = "apps.utils.admin.AdminSite"


site = AdminSite(name="admin")
