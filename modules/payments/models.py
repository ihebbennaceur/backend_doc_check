"""
Payments Module - Models
Stripe payment processing and order confirmation
"""

from django.db import models
from shared.constants.theme import SERVICE_TIERS, ORDER_STATUS


class Payment(models.Model):
    """Payment transaction record"""

    PAYMENT_STATUS = {
        "pending": "pending",
        "processing": "processing",
        "succeeded": "succeeded",
        "failed": "failed",
        "refunded": "refunded",
    }

    id = models.CharField(max_length=36, primary_key=True, default="uuid")
    order_id = models.CharField(max_length=50, db_index=True)
    stripe_checkout_session_id = models.CharField(max_length=255, unique=True, db_index=True)
    stripe_payment_intent_id = models.CharField(max_length=255, null=True, blank=True)
    seller_email = models.EmailField(db_index=True)
    amount_cents = models.IntegerField()  # In cents (e.g., 39900 = €399.00)
    currency = models.CharField(max_length=3, default="EUR")
    service_tier = models.CharField(max_length=50, choices=[(k, v["name"]) for k, v in SERVICE_TIERS.items()])
    status = models.CharField(
        max_length=20,
        choices=[(k, k) for k in PAYMENT_STATUS.values()],
        default=PAYMENT_STATUS["pending"],
    )
    refunded_amount_cents = models.IntegerField(default=0)
    reason_for_refund = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "payments"
        indexes = [
            models.Index(fields=["order_id", "-created_at"]),
            models.Index(fields=["seller_email", "status"]),
        ]

    def __str__(self):
        return f"Payment {self.id} - {self.order_id}"

    @property
    def amount_eur(self) -> float:
        """Amount in EUR"""
        return self.amount_cents / 100

    def mark_succeeded(self, stripe_payment_id: str = None):
        """Mark payment as successful"""
        from django.utils.timezone import now

        self.status = self.PAYMENT_STATUS["succeeded"]
        if stripe_payment_id:
            self.stripe_payment_intent_id = stripe_payment_id
        self.completed_at = now()
        self.save()

    def mark_failed(self):
        """Mark payment as failed"""
        self.status = self.PAYMENT_STATUS["failed"]
        self.save()
