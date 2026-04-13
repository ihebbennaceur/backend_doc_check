from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    UserUpdateView,
    EmailVerificationView,
    AdminUserManagementView,
    AdminUserListView,
    DocumentUploadView,
    DocumentDetailView,
    DocumentExtractionView,
    UserDocumentsView,
    AdminDocumentListView,
    AdminDocumentApprovalView,
    GoogleAuthView,
    seller_profile,
    agent_profile,
    lawyer_profile,
    buyer_profile
)

urlpatterns = [
    # Auth endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("auth/google/", GoogleAuthView.as_view(), name="google_auth"),
    path("profile/", UserUpdateView.as_view(), name="profile"),
    
    # Email verification
    path("verify-email/", EmailVerificationView.as_view(), name="verify_email"),
    
    # Document upload (user)
    path("documents/upload/", DocumentUploadView.as_view(), name="upload_document"),
    path("documents/", UserDocumentsView.as_view(), name="user_documents"),
    path("documents/<int:document_id>/", DocumentDetailView.as_view(), name="document_detail"),
    path("documents/<int:document_id>/extract/", DocumentExtractionView.as_view(), name="document_extraction"),
    
    # Profile endpoints (with decorators)
    path("profiles/seller/", seller_profile, name="seller_profile"),
    path("profiles/agent/", agent_profile, name="agent_profile"),
    path("profiles/lawyer/", lawyer_profile, name="lawyer_profile"),
    path("profiles/buyer/", buyer_profile, name="buyer_profile"),
    
    # Admin endpoints
    path("admin/users/", AdminUserListView.as_view(), name="admin_users_list"),
    path("admin/users/<int:user_id>/", AdminUserManagementView.as_view(), name="admin_user_detail"),
    path("admin/documents/", AdminDocumentListView.as_view(), name="admin_documents_list"),
    path("admin/documents/<int:document_id>/", AdminDocumentApprovalView.as_view(), name="admin_document_approval"),
]