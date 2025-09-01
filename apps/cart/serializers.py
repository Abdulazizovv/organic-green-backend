"""
Cart API Serializers
Professional-grade serializers for cart functionality
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.db import transaction
from apps.products.models import Product
from .models import Cart, CartItem, CartHistory


# Simple product serializer for cart items
class CartProductSerializer(serializers.ModelSerializer):
    """Simple product serializer for cart items"""
    
    image_url = serializers.SerializerMethodField()
    is_on_sale = serializers.SerializerMethodField()
    current_price = serializers.SerializerMethodField()
    primary_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name_uz', 'name_ru', 'name_en', 'slug',
            'image_url', 'primary_image_url', 'price', 'sale_price', 
            'current_price', 'is_on_sale', 'stock', 'is_active'
        ]
    
    def get_image_url(self, obj):
        """Get full URL for the primary image"""
        primary_image = obj.primary_image
        if primary_image and primary_image.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url
        return None
    
    def get_primary_image_url(self, obj):
        """Get primary image URL (alias for image_url)"""
        return self.get_image_url(obj)
    
    def get_is_on_sale(self, obj):
        """Check if product is on sale"""
        return bool(obj.sale_price and obj.sale_price < obj.price)
    
    def get_current_price(self, obj):
        """Get current selling price"""
        return float(obj.sale_price if obj.sale_price else obj.price)


class CartItemSerializer(serializers.ModelSerializer):
    """Serializer for CartItem model"""
    
    product = CartProductSerializer(read_only=True)
    product_id = serializers.UUIDField(write_only=True)
    unit_price = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    is_available = serializers.SerializerMethodField()
    max_quantity = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'quantity', 
            'unit_price', 'total_price', 'is_available', 'max_quantity',
            'added_at', 'updated_at'
        ]
        read_only_fields = ['id', 'added_at', 'updated_at']
    
    def get_unit_price(self, obj):
        """Get unit price with sale consideration"""
        return float(obj.get_unit_price())
    
    def get_total_price(self, obj):
        """Get total price for this item"""
        return float(obj.get_total_price())
    
    def get_is_available(self, obj):
        """Check if product is available in requested quantity"""
        return obj.product.stock >= obj.quantity and obj.product.is_active
    
    def get_max_quantity(self, obj):
        """Get maximum available quantity"""
        return obj.product.stock
    
    def validate_product_id(self, value):
        """Validate product exists and is active"""
        try:
            product = Product.objects.get(id=value)
            if not product.is_active:
                raise serializers.ValidationError("Mahsulot faol emas.")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Mahsulot topilmadi.")
    
    def validate_quantity(self, value):
        """Validate quantity"""
        if value < 1:
            raise serializers.ValidationError("Miqdor kamida 1 bo'lishi kerak.")
        if value > 999:
            raise serializers.ValidationError("Miqdor 999 dan oshmasligi kerak.")
        return value
    
    def validate(self, attrs):
        """Validate cart item data"""
        if 'product_id' in attrs:
            try:
                product = Product.objects.get(id=attrs['product_id'])
                quantity = attrs.get('quantity', 1)
                
                if product.stock < quantity:
                    raise serializers.ValidationError({
                        'quantity': f"Mahsulot omborda yetarli emas. Mavjud: {product.stock}"
                    })
                    
            except Product.DoesNotExist:
                raise serializers.ValidationError({
                    'product_id': "Mahsulot topilmadi."
                })
        
        return attrs


class CartItemUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating cart item quantity"""
    
    class Meta:
        model = CartItem
        fields = ['quantity']
    
    def validate_quantity(self, value):
        """Validate quantity for update"""
        # Allow 0 or negative values for removal logic in view
        if value < 0:
            # Just return the value, view will handle removal
            return value
        if value == 0:
            # Allow 0 for removal logic in view
            return value
        if value > 999:
            raise serializers.ValidationError("Miqdor 999 dan oshmasligi kerak.")
        
        # Check stock availability only for positive quantities
        cart_item = self.instance
        if cart_item and cart_item.product.stock < value:
            raise serializers.ValidationError(
                f"Mahsulot omborda yetarli emas. Mavjud: {cart_item.product.stock}"
            )
        
        return value


class CartSerializer(serializers.ModelSerializer):
    """Serializer for Cart model"""
    
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.SerializerMethodField()
    items_count = serializers.ReadOnlyField()
    is_empty = serializers.SerializerMethodField()
    owner = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'owner', 'items', 'total_items', 'total_price', 
            'items_count', 'is_empty', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_price(self, obj):
        """Get formatted total price"""
        return float(obj.total_price)
    
    def get_is_empty(self, obj):
        """Check if cart is empty"""
        return obj.is_empty()
    
    def get_owner(self, obj):
        """Get cart owner info"""
        if obj.user:
            return {
                'type': 'registered',
                'username': obj.user.username,
                'email': obj.user.email
            }
        return {
            'type': 'anonymous',
            'session_key': obj.session_key[:8] + '...' if obj.session_key else None
        }


class AddToCartSerializer(serializers.Serializer):
    """Serializer for adding items to cart"""
    
    product_id = serializers.UUIDField(required=True)
    quantity = serializers.IntegerField(default=1, min_value=1, max_value=999)
    
    def validate_product_id(self, value):
        """Validate product exists and is active"""
        try:
            product = Product.objects.get(id=value)
            if not product.is_active:
                raise serializers.ValidationError("Mahsulot faol emas.")
            return value
        except Product.DoesNotExist:
            raise serializers.ValidationError("Mahsulot topilmadi.")
    
    def validate(self, attrs):
        """Validate add to cart data"""
        try:
            product = Product.objects.get(id=attrs['product_id'])
            quantity = attrs['quantity']
            
            if product.stock < quantity:
                raise serializers.ValidationError({
                    'quantity': f"Mahsulot omborda yetarli emas. Mavjud: {product.stock}"
                })
                
        except Product.DoesNotExist:
            raise serializers.ValidationError({
                'product_id': "Mahsulot topilmadi."
            })
        
        return attrs


class CartSummarySerializer(serializers.Serializer):
    """Serializer for cart summary"""
    
    total_items = serializers.IntegerField()
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    items_count = serializers.IntegerField()
    is_empty = serializers.BooleanField()
    
    # Price breakdown
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_discount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    # Items summary
    items_summary = serializers.ListField(
        child=serializers.DictField(), read_only=True
    )


class CartHistorySerializer(serializers.ModelSerializer):
    """Serializer for CartHistory model"""
    
    product_name = serializers.SerializerMethodField()
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    formatted_price = serializers.SerializerMethodField()
    
    class Meta:
        model = CartHistory
        fields = [
            'id', 'action', 'action_display', 'product', 'product_name',
            'quantity', 'price', 'formatted_price', 'timestamp'
        ]
    
    def get_product_name(self, obj):
        """Get product name"""
        if obj.product:
            return obj.product.name_uz
        return None
    
    def get_formatted_price(self, obj):
        """Get formatted price"""
        if obj.price:
            return float(obj.price)
        return None
