"""
DocReady Module - Serializers
"""

from rest_framework import serializers
from .models import FizboOrder
from shared.constants.theme import SERVICE_TIERS


class OrderCreateSerializer(serializers.Serializer):
    """Create or update order"""

    seller_email = serializers.EmailField(required=False)
    seller_name = serializers.CharField(max_length=200, required=False)
    seller_phone = serializers.CharField(max_length=20, required=False)
    phone = serializers.CharField(max_length=20, required=False)
    service_tier = serializers.CharField(max_length=50, required=False)
    whatsapp_opt_in = serializers.BooleanField(required=False)

    def validate_service_tier(self, value):
        if value and value not in SERVICE_TIERS:
            raise serializers.ValidationError("Invalid service tier")
        return value


class OrderDetailSerializer(serializers.ModelSerializer):
    """Order details"""

    service_tier_name = serializers.SerializerMethodField()

    class Meta:
        model = FizboOrder
        fields = [
            "id",
            "seller_email",
            "seller_name",
            "seller_phone",
            "phone",
            "service_tier",
            "service_tier_name",
            "status",
            "whatsapp_opt_in",
            "assigned_operator",
            "created_at",
            "completed_at",
        ]

    def get_service_tier_name(self, obj):
        return SERVICE_TIERS.get(obj.service_tier, {}).get("name")


class OrderListSerializer(serializers.ModelSerializer):
    """Order list"""

    class Meta:
        model = FizboOrder
        fields = ["id", "status", "created_at", "completed_at"]
