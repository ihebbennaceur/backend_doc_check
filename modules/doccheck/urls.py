"""DocCheck Module - URL Configuration"""

from django.urls import path
from . import views

app_name = "doccheck"

urlpatterns = [
    # Enhanced assessment (8 questions with persona detection)
    path("assess", views.assess_enhanced, name="assess_enhanced"),
    
    # Legacy endpoints (kept for backward compatibility)
    path("start", views.start_assessment, name="start_assessment"),
    path("<str:session_id>/result", views.get_assessment_result, name="get_result"),
]
