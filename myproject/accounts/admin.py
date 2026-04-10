from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Document, SellerProfile, AgentProfile, LawyerProfile, BuyerProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_active', 'email_verified', 'created_at']
    list_filter = ['role', 'is_active', 'email_verified', 'created_at']
    search_fields = ['username', 'email']
    readonly_fields = ['created_at', 'updated_at', 'password']
    
    fieldsets = (
        ('Account Info', {'fields': ('username', 'email')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone')}),
        ('Permissions', {'fields': ('role', 'is_active', 'email_verified', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Password', {'fields': ('password',), 'classes': ('collapse',), 'description': 'Password is hashed and cannot be viewed. Use "Change password" to reset.'}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'role'),
        }),
    )



@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['user', 'document_type', 'status', 'uploaded_at', 'reviewed_at']
    list_filter = ['status', 'document_type', 'uploaded_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['uploaded_at', 'reviewed_at']
    fieldsets = (
        ('Document Info', {'fields': ('user', 'document_type', 'file')}),
        ('Verification', {'fields': ('status', 'rejection_reason')}),
        ('Timestamps', {'fields': ('uploaded_at', 'reviewed_at'), 'classes': ('collapse',)}),
    )


@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'seller_type', 'property_count']
    search_fields = ['user__username', 'seller_type']


@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'ami_license_number', 'total_sales_volume']
    search_fields = ['user__username', 'ami_license_number']


@admin.register(LawyerProfile)
class LawyerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'registration_number', 'specialization']
    search_fields = ['user__username', 'registration_number']


@admin.register(BuyerProfile)
class BuyerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'nationality', 'financing_type']
    search_fields = ['user__username', 'nationality']
