"""
Payments Module - Serializers
"""

from rest_framework import serializers
from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    """Payment details"""

    amount_eur = serializers.FloatField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "order_id",
            "stripe_checkout_session_id",
            "seller_email",
            "amount_eur",
            "currency",
            "service_tier",
            "status",
            "created_at",
            "completed_at",
        ]
        read_only_fields = fields


class CheckoutSessionSerializer(serializers.Serializer):
    """Create checkout session"""

    order_id = serializers.CharField(max_length=50)
    service_tier = serializers.CharField(max_length=50)
    seller_email = serializers.EmailField()


class RefundSerializer(serializers.Serializer):
    """Refund request"""

    payment_id = serializers.CharField(max_length=36)
    reason = serializers.CharField(max_length=500, required=False)
