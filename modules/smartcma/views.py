"""
SmartCMA Module - Views
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from shared.utils.helpers import ResponseUtils, LoggingUtils
from .models import CMAReport
from .serializers import CMAReportSerializer, GenerateReportSerializer
from .services import SmartCMAService


@api_view(["POST"])
def generate_report(request):
    """Generate CMA report
    POST /api/cma/generate
    """
    serializer = GenerateReportSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        report = SmartCMAService.generate_report(
            order_id=serializer.validated_data["order_id"],
            seller_email=request.user.email,
            property_data=serializer.validated_data,
        )

        LoggingUtils.log_action(
            "cma_report_generated",
            request.user.id,
            {"report_id": report.id},
        )

        return Response(
            ResponseUtils.success(CMAReportSerializer(report).data, "Report generated"),
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        LoggingUtils.log_error(e, {"endpoint": "generate_report"})
        return Response(
            ResponseUtils.error("Report generation failed"),
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
def report_detail(request, report_id):
    """Get CMA report
    GET /api/cma/<report_id>
    """
    try:
        report = CMAReport.objects.get(id=report_id)
        serializer = CMAReportSerializer(report)
        return Response(ResponseUtils.success(serializer.data))
    except CMAReport.DoesNotExist:
        return Response(
            ResponseUtils.error("Report not found"),
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["POST"])
def export_pdf(request, report_id):
    """Export report as PDF
    POST /api/cma/<report_id>/export
    """
    try:
        pdf_path = SmartCMAService.generate_pdf_report(report_id)
        LoggingUtils.log_action("cma_report_exported", request.user.id, {"report_id": report_id})
        return Response(ResponseUtils.success(data={"pdf_path": pdf_path}))
    except Exception as e:
        LoggingUtils.log_error(e, {"endpoint": "export_pdf"})
        return Response(
            ResponseUtils.error("Export failed"),
            status=status.HTTP_400_BAD_REQUEST,
        )
