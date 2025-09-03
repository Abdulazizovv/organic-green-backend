"""
Order serializers for Organic Green e-commerce
"""
from decimal import Decimal
from rest_framework import serializers
from django.db import transaction
from django.contrib.auth import get_user_model
from apps.cart.utils import get_or_create_cart
from apps.products.models import Product
from .models import Order, OrderItem, OrderStatus, PaymentMethod


User = get_user_model()



class OrderItemSerializer(serializers.ModelSerializer):
    """Serializer for OrderItem (read-only for nested display)"""
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'quantity', 
            'unit_price', 'total_price', 'is_sale_price'
        ]
        read_only_fields = fields


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for Order (list/retrieve operations)"""
    
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    customer_display = serializers.CharField(read_only=True)
    is_cancellable = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'status', 'status_display',
            'payment_method', 'payment_method_display', 'full_name',
            'contact_phone', 'delivery_address', 'notes', 'subtotal',
            'discount_total', 'total_price', 'total_items', 'items',
            'customer_display', 'is_cancellable', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'order_number', 'user', 'subtotal', 'discount_total',
            'total_price', 'total_items', 'items', 'customer_display',
            'is_cancellable', 'created_at', 'updated_at', 'status_display',
            'payment_method_display'
        ]


class OrderCreateSerializer(serializers.Serializer):
    """Serializer for creating orders from cart"""
    
    full_name = serializers.CharField(
        max_length=150, 
        required=False,
        help_text="Customer full name (required if not in user profile)"
    )
    contact_phone = serializers.CharField(
        max_length=32, 
        required=False,
        help_text="Customer phone (required if not in user profile)"
    )
    delivery_address = serializers.CharField(
        required=True,
        help_text="Delivery address (always required)"
    )
    notes = serializers.CharField(
        required=False, 
        allow_blank=True,
        help_text="Special instructions or notes"
    )
    payment_method = serializers.ChoiceField(
        choices=PaymentMethod.choices,
        default=PaymentMethod.COD,
        required=False,
        help_text="Payment method"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get('request')
        
        # If user is authenticated and has profile data, make contact fields optional
        if request and request.user.is_authenticated:
            user = request.user
            # Check if user has required profile fields
            has_full_name = bool(user.first_name and user.last_name)
            has_phone = hasattr(user, 'phone') and bool(user.phone)
            
            # If user doesn't have profile data, make fields required
            if not has_full_name:
                self.fields['full_name'].required = True
            if not has_phone:
                self.fields['contact_phone'].required = True
        else:
            # Anonymous user - all contact fields required
            self.fields['full_name'].required = True
            self.fields['contact_phone'].required = True
    
    def validate(self, attrs):
        """Validate cart and stock availability"""
        request = self.context['request']
        
        # Get current cart
        cart, _ = get_or_create_cart(request)
        
        # Check if cart is empty
        if not cart.items.exists():
            raise serializers.ValidationError({
                'cart': ['Savat bo\'sh. Buyurtma berish uchun mahsulot qo\'shing.']
            })
        
        # Validate stock for each cart item
        insufficient_stock = []
        for cart_item in cart.items.select_related('product'):
            product = cart_item.product
            if not product.is_active:
                insufficient_stock.append(
                    f"{product.name_uz} - mahsulot faol emas"
                )
            elif cart_item.quantity > product.stock:
                insufficient_stock.append(
                    f"{product.name_uz} - talab: {cart_item.quantity}, mavjud: {product.stock}"
                )
        
        if insufficient_stock:
            raise serializers.ValidationError({
                'stock': insufficient_stock
            })
        
        # Get contact info from user profile if not provided
        if request.user.is_authenticated:
            user = request.user
            
            # Use profile data if not provided in request
            if not attrs.get('full_name'):
                if user.first_name and user.last_name:
                    attrs['full_name'] = f"{user.first_name} {user.last_name}".strip()
                elif user.first_name:
                    attrs['full_name'] = user.first_name
                elif user.last_name:
                    attrs['full_name'] = user.last_name
                else:
                    # This should be caught by field validation, but just in case
                    raise serializers.ValidationError({
                        'full_name': ['Bu maydon talab qilinadi yoki profilda ism-familiya bo\'lishi kerak.']
                    })
            
            if not attrs.get('contact_phone'):
                if hasattr(user, 'phone') and user.phone:
                    attrs['contact_phone'] = user.phone
                else:
                    # This should be caught by field validation, but just in case
                    raise serializers.ValidationError({
                        'contact_phone': ['Bu maydon talab qilinadi yoki profilga telefon raqam qo\'shilishi kerak.']
                    })
        
        # Store cart in validated data for create method
        attrs['_cart'] = cart
        
        return attrs
    
    def create(self, validated_data):
        """Create order from cart with atomic transaction"""
        request = self.context['request']
        cart = validated_data.pop('_cart')
        
        user = request.user if request.user.is_authenticated else None
        session_key = None if user else request.session.session_key
        
        with transaction.atomic():
            # Pre-lock products to prevent race conditions
            cart_items = list(
                cart.items.select_related('product')
                .select_for_update()
                .order_by('product_id')  # Consistent ordering to prevent deadlocks
            )
            
            if not cart_items:
                raise serializers.ValidationError({
                    'cart': ['Savat bo\'sh. Buyurtma berish uchun mahsulot qo\'shing.']
                })
            
            # Validate stock availability again (with locks)
            insufficient_stock = []
            for cart_item in cart_items:
                product = cart_item.product
                if not product.is_active:
                    insufficient_stock.append(
                        f"{product.name_uz} - mahsulot faol emas"
                    )
                elif cart_item.quantity > product.stock:
                    insufficient_stock.append(
                        f"{product.name_uz} - yetarli emas. Talab: {cart_item.quantity}, mavjud: {product.stock}"
                    )
            
            if insufficient_stock:
                raise serializers.ValidationError({
                    'stock': insufficient_stock
                })
            
            # Calculate totals
            subtotal = Decimal('0.00')
            total_items = 0
            
            for cart_item in cart_items:
                # Calculate total price dynamically as unit_price * quantity
                unit_price = cart_item.get_unit_price()
                item_total = unit_price * cart_item.quantity
                subtotal += item_total
                total_items += cart_item.quantity
            
            # Create order
            order = Order.objects.create(
                user=user,
                session_key=session_key,
                full_name=validated_data['full_name'],
                contact_phone=validated_data['contact_phone'],
                delivery_address=validated_data['delivery_address'],
                notes=validated_data.get('notes', ''),
                payment_method=validated_data.get('payment_method', PaymentMethod.COD),
                subtotal=subtotal,
                discount_total=Decimal('0.00'),  # Future feature
                total_items=total_items
            )
            
            # Create order items and reduce stock
            for cart_item in cart_items:
                product = cart_item.product
                unit_price = cart_item.get_unit_price()
                
                # Create order item snapshot
                OrderItem.objects.create(
                    order=order,
                    product=product,
                    product_name=product.name_uz,
                    quantity=cart_item.quantity,
                    unit_price=unit_price,
                    is_sale_price=bool(product.sale_price and product.sale_price < product.price)
                )
                
                # Reduce product stock
                product.stock -= cart_item.quantity
                product.save(update_fields=['stock'])
            
            # Update order total_price (in case of future discount logic)
            order.total_price = order.subtotal - order.discount_total
            order.save(update_fields=['total_price'])
            
            # Clear cart after successful order creation
            cart.items.all().delete()
            
            return order
