"""Documents Module - Apps"""

from django.apps import AppConfig


class DocumentsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.documents"
    verbose_name = "Documents - Storage & Lifecycle"
