"""Payments Module - URLs"""

from django.urls import path
from . import views

app_name = "payments"

urlpatterns = [
    path("checkout", views.create_checkout, name="checkout"),
    path("<str:session_id>/status", views.payment_status, name="status"),
    path("webhook", views.webhook_payment_confirmed, name="webhook"),
    path("refund", views.refund_payment, name="refund"),
]
