"""
Operator Module - Models
Queue management and order processing
"""

from django.db import models
from shared.constants.theme import ORDER_STATUS


class OperatorQueue(models.Model):
    """Operator's work queue"""

    PRIORITY_CHOICES = [
        ("critical", "Critical"),
        ("high", "High"),
        ("normal", "Normal"),
        ("low", "Low"),
    ]

    id = models.CharField(max_length=36, primary_key=True, default="uuid")
    order_id = models.CharField(max_length=50, db_index=True)
    assigned_operator = models.CharField(max_length=200, db_index=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default="normal")
    status = models.CharField(
        max_length=30,
        choices=[(k, k) for k in ORDER_STATUS.values()],
        default=ORDER_STATUS["processing"],
    )
    seller_name = models.CharField(max_length=200)
    seller_email = models.EmailField()
    seller_phone = models.CharField(max_length=20, null=True, blank=True)
    action_required = models.TextField(blank=True)
    blocked_reason = models.TextField(null=True, blank=True)
    last_contact_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "operator"
        indexes = [
            models.Index(fields=["assigned_operator", "-priority", "-updated_at"]),
            models.Index(fields=["status"]),
        ]
        unique_together = [("order_id", "assigned_operator")]

    def __str__(self):
        return f"Queue {self.order_id} - {self.assigned_operator}"


class OperatorNote(models.Model):
    """Notes on order processing"""

    id = models.CharField(max_length=36, primary_key=True, default="uuid")
    order_id = models.CharField(max_length=50, db_index=True)
    operator_name = models.CharField(max_length=200)
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "operator"
        indexes = [
            models.Index(fields=["order_id", "-created_at"]),
        ]

    def __str__(self):
        return f"Note on {self.order_id}"
