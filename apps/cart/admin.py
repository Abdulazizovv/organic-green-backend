from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from .models import Cart, CartItem, CartHistory


class CartItemInline(admin.TabularInline):
    """Inline for cart items"""
    model = CartItem
    extra = 0
    readonly_fields = ('added_at', 'updated_at', 'get_total_price')
    fields = ('product', 'quantity', 'get_total_price', 'added_at')
    
    def get_total_price(self, obj):
        if obj.pk:
            return f"{obj.get_total_price():,.2f} so'm"
        return "-"
    get_total_price.short_description = "Jami narx"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    """Admin for Cart model"""
    list_display = [
        'id', 'get_owner', 'items_count', 'total_items', 'get_total_price', 
        'created_at', 'updated_at'
    ]
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email', 'session_key']
    readonly_fields = ['id', 'created_at', 'updated_at', 'get_cart_summary']
    inlines = [CartItemInline]
    date_hierarchy = 'created_at'
    
    def get_owner(self, obj):
        if obj.user:
            return format_html(
                '<strong>{}</strong><br><small>{}</small>',
                obj.user.username,
                obj.user.email
            )
        return format_html(
            '<em>Anonim</em><br><small>{}</small>',
            obj.session_key[:8] + '...' if obj.session_key else 'No session'
        )
    get_owner.short_description = "Egasi"
    get_owner.admin_order_field = 'user__username'
    
    def get_total_price(self, obj):
        total = obj.total_price
        if total > 0:
            return format_html(
                '<strong>{:,.2f} so\'m</strong>',
                total
            )
        return "-"
    get_total_price.short_description = "Jami narx"
    
    def get_cart_summary(self, obj):
        if obj.pk:
            items = obj.items.all()
            if items:
                summary = "<h3>Savat tarkibi:</h3><ul>"
                for item in items:
                    summary += f"<li>{item.product.name_uz} x {item.quantity} = {item.get_total_price():,.2f} so'm</li>"
                summary += f"</ul><h4>Jami: {obj.total_price:,.2f} so'm</h4>"
                return format_html(summary)
        return "Savat bo'sh"
    get_cart_summary.short_description = "Savat xulosasi"


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    """Admin for CartItem model"""
    list_display = [
        'id', 'get_cart_owner', 'product', 'quantity', 'get_unit_price', 
        'get_total_price', 'added_at', 'updated_at'
    ]
    list_filter = ['added_at', 'updated_at', 'product__category']
    search_fields = [
        'cart__user__username', 'product__name_uz', 'product__name_ru', 
        'product__name_en'
    ]
    readonly_fields = ['id', 'added_at', 'updated_at', 'get_total_price']
    raw_id_fields = ['cart', 'product']
    date_hierarchy = 'added_at'
    
    def get_cart_owner(self, obj):
        if obj.cart.user:
            return obj.cart.user.username
        return "Anonim"
    get_cart_owner.short_description = "Savat egasi"
    get_cart_owner.admin_order_field = 'cart__user__username'
    
    def get_unit_price(self, obj):
        return f"{obj.get_unit_price():,.2f} so'm"
    get_unit_price.short_description = "Birlik narxi"
    
    def get_total_price(self, obj):
        return f"{obj.get_total_price():,.2f} so'm"
    get_total_price.short_description = "Jami narx"


@admin.register(CartHistory)
class CartHistoryAdmin(admin.ModelAdmin):
    """Admin for CartHistory model"""
    list_display = [
        'id', 'get_cart_owner', 'action', 'product', 'quantity', 
        'get_price', 'timestamp'
    ]
    list_filter = ['action', 'timestamp']
    search_fields = [
        'cart__user__username', 'product__name_uz', 'action'
    ]
    readonly_fields = [
        'id', 'cart', 'product', 'action', 'quantity', 'price', 
        'timestamp', 'user_agent', 'ip_address'
    ]
    date_hierarchy = 'timestamp'
    
    def get_cart_owner(self, obj):
        if obj.cart.user:
            return obj.cart.user.username
        return "Anonim"
    get_cart_owner.short_description = "Savat egasi"
    get_cart_owner.admin_order_field = 'cart__user__username'
    
    def get_price(self, obj):
        if obj.price:
            return f"{obj.price:,.2f} so'm"
        return "-"
    get_price.short_description = "Narx"
    
    def has_add_permission(self, request):
        return False  # History should not be manually added
    
    def has_change_permission(self, request, obj=None):
        return False  # History should not be modified
