from django.apps import AppConfig


class AddressRegistryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.address_registry"
    verbose_name = "Address Registry"
    verbose_name_plural = "Address Registries"
