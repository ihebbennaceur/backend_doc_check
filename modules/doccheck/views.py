"""
DocCheck Module - Views/API Endpoints
Enhanced with professional persona detection and tier recommendation
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from shared.utils.helpers import ResponseUtils, LoggingUtils
from shared.exceptions import ValidationError, NotFoundError
from .serializers import (
    DocCheckAssessmentSerializer,
    DocCheckEnhancedAssessmentSerializer,
    DocCheckResultSerializer,
)
from .services import DocCheckService


@api_view(["POST"])
@permission_classes([AllowAny])
def assess_enhanced(request):
    """
    Execute enhanced 8-question DocCheck assessment with persona detection.
    
    POST /api/doccheck/assess
    
    Request body:
    {
        "email": "seller@example.com",
        "property_type": "apartment",
        "has_condominium": true,
        "building_construction": "post_2007",
        "has_mortgage": false,
        "acquisition_type": "purchase",
        "is_primary_residence": true,
        "has_valid_energy_cert": true,
        "all_owners_available": "yes",
        "energy_class": "B",
        "urgency": "normal",
        "is_portugal_resident": true,
        "ownership_type": "sole"
    }
    
    Response:
    {
        "success": true,
        "data": {
            "email": "...",
            "persona": {
                "slug": "urban_resident",
                "name": "Urban Resident",
                "description": "...",
                "recommended_tier": "standard"
            },
            "missing_documents": [".."],
            "missing_document_count": 1,
            "recommended_tier": {
                "slug": "standard",
                "name": "Standard",
                "price": 399
            },
            "risk_flags": [...],
            "has_risk_flags": false,
            "summary": {
                "documents_always_required": 2,
                "documents_missing_count": 1,
                "risk_flag_count": 0,
                "is_free_tier": false,
                "is_urgent": false
            }
        },
        "message": "Assessment complete"
    }
    """
    serializer = DocCheckEnhancedAssessmentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        validated_data = serializer.validated_data
        email = validated_data.get("email")
        
        # Build assessment result using professional service
        result = DocCheckService.build_assessment_result(email, validated_data)
        
        # Serialize for response
        output_serializer = DocCheckResultSerializer(result)
        
        LoggingUtils.log_action(
            "doccheck_assessment_complete",
            details={
                "email": email,
                "persona": result["persona"]["slug"],
                "tier": result["recommended_tier"]["slug"],
                "missing_docs": result["missing_document_count"],
            },
        )

        return Response(
            ResponseUtils.success(
                data=output_serializer.data,
                message="Assessment complete",
            ),
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        LoggingUtils.log_error(e, {"endpoint": "assess_enhanced"})
        return Response(
            ResponseUtils.error(f"Assessment failed: {str(e)}"),
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def start_assessment(request):
    """Start a new DocCheck assessment [LEGACY]
    POST /api/doccheck/start
    """
    serializer = DocCheckAssessmentSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        session = DocCheckService.start_session(**serializer.validated_data)
        LoggingUtils.log_action("doccheck_session_started", details={"session_id": session.id})

        return Response(
            ResponseUtils.success(
                data={"session_id": session.id, "expires_at": session.expires_at},
                message="Assessment session started",
            ),
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        LoggingUtils.log_error(e, {"endpoint": "start_assessment"})
        return Response(
            ResponseUtils.error("Failed to start assessment"),
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_assessment_result(request, session_id):
    """Get assessment result [LEGACY]
    GET /api/doccheck/<session_id>/result
    """
    try:
        result = DocCheckService.assess(session_id)
        serializer = DocCheckResultSerializer(result)

        return Response(ResponseUtils.success(data=serializer.data, message="Assessment complete"))
    except Exception as e:
        LoggingUtils.log_error(e, {"endpoint": "get_assessment_result", "session_id": session_id})
        return Response(
            ResponseUtils.error("Assessment not found"),
            status=status.HTTP_404_NOT_FOUND,
        )
