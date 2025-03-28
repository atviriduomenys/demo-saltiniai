from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.views import serve
from django.urls import include, path

from apps.utils.swagger import schema_view

urlpatterns = []

if settings.DEBUG:
    # static files (images, css, javascript, etc.)
    urlpatterns += [path("static/<path>", serve)] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    # Admin
    path("admin/", admin.site.urls),
    # 3rd party apps
    path("swagger.<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"),
    path("swagger/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
    # Local apps
    path("health/", include("health_check.urls")),
    path("api/v1/", include("apps.address_registry.urls")),
]

admin.autodiscover()
admin.site.enable_nav_sidebar = False
