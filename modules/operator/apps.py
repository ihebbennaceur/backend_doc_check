"""Operator Module - Apps"""

from django.apps import AppConfig


class OperatorConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "modules.operator"
    verbose_name = "Operator - Queue Management"
