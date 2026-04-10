"""
Swagger/OpenAPI Schema Customization Examples

This file shows how to add better documentation to your API endpoints using drf-spectacular.
"""

from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from rest_framework import serializers

# Example: Adding detailed schema documentation to a view

example_request = OpenApiExample(
    'Valid Request Example',
    value={
        'email': 'user@example.com',
        'password': 'securepassword123'
    }
)

example_response = OpenApiExample(
    'Success Response Example',
    value={
        'access': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
        'refresh': 'eyJ0eXAiOiJKV1QiLCJhbGc...',
        'user': {
            'id': 1,
            'email': 'user@example.com',
            'first_name': 'John',
            'last_name': 'Doe'
        }
    }
)

# Example: How to apply to a view

"""
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView

class LoginView(APIView):
    @extend_schema(
        operation_id='user_login',
        summary='User Login',
        description='Authenticate user and return JWT tokens',
        request=LoginSerializer,
        responses={
            200: example_response,
            401: {'description': 'Invalid credentials'}
        },
        examples=[example_request, example_response],
        tags=['Authentication'],
        security=[],  # No authentication required
    )
    def post(self, request):
        # ... implementation
        pass
"""

# Example: Parameter documentation

"""
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.viewsets import ModelViewSet

class DocumentViewSet(ModelViewSet):
    @extend_schema(
        operation_id='list_documents',
        summary='List all documents',
        description='Get a paginated list of user documents with optional filtering',
        parameters=[
            OpenApiParameter(
                'document_type',
                str,
                OpenApiParameter.QUERY,
                description='Filter by document type (ID, PASSPORT, DRIVER_LICENSE, etc)',
                examples=['ID', 'PASSPORT']
            ),
            OpenApiParameter(
                'status',
                str,
                OpenApiParameter.QUERY,
                description='Filter by verification status (PENDING, VERIFIED, REJECTED)',
            ),
            OpenApiParameter(
                'page',
                int,
                OpenApiParameter.QUERY,
                description='Page number for pagination',
            ),
            OpenApiParameter(
                'limit',
                int,
                OpenApiParameter.QUERY,
                description='Number of items per page',
            ),
        ],
        tags=['Documents'],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
"""

# Example: Error response documentation

"""
from drf_spectacular.utils import extend_schema

error_responses = {
    400: {'description': 'Bad Request - Invalid input parameters'},
    401: {'description': 'Unauthorized - Authentication required'},
    403: {'description': 'Forbidden - Insufficient permissions'},
    404: {'description': 'Not Found - Resource does not exist'},
    500: {'description': 'Internal Server Error - Server error occurred'},
}

class DocumentDetailView(APIView):
    @extend_schema(
        responses={
            200: DocumentSerializer,
            **error_responses
        },
    )
    def get(self, request, pk):
        pass
"""

# Example: File upload documentation

"""
from drf_spectacular.utils import extend_schema
from rest_framework.parsers import MultiPartParser

class DocumentUploadView(APIView):
    parser_classes = (MultiPartParser,)
    
    @extend_schema(
        operation_id='upload_document',
        summary='Upload a document',
        description='Upload a document file (PDF, JPG, PNG)',
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'file': {
                        'type': 'string',
                        'format': 'binary',
                        'description': 'Document file to upload'
                    },
                    'document_type': {
                        'type': 'string',
                        'description': 'Type of document'
                    }
                }
            }
        },
        responses={201: DocumentSerializer},
    )
    def post(self, request):
        pass
"""

print("Swagger Customization Examples loaded")
print("See comments above for implementation patterns")
