import logging
import uuid

from django.db import models
from solo.models import SingletonModel

LOGGER = logging.getLogger("app")


class SiteConfiguration(SingletonModel):
    manifest_version = models.CharField(max_length=300, default="1")

    class Meta:
        verbose_name = "Site Configuration"

    def __str__(self):
        return "Site Configuration"

    def save(self, *args, **kwargs):
        self.manifest_version = uuid.uuid4().hex
        return super().save(*args, **kwargs)
