"""
Payments Module - Views
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from shared.utils.helpers import ResponseUtils, LoggingUtils
from .serializers import CheckoutSessionSerializer, PaymentSerializer, RefundSerializer
from .services import PaymentService


@api_view(["POST"])
def create_checkout(request):
    """Create Stripe checkout session
    POST /api/payments/checkout
    """
    serializer = CheckoutSessionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        checkout_url = PaymentService.create_checkout_session(**serializer.validated_data)

        LoggingUtils.log_action(
            "checkout_created",
            details={"order_id": serializer.validated_data["order_id"]},
        )

        return Response(
            ResponseUtils.success(data={"checkout_url": checkout_url}, message="Checkout session created"),
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        LoggingUtils.log_error(e, {"endpoint": "create_checkout"})
        return Response(
            ResponseUtils.error("Failed to create checkout"),
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
def payment_status(request, session_id):
    """Get payment status
    GET /api/payments/<session_id>/status
    """
    try:
        status_data = PaymentService.get_payment_status(session_id)
        return Response(ResponseUtils.success(status_data))
    except Exception as e:
        return Response(
            ResponseUtils.error("Payment not found"),
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
def webhook_payment_confirmed(request):
    """Webhook handler for Stripe payment confirmed
    POST /api/payments/webhook
    """
    event = request.data
    session_id = event.get("data", {}).get("object", {}).get("id")

    if event.get("type") == "checkout.session.completed":
        try:
            PaymentService.confirm_payment(session_id)
            LoggingUtils.log_action("payment_confirmed", details={"session_id": session_id})
            return Response({"status": "success"})
        except Exception as e:
            LoggingUtils.log_error(e, {"endpoint": "webhook_payment_confirmed"})
            return Response({"status": "error"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"status": "ignored"})


@api_view(["POST"])
def refund_payment(request):
    """Request refund
    POST /api/payments/refund
    """
    serializer = RefundSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        PaymentService.refund_payment(**serializer.validated_data)
        LoggingUtils.log_action(
            "payment_refunded",
            details={"payment_id": serializer.validated_data["payment_id"]},
        )
        return Response(ResponseUtils.success(message="Refund processed"))
    except Exception as e:
        LoggingUtils.log_error(e, {"endpoint": "refund_payment"})
        return Response(
            ResponseUtils.error("Refund failed"),
            status=status.HTTP_400_BAD_REQUEST,
        )
