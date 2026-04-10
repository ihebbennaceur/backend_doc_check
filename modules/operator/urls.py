"""Operator Module - URLs"""

from django.urls import path
from . import views

app_name = "operator"

urlpatterns = [
    path("queue", views.operator_queue, name="queue"),
    path("<str:order_id>", views.order_details, name="detail"),
    path("<str:order_id>/status", views.update_queue_status, name="update_status"),
    path("note", views.add_note, name="add_note"),
    path("blocked", views.blocked_orders, name="blocked"),
]
