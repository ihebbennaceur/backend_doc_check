from rest_framework.generics import CreateAPIView, RetrieveUpdateAPIView, ListAPIView, UpdateAPIView, DestroyAPIView
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
from .models import User, Document, SellerProfile, AgentProfile, LawyerProfile, BuyerProfile
from .serializers import (
    RegisterSerializer,
    LoginSerializer,
    UserUpdateSerializer,
    AdminUserManagementSerializer,
    EmailVerificationSerializer,
    DocumentSerializer,
    DocumentListSerializer,
    DocumentApprovalSerializer,
    SellerProfileSerializer,
    AgentProfileSerializer,
    LawyerProfileSerializer,
    BuyerProfileSerializer,
    GoogleAuthSerializer
)

logger = logging.getLogger(__name__)


class IsAdmin(IsAdminUser):
    """Custom permission to check if user is admin role"""
    def has_permission(self, request, view):
        return bool(request.user and request.user.role == User.Role.ADMIN)


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


class GoogleAuthView(CreateAPIView):
    """
    Handle Google OAuth authentication
    Receives Google access token and returns JWT tokens
    POST /api/auth/google/
    """
    serializer_class = GoogleAuthSerializer
    permission_classes = []
    authentication_classes = []
    
    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            
            google_token = serializer.validated_data['access_token']
            
            # Verify the token with Google
            from google.auth.transport import requests as google_requests
            from google.oauth2 import id_token
            import os
            
            # Get the client ID from environment variable or settings
            from django.conf import settings
            client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID') or settings.SOCIALACCOUNT_PROVIDERS.get('google', {}).get('APP', {}).get('client_id')
            
            if not client_id:
                return Response(
                    {'error': 'Google OAuth not properly configured'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            # Verify the token
            try:
                idinfo = id_token.verify_oauth2_token(google_token, google_requests.Request(), client_id)
                
                # Token is valid, extract user info
                email = idinfo.get('email')
                first_name = idinfo.get('given_name', '')
                last_name = idinfo.get('family_name', '')
                picture_url = idinfo.get('picture', '')
                
                if not email:
                    return Response(
                        {'error': 'Email not provided in Google token'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Get or create user
                user, created = User.objects.get_or_create(
                    email=email.lower(),
                    defaults={
                        'username': email.split('@')[0].lower(),
                        'first_name': first_name,
                        'last_name': last_name,
                        'is_active': True,
                        'role': User.Role.SELLER  # Default role
                    }
                )
                
                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)
                
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'role': user.role
                    },
                    'is_new': created
                }, status=status.HTTP_200_OK)
                
            except ValueError as e:
                # Invalid token
                logger.error(f"Invalid Google token: {str(e)}")
                return Response(
                    {'error': 'Invalid Google token'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        except Exception as e:
            logger.error(f"Google auth error: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )