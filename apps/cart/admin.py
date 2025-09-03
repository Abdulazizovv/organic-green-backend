from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin configuration for Cart model"""
    
    list_display = [
        'id', 'get_owner', 'total_items', 'get_total_price', 
        'created_at', 'updated_at'
    ]
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'session_key']
    readonly_fields = ['id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    def get_owner(self, obj):
        """Display cart owner information"""
        if obj.user:
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                obj.user.username,
                obj.user.email or 'No email'
            )
        session_display = obj.session_key[:12] + '...' if obj.session_key and len(obj.session_key) > 12 else obj.session_key or 'No session'
        return format_html(
            '<em>Anonymous</em><br><small>{}</small>',
            session_display
        )
    get_owner.short_description = "Owner"
    get_owner.admin_order_field = 'user__username'
    
    def get_total_price(self, obj):
        """Display formatted total price"""
        total = obj.total_price
        if total > 0:
            formatted_price = f"{total:.2f}"
            return format_html(
                '<strong>{} UZS</strong>',
                formatted_price
            )
        return "-"
    get_total_price.short_description = "Total Price"
    get_total_price.admin_order_field = 'total_price'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('user')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin configuration for CartItem model"""
    
    list_display = [
        'id', 'get_cart_link', 'get_product_info', 'quantity', 
        'get_unit_price', 'get_total_price', 'added_at'
    ]
    list_filter = ['added_at', 'updated_at', 'product__category']
    search_fields = [
        'cart__user__username', 
        'product__name_uz', 
        'product__name_ru', 
        'product__name_en'
    ]
    readonly_fields = ['id', 'added_at', 'updated_at']
    raw_id_fields = ['cart', 'product']
    date_hierarchy = 'added_at'
    ordering = ['-added_at']
    
    def get_cart_link(self, obj):
        """Display link to cart"""
        if obj.cart.user:
            cart_display = obj.cart.user.username
        else:
            session_key = obj.cart.session_key
            cart_display = f"Anonymous ({session_key[:8]}...)" if session_key else "Anonymous"
        
        url = reverse('admin:cart_cart_change', args=[obj.cart.pk])
        return format_html('<a href="{}">{}</a>', url, cart_display)
    get_cart_link.short_description = "Cart"
    get_cart_link.admin_order_field = 'cart__user__username'
    
    def get_product_info(self, obj):
        """Display product information with link"""
        if obj.product:
            url = reverse('admin:products_product_change', args=[obj.product.pk])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                obj.product.name_uz
            )
        return "Product deleted"
    get_product_info.short_description = "Product"
    get_product_info.admin_order_field = 'product__name_uz'
    
    def get_unit_price(self, obj):
        """Display formatted unit price"""
        unit_price = obj.get_unit_price()
        formatted_price = f"{unit_price:.2f}"
        return format_html('<span>{} UZS</span>', formatted_price)
    get_unit_price.short_description = "Unit Price"
    
    def get_total_price(self, obj):
        """Display formatted total price"""
        total_price = obj.get_total_price()
        formatted_price = f"{total_price:.2f}"
        return format_html('<span>{} UZS</span>', formatted_price)
    get_total_price.short_description = "Total Price"
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related(
            'cart__user', 'product', 'product__category'
        )
