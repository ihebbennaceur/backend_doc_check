"""
Payments Module - Services
Stripe integration and payment workflow
"""

import stripe
from django.conf import settings
from django.utils.timezone import now
from shared.constants.theme import SERVICE_TIERS
from shared.utils.helpers import IDGenerator
from shared.exceptions import PaymentError, ExternalServiceError
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentService:
    """Payment processing and management"""

    @staticmethod
    def create_checkout_session(order_id: str, seller_email: str, service_tier: str) -> str:
        """Create Stripe checkout session"""
        tier_data = SERVICE_TIERS.get(service_tier)
        if not tier_data:
            raise PaymentError("Invalid service tier")

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "eur",
                            "product_data": {
                                "name": tier_data["name"],
                                "description": tier_data["description"],
                            },
                            "unit_amount": tier_data["price"] * 100,
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=f"{settings.FRONTEND_URL}/success?order_id={order_id}",
                cancel_url=f"{settings.FRONTEND_URL}/cancel?order_id={order_id}",
                customer_email=seller_email,
                metadata={"order_id": order_id, "service_tier": service_tier},
            )

            payment = Payment.objects.create(
                id=IDGenerator.uuid(),
                order_id=order_id,
                stripe_checkout_session_id=session.id,
                seller_email=seller_email,
                amount_cents=tier_data["price"] * 100,
                service_tier=service_tier,
                status=Payment.PAYMENT_STATUS["pending"],
            )

            return session.url

        except stripe.error.StripeError as e:
            raise ExternalServiceError("Stripe", str(e))

    @staticmethod
    def confirm_payment(checkout_session_id: str):
        """Confirm payment from Stripe webhook"""
        try:
            session = stripe.checkout.Session.retrieve(checkout_session_id)

            payment = Payment.objects.get(stripe_checkout_session_id=checkout_session_id)

            if session.payment_status == "paid":
                payment.mark_succeeded(session.payment_intent)
                return payment
            else:
                payment.mark_failed()
                return None

        except stripe.error.StripeError as e:
            raise ExternalServiceError("Stripe", str(e))

    @staticmethod
    def refund_payment(payment_id: str, reason: str = None) -> bool:
        """Refund a payment"""
        payment = Payment.objects.get(id=payment_id)

        try:
            if payment.stripe_payment_intent_id:
                refund = stripe.Refund.create(payment_intent=payment.stripe_payment_intent_id)

                payment.status = Payment.PAYMENT_STATUS["refunded"]
                payment.refunded_amount_cents = payment.amount_cents
                payment.reason_for_refund = reason
                payment.save()

                return True
            else:
                raise PaymentError("No payment intent found for refund")

        except stripe.error.StripeError as e:
            raise ExternalServiceError("Stripe", str(e))

    @staticmethod
    def get_payment_status(checkout_session_id: str) -> dict:
        """Get payment status"""
        try:
            payment = Payment.objects.get(stripe_checkout_session_id=checkout_session_id)
            return {
                "status": payment.status,
                "order_id": payment.order_id,
                "amount": payment.amount_eur,
                "completed_at": payment.completed_at,
            }
        except Payment.DoesNotExist:
            raise PaymentError("Payment not found")
