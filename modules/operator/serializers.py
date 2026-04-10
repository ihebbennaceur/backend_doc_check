"""
Operator Module - Serializers
"""

from rest_framework import serializers
from .models import OperatorQueue, OperatorNote


class OperatorQueueSerializer(serializers.ModelSerializer):
    """Queue item"""

    class Meta:
        model = OperatorQueue
        fields = [
            "id",
            "order_id",
            "seller_name",
            "seller_email",
            "priority",
            "status",
            "action_required",
            "blocked_reason",
            "last_contact_date",
            "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


class OperatorNoteSerializer(serializers.ModelSerializer):
    """Note"""

    class Meta:
        model = OperatorNote
        fields = ["id", "operator_name", "note", "created_at"]
        read_only_fields = fields


class AddNoteSerializer(serializers.Serializer):
    """Add note"""

    order_id = serializers.CharField(max_length=50)
    note = serializers.CharField()


class UpdateQueueSerializer(serializers.Serializer):
    """Update queue"""

    status = serializers.CharField(max_length=30)
    action_required = serializers.CharField(required=False)
    blocked_reason = serializers.CharField(required=False)
