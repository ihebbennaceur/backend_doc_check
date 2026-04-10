"""DocCheck Module - Apps Configuration"""

from django.apps import AppConfig


class DocCheckConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.doccheck"
    verbose_name = "DocCheck - Free Assessment"
