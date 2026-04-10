"""
Documents Module - Serializers
"""

from rest_framework import serializers
from .models import Document
from shared.constants.theme import DOCUMENT_TYPES


class DocumentSerializer(serializers.ModelSerializer):
    """Document detail"""

    document_type_name = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)
    days_to_expiry = serializers.IntegerField(read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "order_id",
            "document_type",
            "document_type_name",
            "status",
            "file_path",
            "issue_date",
            "expiry_date",
            "is_expired",
            "days_to_expiry",
            "verification_status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_document_type_name(self, obj):
        return DOCUMENT_TYPES.get(obj.document_type, {}).get("name")


class DocumentUploadSerializer(serializers.Serializer):
    """Document upload"""

    file = serializers.FileField()
    document_type = serializers.CharField(max_length=50)

    def validate_document_type(self, value):
        if value not in DOCUMENT_TYPES:
            raise serializers.ValidationError("Invalid document type")
        return value


class DocumentListSerializer(serializers.ModelSerializer):
    """List of documents for an order"""

    class Meta:
        model = Document
        fields = ["id", "document_type", "status", "expiry_date", "is_expired"]
