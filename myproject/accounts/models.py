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
# Signals to auto-create role-specific profiles

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically create role-specific profile when user is created or role changes"""
    if instance.role == User.Role.SELLER:
        SellerProfile.objects.get_or_create(user=instance, defaults={'seller_type': 'individual'})
    elif instance.role == User.Role.AGENT:
        AgentProfile.objects.get_or_create(user=instance, defaults={'ami_license_number': '', 'languages': []})
    elif instance.role == User.Role.LAWYER:
        LawyerProfile.objects.get_or_create(user=instance, defaults={'registration_number': '', 'specialization': ''})
    elif instance.role == User.Role.BUYER:
        BuyerProfile.objects.get_or_create(user=instance, defaults={'nationality': '', 'financing_type': ''})