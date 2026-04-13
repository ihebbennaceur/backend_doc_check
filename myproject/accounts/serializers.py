from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Document, SellerProfile, AgentProfile, LawyerProfile, BuyerProfile


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


class GoogleAuthSerializer(serializers.Serializer):
    """Serializer for Google OAuth token exchange"""
    access_token = serializers.CharField(required=True, write_only=True)
    
    def validate_access_token(self, value):
        """Validate the Google access token"""
        if not value:
            raise serializers.ValidationError("Access token is required")
        return value

    def create(self, validated_data):
        """
        Exchange Google token for user and JWT tokens.
        This will be handled in the view.
        """
        return validated_data