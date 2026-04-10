"""
DocCheck Module - Models
Free assessment tool to identify missing documents
"""

from django.db import models
from django.utils.timezone import now
from shared.constants.theme import DOCUMENT_TYPES, SELLER_PERSONAS


class DocCheckSession(models.Model):
    """Assessment session for a seller"""

    id = models.CharField(max_length=36, primary_key=True, default="uuid")
    email = models.EmailField(unique=False)
    property_type = models.CharField(max_length=50)  # apartment, house, quinta
    property_location = models.CharField(max_length=100)  # district
    is_mortgaged = models.BooleanField(default=False)
    is_inherited = models.BooleanField(default=False)
    # Persona detection fields
    is_portugal_resident = models.BooleanField(default=True, null=True)  # Portugal resident or abroad?
    ownership_type = models.CharField(max_length=50, default='sole', choices=[
        ('sole', 'Sole Owner'),
        ('joint', 'Joint Ownership'),
        ('inherited', 'Inherited'),
        ('multiple_heirs', 'Multiple Heirs'),
        ('other', 'Other'),
    ])
    urgency = models.CharField(max_length=50, default='normal', choices=[
        ('normal', 'Normal Timeline'),
        ('urgent', 'Urgent (30 days)'),
        ('very_urgent', 'Very Urgent (2 weeks)'),
    ])
    seller_persona = models.CharField(max_length=50, choices=[(k, v["name"]) for k, v in SELLER_PERSONAS.items()], null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()

    class Meta:
        app_label = "doccheck"
        verbose_name = "DocCheck Session"
        verbose_name_plural = "DocCheck Sessions"
        indexes = [models.Index(fields=["email", "-created_at"])]

    def __str__(self):
        return f"DocCheck {self.email} - {self.id}"


class DocCheckResult(models.Model):
    """Assessment result with missing documents"""

    session = models.OneToOneField(DocCheckSession, on_delete=models.CASCADE, related_name="result")
    missing_documents = models.JSONField(default=list)  # list of document slugs
    required_tier = models.CharField(max_length=50)  # recommended service tier
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    estimated_days = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "doccheck"
        verbose_name = "DocCheck Result"

    def __str__(self):
        return f"Result for {self.session.email}"
