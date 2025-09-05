"""
Admin Serializers
Enhanced serializers with detailed information for admin interfaces
"""
from rest_framework import serializers
from accounts.models import User  # Use custom user model with extra fields
from django.db.models import Sum, Count, Avg
from django.utils import timezone
from datetime import timedelta

# Models
from apps.products.models import Product, ProductCategory, ProductTag, ProductImage
from apps.order.models import Order, OrderItem
from apps.course.models import Application as CourseApplication
from apps.franchise.models import FranchiseApplication
from apps.cart.models import Cart, CartItem
from apps.favorites.models import Favorite


# ===== USER SERIALIZERS =====

class UserAdminSerializer(serializers.ModelSerializer):
    """Basic admin serializer for Users"""
    orders_count = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 
            'is_active', 'is_staff', 'is_superuser', 'date_joined',
            'last_login', 'orders_count', 'total_spent'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_orders_count(self, obj):
        """Get user's orders count"""
        return obj.orders.count()
    
    def get_total_spent(self, obj):
        """Get total amount spent by user"""
        total = obj.orders.aggregate(total=Sum('total_price'))['total']
        return float(total) if total else 0.0


class UserDetailAdminSerializer(UserAdminSerializer):
    """Detailed admin serializer for Users with comprehensive information"""
    recent_orders = serializers.SerializerMethodField()
    recent_favorites = serializers.SerializerMethodField()
    course_applications = serializers.SerializerMethodField()
    franchise_applications = serializers.SerializerMethodField()
    
    class Meta(UserAdminSerializer.Meta):
        fields = UserAdminSerializer.Meta.fields + [
            'recent_orders', 'recent_favorites', 'course_applications', 
            'franchise_applications'
        ]
    
    def get_recent_orders(self, obj):
        """Get recent orders (last 5)"""
        orders = obj.orders.order_by('-created_at')[:5]
        return [{
            'id': str(order.id),
            'order_number': order.order_number,
            'total_price': float(order.total_price),
            'status': order.status,
            'created_at': order.created_at.isoformat()
        } for order in orders]
    
    def get_recent_favorites(self, obj):
        """Get recent favorites (last 5)"""
        favorites = obj.favorites.select_related('product').order_by('-created_at')[:5]
        return [{
            'product_id': str(fav.product.id),
            'product_name': fav.product.name_uz,
            'created_at': fav.created_at.isoformat()
        } for fav in favorites]
    
    def get_course_applications(self, obj):
        """Get course applications count"""
        # Since CourseApplication doesn't have user field, we can't get by user
        # This is just a placeholder
        return 0
    
    def get_franchise_applications(self, obj):
        """Get franchise applications count"""
        # Since FranchiseApplication doesn't have user field, we can't get by user
        # This is just a placeholder  
        return 0


# ===== PRODUCT SERIALIZERS =====

class ProductImageReadAdminSerializer(serializers.ModelSerializer):
    """Read-only serializer for Product Images (admin)"""
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = [
            'id', 'image_url', 'alt_text_uz', 'alt_text_ru', 'alt_text_en',
            'is_primary', 'order', 'created_at'
        ]
        read_only_fields = ['id', 'image_url', 'created_at']

    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProductImageWriteAdminSerializer(serializers.ModelSerializer):
    """Write serializer for creating product images together with product"""
    class Meta:
        model = ProductImage
        fields = [
            'image', 'alt_text_uz', 'alt_text_ru', 'alt_text_en', 'is_primary', 'order'
        ]


class ProductAdminSerializer(serializers.ModelSerializer):
    """Basic admin serializer for Products"""
    category_name = serializers.CharField(source='category.name_uz', read_only=True)
    orders_count = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()
    images = ProductImageWriteAdminSerializer(many=True, write_only=True, required=False, help_text="Mahsulot yaratishda bir nechta rasm yuborish uchun")
    images_list = ProductImageReadAdminSerializer(source='images', many=True, read_only=True)
    primary_image_url = serializers.SerializerMethodField()
    image_url = serializers.SerializerMethodField(help_text="Primary image URL (alias)")
    image_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name_uz', 'name_ru', 'name_en', 'slug', 'price', 'sale_price',
            'stock', 'category', 'category_name', 'is_active', 'is_featured',
            'orders_count', 'favorites_count', 'created_at', 'updated_at',
            'images', 'images_list', 'primary_image_url', 'image_url', 'image_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'orders_count', 'favorites_count', 'image_count']
    
    def get_orders_count(self, obj):
        """Get how many times this product was ordered"""
        return obj.order_items.count()
    
    def get_favorites_count(self, obj):
        """Get how many users favorited this product"""
        return obj.favorited_by.count()
    
    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        product = super().create(validated_data)
        for order_index, image_data in enumerate(images_data):
            # Ensure order if not provided
            if image_data.get('order') is None:
                image_data['order'] = order_index
            ProductImage.objects.create(product=product, **image_data)
        return product

    def update(self, instance, validated_data):
        # Images are not updated via this endpoint (separate upload endpoint), so pop if present
        validated_data.pop('images', None)
        return super().update(instance, validated_data)

    def get_primary_image_url(self, obj):
        primary = obj.primary_image
        if primary and primary.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary.image.url)
            return primary.image.url
        return None

    def get_image_url(self, obj):
        return self.get_primary_image_url(obj)


class ProductDetailAdminSerializer(ProductAdminSerializer):
    """Detailed admin serializer for Products with comprehensive statistics"""
    total_sold = serializers.SerializerMethodField()
    revenue_generated = serializers.SerializerMethodField()
    recent_orders = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    
    class Meta(ProductAdminSerializer.Meta):
        fields = ProductAdminSerializer.Meta.fields + [
            'total_sold', 'revenue_generated', 'recent_orders', 'stock_status'
        ]
    
    def get_total_sold(self, obj):
        """Get total quantity sold"""
        total = obj.order_items.aggregate(total=Sum('quantity'))['total']
        return total if total else 0
    
    def get_revenue_generated(self, obj):
        """Get total revenue from this product"""
        total = obj.order_items.aggregate(
            total=Sum('total_price')
        )['total']
        return float(total) if total else 0.0
    
    def get_recent_orders(self, obj):
        """Get recent orders for this product (last 5)"""
        recent_items = obj.order_items.select_related('order').order_by('-order__created_at')[:5]
        return [{
            'order_id': str(item.order.id),
            'order_number': item.order.order_number,
            'quantity': item.quantity,
            'price': float(item.total_price),
            'created_at': item.order.created_at.isoformat()
        } for item in recent_items]
    
    def get_stock_status(self, obj):
        """Get stock status description"""
        if obj.stock == 0:
            return "Out of Stock"
        elif obj.stock < 10:
            return "Low Stock"
        else:
            return "In Stock"


class ProductCategoryAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Product Categories"""
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name_uz', 'name_ru', 'name_en', 'description_uz',
            'description_ru', 'description_en', 'products_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_products_count(self, obj):
        """Get products count in this category"""
        return obj.products.filter(is_active=True, deleted_at__isnull=True).count()


class ProductTagAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Product Tags"""
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductTag
        fields = [
            'id', 'name_uz', 'name_ru', 'name_en', 'products_count',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_products_count(self, obj):
        """Get products count with this tag"""
        return obj.products.filter(is_active=True, deleted_at__isnull=True).count()


# ===== ORDER SERIALIZERS =====

class OrderItemAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Order Items"""
    product_name = serializers.CharField(source='product.name_uz', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'quantity', 'total_price', 'unit_price'
        ]


class OrderAdminSerializer(serializers.ModelSerializer):
    """Basic admin serializer for Orders"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'user_email', 'full_name',
            'contact_phone', 'delivery_address', 'status', 'payment_method',
            'total_price', 'items_count', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']
    
    def get_items_count(self, obj):
        """Get order items count"""
        return obj.items.count()


class OrderDetailAdminSerializer(OrderAdminSerializer):
    """Detailed admin serializer for Orders"""
    items = OrderItemAdminSerializer(many=True, read_only=True)
    
    class Meta(OrderAdminSerializer.Meta):
        fields = OrderAdminSerializer.Meta.fields + ['items']


# ===== APPLICATION SERIALIZERS =====

class CourseApplicationAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Course Applications"""
    status_display = serializers.SerializerMethodField()
    created_at_formatted = serializers.SerializerMethodField()
    application_age = serializers.SerializerMethodField()
    
    class Meta:
        model = CourseApplication
        fields = [
            'id', 'application_number', 'full_name', 'email', 'phone_number',
            'course_name', 'message', 'processed', 'status_display',
            'created_at', 'created_at_formatted', 'updated_at', 'application_age'
        ]
        read_only_fields = ['id', 'application_number', 'created_at', 'updated_at']
    
    def get_status_display(self, obj):
        """Get human readable status"""
        return "Qayta ishlangan" if obj.processed else "Kutilmoqda"
    
    def get_created_at_formatted(self, obj):
        """Get formatted creation date"""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')
    
    def get_application_age(self, obj):
        """Get application age in days"""
        diff = timezone.now() - obj.created_at
        return diff.days


class FranchiseApplicationAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Franchise Applications"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_at_formatted = serializers.SerializerMethodField()
    investment_amount_formatted = serializers.SerializerMethodField()
    is_pending = serializers.ReadOnlyField()
    is_approved = serializers.ReadOnlyField()
    formatted_investment_amount = serializers.ReadOnlyField()
    
    class Meta:
        model = FranchiseApplication
        fields = [
            'id', 'full_name', 'phone', 'email', 'city', 'investment_amount',
            'investment_amount_formatted', 'formatted_investment_amount',
            'experience', 'message', 'status', 'status_display',
            'is_pending', 'is_approved', 'created_at', 'created_at_formatted', 
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_created_at_formatted(self, obj):
        """Get formatted creation date"""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')
    
    def get_investment_amount_formatted(self, obj):
        """Get formatted investment amount"""
        return f"${obj.investment_amount:,.2f}"


# ===== CART & FAVORITES SERIALIZERS =====

class CartAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Cart"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    items_count = serializers.SerializerMethodField()
    total_value = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'user_email', 'session_key', 'items_count',
            'total_value', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_items_count(self, obj):
        """Get cart items count"""
        return obj.items.count()
    
    def get_total_value(self, obj):
        """Get total cart value"""
        total = sum(item.quantity * item.product.final_price for item in obj.items.all())
        return float(total)


class FavoriteAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Favorites"""
    user_email = serializers.CharField(source='user.email', read_only=True)
    product_name = serializers.CharField(source='product.name_uz', read_only=True)
    product_price = serializers.DecimalField(source='product.final_price', read_only=True, max_digits=15, decimal_places=2)
    
    class Meta:
        model = Favorite
        fields = [
            'id', 'user', 'user_email', 'product', 'product_name',
            'product_price', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
