"""DocReady Module - Apps"""

from django.apps import AppConfig


class DocReadyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.docready"
    verbose_name = "DocReady - Order Management"
