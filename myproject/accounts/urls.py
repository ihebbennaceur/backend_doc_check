from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    UserUpdateView,
    UserDetailView,
    current_user,
    EmailVerificationView,
    AdminUserManagementView,
    AdminUserListView,
    DocumentUploadView,
    DocumentDetailView,
    DocumentExtractionView,
    UserDocumentsView,
    AdminDocumentListView,
    AdminDocumentApprovalView,
    analyze_document_pdf,
    seller_profile,
    agent_profile,
    lawyer_profile,
    buyer_profile,
    PropertyListView,
    PropertyDetailView,
    PropertyFolderListView,
    PropertyFolderDetailView,
    PropertyDocumentTemplateListView,
    AdminPropertyDocumentsListView,
    SellerDocumentSubmissionListView,
    SellerDocumentSubmissionDetailView,
    seller_documents_dashboard,
    admin_review_document
)

urlpatterns = [
    # Auth endpoints
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("me/", current_user, name="current_user"),  # Simple GET endpoint for current user
    path("profile/", UserUpdateView.as_view(), name="profile"),
    path("user/", UserDetailView.as_view(), name="user_detail"),  # Detailed profile endpoint
    
    # Email verification
    path("verify-email/", EmailVerificationView.as_view(), name="verify_email"),
    
    # Document upload (user)
    path("documents/upload/", DocumentUploadView.as_view(), name="upload_document"),
    path("documents/", UserDocumentsView.as_view(), name="user_documents"),
    path("documents/<int:document_id>/", DocumentDetailView.as_view(), name="document_detail"),
    path("documents/<int:document_id>/extract/", DocumentExtractionView.as_view(), name="document_extraction"),
    path("documents/<int:document_id>/analyze/", analyze_document_pdf, name="analyze_pdf"),  # AI PDF analysis
    
    # Property selling documents
    path("property-documents/templates/", PropertyDocumentTemplateListView.as_view(), name="property_document_templates"),
    path("property-documents/", SellerDocumentSubmissionListView.as_view(), name="seller_documents_list"),
    path("property-documents/<int:id>/", SellerDocumentSubmissionDetailView.as_view(), name="seller_document_detail"),
    path("property-documents/dashboard/", seller_documents_dashboard, name="seller_documents_dashboard"),
    
    # Profile endpoints (with decorators)
    path("profiles/seller/", seller_profile, name="seller_profile"),
    path("profiles/agent/", agent_profile, name="agent_profile"),
    path("profiles/lawyer/", lawyer_profile, name="lawyer_profile"),
    path("profiles/buyer/", buyer_profile, name="buyer_profile"),
    
    # Property management (seller)
    path("properties/", PropertyListView.as_view(), name="properties_list"),
    path("properties/<int:id>/", PropertyDetailView.as_view(), name="property_detail"),
    
    # Folder-based workflow (new process UI)
    path("folders/", PropertyFolderListView.as_view(), name="property_folders_list"),
    path("folders/<int:id>/", PropertyFolderDetailView.as_view(), name="property_folder_detail"),
    
    # Admin endpoints
    path("admin/users/", AdminUserListView.as_view(), name="admin_users_list"),
    path("admin/users/<int:user_id>/", AdminUserManagementView.as_view(), name="admin_user_detail"),
    path("admin/documents/", AdminDocumentListView.as_view(), name="admin_documents_list"),
    path("admin/documents/<int:document_id>/", AdminDocumentApprovalView.as_view(), name="admin_document_approval"),
    path("admin/property-documents/", AdminPropertyDocumentsListView.as_view(), name="admin_property_documents_list"),
    path("admin/property-documents/<int:submission_id>/review/", admin_review_document, name="admin_review_property_document"),
]