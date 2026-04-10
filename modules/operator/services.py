"""
Operator Module - Services
Queue management and order processing
"""

from django.utils.timezone import now
from shared.utils.helpers import IDGenerator, LoggingUtils
from .models import OperatorQueue, OperatorNote


class OperatorService:
    """Operator queue and workflow management"""

    @staticmethod
    def add_to_queue(order_id: str, operator_name: str, seller_data: dict, priority: str = "normal"):
        """Add order to operator queue"""
        queue_item = OperatorQueue.objects.create(
            id=IDGenerator.uuid(),
            order_id=order_id,
            assigned_operator=operator_name,
            priority=priority,
            seller_name=seller_data.get("name"),
            seller_email=seller_data.get("email"),
            seller_phone=seller_data.get("phone"),
        )
        LoggingUtils.log_action("order_assigned_to_operator", details={"order_id": order_id, "operator": operator_name})
        return queue_item

    @staticmethod
    def get_operator_queue(operator_name: str, priority_order: bool = True):
        """Get queue for operator"""
        query = OperatorQueue.objects.filter(assigned_operator=operator_name)

        if priority_order:
            priority_map = {"critical": 0, "high": 1, "normal": 2, "low": 3}
            query = query.extra(select={"priority_order": f"CASE WHEN priority='{list(priority_map.keys())[0]}' THEN 0"})
            query = query.order_by("-priority", "-updated_at")
        else:
            query = query.order_by("-updated_at")

        return query

    @staticmethod
    def update_queue_status(order_id: str, status: str, action_required: str = None, blocked_reason: str = None):
        """Update queue item status"""
        queue_item = OperatorQueue.objects.get(order_id=order_id)
        queue_item.status = status
        if action_required:
            queue_item.action_required = action_required
        if blocked_reason:
            queue_item.blocked_reason = blocked_reason
        queue_item.save()

        LoggingUtils.log_action("queue_status_updated", details={"order_id": order_id, "status": status})

        return queue_item

    @staticmethod
    def add_note(order_id: str, operator_name: str, note: str):
        """Add note to order"""
        note_obj = OperatorNote.objects.create(
            id=IDGenerator.uuid(),
            order_id=order_id,
            operator_name=operator_name,
            note=note,
        )
        return note_obj

    @staticmethod
    def get_order_notes(order_id: str):
        """Get all notes for order"""
        return OperatorNote.objects.filter(order_id=order_id).order_by("-created_at")

    @staticmethod
    def get_blocked_orders():
        """Get all blocked orders"""
        return OperatorQueue.objects.exclude(blocked_reason__isnull=True).exclude(blocked_reason__exact="")

    @staticmethod
    def contact_seller(order_id: str):
        """Log seller contact"""
        queue_item = OperatorQueue.objects.get(order_id=order_id)
        queue_item.last_contact_date = now()
        queue_item.save()
        return queue_item
