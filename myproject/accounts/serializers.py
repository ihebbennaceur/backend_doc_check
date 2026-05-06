from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Document, SellerProfile, AgentProfile, LawyerProfile, BuyerProfile, Property, PropertyDocumentTemplate, SellerDocumentSubmission


class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True, min_length=8, required=True)
    confirm_password = serializers.CharField(write_only=True, min_length=8, required=True)
    role = serializers.CharField(required=False, allow_blank=True, default=User.Role.SELLER)

    def validate_email(self, value):
        """Check if user with this email already exists"""
        if not value:
            raise serializers.ValidationError("Email is required.")
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value

    def validate(self, data):
        """Validate that passwords match"""
        password = data.get('password')
        confirm_password = data.pop('confirm_password', None)
        
        if not password or not confirm_password:
            raise serializers.ValidationError("Password and confirmation password are required.")
        
        if password != confirm_password:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        
        if len(password) < 8:
            raise serializers.ValidationError({"password": "Password must be at least 8 characters long."})
        
        return data

    def create(self, validated_data):
        email = validated_data.get("email")
        password = validated_data.get("password")
        role = validated_data.get("role") or User.Role.SELLER
        
        if not email or not password:
            raise serializers.ValidationError("Email and password are required.")
        
        # Generate username from email (part before @)
        username = email.split('@')[0].lower()
        
        # Ensure unique username
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role=role
        )

        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            raise serializers.ValidationError("Email and password are required")
        
        # Try to authenticate with email by first getting the user
        try:
            user = User.objects.get(email=email)
            # Now authenticate with username
            user = authenticate(username=user.username, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password. Please check your credentials.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email or password. Please check your credentials.")
        
        if not user.is_active:
            raise serializers.ValidationError("This account has been deactivated")
        
        data['user'] = user
        return data


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "first_name",
            "last_name",
            "phone",
            "role"
        ]

    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.role = validated_data.get('role', instance.role)
        instance.save()
        return instance


class UserDetailSerializer(serializers.ModelSerializer):
    """Serializer for user profile details with all fields"""
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "phone",
            "role",
            "email_verified",
            "created_at",
            "updated_at"
        ]
        read_only_fields = ["id", "username", "role", "email_verified", "created_at", "updated_at"]
    
    def get_full_name(self, obj):
        """Return full name or N/A if empty"""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        elif obj.first_name:
            return obj.first_name
        elif obj.last_name:
            return obj.last_name
        return None
    
    def update(self, instance, validated_data):
        instance.email = validated_data.get('email', instance.email)
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.phone = validated_data.get('phone', instance.phone)
        instance.save()
        return instance


class AdminUserManagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "role",
            "is_active",
            "email_verified",
            "created_at"
        ]
        read_only_fields = ["id", "username", "created_at"]

    def update(self, instance, validated_data):
        instance.role = validated_data.get('role', instance.role)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.email_verified = validated_data.get('email_verified', instance.email_verified)
        instance.save()
        return instance


class EmailVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist")
        return value


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "id",
            "document_type",
            "file",
            "status",
            "rejection_reason",
            "extracted_fields",
            "uploaded_at",
            "reviewed_at"
        ]
        read_only_fields = ["id", "status", "rejection_reason", "uploaded_at", "reviewed_at"]


class DocumentListSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Document
        fields = [
            "id",
            "user_username",
            "document_type",
            "status",
            "uploaded_at",
            "reviewed_at"
        ]


class DocumentApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = [
            "status",
            "rejection_reason"
        ]

    def validate(self, data):
        if data.get('status') == Document.VerificationStatus.REJECTED and not data.get('rejection_reason'):
            raise serializers.ValidationError("Rejection reason is required when rejecting a document")
        return data


class SellerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SellerProfile
        fields = [
            "id",
            "seller_type",
            "property_count"
        ]


class AgentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = AgentProfile
        fields = [
            "id",
            "ami_license_number",
            "languages",
            "total_sales_volume"
        ]


class LawyerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LawyerProfile
        fields = [
            "id",
            "registration_number",
            "specialization"
        ]


class BuyerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerProfile
        fields = [
            "id",
            "nationality",
            "financing_type"
        ]


# Document Template and Submission Serializers

class PropertyDocumentTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import PropertyDocumentTemplate
        model = PropertyDocumentTemplate
        fields = [
            'id',
            'name',
            'description',
            'category',
            'required',
            'required_fields',
            'order'
        ]


class SellerDocumentSubmissionListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing submissions"""
    template_name = serializers.CharField(source='template.name', read_only=True)
    template_description = serializers.CharField(source='template.description', read_only=True)
    template_category = serializers.CharField(source='template.category', read_only=True)
    template_required_fields = serializers.ListField(source='template.required_fields', read_only=True)
    
    class Meta:
        from .models import SellerDocumentSubmission
        model = SellerDocumentSubmission
        fields = [
            'id',
            'template',
            'template_name',
            'template_description',
            'template_category',
            'template_required_fields',
            'status',
            'extracted_data',
            'missing_fields',
            'reviewer_notes',
            'submitted_at',
            'reviewed_at'
        ]
        read_only_fields = ['extracted_data', 'missing_fields', 'reviewer_notes', 'reviewed_at']


class SellerDocumentSubmissionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for viewing/uploading submissions"""
    template_data = PropertyDocumentTemplateSerializer(source='template', read_only=True)
    reviewer_username = serializers.CharField(source='reviewer.username', read_only=True, allow_null=True)
    
    class Meta:
        from .models import SellerDocumentSubmission
        model = SellerDocumentSubmission
        fields = [
            'id',
            'template',
            'template_data',
            'status',
            'file',
            'extracted_data',
            'missing_fields',
            'reviewer_notes',
            'reviewer',
            'reviewer_username',
            'submitted_at',
            'reviewed_at'
        ]
        read_only_fields = ['extracted_data', 'missing_fields', 'reviewer_notes', 'reviewer', 'reviewer_username', 'reviewed_at']


class PropertySerializer(serializers.ModelSerializer):
    """Serializer for Property model - listing and creating properties"""
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    document_submissions_count = serializers.SerializerMethodField()
    completed_documents_count = serializers.SerializerMethodField()
    total_required_documents = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id',
            'seller',
            'seller_username',
            'title',
            'description',
            'address',
            'city',
            'postal_code',
            'price',
            'area_sqm',
            'bedrooms',
            'bathrooms',
            'status',
            'document_submissions_count',
            'completed_documents_count',
            'total_required_documents',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'seller', 'seller_username', 'created_at', 'updated_at']
    
    def get_document_submissions_count(self, obj):
        """Count of document submissions for this property"""
        return obj.document_submissions.count()
    
    def get_completed_documents_count(self, obj):
        """Count of approved documents"""
        return obj.document_submissions.filter(
            status=SellerDocumentSubmission.SubmissionStatus.APPROVED
        ).count()
    
    def get_total_required_documents(self, obj):
        """Count of required document templates"""
        return PropertyDocumentTemplate.objects.filter(required=True).count()


class PropertyDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Property with document submissions"""
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    document_submissions = SellerDocumentSubmissionListSerializer(many=True, read_only=True)
    document_submissions_count = serializers.SerializerMethodField()
    completed_documents_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id',
            'seller',
            'seller_username',
            'title',
            'description',
            'address',
            'city',
            'postal_code',
            'price',
            'area_sqm',
            'bedrooms',
            'bathrooms',
            'status',
            'document_submissions',
            'document_submissions_count',
            'completed_documents_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'seller', 'seller_username', 'created_at', 'updated_at', 'document_submissions']
    
    def get_document_submissions_count(self, obj):
        """Count of document submissions for this property"""
        return obj.document_submissions.count()
    
    def get_completed_documents_count(self, obj):
        """Count of approved documents"""
        return obj.document_submissions.filter(
            status=SellerDocumentSubmission.SubmissionStatus.APPROVED
        ).count()# New serializers for folder-based workflow


class PropertyFolderListSerializer(serializers.ModelSerializer):
    """Serializer for property folders listing (for process/workflow UI)"""
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    total_documents = serializers.SerializerMethodField()
    approved_documents = serializers.SerializerMethodField()
    pending_documents = serializers.SerializerMethodField()
    rejected_documents = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id',
            'seller',
            'seller_username',
            'title',
            'address',
            'description',
            'price',
            'total_documents',
            'approved_documents',
            'pending_documents',
            'rejected_documents',
            'progress_percentage',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'seller', 'seller_username', 'created_at', 'updated_at']
    
    def get_total_documents(self, obj):
        """Total document submissions"""
        return obj.document_submissions.count()
    
    def get_approved_documents(self, obj):
        """Count of approved documents"""
        return obj.document_submissions.filter(
            status=SellerDocumentSubmission.SubmissionStatus.APPROVED
        ).count()
    
    def get_pending_documents(self, obj):
        """Count of pending documents"""
        return obj.document_submissions.filter(
            status=SellerDocumentSubmission.SubmissionStatus.PENDING_REVIEW
        ).count()
    
    def get_rejected_documents(self, obj):
        """Count of rejected documents"""
        return obj.document_submissions.filter(
            status=SellerDocumentSubmission.SubmissionStatus.REJECTED
        ).count()
    
    def get_progress_percentage(self, obj):
        """Calculate progress percentage (approved / total required documents)"""
        total_required = PropertyDocumentTemplate.objects.filter(required=True).count()
        if total_required == 0:
            return 0
        approved = obj.document_submissions.filter(
            status=SellerDocumentSubmission.SubmissionStatus.APPROVED
        ).count()
        return int((approved / total_required) * 100)


class PropertyFolderDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for property folder with grouped documents"""
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    documents_by_category = serializers.SerializerMethodField()
    total_documents = serializers.SerializerMethodField()
    approved_documents = serializers.SerializerMethodField()
    pending_documents = serializers.SerializerMethodField()
    progress_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Property
        fields = [
            'id',
            'seller',
            'seller_username',
            'title',
            'address',
            'description',
            'price',
            'documents_by_category',
            'total_documents',
            'approved_documents',
            'pending_documents',
            'progress_percentage',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'seller', 'seller_username', 'created_at', 'updated_at']
    
    def get_documents_by_category(self, obj):
        """Group document submissions by template category"""
        submissions = obj.document_submissions.select_related('template').all()
        
        categories = {}
        for submission in submissions:
            category = submission.template.category
            
            if category not in categories:
                categories[category] = {
                    'name': category,
                    'documents': []
                }
            
            categories[category]['documents'].append({
                'id': submission.id,
                'template_id': submission.template.id,
                'template_name': submission.template.name,
                'template_description': submission.template.description,
                'status': submission.status,
                'extracted_data': submission.extracted_data,
                'missing_fields': submission.missing_fields,
                'reviewer_notes': submission.reviewer_notes,
                'submitted_at': submission.submitted_at,
                'reviewed_at': submission.reviewed_at,
                'file': submission.file.url if submission.file else None
            })
        
        return list(categories.values())
    
    def get_total_documents(self, obj):
        """Total document submissions"""
        return obj.document_submissions.count()
    
    def get_approved_documents(self, obj):
        """Count of approved documents"""
        return obj.document_submissions.filter(
            status=SellerDocumentSubmission.SubmissionStatus.APPROVED
        ).count()
    
    def get_pending_documents(self, obj):
        """Count of pending documents"""
        return obj.document_submissions.filter(
            status=SellerDocumentSubmission.SubmissionStatus.PENDING_REVIEW
        ).count()
    
    def get_progress_percentage(self, obj):
        """Calculate progress percentage (approved / total required documents)"""
        total_required = PropertyDocumentTemplate.objects.filter(required=True).count()
        if total_required == 0:
            return 0
        approved = obj.document_submissions.filter(
            status=SellerDocumentSubmission.SubmissionStatus.APPROVED
        ).count()
        return int((approved / total_required) * 100)
