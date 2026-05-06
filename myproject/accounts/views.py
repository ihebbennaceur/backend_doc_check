from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, ListAPIView, ListCreateAPIView, UpdateAPIView, DestroyAPIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from django.shortcuts import get_object_or_404
import json
import logging
from .models import (
    User, Document, SellerProfile, AgentProfile, LawyerProfile, BuyerProfile,
    Property, PropertyDocumentTemplate, SellerDocumentSubmission
)
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserUpdateSerializer,
    UserDetailSerializer,
    AdminUserManagementSerializer,
    EmailVerificationSerializer,
    DocumentSerializer,
    DocumentListSerializer,
    DocumentApprovalSerializer,
    SellerProfileSerializer,
    AgentProfileSerializer,
    LawyerProfileSerializer,
    BuyerProfileSerializer,
    PropertySerializer,
    PropertyDetailSerializer,
    PropertyDocumentTemplateSerializer,
    SellerDocumentSubmissionListSerializer,
    SellerDocumentSubmissionDetailSerializer,
    PropertyFolderListSerializer,
    PropertyFolderDetailSerializer
)
from .pdf_analyzer import pdf_analyzer

logger = logging.getLogger(__name__)


class IsAdmin(IsAdminUser):
    """Custom permission to check if user is admin role"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == User.Role.ADMIN)


@api_view(['GET', 'PATCH'])
@permission_classes([IsAuthenticated])
def current_user(request):
    """Get or update current authenticated user details"""
    if request.method == 'GET':
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
    elif request.method == 'PATCH':
        serializer = UserDetailSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()
    permission_classes = []
    authentication_classes = []

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {'errors': serializer.errors},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            self.perform_create(serializer)
            user = serializer.instance
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role
                }
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )



class LoginView(CreateAPIView):
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }, status=status.HTTP_200_OK)


class UserUpdateView(RetrieveUpdateAPIView):
    serializer_class = UserUpdateSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserDetailView(RetrieveUpdateAPIView):
    """Get and update user profile details"""
    serializer_class = UserDetailSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class EmailVerificationView(CreateAPIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = User.objects.get(email=serializer.validated_data['email'])
        user.email_verified = True
        user.save()
        
        return Response({
            'message': 'Email verified successfully',
            'email': user.email,
            'email_verified': user.email_verified
        }, status=status.HTTP_200_OK)


class AdminUserManagementView(RetrieveUpdateAPIView):
    """Admin endpoint to manage users: change roles, activate/deactivate, verify email"""
    serializer_class = AdminUserManagementSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self):
        user_id = self.kwargs.get('user_id')
        return User.objects.get(id=user_id)


class AdminUserListView(ListAPIView):
    """Admin endpoint to list all users"""
    serializer_class = AdminUserManagementSerializer
    permission_classes = [IsAuthenticated, IsAdmin]
    queryset = User.objects.all()


class DocumentUploadView(CreateAPIView):
    """Users upload documents for verification"""
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        document = Document.objects.create(
            user=request.user,
            document_type=serializer.validated_data['document_type'],
            file=serializer.validated_data['file']
        )
        
        return Response(
            DocumentSerializer(document).data,
            status=status.HTTP_201_CREATED
        )


class UserDocumentsView(ListAPIView):
    """Users view their uploaded documents"""
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)


class DocumentDetailView(DestroyAPIView):
    """Users delete their own documents"""
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        document_id = self.kwargs.get('document_id')
        document = Document.objects.get(id=document_id)
        # Ensure user can only delete their own documents
        if document.user != self.request.user:
            raise PermissionDenied("You can only delete your own documents")
        return document


class AdminDocumentListView(ListAPIView):
    """Admin view all pending documents for approval"""
    serializer_class = DocumentListSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_queryset(self):
        status_filter = self.request.query_params.get('status', 'pending')
        return Document.objects.filter(status=status_filter)


class AdminDocumentApprovalView(RetrieveUpdateAPIView):
    """Admin approve/reject documents"""
    serializer_class = DocumentApprovalSerializer
    permission_classes = [IsAuthenticated, IsAdmin]

    def get_object(self):
        document_id = self.kwargs.get('document_id')
        return Document.objects.get(id=document_id)

    def update(self, request, *args, **kwargs):
        document = self.get_object()
        serializer = self.get_serializer(document, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        document.status = serializer.validated_data.get('status', document.status)
        document.rejection_reason = serializer.validated_data.get('rejection_reason', document.rejection_reason)
        document.reviewed_at = timezone.now()
        
        # If all documents are approved, mark user as verified
        if document.status == Document.VerificationStatus.APPROVED:
            if not document.user.documents.filter(status=Document.VerificationStatus.REJECTED).exists():
                document.user.email_verified = True
                document.user.save()
        
        document.save()
        
        return Response(
            DocumentListSerializer(document).data,
            status=status.HTTP_200_OK
        )


# ============================================================================
# PROFILE ENDPOINTS - Using Decorators
# ============================================================================

@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def seller_profile(request):
    """Get or update seller profile for current user"""
    try:
        profile = request.user.seller_profile
    except SellerProfile.DoesNotExist:
        return Response(
            {'detail': 'Seller profile does not exist for this user. Make sure your role is set to seller.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = SellerProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = SellerProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def agent_profile(request):
    """Get or update agent profile for current user"""
    try:
        profile = request.user.agent_profile
    except AgentProfile.DoesNotExist:
        return Response(
            {'detail': 'Agent profile does not exist for this user. Make sure your role is set to agent.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = AgentProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = AgentProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def lawyer_profile(request):
    """Get or update lawyer profile for current user"""
    try:
        profile = request.user.lawyer_profile
    except LawyerProfile.DoesNotExist:
        return Response(
            {'detail': 'Lawyer profile does not exist for this user. Make sure your role is set to lawyer.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = LawyerProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = LawyerProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def buyer_profile(request):
    """Get or update buyer profile for current user"""
    try:
        profile = request.user.buyer_profile
    except BuyerProfile.DoesNotExist:
        return Response(
            {'detail': 'Buyer profile does not exist for this user. Make sure your role is set to buyer.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    if request.method == 'GET':
        serializer = BuyerProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = BuyerProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DocumentExtractionView(UpdateAPIView):
    """Trigger extraction for a document - extracts fields and populates extracted_fields"""
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        document_id = self.kwargs.get('document_id')
        document = Document.objects.get(id=document_id)
        # Ensure user can only extract their own documents
        if document.user != self.request.user:
            raise PermissionDenied("You can only extract fields from your own documents")
        return document

    def update(self, request, *args, **kwargs):
        """Trigger extraction and return updated document"""
        document = self.get_object()
        
        try:
            # Import the extraction service from doccheck_service
            import sys
            import os
            doccheck_path = os.path.join(os.path.dirname(__file__), '../../../../django/doccheck_service')
            if doccheck_path not in sys.path:
                sys.path.insert(0, doccheck_path)
            
            # Try real extraction first, fall back to mock
            try:
                from cases.extraction_service import ExtractionService
                extraction_service = ExtractionService()
                extracted_data = extraction_service.extract_from_file(
                    document.file.path,
                    document.document_type
                )
            except Exception as e:
                logger.warning(f"Real extraction failed, using mock: {str(e)}")
                from cases.mock_extraction import extract_from_file_mock
                extracted_data = extract_from_file_mock(
                    document.file.path,
                    document.document_type
                )
            
            # Parse extraction result
            if isinstance(extracted_data, str):
                extracted_data = json.loads(extracted_data)
            
            # Store extracted_fields from the API response
            if extracted_data and isinstance(extracted_data, dict):
                # Get the extracted_fields from the API response structure
                document.extracted_fields = extracted_data.get('extracted_fields', {})
                document.save()
            
            # Return updated document
            serializer = self.get_serializer(document)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Extraction failed for document {document.id}: {str(e)}")
            return Response(
                {'error': f'Extraction failed: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def analyze_document_pdf(request, document_id):
    """
    Analyze a PDF document using AI (extract text, detect type, extract structured data)
    POST /api/documents/{document_id}/analyze/
    """
    try:
        document = Document.objects.get(id=document_id, user=request.user)
        
        # Check if document is PDF
        if not document.file.name.lower().endswith('.pdf'):
            return Response(
                {'error': 'Only PDF documents can be analyzed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get file path
        file_path = document.file.path
        
        # Get analysis type from request
        analysis_type = request.data.get('analysis_type', 'full')
        
        result = {}
        
        if analysis_type in ['extract', 'full']:
            # Extract text from PDF
            result['text_extraction'] = pdf_analyzer.extract_text_from_pdf(file_path)
        
        if analysis_type in ['detect', 'full']:
            # Detect document type
            type_analysis = pdf_analyzer.detect_document_type(file_path)
            result['document_type_analysis'] = type_analysis
        
        if analysis_type == 'structured':
            # Extract specific fields
            fields = request.data.get('fields', ['invoice_number', 'date', 'amount'])
            result['structured_data'] = pdf_analyzer.extract_structured_data(file_path, fields)
        
        # Store results in document
        document.analysis_result = result
        document.save()
        
        return Response({
            'document_id': document.id,
            'analysis_type': analysis_type,
            'result': result,
            'status': 'completed'
        }, status=status.HTTP_200_OK)
        
    except Document.DoesNotExist:
        return Response(
            {'error': 'Document not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"PDF analysis failed: {str(e)}")
        return Response(
            {'error': f'Analysis failed: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Property Document Templates Views

class PropertyDocumentTemplateListView(ListAPIView):
    """Get all property document templates required for house sale"""
    queryset = PropertyDocumentTemplate.objects.all()
    serializer_class = PropertyDocumentTemplateSerializer
    permission_classes = []
    authentication_classes = []


class AdminPropertyDocumentsListView(ListAPIView):
    """Admin endpoint to list all property document submissions for review"""
    serializer_class = SellerDocumentSubmissionDetailSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        # Get filter from query params
        status = self.request.query_params.get('status', None)
        
        queryset = SellerDocumentSubmission.objects.all()
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset.order_by('-submitted_at')


# Seller Document Submission Views

class SellerDocumentSubmissionListView(ListAPIView):
    """Get all document submissions for the current seller"""
    serializer_class = SellerDocumentSubmissionListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only return submissions for the current user (if seller)
        if self.request.user.role != User.Role.SELLER:
            return SellerDocumentSubmission.objects.none()
        return SellerDocumentSubmission.objects.filter(seller=self.request.user)


class SellerDocumentSubmissionDetailView(RetrieveUpdateAPIView):
    """Get or update a specific document submission"""
    serializer_class = SellerDocumentSubmissionDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        # Only return submissions for the current user
        return SellerDocumentSubmission.objects.filter(seller=self.request.user)
    
    def get_object(self):
        obj = super().get_object()
        if obj.seller != self.request.user:
            raise PermissionDenied("You can only access your own submissions")
        return obj
    
    def perform_update(self, serializer):
        """When file is uploaded, extract data and check for missing fields"""
        submission = serializer.save()
        
        if submission.file:
            try:
                # Analyze the uploaded PDF
                file_path = submission.file.path
                
                # Extract structured data for required fields
                fields = submission.template.required_fields or []
                if fields:
                    analysis = pdf_analyzer.extract_structured_data(file_path, fields)
                    submission.extracted_data = analysis.get('result', {}).get('structured_data', {})
                else:
                    # Extract all text if no specific fields defined
                    text = pdf_analyzer.extract_text_from_pdf(file_path)
                    submission.extracted_data = {'full_text': text}
                
                # Check for missing fields
                missing = []
                extracted_data = submission.extracted_data.get('structured_data', {}) if 'structured_data' in str(submission.extracted_data) else submission.extracted_data
                
                for field in fields:
                    if field not in extracted_data or not extracted_data[field]:
                        missing.append(field)
                
                submission.missing_fields = missing
                submission.status = SellerDocumentSubmission.SubmissionStatus.PENDING_REVIEW
                submission.submitted_at = timezone.now()
                submission.save()
                
            except Exception as e:
                logger.error(f"Error analyzing document: {str(e)}")
                submission.extracted_data = {'error': str(e)}
                submission.save()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def seller_documents_dashboard(request):
    """Get seller's document submission dashboard with summary"""
    if request.user.role != User.Role.SELLER:
        return Response(
            {'error': 'Only sellers can access this endpoint'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    submissions = SellerDocumentSubmission.objects.filter(seller=request.user)
    
    summary = {
        'total_documents': submissions.count(),
        'submitted': submissions.filter(status__in=[
            SellerDocumentSubmission.SubmissionStatus.PENDING_REVIEW,
            SellerDocumentSubmission.SubmissionStatus.APPROVED,
            SellerDocumentSubmission.SubmissionStatus.REJECTED,
            SellerDocumentSubmission.SubmissionStatus.NEEDS_REVISION
        ]).count(),
        'approved': submissions.filter(status=SellerDocumentSubmission.SubmissionStatus.APPROVED).count(),
        'pending_review': submissions.filter(status=SellerDocumentSubmission.SubmissionStatus.PENDING_REVIEW).count(),
        'rejected': submissions.filter(status=SellerDocumentSubmission.SubmissionStatus.REJECTED).count(),
        'needs_revision': submissions.filter(status=SellerDocumentSubmission.SubmissionStatus.NEEDS_REVISION).count(),
        'not_submitted': submissions.filter(status=SellerDocumentSubmission.SubmissionStatus.NOT_SUBMITTED).count(),
        'submissions': SellerDocumentSubmissionListSerializer(submissions, many=True).data
    }
    
    return Response(summary, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, IsAdminUser])
def admin_review_document(request, submission_id):
    """Admin endpoint to review and approve/reject document submissions"""
    try:
        submission = SellerDocumentSubmission.objects.get(id=submission_id)
        
        action = request.data.get('action')  # 'approve', 'reject', 'needs_revision'
        notes = request.data.get('notes', '')
        
        if action == 'approve':
            submission.status = SellerDocumentSubmission.SubmissionStatus.APPROVED
        elif action == 'reject':
            submission.status = SellerDocumentSubmission.SubmissionStatus.REJECTED
        elif action == 'needs_revision':
            submission.status = SellerDocumentSubmission.SubmissionStatus.NEEDS_REVISION
        else:
            return Response(
                {'error': 'Invalid action. Use: approve, reject, or needs_revision'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        submission.reviewer_notes = notes
        submission.reviewer = request.user
        submission.reviewed_at = timezone.now()
        submission.save()
        
        serializer = SellerDocumentSubmissionDetailSerializer(submission)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    except SellerDocumentSubmission.DoesNotExist:
        return Response(
            {'error': 'Submission not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error reviewing document: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


########################################################################
# PROPERTY MANAGEMENT VIEWS

class PropertyListView(ListCreateAPIView):
    """List seller's properties and create new property"""
    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only show properties for authenticated seller"""
        if self.request.user.role != User.Role.SELLER:
            return Property.objects.none()
        return Property.objects.filter(seller=self.request.user)
    
    def perform_create(self, serializer):
        """Create new property with current user as seller"""
        if self.request.user.role != User.Role.SELLER:
            raise PermissionDenied("Only sellers can create properties")
        serializer.save(seller=self.request.user)


class PropertyDetailView(RetrieveUpdateAPIView):
    """Get, update property details"""
    serializer_class = PropertyDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        """Only show property if user is the seller"""
        user = self.request.user
        if user.role == User.Role.SELLER:
            return Property.objects.filter(seller=user)
        elif user.role == User.Role.ADMIN:
            return Property.objects.all()
        return Property.objects.none()
    
    def get_object(self):
        """Get property by id"""
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs['id'])
        self.check_object_permissions(self.request, obj)
        return obj
    
    def put(self, request, *args, **kwargs):
        """Update property - sellers can only update their own"""
        property_obj = self.get_object()
        
        if property_obj.seller != request.user and request.user.role != User.Role.ADMIN:
            raise PermissionDenied("You can only update your own properties")
        
        serializer = self.get_serializer(property_obj, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, *args, **kwargs):
        """Partial update property"""
        property_obj = self.get_object()
        
        if property_obj.seller != request.user and request.user.role != User.Role.ADMIN:
            raise PermissionDenied("You can only update your own properties")
        
        serializer = self.get_serializer(property_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)


# ============================================================================
# Process/Folder-based Workflow Views
# ============================================================================

class PropertyFolderListView(ListCreateAPIView):
    """List all property folders (requests/cases) for seller with document summaries"""
    serializer_class = PropertyFolderListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Only show properties for authenticated seller"""
        if self.request.user.role != User.Role.SELLER:
            return Property.objects.none()
        return Property.objects.filter(seller=self.request.user).prefetch_related('document_submissions')
    
    def perform_create(self, serializer):
        """Create new property (folder) with current user as seller"""
        if self.request.user.role != User.Role.SELLER:
            raise PermissionDenied("Only sellers can create properties")
        serializer.save(seller=self.request.user)


class PropertyFolderDetailView(RetrieveUpdateAPIView):
    """Get property folder details with documents grouped by category"""
    serializer_class = PropertyFolderDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        """Only show property if user is the seller"""
        user = self.request.user
        if user.role == User.Role.SELLER:
            return Property.objects.filter(seller=user).prefetch_related('document_submissions__template')
        elif user.role == User.Role.ADMIN:
            return Property.objects.all().prefetch_related('document_submissions__template')
        return Property.objects.none()
    
    def get_object(self):
        """Get property by id"""
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, id=self.kwargs['id'])
        self.check_object_permissions(self.request, obj)
        return obj
    
    def put(self, request, *args, **kwargs):
        """Update property folder"""
        property_obj = self.get_object()
        
        if property_obj.seller != request.user and request.user.role != User.Role.ADMIN:
            raise PermissionDenied("You can only update your own properties")
        
        serializer = self.get_serializer(property_obj, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request, *args, **kwargs):
        """Partial update property folder"""
        property_obj = self.get_object()
        
        if property_obj.seller != request.user and request.user.role != User.Role.ADMIN:
            raise PermissionDenied("You can only update your own properties")
        
        serializer = self.get_serializer(property_obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(serializer.data, status=status.HTTP_200_OK)