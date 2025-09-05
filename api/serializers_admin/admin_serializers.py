"""
Admin serializers for all project entities
"""
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.db.models import Sum, Count
from decimal import Decimal

# Models
from accounts.models import User
from apps.products.models import Product, ProductCategory, ProductTag, ProductImage
from apps.order.models import Order, OrderItem
from apps.course.models import Application as CourseApplication
from apps.franchise.models import FranchiseApplication
from apps.cart.models import Cart, CartItem
from apps.favorites.models import Favorite


class UserDetailAdminSerializer(serializers.ModelSerializer):
    """Detailed admin serializer for User model with full activity"""
    full_name = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    
    # User Statistics
    orders_count = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    last_order_date = serializers.SerializerMethodField()
    average_order_value = serializers.SerializerMethodField()
    
    # Activity Information
    course_applications = serializers.SerializerMethodField()
    franchise_applications = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()
    cart_items_count = serializers.SerializerMethodField()
    
    # Recent Activity
    recent_orders = serializers.SerializerMethodField()
    recent_favorites = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'display_name', 'phone', 'avatar', 'is_active', 'is_staff', 
            'is_superuser', 'is_verified', 'date_joined', 'last_login',
            # Statistics
            'orders_count', 'total_spent', 'last_order_date', 'average_order_value',
            # Activity
            'course_applications', 'franchise_applications', 'favorites_count', 
            'cart_items_count',
            # Recent activity
            'recent_orders', 'recent_favorites'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_orders_count(self, obj):
        """Get total orders count for user"""
        return obj.orders.count()
    
    def get_total_spent(self, obj):
        """Get total amount spent by user"""
        total = obj.orders.aggregate(total=Sum('total_price'))['total']
        return total or Decimal('0.00')
    
    def get_last_order_date(self, obj):
        """Get last order date"""
        last_order = obj.orders.first()
        return last_order.created_at if last_order else None
    
    def get_average_order_value(self, obj):
        """Get average order value"""
        total_spent = self.get_total_spent(obj)
        orders_count = self.get_orders_count(obj)
        if orders_count > 0:
            return total_spent / orders_count
        return Decimal('0.00')
    
    def get_course_applications(self, obj):
        """Get course applications summary"""
        # Note: CourseApplication doesn't have user FK, so we can't directly relate
        # But we can search by email/phone if needed
        return {
            'total': 0,  # Would need to implement search by email/phone
            'pending': 0,
            'processed': 0
        }
    
    def get_franchise_applications(self, obj):
        """Get franchise applications summary"""
        # Same as course applications - search by email/phone
        return {
            'total': 0,
            'pending': 0,
            'approved': 0,
            'rejected': 0
        }
    
    def get_favorites_count(self, obj):
        """Get favorites count"""
        return obj.favorites.count()
    
    def get_cart_items_count(self, obj):
        """Get cart items count"""
        try:
            return obj.cart.items.count()
        except:
            return 0
    
    def get_recent_orders(self, obj):
        """Get recent orders (last 5)"""
        recent_orders = obj.orders.all()[:5]
        return [
            {
                'id': order.id,
                'order_number': order.order_number,
                'total_price': order.total_price,
                'status': order.status,
                'created_at': order.created_at
            }
            for order in recent_orders
        ]
    
    def get_recent_favorites(self, obj):
        """Get recent favorites (last 5)"""
        recent_favorites = obj.favorites.select_related('product').all()[:5]
        return [
            {
                'id': fav.id,
                'product_name': fav.product.name_uz,
                'product_slug': fav.product.slug,
                'created_at': fav.created_at
            }
            for fav in recent_favorites
        ]


class UserAdminSerializer(serializers.ModelSerializer):
    """List admin serializer for User model"""
    full_name = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    orders_count = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    last_order_date = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'display_name', 'phone', 'avatar', 'is_active', 'is_staff', 
            'is_superuser', 'is_verified', 'date_joined', 'last_login',
            'orders_count', 'total_spent', 'last_order_date'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_orders_count(self, obj):
        """Get total orders count for user"""
        return getattr(obj, 'orders_count', obj.orders.count())
    
    def get_total_spent(self, obj):
        """Get total amount spent by user"""
        return getattr(obj, 'total_spent', obj.orders.aggregate(total=Sum('total_price'))['total'] or Decimal('0.00'))
    
    def get_last_order_date(self, obj):
        """Get last order date"""
        last_order = obj.orders.first()
        return last_order.created_at if last_order else None


class ProductImageAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Product Images"""
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text_uz', 'alt_text_ru', 'alt_text_en', 'is_primary', 'order']


class ProductDetailAdminSerializer(serializers.ModelSerializer):
    """Detailed admin serializer for Product model"""
    category_name = serializers.CharField(source='category.name_uz', read_only=True)
    tags_list = serializers.StringRelatedField(source='tags', many=True, read_only=True)
    images = ProductImageAdminSerializer(many=True, read_only=True)
    is_on_sale = serializers.ReadOnlyField()
    final_price = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    
    # Product Statistics
    orders_count = serializers.SerializerMethodField()
    total_sold = serializers.SerializerMethodField()
    revenue_generated = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    favorites_count = serializers.SerializerMethodField()
    
    # Recent Activity
    recent_orders = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name_uz', 'name_ru', 'name_en', 'slug', 'description_uz',
            'description_ru', 'description_en', 'price', 'sale_price', 'stock',
            'category', 'category_name', 'tags', 'tags_list', 'is_active',
            'is_featured', 'suggested_products', 'created_at', 'updated_at',
            'deleted_at', 'images', 'is_on_sale', 'final_price', 'display_name',
            # Statistics
            'orders_count', 'total_sold', 'revenue_generated', 'average_rating',
            'favorites_count',
            # Status
            'recent_orders', 'stock_status'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_orders_count(self, obj):
        """Get how many times this product was ordered"""
        return obj.order_items.count()
    
    def get_total_sold(self, obj):
        """Get total quantity sold"""
        return obj.order_items.aggregate(total=Sum('quantity'))['total'] or 0
    
    def get_revenue_generated(self, obj):
        """Get total revenue from this product"""
        return obj.order_items.aggregate(
            total=Sum('total_price')
        )['total'] or Decimal('0.00')
    
    def get_average_rating(self, obj):
        """Get average rating (placeholder - implement if you have reviews)"""
        return None  # Implement when review system is available
    
    def get_favorites_count(self, obj):
        """Get how many users favorited this product"""
        return obj.favorited_by.count()
    
    def get_recent_orders(self, obj):
        """Get recent orders containing this product"""
        recent_items = obj.order_items.select_related('order').order_by('-order__created_at')[:5]
        return [
            {
                'order_number': item.order.order_number,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'created_at': item.order.created_at
            }
            for item in recent_items
        ]
    
    def get_stock_status(self, obj):
        """Get stock status information"""
        if obj.stock == 0:
            return 'out_of_stock'
        elif obj.stock < 10:
            return 'low_stock'
        elif obj.stock < 50:
            return 'medium_stock'
        else:
            return 'in_stock'


class ProductAdminSerializer(serializers.ModelSerializer):
    """List admin serializer for Product model"""
    category_name = serializers.CharField(source='category.name_uz', read_only=True)
    tags_list = serializers.StringRelatedField(source='tags', many=True, read_only=True)
    is_on_sale = serializers.ReadOnlyField()
    final_price = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    orders_count = serializers.SerializerMethodField()
    stock_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name_uz', 'name_ru', 'name_en', 'slug', 'price', 'sale_price', 
            'stock', 'category', 'category_name', 'tags', 'tags_list', 'is_active',
            'is_featured', 'created_at', 'updated_at', 'deleted_at', 'is_on_sale', 
            'final_price', 'display_name', 'orders_count', 'stock_status'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_orders_count(self, obj):
        """Get how many times this product was ordered"""
        return getattr(obj, 'orders_count', obj.order_items.count())
    
    def get_stock_status(self, obj):
        """Get stock status"""
        if obj.stock == 0:
            return 'out_of_stock'
        elif obj.stock < 10:
            return 'low_stock'
        else:
            return 'in_stock'


class ProductCategoryAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Product Category"""
    products_count = serializers.SerializerMethodField()
    active_products_count = serializers.SerializerMethodField()
    total_revenue = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name_uz', 'name_ru', 'name_en', 'description_uz',
            'description_ru', 'description_en', 'created_at', 'updated_at',
            'products_count', 'active_products_count', 'total_revenue'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_products_count(self, obj):
        """Get total products count in this category"""
        return obj.products.count()
    
    def get_active_products_count(self, obj):
        """Get active products count in this category"""
        return obj.products.filter(is_active=True, deleted_at__isnull=True).count()
    
    def get_total_revenue(self, obj):
        """Get total revenue from this category"""
        return OrderItem.objects.filter(
            product__category=obj
        ).aggregate(total=Sum('total_price'))['total'] or Decimal('0.00')


class ProductTagAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Product Tag"""
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductTag
        fields = [
            'id', 'name_uz', 'name_ru', 'name_en', 'created_at', 'updated_at',
            'products_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_products_count(self, obj):
        """Get products count with this tag"""
        return obj.products.filter(is_active=True, deleted_at__isnull=True).count()


class OrderItemAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Order Items"""
    product_name = serializers.CharField(source='product.name_uz', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_slug', 'quantity',
            'unit_price', 'total_price'
        ]


class OrderDetailAdminSerializer(serializers.ModelSerializer):
    """Detailed admin serializer for Order model"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    items = OrderItemAdminSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'user_name', 'user_email',
            'full_name', 'contact_phone', 'delivery_address', 'notes',
            'status', 'status_display', 'payment_method', 'payment_method_display',
            'subtotal', 'delivery_price', 'discount_total', 'total_price',
            'total_items', 'created_at', 'updated_at', 'items', 'items_count'
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']
    
    def get_items_count(self, obj):
        """Get total items count in order"""
        return obj.items.count()


class OrderAdminSerializer(serializers.ModelSerializer):
    """List admin serializer for Order model"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    items_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'user_name', 'full_name', 
            'contact_phone', 'status', 'status_display', 'payment_method',
            'payment_method_display', 'total_price', 'total_items',
            'created_at', 'updated_at', 'items_count'
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']
    
    def get_items_count(self, obj):
        """Get total items count in order"""
        return obj.items.count()


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
        from django.utils import timezone
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


class CartItemAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Cart Items"""
    product_name = serializers.CharField(source='product.name_uz', read_only=True)
    product_price = serializers.DecimalField(source='product.final_price', max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'added_at']


class CartAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Cart model"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    items = CartItemAdminSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'user_name', 'created_at', 'updated_at', 
            'items', 'items_count', 'total_amount'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_items_count(self, obj):
        """Get total items count in cart"""
        return obj.items.count()
    
    def get_total_amount(self, obj):
        """Calculate total cart amount"""
        total = Decimal('0.00')
        for item in obj.items.all():
            total += item.product.final_price * item.quantity
        return total


class FavoriteAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Favorites"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    product_name = serializers.CharField(source='product.name_uz', read_only=True)
    product_price = serializers.DecimalField(source='product.final_price', max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = Favorite
        fields = [
            'id', 'user', 'user_name', 'product', 'product_name', 
            'product_price', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# Stats Serializers
class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    users = serializers.DictField()
    products = serializers.DictField()
    orders = serializers.DictField()
    courses = serializers.DictField()
    franchises = serializers.DictField()
    revenue = serializers.DictField()


class ApplicationStatsSerializer(serializers.Serializer):
    """Serializer for applications statistics"""
    course_applications = serializers.DictField()
    franchise_applications = serializers.DictField()
from rest_framework import serializers
from django.contrib.auth import get_user_model
from decimal import Decimal

# Models
from accounts.models import User
from apps.products.models import Product, ProductCategory, ProductTag, ProductImage
from apps.order.models import Order, OrderItem
from apps.course.models import Application as CourseApplication
from apps.franchise.models import FranchiseApplication
from apps.cart.models import Cart, CartItem
from apps.favorites.models import Favorite


class UserAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for User model"""
    full_name = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    orders_count = serializers.SerializerMethodField()
    total_spent = serializers.SerializerMethodField()
    last_order_date = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'display_name', 'phone', 'avatar', 'is_active', 'is_staff', 
            'is_superuser', 'is_verified', 'date_joined', 'last_login',
            'orders_count', 'total_spent', 'last_order_date'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_orders_count(self, obj):
        """Get total orders count for user"""
        return getattr(obj, 'orders_count', 0)
    
    def get_total_spent(self, obj):
        """Get total amount spent by user"""
        return getattr(obj, 'total_spent', Decimal('0.00'))
    
    def get_last_order_date(self, obj):
        """Get last order date"""
        return getattr(obj, 'last_order_date', None)


class ProductImageAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Product Images"""
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text_uz', 'alt_text_ru', 'alt_text_en', 'is_primary', 'order']


class ProductAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Product model"""
    category_name = serializers.CharField(source='category.name_uz', read_only=True)
    tags_list = serializers.StringRelatedField(source='tags', many=True, read_only=True)
    images = ProductImageAdminSerializer(many=True, read_only=True)
    is_on_sale = serializers.ReadOnlyField()
    final_price = serializers.ReadOnlyField()
    display_name = serializers.ReadOnlyField()
    orders_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name_uz', 'name_ru', 'name_en', 'slug', 'description_uz',
            'description_ru', 'description_en', 'price', 'sale_price', 'stock',
            'category', 'category_name', 'tags', 'tags_list', 'is_active',
            'is_featured', 'suggested_products', 'created_at', 'updated_at',
            'deleted_at', 'images', 'is_on_sale', 'final_price', 'display_name',
            'orders_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_orders_count(self, obj):
        """Get how many times this product was ordered"""
        return getattr(obj, 'orders_count', 0)


class ProductCategoryAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Product Category"""
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductCategory
        fields = [
            'id', 'name_uz', 'name_ru', 'name_en', 'description_uz',
            'description_ru', 'description_en', 'created_at', 'updated_at',
            'products_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_products_count(self, obj):
        """Get products count in this category"""
        return obj.products.filter(is_active=True, deleted_at__isnull=True).count()


class ProductTagAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Product Tag"""
    products_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductTag
        fields = [
            'id', 'name_uz', 'name_ru', 'name_en', 'created_at', 'updated_at',
            'products_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_products_count(self, obj):
        """Get products count with this tag"""
        return obj.products.filter(is_active=True, deleted_at__isnull=True).count()


class OrderItemAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Order Items"""
    product_name = serializers.CharField(source='product.name_uz', read_only=True)
    product_slug = serializers.CharField(source='product.slug', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_name', 'product_slug', 'quantity',
            'unit_price', 'total_price'
        ]


class OrderAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Order model"""
    customer_name = serializers.CharField(read_only=True)
    items = OrderItemAdminSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_number', 'user', 'customer_name', 'customer_email',
            'customer_phone', 'shipping_address', 'billing_address', 'status',
            'status_display', 'payment_method', 'payment_method_display',
            'is_paid', 'subtotal', 'shipping_cost', 'tax_amount', 'discount_amount',
            'total_amount', 'notes', 'created_at', 'updated_at', 'items',
            'items_count'
        ]
        read_only_fields = ['id', 'order_number', 'created_at', 'updated_at']
    
    def get_items_count(self, obj):
        """Get total items count in order"""
        return obj.items.count()


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
        from django.utils import timezone
        diff = timezone.now() - obj.created_at
        return diff.days


class FranchiseApplicationAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Franchise Applications"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    created_at_formatted = serializers.SerializerMethodField()
    investment_amount_formatted = serializers.SerializerMethodField()
    
    class Meta:
        model = FranchiseApplication
        fields = [
            'id', 'full_name', 'phone', 'email', 'city', 'investment_amount',
            'investment_amount_formatted', 'experience', 'business_plan',
            'preferred_location', 'timeline', 'status', 'status_display',
            'admin_notes', 'created_at', 'created_at_formatted', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_created_at_formatted(self, obj):
        """Get formatted creation date"""
        return obj.created_at.strftime('%d.%m.%Y %H:%M')
    
    def get_investment_amount_formatted(self, obj):
        """Get formatted investment amount"""
        return f"${obj.investment_amount:,.2f}"


class CartItemAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Cart Items"""
    product_name = serializers.CharField(source='product.name_uz', read_only=True)
    product_price = serializers.DecimalField(source='product.final_price', max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity', 'added_at']


class CartAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Cart model"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    items = CartItemAdminSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Cart
        fields = [
            'id', 'user', 'user_name', 'created_at', 'updated_at', 
            'items', 'items_count', 'total_amount'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_items_count(self, obj):
        """Get total items count in cart"""
        return obj.items.count()
    
    def get_total_amount(self, obj):
        """Calculate total cart amount"""
        total = Decimal('0.00')
        for item in obj.items.all():
            total += item.product.final_price * item.quantity
        return total


class FavoriteAdminSerializer(serializers.ModelSerializer):
    """Admin serializer for Favorites"""
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    product_name = serializers.CharField(source='product.name_uz', read_only=True)
    product_price = serializers.DecimalField(source='product.final_price', max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = Favorite
        fields = [
            'id', 'user', 'user_name', 'product', 'product_name', 
            'product_price', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


# Stats Serializers
class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    users = serializers.DictField()
    products = serializers.DictField()
    orders = serializers.DictField()
    courses = serializers.DictField()
    franchises = serializers.DictField()
    revenue = serializers.DictField()


class ApplicationStatsSerializer(serializers.Serializer):
    """Serializer for applications statistics"""
    course_applications = serializers.DictField()
    franchise_applications = serializers.DictField()
