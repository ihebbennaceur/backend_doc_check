"""
Documents Module - Models
Secure storage and lifecycle management of documents
"""

from django.db import models
from django.utils.timezone import now
from shared.constants.theme import DOCUMENT_STATUS, DOCUMENT_TYPES
from shared.utils.helpers import DateUtils


class Document(models.Model):
    """Document entity with lifecycle tracking"""

    id = models.CharField(max_length=36, primary_key=True, default="uuid")
    order_id = models.CharField(max_length=50, db_index=True)  # FK to DocReady order
    seller_email = models.EmailField(db_index=True)
    document_type = models.CharField(max_length=50, choices=[(k, v["name"]) for k, v in DOCUMENT_TYPES.items()])
    status = models.CharField(
        max_length=20,
        choices=[(k, k) for k in DOCUMENT_STATUS.values()],
        default=DOCUMENT_STATUS["pending"],
    )
    file_path = models.CharField(max_length=255, null=True, blank=True)  # Supabase Storage path
    file_size_bytes = models.IntegerField(null=True)
    issue_date = models.DateField(null=True, blank=True)
    expiry_date = models.DateField(null=True, blank=True)
    ocr_data = models.JSONField(default=dict, blank=True)  # Extracted fields from OCR
    verification_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "documents"
        unique_together = ("order_id", "document_type")
        indexes = [
            models.Index(fields=["seller_email", "-updated_at"]),
            models.Index(fields=["order_id", "status"]),
            models.Index(fields=["expiry_date"]),
        ]

    def __str__(self):
        return f"{self.document_type} - {self.order_id}"

    @property
    def is_expired(self) -> bool:
        """Check if document is expired"""
        if self.expiry_date is None:
            return False
        return DateUtils.is_expired(self.expiry_date)

    @property
    def days_to_expiry(self) -> int:
        """Days until expiry"""
        if self.expiry_date is None:
            return None
        return DateUtils.days_until_expiry(self.expiry_date)

    def mark_complete(self):
        """Mark document as complete"""
        self.status = DOCUMENT_STATUS["complete"]
        self.verification_status = True
        self.save()

    def mark_expired(self):
        """Mark document as expired"""
        self.status = DOCUMENT_STATUS["expired"]
        self.save()
