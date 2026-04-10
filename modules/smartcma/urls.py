"""SmartCMA Module - URLs"""

from django.urls import path
from . import views

app_name = "smartcma"

urlpatterns = [
    path("generate", views.generate_report, name="generate"),
    path("<str:report_id>", views.report_detail, name="detail"),
    path("<str:report_id>/export", views.export_pdf, name="export"),
]
