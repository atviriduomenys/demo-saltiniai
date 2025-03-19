from .settings import *

DEBUG = False
TEMPLATE_DEBUG = False
ADMIN_COLOR = "#007704"  # Green
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = list(INSTALLED_APPS) + [
    "health_check.db",
    "health_check.contrib.migrations",
]
