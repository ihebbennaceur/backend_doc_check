"""
DocReady Module - Models
Order management and document procurement workflow
"""

from django.db import models
from shared.constants.theme import ORDER_STATUS, SERVICE_TIERS


class FizboOrder(models.Model):
    """Order for document preparation service"""

    id = models.CharField(max_length=50, primary_key=True)  # FIZ-TIMESTAMP-SHORT
    seller_email = models.EmailField(db_index=True)
    seller_phone = models.CharField(max_length=20, null=True, blank=True)
    seller_name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, null=True, blank=True)  # Account phone (collected during onboarding)
    service_tier = models.CharField(
        max_length=50,
        choices=[(k, v["name"]) for k, v in SERVICE_TIERS.items()],
    )
    status = models.CharField(
        max_length=30,
        choices=[(k, k) for k in ORDER_STATUS.values()],
        default=ORDER_STATUS["draft"],
    )
    payment_id = models.CharField(max_length=36, null=True, blank=True, db_index=True)
    property_address = models.TextField(null=True, blank=True)
    property_type = models.CharField(max_length=50, null=True, blank=True)  # apartment, house, quinta
    notes = models.TextField(blank=True)
    assigned_operator = models.CharField(max_length=200, null=True, blank=True)
    whatsapp_opt_in = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "docready"
        indexes = [
            models.Index(fields=["seller_email", "-created_at"]),
            models.Index(fields=["status", "-updated_at"]),
            models.Index(fields=["assigned_operator"]),
        ]

    def __str__(self):
        return f"Order {self.id}"

    @property
    def is_completed(self) -> bool:
        return self.status == ORDER_STATUS["completed"]

    def mark_payment_confirmed(self, payment_id: str):
        """Mark payment as confirmed"""
        from django.utils.timezone import now

        self.payment_id = payment_id
        self.status = ORDER_STATUS["payment_confirmed"]
        self.payment_confirmed_at = now()
        self.save()

    def mark_processing(self):
        """Mark order as processing"""
        self.status = ORDER_STATUS["processing"]
        self.save()

    def mark_completed(self):
        """Mark order as completed"""
        from django.utils.timezone import now

        self.status = ORDER_STATUS["completed"]
        self.completed_at = now()
        self.save()
