"""
DocCheck Module - Serializers
Enhanced with professional assessment input/output
"""

from rest_framework import serializers
from .models import DocCheckSession, DocCheckResult
from shared.constants.theme import DOCUMENT_TYPES, SERVICE_TIERS, SELLER_PERSONAS


class RiskFlagSerializer(serializers.Serializer):
    """Serializer for risk flags"""
    
    key = serializers.CharField()
    message = serializers.CharField()
    recommendation = serializers.CharField()
    severity = serializers.CharField()  # critical, high, medium, low


class PersonaSerializer(serializers.Serializer):
    """Serializer for detected persona"""
    
    slug = serializers.CharField()
    name = serializers.CharField()
    description = serializers.CharField()
    recommended_tier = serializers.CharField()


class TierRecommendationSerializer(serializers.Serializer):
    """Serializer for tier recommendation"""
    
    slug = serializers.CharField()
    name = serializers.CharField()
    price = serializers.IntegerField()


class AssessmentSummarySerializer(serializers.Serializer):
    """Summary statistics for assessment"""
    
    documents_always_required = serializers.IntegerField()
    documents_missing_count = serializers.IntegerField()
    risk_flag_count = serializers.IntegerField()
    is_free_tier = serializers.BooleanField()
    is_urgent = serializers.BooleanField()


class DocCheckResultSerializer(serializers.Serializer):
    """Enhanced assessment result with persona, tier, and risk flags"""

    email = serializers.EmailField()
    persona = PersonaSerializer()
    missing_documents = serializers.ListField(child=serializers.CharField())
    missing_document_count = serializers.IntegerField()
    recommended_tier = TierRecommendationSerializer()
    risk_flags = RiskFlagSerializer(many=True)
    has_risk_flags = serializers.BooleanField()
    summary = AssessmentSummarySerializer()


class DocCheckEnhancedAssessmentSerializer(serializers.Serializer):
    """Input for enhanced 8-question assessment
    
    Handles all answers needed for:
    - Persona detection (P1-P5)
    - Missing document calculation
    - Tier recommendation
    - Risk flag identification
    """

    email = serializers.EmailField()
    
    # Question 1: Property type
    property_type = serializers.CharField(
        max_length=50,
        help_text="apartment, house, land, other"
    )
    
    # Question 2: Condominium
    has_condominium = serializers.BooleanField(
        help_text="Is property in condominium?"
    )
    
    # Question 3: Building construction age
    building_construction = serializers.CharField(
        max_length=50,
        help_text="pre_1951, 1951_1990, 1991_2007, post_2007"
    )
    
    # Question 4: Mortgage
    has_mortgage = serializers.BooleanField(
        help_text="Is property mortgaged?"
    )
    
    # Question 5: How acquired
    acquisition_type = serializers.CharField(
        max_length=50,
        help_text="purchase, inheritance, divorce, gift, other"
    )
    
    # Question 6: Primary residence
    is_primary_residence = serializers.BooleanField(
        help_text="Is this primary residence?"
    )
    
    # Question 7: Energy certificate
    has_valid_energy_cert = serializers.BooleanField(
        help_text="Do you have valid energy certificate (< 10 years)?"
    )
    
    # Question 8: All owners available
    all_owners_available = serializers.CharField(
        max_length=50,
        help_text="yes, one_abroad, one_deceased, disputed"
    )
    
    # Optional: Energy class
    energy_class = serializers.CharField(
        max_length=1,
        required=False,
        allow_blank=True,
        help_text="A-G energy rating"
    )
    
    # Optional: Is Portugal resident
    is_portugal_resident = serializers.BooleanField(
        required=False,
        default=True,
        help_text="Is seller resident in Portugal?"
    )
    
    # Optional: Ownership type
    ownership_type = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="sole, joint, inherited, multiple_heirs"
    )

    # Question 9: Seller residency (Persona P1 vs P2)
    seller_residency = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="portugal_resident, non_resident_eu, non_resident_other"
    )

    # Question 10: Number of heirs (Persona P3)
    number_of_heirs = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="1, 2_3, 4_or_more, disputed"
    )

    # Question 11: Divorce case (Persona P4)
    is_divorce_case = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Is this a divorce case?"
    )

    # Question 12: Urgency/Timeline (Persona P4 vs P5)
    urgency = serializers.CharField(
        max_length=50,
        required=False,
        allow_blank=True,
        help_text="flexible, 3_months, 1_month, urgent (or normal, urgent, very_urgent for backward compat)"
    )

    def validate_property_type(self, value):
        """Validate property type"""
        valid_types = ["apartment", "house", "land", "other"]
        if value.lower() not in valid_types:
            raise serializers.ValidationError(f"Property type must be one of {valid_types}")
        return value.lower()

    def validate_building_construction(self, value):
        """Validate building age"""
        valid_ages = ["pre_1951", "1951_1990", "1991_2007", "post_2007"]
        if value.lower() not in valid_ages:
            raise serializers.ValidationError(f"Building construction must be one of {valid_ages}")
        return value.lower()

    def validate_acquisition_type(self, value):
        """Validate acquisition type"""
        valid_types = ["purchase", "inheritance", "divorce", "gift", "other"]
        if value.lower() not in valid_types:
            raise serializers.ValidationError(f"Acquisition type must be one of {valid_types}")
        return value.lower()

    def validate_all_owners_available(self, value):
        """Validate owners available status"""
        valid_statuses = ["yes", "one_abroad", "one_deceased", "disputed"]
        if value.lower() not in valid_statuses:
            raise serializers.ValidationError(f"Owner status must be one of {valid_statuses}")
        return value.lower()

    def validate_energy_class(self, value):
        """Validate energy class if provided"""
        if value and value.upper() not in ["A", "B", "C", "D", "E", "F", "G"]:
            raise serializers.ValidationError("Energy class must be A-G")
        return value.upper() if value else ""

    def validate_urgency(self, value):
        """Validate urgency - accepts both old format (normal/urgent/very_urgent) and new format (flexible/3_months/1_month/urgent)"""
        if not value:
            return "flexible"
        valid_values = ["flexible", "3_months", "1_month", "urgent", "normal", "very_urgent"]
        if value.lower() not in valid_values:
            raise serializers.ValidationError(f"Urgency must be one of: {', '.join(valid_values)}")
        return value.lower()

    def validate_ownership_type(self, value):
        """Validate ownership type if provided"""
        if value and value.lower() not in ["sole", "joint", "inherited", "multiple_heirs"]:
            raise serializers.ValidationError("Ownership type must be one of: sole, joint, inherited, multiple_heirs")
        return value.lower() if value else ""

    def validate_seller_residency(self, value):
        """Validate seller residency (Q9)"""
        if value and value.lower() not in ["portugal_resident", "non_resident_eu", "non_resident_other"]:
            raise serializers.ValidationError("Seller residency must be one of: portugal_resident, non_resident_eu, non_resident_other")
        return value.lower() if value else ""

    def validate_number_of_heirs(self, value):
        """Validate number of heirs (Q10)"""
        if value and value.lower() not in ["1", "2_3", "4_or_more", "disputed"]:
            raise serializers.ValidationError("Number of heirs must be one of: 1, 2_3, 4_or_more, disputed")
        return value.lower() if value else ""


class DocCheckAssessmentSerializer(serializers.Serializer):
    """Input for legacy assessment [DEPRECATED - use DocCheckEnhancedAssessmentSerializer]"""

    email = serializers.EmailField()
    property_type = serializers.CharField(max_length=50)
    property_location = serializers.CharField(max_length=100)
    is_mortgaged = serializers.BooleanField(default=False)
    is_inherited = serializers.BooleanField(default=False)

    def validate_property_type(self, value):
        valid_types = ["apartment", "house", "quinta"]
        if value.lower() not in valid_types:
            raise serializers.ValidationError(f"Property type must be one of {valid_types}")
        return value.lower()
