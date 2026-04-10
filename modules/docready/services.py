"""
DocReady Module - Services
Order lifecycle and workflow management
"""

from shared.constants.theme import SERVICE_TIERS, ORDER_STATUS, DOCUMENT_TYPES
from shared.utils.helpers import IDGenerator, ResponseUtils
from shared.exceptions import NotFoundError, WorkflowError
from modules.documents.services import DocumentService
from .models import FizboOrder


class OrderService:
    """Order management"""

    @staticmethod
    def create_order(seller_email: str, seller_name: str, service_tier: str, seller_phone: str = None, phone: str = None, whatsapp_opt_in: bool = False) -> FizboOrder:
        """Create new order"""
        if service_tier not in SERVICE_TIERS:
            raise ValueError("Invalid service tier")

        order_id = IDGenerator.order_id()

        order = FizboOrder.objects.create(
            id=order_id,
            seller_email=seller_email,
            seller_name=seller_name,
            seller_phone=seller_phone,
            phone=phone,
            service_tier=service_tier,
            whatsapp_opt_in=whatsapp_opt_in,
            status=ORDER_STATUS["draft"],
        )

        # Skip document creation for now - will implement after payment
        # OrderService._create_initial_documents(order)

        return order

    @staticmethod
    def _create_initial_documents(order: FizboOrder):
        """Create document records based on service tier"""
        required_docs = ["caderneta", "certidao", "energy_cert"]

        for doc_type in required_docs:
            DocumentService.create_document(order.id, order.seller_email, doc_type)

    @staticmethod
    def confirm_payment(order_id: str, payment_id: str) -> FizboOrder:
        """Update order after successful payment"""
        order = FizboOrder.objects.get(id=order_id)
        order.mark_payment_confirmed(payment_id)
        return order

    @staticmethod
    def get_order(order_id: str) -> FizboOrder:
        """Get order details"""
        try:
            return FizboOrder.objects.get(id=order_id)
        except FizboOrder.DoesNotExist:
            raise NotFoundError("Order", order_id)

    @staticmethod
    def get_seller_orders(seller_email: str, status: str = None):
        """Get all orders for a seller"""
        query = FizboOrder.objects.filter(seller_email=seller_email)
        if status:
            query = query.filter(status=status)
        return query.order_by("-created_at")

    @staticmethod
    def update_order(order_id: str, **kwargs) -> FizboOrder:
        """Update order details"""
        order = FizboOrder.objects.get(id=order_id)
        for key, value in kwargs.items():
            if hasattr(order, key):
                setattr(order, key, value)
        order.save()
        return order

    @staticmethod
    def assign_to_operator(order_id: str, operator_name: str) -> FizboOrder:
        """Assign order to operator"""
        order = FizboOrder.objects.get(id=order_id)
        order.assigned_operator = operator_name
        order.status = ORDER_STATUS["processing"]
        order.save()
        return order
