"""
Operator Module - Views
"""

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from shared.utils.helpers import ResponseUtils, LoggingUtils
from .models import OperatorQueue
from .serializers import OperatorQueueSerializer, OperatorNoteSerializer, AddNoteSerializer, UpdateQueueSerializer
from .services import OperatorService


@api_view(["GET"])
def operator_queue(request):
    """Get operator's queue
    GET /api/operator/queue?operator=<name>
    """
    operator_name = request.query_params.get("operator")
    if not operator_name:
        return Response(
            ResponseUtils.error("Operator name required"),
            status=status.HTTP_400_BAD_REQUEST,
        )

    queue = OperatorService.get_operator_queue(operator_name)
    serializer = OperatorQueueSerializer(queue, many=True)
    return Response(ResponseUtils.success(serializer.data))


@api_view(["GET"])
def order_details(request, order_id):
    """Get order details for operator
    GET /api/operator/<order_id>
    """
    try:
        queue_item = OperatorQueue.objects.get(order_id=order_id)
        notes = OperatorService.get_order_notes(order_id)

        return Response(
            ResponseUtils.success(
                data={
                    "queue": OperatorQueueSerializer(queue_item).data,
                    "notes": OperatorNoteSerializer(notes, many=True).data,
                }
            )
        )
    except OperatorQueue.DoesNotExist:
        return Response(
            ResponseUtils.error("Order not found"),
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["PATCH"])
def update_queue_status(request, order_id):
    """Update order status
    PATCH /api/operator/<order_id>/status
    """
    serializer = UpdateQueueSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        queue_item = OperatorService.update_queue_status(order_id, **serializer.validated_data)
        LoggingUtils.log_action("operator_updated_status", request.user.id, {"order_id": order_id})
        return Response(ResponseUtils.success(OperatorQueueSerializer(queue_item).data))
    except Exception as e:
        LoggingUtils.log_error(e, {"endpoint": "update_queue_status"})
        return Response(
            ResponseUtils.error("Update failed"),
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
def add_note(request):
    """Add note to order
    POST /api/operator/note
    """
    serializer = AddNoteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        note = OperatorService.add_note(
            order_id=serializer.validated_data["order_id"],
            operator_name=request.user.username,
            note=serializer.validated_data["note"],
        )
        return Response(
            ResponseUtils.success(OperatorNoteSerializer(note).data, "Note added"),
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        LoggingUtils.log_error(e, {"endpoint": "add_note"})
        return Response(
            ResponseUtils.error("Failed to add note"),
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET"])
def blocked_orders(request):
    """Get all blocked orders
    GET /api/operator/blocked
    """
    blocked = OperatorService.get_blocked_orders()
    serializer = OperatorQueueSerializer(blocked, many=True)
    return Response(ResponseUtils.success(serializer.data))
