from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):

    class Role(models.TextChoices):
        SELLER = "seller"
        BUYER = "buyer"
        AGENT = "agent"
        LAWYER = "lawyer"
        ADMIN = "admin"

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.SELLER
    )

    phone = models.CharField(max_length=20, blank=True)

    email_verified = models.BooleanField(default=False)
    
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    
    updated_at = models.DateTimeField(auto_now=True)


########################################################
class SellerProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="seller_profile"
    )

    seller_type = models.CharField(max_length=50)
    property_count = models.IntegerField(default=0)


#################################################################
# 
class AgentProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="agent_profile"
    )

    ami_license_number = models.CharField(max_length=100)

    languages = models.JSONField(default=list)

    total_sales_volume = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )    

####################################################################
# 
###########################################################
# 
class LawyerProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="lawyer_profile"
    )

    registration_number = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)

########################################################################
# 
class BuyerProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="buyer_profile"
    )

    nationality = models.CharField(max_length=100)
    financing_type = models.CharField(max_length=100)


########################################################################
# Document upload for user verification
class Document(models.Model):
    class DocumentType(models.TextChoices):
        ID = "id"
        LICENSE = "license"
        PROOF_OF_ADDRESS = "proof_of_address"
        OTHER = "other"

    class VerificationStatus(models.TextChoices):
        PENDING = "pending"
        APPROVED = "approved"
        REJECTED = "rejected"

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="documents"
    )

    document_type = models.CharField(
        max_length=50,
        choices=DocumentType.choices,
        default=DocumentType.OTHER
    )

    file = models.FileField(upload_to="documents/%Y/%m/%d/")

    status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING
    )

    rejection_reason = models.TextField(blank=True, null=True)

    extracted_fields = models.JSONField(default=dict, blank=True, null=True)

    analysis_result = models.JSONField(default=dict, blank=True, null=True)  # AI analysis results (text extraction, type detection, etc)

    uploaded_at = models.DateTimeField(auto_now_add=True)

    reviewed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.user.username} - {self.document_type}"


########################################################
class SellerProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="seller_profile"
    )

    seller_type = models.CharField(max_length=50)
    property_count = models.IntegerField(default=0)


#################################################################
# 
class AgentProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="agent_profile"
    )

    ami_license_number = models.CharField(max_length=100)

    languages = models.JSONField(default=list)

    total_sales_volume = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )    

####################################################################
# 
###########################################################
# 
class LawyerProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="lawyer_profile"
    )

    registration_number = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)

########################################################################
# 
class BuyerProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="buyer_profile"
    )

    nationality = models.CharField(max_length=100)
    financing_type = models.CharField(max_length=100)


########################################################################
# Generic Document Requirements for House Sale

class PropertyDocumentTemplate(models.Model):
    """Generic documents required for selling a house"""
    
    class DocumentCategory(models.TextChoices):
        PROPERTY = "property"  # Property documents
        LEGAL = "legal"  # Legal documents
        FINANCIAL = "financial"  # Financial documents
        INSPECTION = "inspection"  # Inspection documents
        TAX = "tax"  # Tax documents
    
    name = models.CharField(max_length=100, unique=True)  # e.g., "Property Deed"
    description = models.TextField()  # e.g., "Proof of ownership of the property"
    category = models.CharField(max_length=20, choices=DocumentCategory.choices, default=DocumentCategory.PROPERTY)
    required = models.BooleanField(default=True)  # Is this document mandatory?
    required_fields = models.JSONField(default=list)  # e.g., ["owner_name", "property_address", "deed_date"]
    
    order = models.IntegerField(default=0)  # Display order
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.category})"


class SellerDocumentSubmission(models.Model):
    """User's submission for a specific document template"""
    
    class SubmissionStatus(models.TextChoices):
        NOT_SUBMITTED = "not_submitted"
        PENDING_REVIEW = "pending_review"
        APPROVED = "approved"
        REJECTED = "rejected"
        NEEDS_REVISION = "needs_revision"
    
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="document_submissions")
    template = models.ForeignKey(PropertyDocumentTemplate, on_delete=models.CASCADE, related_name="submissions")
    
    status = models.CharField(
        max_length=20,
        choices=SubmissionStatus.choices,
        default=SubmissionStatus.NOT_SUBMITTED
    )
    
    file = models.FileField(upload_to="seller_documents/%Y/%m/%d/", null=True, blank=True)
    extracted_data = models.JSONField(default=dict, blank=True)  # Data extracted from file
    missing_fields = models.JSONField(default=list, blank=True)  # Required fields that are missing
    
    reviewer_notes = models.TextField(blank=True)  # Notes from manual review
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reviewed_submissions")
    
    submitted_at = models.DateTimeField(null=True, blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ('seller', 'template')
        ordering = ['template__order', '-submitted_at']
    
    def __str__(self):
        return f"{self.seller.username} - {self.template.name} ({self.status})"


########################################################################

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create role-specific profile when user is created or role changes"""
    if instance.role == User.Role.SELLER:
        SellerProfile.objects.get_or_create(user=instance, defaults={'seller_type': 'individual'})
        # Create default document submissions for seller
        _create_seller_document_submissions(instance)
    elif instance.role == User.Role.AGENT:
        AgentProfile.objects.get_or_create(user=instance, defaults={'ami_license_number': '', 'languages': []})
    elif instance.role == User.Role.LAWYER:
        LawyerProfile.objects.get_or_create(user=instance, defaults={'registration_number': '', 'specialization': ''})
    elif instance.role == User.Role.BUYER:
        BuyerProfile.objects.get_or_create(user=instance, defaults={'nationality': '', 'financing_type': ''})


def _create_seller_document_submissions(user):
    """Create document submissions for a seller using all templates"""
    if user.role != User.Role.SELLER:
        return
    
    for template in PropertyDocumentTemplate.objects.all():
        SellerDocumentSubmission.objects.get_or_create(
            seller=user,
            template=template
        )