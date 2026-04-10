"""Documents Module - URLs"""

from django.urls import path
from . import views

app_name = "documents"

urlpatterns = [
    path("", views.list_all_documents, name="list_all"),
    path("upload/", views.upload_document_general, name="upload_general"),
    path("<str:order_id>/upload/", views.upload_document, name="upload"),
    path("<str:order_id>/", views.list_documents, name="list"),
    path("detail/<str:document_id>/", views.document_detail, name="detail"),
]
