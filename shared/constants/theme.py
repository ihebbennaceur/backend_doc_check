"""
Fizbo Theme & Brand Constants
Centralized theme, colors, and branding for the entire platform
"""

# ============================================================================
# BRAND COLORS
# ============================================================================

BRAND_COLORS = {
    "primary": "#2E5D4B",      # Forest green
    "accent": "#4A9B7F",       # Mid green
    "gold": "#C9A84C",         # Warm gold
    "background": "#F5F0E8",   # Warm cream
    "text_dark": "#1A1A2E",    # Dark text
    "text_light": "#FFFFFF",   # Light text
    "error": "#D32F2F",        # Error red
    "warning": "#F57C00",      # Warning orange
    "success": "#388E3C",      # Success green
    "info": "#1976D2",         # Info blue
}

# ============================================================================
# TYPOGRAPHY
# ============================================================================

FONTS = {
    "heading": "Inter",
    "body": "Source Serif 4",
}

FONT_SIZES = {
    "xs": "12px",
    "sm": "14px",
    "base": "16px",
    "lg": "18px",
    "xl": "20px",
    "2xl": "24px",
    "3xl": "30px",
}

# ============================================================================
# SPACING
# ============================================================================

SPACING = {
    "xs": "4px",
    "sm": "8px",
    "md": "16px",
    "lg": "24px",
    "xl": "32px",
    "2xl": "48px",
}

# ============================================================================
# BORDER RADIUS
# ============================================================================

BORDER_RADIUS = {
    "sm": "4px",      # Inputs
    "md": "8px",      # Cards
    "lg": "24px",     # CTAs
    "full": "9999px", # Fully rounded
}

# ============================================================================
# SERVICE TIERS
# ============================================================================

SERVICE_TIERS = {
    "standard": {
        "name": "Standard",
        "price": 399,
        "currency": "EUR",
        "slug": "standard",
        "description": "Speed + simplicity for urban residents",
        "included_documents": 8,
        "turnaround_days": 7,
    },
    "premium": {
        "name": "Premium",
        "price": 899,
        "currency": "EUR",
        "slug": "premium",
        "description": "Remote handling + fiscal rep for non-residents",
        "included_documents": 12,
        "turnaround_days": 10,
        "badge": "MOST_POPULAR",
    },
    "express": {
        "name": "DocExpress",
        "price": 1499,
        "currency": "EUR",
        "slug": "express",
        "description": "Speed + coordination for urgent sales",
        "included_documents": 15,
        "turnaround_days": 5,
    },
    "heritage": {
        "name": "DocComplete Heritage",
        "price": None,  # Custom quote
        "currency": "EUR",
        "slug": "heritage",
        "description": "Expert guidance for rural & inherited properties",
        "included_documents": "custom",
        "turnaround_days": "custom",
    },
}

# ============================================================================
# DOCUMENT TYPES & VALIDITY
# ============================================================================

DOCUMENT_TYPES = {
    "caderneta": {
        "name": "Caderneta Predial Urbana",
        "slug": "caderneta",
        "validity_months": 12,
        "cost": 0,
        "issuer": "Finanças",
        "required": True,
    },
    "certidao": {
        "name": "Certidão Permanente do Registo Predial",
        "slug": "certidao",
        "validity_months": 6,
        "cost": 15,
        "issuer": "IRN",
        "required": True,
    },
    "licenca": {
        "name": "Licença de Utilização",
        "slug": "licenca",
        "validity_months": None,  # No expiry
        "cost": 30,
        "issuer": "Câmara Municipal",
        "required": False,
    },
    "ipt": {
        "name": "Imposto sobre Propriedade Imóvel (IPT)",
        "slug": "ipt",
        "validity_months": None,
        "cost": 0,
        "issuer": "Finanças",
        "required": False,
    },
    "energy_cert": {
        "name": "Energy Certificate (RECS)",
        "slug": "energy_cert",
        "validity_months": 10 * 12,  # 10 years
        "cost": 80,
        "issuer": "Perito Qualificado",
        "required": True,
    },
}

# ============================================================================
# DOCUMENT STATUS
# ============================================================================

DOCUMENT_STATUS = {
    "pending": "pending",
    "in_progress": "in_progress",
    "uploaded": "uploaded",
    "verified": "verified",
    "complete": "complete",
    "expired": "expired",
    "error": "error",
}

# ============================================================================
# ORDER STATUS
# ============================================================================

ORDER_STATUS = {
    "draft": "draft",
    "pending_payment": "pending_payment",
    "payment_confirmed": "payment_confirmed",
    "processing": "processing",
    "awaiting_seller": "awaiting_seller",
    "in_progress": "in_progress",
    "completed": "completed",
    "cancelled": "cancelled",
}

# ============================================================================
# SELLER PERSONAS
# ============================================================================

SELLER_PERSONAS = {
    "urban_resident": {
        "slug": "urban_resident",
        "name": "Urban Resident",
        "description": "PT resident, city apartment, mortgage",
        "pain_points": ["Speed", "Simplicity"],
        "recommended_tier": "standard",
    },
    "non_resident": {
        "slug": "non_resident",
        "name": "Non-Resident",
        "description": "British/Dutch/other, villa, abroad",
        "pain_points": ["Remote handling", "Fiscal representation"],
        "recommended_tier": "premium",
    },
    "heir": {
        "slug": "heir",
        "name": "Heir / Inherited",
        "description": "Multiple heirs, possibly abroad",
        "pain_points": ["Legal coordination", "Complexity"],
        "recommended_tier": "premium",
    },
    "divorce": {
        "slug": "divorce",
        "name": "Divorce / Urgent",
        "description": "Joint ownership, time-sensitive",
        "pain_points": ["Speed", "Coordination"],
        "recommended_tier": "express",
    },
    "rural": {
        "slug": "rural",
        "name": "Rural / Legacy",
        "description": "Quinta, missing LU, elderly seller",
        "pain_points": ["Expert guidance", "Realistic timelines"],
        "recommended_tier": "heritage",
    },
}

# ============================================================================
# API RESPONSE TEMPLATES
# ============================================================================

API_RESPONSE_TEMPLATES = {
    "success": {
        "status": "success",
        "code": 200,
        "message": "Operation completed successfully",
    },
    "error": {
        "status": "error",
        "code": 400,
        "message": "An error occurred",
    },
}

# ============================================================================
# PAGINATION
# ============================================================================

PAGINATION = {
    "default_page_size": 20,
    "max_page_size": 100,
    "min_page_size": 1,
}

# ============================================================================
# NOTIFICATIONS
# ============================================================================

NOTIFICATION_TYPES = {
    "order_created": "order_created",
    "payment_confirmed": "payment_confirmed",
    "document_uploaded": "document_uploaded",
    "document_verified": "document_verified",
    "document_expiring": "document_expiring",
    "order_completed": "order_completed",
    "action_required": "action_required",
}

# ============================================================================
# LEGAL & COMPLIANCE
# ============================================================================

AMI_NUMBER = "AMI_NUMBER_HERE"  # Update with actual AMI number
GDPR_COMPLIANCE = True
DATA_RETENTION_MONTHS = 36  # 3 years as per GDPR

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================


def get_color(color_key: str) -> str:
    """Get brand color by key"""
    return BRAND_COLORS.get(color_key, BRAND_COLORS["primary"])


def get_tier_by_slug(slug: str) -> dict:
    """Get service tier details by slug"""
    return SERVICE_TIERS.get(slug)


def get_document_by_slug(slug: str) -> dict:
    """Get document type details by slug"""
    return DOCUMENT_TYPES.get(slug)


def get_persona_by_slug(slug: str) -> dict:
    """Get seller persona details by slug"""
    return SELLER_PERSONAS.get(slug)
