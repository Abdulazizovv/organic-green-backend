"""
Cart API Views
Professional-grade views for cart functionality
"""
from rest_framework import generics, viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.sessions.models import Session
from apps.products.models import Product
from .models import Cart, CartItem, CartHistory
from .serializers import (
    CartSerializer, CartItemSerializer, CartItemUpdateSerializer,
    AddToCartSerializer, CartSummarySerializer, CartHistorySerializer
)
from .utils import get_or_create_cart, log_cart_action
import logging

logger = logging.getLogger(__name__)


class CartViewSet(viewsets.ModelViewSet):
    """
    Cart ViewSet
    
    Provides CRUD operations for shopping cart
    """
    serializer_class = CartSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [AllowAny]  # Allow both authenticated and anonymous users
    # throttle_classes = [UserRateThrottle, AnonRateThrottle]  # Commented out for testing
    
    def get_queryset(self):
        """Get user's cart or anonymous cart"""
        if self.request.user.is_authenticated:
            return Cart.objects.filter(user=self.request.user)
        else:
            session_key = self.request.session.session_key
            if session_key:
                return Cart.objects.filter(session_key=session_key)
            return Cart.objects.none()
    
    def get_object(self):
        """Get or create cart for current user/session"""
        cart, created = get_or_create_cart(self.request)
        return cart
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current user's cart"""
        cart, created = get_or_create_cart(request)
        serializer = self.get_serializer(cart)
        
        response_data = serializer.data
        response_data['message'] = 'Joriy savat' if not created else 'Yangi savat yaratildi'
        
        return Response(response_data)
    
    @action(detail=False, methods=['post'])
    def add_item(self, request):
        """Add item to cart or set quantity"""
        serializer = AddToCartSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        cart, created = get_or_create_cart(request)
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            
            # Check stock availability
            if quantity > product.stock:
                return Response({
                    'quantity': [f'Mahsulot omborda yetarli emas. Mavjud: {product.stock}']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            with transaction.atomic():
                # Check if item already exists in cart
                cart_item, item_created = CartItem.objects.get_or_create(
                    cart=cart,
                    product=product,
                    defaults={'quantity': quantity}
                )
                
                if not item_created:
                    # Set quantity instead of adding (changed logic)
                    cart_item.quantity = quantity
                    cart_item.save()
                    action = 'update'
                    message = 'Mahsulot miqdori yangilandi'
                else:
                    action = 'add'
                    message = 'Mahsulot savatga qo\'shildi'
                
                # Log action
                log_cart_action(
                    cart=cart,
                    action=action,
                    product=product,
                    quantity=quantity,
                    request=request
                )
                
                # Update cart timestamp
                cart.save()
                
                # Serialize updated cart item
                item_serializer = CartItemSerializer(cart_item, context={'request': request})
                
                logger.info(f"Cart item {action}: {quantity} x {product.name_uz}")
                
                return Response({
                    'message': message,
                    'item': item_serializer.data,
                    'cart_summary': {
                        'total_items': cart.total_items,
                        'total_price': str(cart.total_price),
                        'items_count': cart.items_count
                    }
                }, status=status.HTTP_201_CREATED)
                
        except Product.DoesNotExist:
            return Response({
                'product_id': ['Mahsulot topilmadi.']
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error adding item to cart: {str(e)}")
            return Response({
                'error': 'Xatolik yuz berdi'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['patch'])
    def update_item(self, request):
        """Update item quantity in cart or remove if quantity <= 0"""
        item_id = request.data.get('item_id')
        if not item_id:
            return Response({
                'error': 'item_id majburiy'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        quantity = request.data.get('quantity')
        if quantity is None:
            return Response({
                'error': 'quantity majburiy'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            quantity = int(quantity)
        except (ValueError, TypeError):
            return Response({
                'error': 'quantity raqam bo\'lishi kerak'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cart, created = get_or_create_cart(request)
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            old_quantity = cart_item.quantity
            
            # If quantity is 0 or less, remove the item
            if quantity <= 0:
                product_name = cart_item.product.name_uz
                
                # Log removal action
                log_cart_action(
                    cart=cart,
                    action='remove',
                    product=cart_item.product,
                    quantity=old_quantity,
                    request=request
                )
                
                cart_item.delete()
                
                logger.info(f"Removed cart item due to quantity <= 0: {product_name}")
                
                return Response({
                    'message': 'Mahsulot savatdan o\'chirildi',
                    'cart_summary': {
                        'total_items': cart.total_items,
                        'total_price': float(cart.total_price),
                        'items_count': cart.items_count
                    }
                })
            
            # Otherwise, update the quantity normally
            serializer = CartItemUpdateSerializer(
                cart_item, 
                data=request.data, 
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            
            cart_item = serializer.save()
            
            # Log update action
            log_cart_action(
                cart=cart,
                action='update',
                product=cart_item.product,
                quantity=cart_item.quantity,
                request=request
            )
            
            logger.info(f"Updated cart item quantity: {old_quantity} -> {cart_item.quantity}")
            
            return Response({
                'message': 'Mahsulot miqdori yangilandi',
                'item': CartItemSerializer(cart_item).data,
                'cart_summary': {
                    'total_items': cart.total_items,
                    'total_price': float(cart.total_price),
                    'items_count': cart.items_count
                }
            })
            
        except CartItem.DoesNotExist:
            return Response({
                'error': 'Savat elementi topilmadi'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['delete'])
    def remove_item(self, request):
        """Remove item from cart"""
        item_id = request.query_params.get('item_id')
        if not item_id:
            return Response({
                'error': 'item_id majburiy'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        cart, created = get_or_create_cart(request)
        
        try:
            cart_item = CartItem.objects.get(id=item_id, cart=cart)
            product = cart_item.product
            quantity = cart_item.quantity
            
            cart_item.delete()
            
            # Log action
            log_cart_action(
                cart=cart,
                action='remove',
                product=product,
                quantity=quantity,
                request=request
            )
            
            logger.info(f"Removed {product.name_uz} from cart")
            
            return Response({
                'message': 'Mahsulot savatdan o\'chirildi',
                'cart_summary': {
                    'total_items': cart.total_items,
                    'total_price': float(cart.total_price),
                    'items_count': cart.items_count
                }
            })
            
        except CartItem.DoesNotExist:
            return Response({
                'error': 'Savat elementi topilmadi'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['delete'])
    def clear(self, request):
        """Clear all items from cart"""
        cart, created = get_or_create_cart(request)
        
        items_count = cart.items_count
        cart.clear()
        
        # Log action
        log_cart_action(
            cart=cart,
            action='clear',
            request=request
        )
        
        logger.info(f"Cleared cart with {items_count} items")
        
        return Response({
            'message': 'Savat tozalandi',
            'cart_summary': {
                'total_items': 0,
                'total_price': 0.0,
                'items_count': 0
            }
        })
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get cart summary"""
        cart, created = get_or_create_cart(request)
        
        # Calculate summary data
        items = cart.items.all()
        subtotal = sum(item.product.price * item.quantity for item in items)
        total_discount = sum(
            (item.product.price - item.get_unit_price()) * item.quantity 
            for item in items
        )
        
        summary_data = {
            'total_items': cart.total_items,
            'total_price': cart.total_price,
            'items_count': cart.items_count,
            'is_empty': cart.is_empty(),
            'subtotal': subtotal,
            'total_discount': total_discount,
            'items_summary': [
                {
                    'product_name': item.product.name_uz,
                    'quantity': item.quantity,
                    'unit_price': float(item.get_unit_price()),
                    'total_price': float(item.get_total_price()),
                    'is_on_sale': bool(item.product.sale_price)
                }
                for item in items
            ]
        }
        
        serializer = CartSummarySerializer(summary_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get cart history"""
        cart, created = get_or_create_cart(request)
        
        history = CartHistory.objects.filter(cart=cart).order_by('-timestamp')[:50]
        serializer = CartHistorySerializer(history, many=True)
        
        return Response({
            'history': serializer.data,
            'count': history.count()
        })


@api_view(['GET'])
@permission_classes([AllowAny])
def cart_info(request):
    """
    Get cart API information
    """
    return Response({
        'title': 'Savat API',
        'description': 'Xarid savati boshqaruvi uchun API',
        'endpoints': {
            'current_cart': '/api/cart/current/ (GET)',
            'add_item': '/api/cart/add_item/ (POST)',
            'update_item': '/api/cart/update_item/ (PATCH)',
            'remove_item': '/api/cart/remove_item/ (DELETE)',
            'clear_cart': '/api/cart/clear/ (DELETE)',
            'cart_summary': '/api/cart/summary/ (GET)',
            'cart_history': '/api/cart/history/ (GET)',
        },
        'features': [
            'Foydalanuvchi va anonim savatlar',
            'Mahsulot miqdorini boshqarish',
            'Avtomatik narx hisoblash',
            'Savat tarixi',
            'Stok nazorati',
            'Session-based anonymous carts'
        ],
        'notes': {
            'authentication': 'Ixtiyoriy - tizimga kirgan va kirimagan foydalanuvchilar uchun',
            'session': 'Anonim foydalanuvchilar uchun session asosida savat yaratiladi',
            'stock_check': 'Mahsulot qo\'shishda va yangilashda stok tekshiriladi'
        }
    })


# Cart utilities for other views
class CartMixin:
    """Mixin to add cart functionality to other views"""
    
    def get_cart(self):
        """Get current user's cart"""
        cart, created = get_or_create_cart(self.request)
        return cart
    
    def add_to_cart(self, product, quantity=1):
        """Add product to cart"""
        cart = self.get_cart()
        
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return cart_item
