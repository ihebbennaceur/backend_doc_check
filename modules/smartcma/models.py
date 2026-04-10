"""
SmartCMA Module - Models
Price intelligence and valuation reports
"""

from django.db import models


class CMAReport(models.Model):
    """Comparative Market Analysis Report"""

    id = models.CharField(max_length=36, primary_key=True, default="uuid")
    order_id = models.CharField(max_length=50, db_index=True)
    seller_email = models.EmailField(db_index=True)
    property_address = models.CharField(max_length=255)
    property_type = models.CharField(max_length=50)  # apartment, house, quinta
    area_sqm = models.FloatField(null=True, blank=True)
    bedrooms = models.IntegerField(null=True, blank=True)
    bathrooms = models.IntegerField(null=True, blank=True)
    estimated_price = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    price_range_min = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    price_range_max = models.DecimalField(max_digits=12, decimal_places=2, null=True)
    comparables = models.JSONField(default=list)  # List of similar properties
    market_analysis = models.JSONField(default=dict)  # Market data
    report_pdf_path = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "smartcma"
        indexes = [
            models.Index(fields=["order_id"]),
            models.Index(fields=["seller_email"]),
        ]

    def __str__(self):
        return f"CMA {self.id}"
