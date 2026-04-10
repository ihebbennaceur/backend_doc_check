"""DocReady Module - URLs"""

from django.urls import path
from . import views

app_name = "docready"

urlpatterns = [
    path("", views.create_order, name="create"),
    path("<str:order_id>/", views.order_detail, name="detail"),
    path("seller/list/", views.seller_orders, name="seller_orders"),
    path("<str:order_id>/update/", views.update_order, name="update"),
]
