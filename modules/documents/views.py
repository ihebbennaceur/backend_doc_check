"""
Documents Module - Views
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from shared.utils.helpers import ResponseUtils, LoggingUtils
from shared.exceptions import ValidationError, NotFoundError
from .models import Document
from .serializers import DocumentSerializer, DocumentUploadSerializer, DocumentListSerializer
from .services import DocumentService


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_all_documents(request):
    """Get all documents
    GET /api/documents/
    """
    docs = Document.objects.all()
    serializer = DocumentListSerializer(docs, many=True)
    return Response(ResponseUtils.success(serializer.data))


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_document_general(request):
    """Upload document (general endpoint without order_id)
    POST /api/documents/upload/
    """
    serializer = DocumentUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        # If order_id provided in request data, use it; otherwise create without order
        order_id = request.data.get("order_id", None)
        
        doc = DocumentService.upload_document(
            order_id=order_id,
            seller_email=request.user.email,
            document_type=serializer.validated_data.get("document_type", "general"),
            file_content=serializer.validated_data["file"].read(),
            filename=serializer.validated_data["file"].name,
        )

        LoggingUtils.log_action(
            "document_uploaded",
            request.user.id,
            {"document_id": doc.id},
        )

        return Response(
            ResponseUtils.success(DocumentSerializer(doc).data, "Document uploaded"),
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        LoggingUtils.log_error(e, {"endpoint": "upload_document_general"})
        return Response(
            ResponseUtils.error("Upload failed"),
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_document(request, order_id):
    """Upload document for order
    POST /api/documents/<order_id>/upload/
    """
    serializer = DocumentUploadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        doc = DocumentService.upload_document(
            order_id=order_id,
            seller_email=request.user.email,
            document_type=serializer.validated_data["document_type"],
            file_content=serializer.validated_data["file"].read(),
            filename=serializer.validated_data["file"].name,
        )

        LoggingUtils.log_action(
            "document_uploaded",
            request.user.id,
            {"document_id": doc.id, "order_id": order_id},
        )

        return Response(
            ResponseUtils.success(DocumentSerializer(doc).data, "Document uploaded"),
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        LoggingUtils.log_error(e, {"endpoint": "upload_document", "order_id": order_id})
        return Response(
            ResponseUtils.error("Upload failed"),
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_documents(request, order_id):
    """Get all documents for order
    GET /api/documents/<order_id>/
    """
    docs = DocumentService.get_documents_by_order(order_id)
    serializer = DocumentListSerializer(docs, many=True)
    return Response(ResponseUtils.success(serializer.data))


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def document_detail(request, document_id):
    """Get document details
    GET /api/documents/<document_id>
    """
    try:
        doc = Document.objects.get(id=document_id)
        serializer = DocumentSerializer(doc)
        return Response(ResponseUtils.success(serializer.data))
    except Document.DoesNotExist:
        return Response(
            ResponseUtils.error("Document not found"),
            status=status.HTTP_404_NOT_FOUND,
        )
