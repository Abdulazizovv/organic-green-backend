"""
Order views for Organic Green e-commerce
"""
import logging
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from apps.cart.utils import get_or_create_cart
from .models import Order, OrderStatus
from .serializers import OrderSerializer, OrderCreateSerializer
from .permissions import IsOrderOwner

logger = logging.getLogger(__name__)


class OrderPagination(PageNumberPagination):
    """Custom pagination for orders"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Order operations
    
    Provides list, retrieve, create, and cancel operations
    Supports both authenticated and anonymous users
    """
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]  # Object-level permissions handled separately
    pagination_class = OrderPagination
    
    def get_queryset(self):
        """
        Filter orders based on user authentication status
        """
        queryset = Order.objects.select_related('user').prefetch_related(
            'items', 'items__product'
        )
        
        request = self.request
        
        if request.user.is_authenticated:
            # Authenticated users see only their orders
            return queryset.filter(user=request.user)
        else:
            # Anonymous users see orders for their session
            session_key = request.session.session_key
            header_session_key = request.headers.get('X-Session-Key')
            
            if not session_key and not header_session_key:
                # No session, return empty queryset
                return queryset.none()
            
            # Filter by session key or header session key
            session_filter = queryset.filter(session_key=session_key)
            if header_session_key and header_session_key != session_key:
                session_filter = session_filter | queryset.filter(session_key=header_session_key)
            
            return session_filter
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a specific order with owner validation
        """
        try:
            # Get order from filtered queryset (ensures ownership)
            order = get_object_or_404(self.get_queryset(), pk=kwargs['pk'])
            
            # Additional permission check
            permission = IsOrderOwner()
            if not permission.has_object_permission(request, self, order):
                return Response(
                    {'detail': 'Sizda bu buyurtmani ko\'rish huquqi yo\'q.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            serializer = self.get_serializer(order)
            return Response(serializer.data)
            
        except Exception as e:
            logger.error(f"Error retrieving order {kwargs.get('pk')}: {str(e)}")
            return Response(
                {'detail': 'Buyurtma topilmadi.'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def create_order(self, request):
        """
        Create a new order from current cart
        """
        try:
            # Get or create cart for validation
            cart, _ = get_or_create_cart(request)
            
            serializer = OrderCreateSerializer(
                data=request.data,
                context={'request': request}
            )
            
            if serializer.is_valid():
                order = serializer.save()
                
                logger.info(
                    f"Order created: {order.order_number} by "
                    f"{'user ' + request.user.username if request.user.is_authenticated else 'anonymous'}"
                )
                
                # Return created order data
                response_serializer = OrderSerializer(order, context={'request': request})
                return Response(
                    {
                        'message': 'Buyurtma muvaffaqiyatli yaratildi',
                        'order': response_serializer.data
                    },
                    status=status.HTTP_201_CREATED
                )
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Error creating order: {str(e)}")
            return Response(
                {
                    'error': 'Buyurtma yaratishda xatolik yuz berdi',
                    'detail': str(e) if request.user.is_staff else 'Server xatosi'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """
        Cancel an order (only if status allows)
        """
        try:
            # Get order from filtered queryset (ensures ownership)
            order = get_object_or_404(self.get_queryset(), pk=pk)
            
            # Additional permission check
            permission = IsOrderOwner()
            if not permission.has_object_permission(request, self, order):
                return Response(
                    {'detail': 'Sizda bu buyurtmani bekor qilish huquqi yo\'q.'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Check if order can be cancelled
            if not order.is_cancellable:
                return Response(
                    {
                        'error': 'Buyurtmani bekor qilib bo\'lmaydi',
                        'detail': f'Status: {order.get_status_display()}'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Cancel the order
            order.status = OrderStatus.CANCELED
            order.save(update_fields=['status', 'updated_at'])
            
            logger.info(f"Order cancelled: {order.order_number}")
            
            return Response({
                'message': 'Buyurtma bekor qilindi',
                'order_number': order.order_number,
                'status': order.status,
                'status_display': order.get_status_display()
            })
            
        except Exception as e:
            logger.error(f"Error cancelling order {pk}: {str(e)}")
            return Response(
                {
                    'error': 'Buyurtmani bekor qilishda xatolik yuz berdi',
                    'detail': str(e) if request.user.is_staff else 'Server xatosi'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get order statistics for current user/session
        """
        try:
            queryset = self.get_queryset()
            
            # Calculate stats
            total_orders = queryset.count()
            pending_orders = queryset.filter(status=OrderStatus.PENDING).count()
            completed_orders = queryset.filter(status=OrderStatus.DELIVERED).count()
            cancelled_orders = queryset.filter(status=OrderStatus.CANCELED).count()
            
            # Calculate total spent
            total_spent = sum(
                order.total_price for order in queryset.filter(
                    status__in=[OrderStatus.PAID, OrderStatus.DELIVERED]
                )
            )
            
            return Response({
                'total_orders': total_orders,
                'pending_orders': pending_orders,
                'completed_orders': completed_orders,
                'cancelled_orders': cancelled_orders,
                'total_spent': str(total_spent),
            })
            
        except Exception as e:
            logger.error(f"Error getting order stats: {str(e)}")
            return Response(
                {'error': 'Statistika olishda xatolik yuz berdi'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
