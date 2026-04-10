"""
SmartCMA Module - Serializers
"""

from rest_framework import serializers
from .models import CMAReport


class CMAReportSerializer(serializers.ModelSerializer):
    """CMA report details"""

    class Meta:
        model = CMAReport
        fields = [
            "id",
            "order_id",
            "property_address",
            "property_type",
            "area_sqm",
            "bedrooms",
            "bathrooms",
            "estimated_price",
            "price_range_min",
            "price_range_max",
            "comparables",
            "market_analysis",
            "report_pdf_path",
            "created_at",
        ]
        read_only_fields = ["id", "created_at", "report_pdf_path"]


class GenerateReportSerializer(serializers.Serializer):
    """Generate CMA report"""

    order_id = serializers.CharField(max_length=50)
    address = serializers.CharField(max_length=255)
    property_type = serializers.CharField(max_length=50)
    area_sqm = serializers.FloatField(required=False)
    bedrooms = serializers.IntegerField(required=False)
    bathrooms = serializers.IntegerField(required=False)
