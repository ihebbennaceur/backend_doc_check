"""
DocReady Module - Views
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from shared.utils.helpers import ResponseUtils, LoggingUtils
from .models import FizboOrder
from .serializers import OrderCreateSerializer, OrderDetailSerializer, OrderListSerializer
from .services import OrderService


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    """Create new order
    POST /api/orders
    """
    serializer = OrderCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        order = OrderService.create_order(**serializer.validated_data)
        LoggingUtils.log_action("order_created", details={"order_id": order.id})

        return Response(
            ResponseUtils.success(
                OrderDetailSerializer(order).data,
                "Order created",
            ),
            status=status.HTTP_201_CREATED,
        )
    except Exception as e:
        LoggingUtils.log_error(e, {"endpoint": "create_order"})
        return Response(
            ResponseUtils.error("Failed to create order"),
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def order_detail(request, order_id):
    """Get or update order details
    GET /api/orders/<order_id>/
    PATCH /api/orders/<order_id>/
    """
    try:
        order = OrderService.get_order(order_id)
        
        if request.method == "GET":
            serializer = OrderDetailSerializer(order)
            return Response(ResponseUtils.success(serializer.data))
        
        elif request.method == "PATCH":
            serializer = OrderCreateSerializer(data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            
            updated_order = OrderService.update_order(order_id, **serializer.validated_data)
            return Response(ResponseUtils.success(OrderDetailSerializer(updated_order).data, "Order updated"))
    except Exception as e:
        LoggingUtils.log_error(e, {"endpoint": "order_detail", "order_id": order_id})
        return Response(
            ResponseUtils.error("Order not found"),
            status=status.HTTP_404_NOT_FOUND,
        )


@api_view(["GET"])
@permission_classes([AllowAny])
def seller_orders(request):
    """Get seller's orders
    GET /api/orders/seller/list/?email=email@example.com
    """
    try:
        seller_email = request.query_params.get("email")
        if not seller_email:
            return Response(
                ResponseUtils.error("Email required"),
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Try to validate JWT token if present
        token = request.META.get('HTTP_AUTHORIZATION', '').replace('Bearer ', '')
        if token:
            try:
                from rest_framework_simplejwt.authentication import JWTAuthentication
                auth = JWTAuthentication()
                validated = auth.authenticate(request)
                if validated:
                    user, _ = validated
                    # Verify user email matches requested email
                    if user.email != seller_email:
                        return Response(
                            ResponseUtils.error("Unauthorized: email mismatch"),
                            status=status.HTTP_403_FORBIDDEN,
                        )
            except Exception as e:
                return Response(
                    ResponseUtils.error(f"Invalid token: {str(e)}"),
                    status=status.HTTP_401_UNAUTHORIZED,
                )

        orders = OrderService.get_seller_orders(seller_email)
        serializer = OrderListSerializer(orders, many=True)
        return Response(ResponseUtils.success(serializer.data))
    except Exception as e:
        LoggingUtils.log_error(e, {"endpoint": "seller_orders"})
        return Response(
            ResponseUtils.error(f"Failed to fetch orders: {str(e)}"),
            status=status.HTTP_400_BAD_REQUEST,
        )



@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_order(request, order_id):
    """Update order
    PATCH /api/orders/<order_id>/update/
    """
    try:
        order = OrderService.update_order(order_id, **request.data)
        LoggingUtils.log_action("order_updated", details={"order_id": order_id})
        return Response(ResponseUtils.success(OrderDetailSerializer(order).data))
    except Exception as e:
        LoggingUtils.log_error(e, {"endpoint": "update_order"})
        return Response(
            ResponseUtils.error("Update failed"),
            status=status.HTTP_400_BAD_REQUEST,
        )
