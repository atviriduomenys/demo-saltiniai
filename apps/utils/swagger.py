from django.urls import get_resolver
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from spyne import Application


class CustomSchemaGenerator(OpenAPISchemaGenerator):
    """
    Very small Swagger schema generator for spyne apps.
      - Loops through all URLs
      - Finds django urls with spyne Application
      - Collects public methods of each spyne application service
      - Creates minimal swagger schema with constructed URL
      - Adds schema to main swagger schema
    """

    @staticmethod
    def _get_spyne_app_schema_patterns(spyne_app: Application) -> list[str]:
        spyne_schema_patterns = []
        for service in spyne_app.services:
            spyne_schema_patterns.extend(service.public_methods.keys())

        return spyne_schema_patterns

    def _get_spyne_view_paths(self) -> dict:
        spyne_paths = {}
        for view, (_, view_url, _, _) in get_resolver().reverse_dict.items():
            # Skip not spyne views
            if not (hasattr(view, "app") and type(view.app) is Application):
                continue

            for spyne_schema_pattern in self._get_spyne_app_schema_patterns(view.app):
                spyne_paths[f"{view_url}{spyne_schema_pattern}"] = {
                    "get": {
                        "summary": f"{view.app.name} for {spyne_schema_pattern}",
                        "parameters": [
                            {
                                "in": "query",
                                "name": "wsdl",
                                "type": "boolean",
                                "required": False,
                                "allowEmptyValue": True,
                                "description": "WSDL schema",
                            }
                        ],
                    }
                }

        return spyne_paths

    def get_schema(self, request=None, public=False):
        schema = super().get_schema(request=request, public=public)

        # Add the new paths from the extra swagger JSON to the schema
        for path, path_data in self._get_spyne_view_paths().items():
            schema.paths.setdefault(path, {}).update(path_data)
        schema.schemes = ('https', 'http')
        return schema


# Generate the base schema view using drf-yasg
schema_view = get_schema_view(
    openapi.Info(
        title="Demo šaltiniai API",
        default_version="v1",
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    generator_class=CustomSchemaGenerator,
)
