"""
Admin configuration for Order app
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    """Inline admin for OrderItem"""
    model = OrderItem
    extra = 0
    readonly_fields = [
        'product', 'product_name', 'quantity', 
        'unit_price', 'total_price', 'is_sale_price'
    ]
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        """Prevent adding new items to existing orders"""
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Admin configuration for Order model"""
    
    list_display = [
        'order_number', 'customer_info', 'status_badge', 
        'payment_method', 'total_price', 'total_items', 'created_at'
    ]
    list_filter = [
        'status', 'payment_method', 'created_at', 'updated_at'
    ]
    search_fields = [
        'order_number', 'full_name', 'contact_phone', 
        'user__username', 'user__email'
    ]
    readonly_fields = [
        'id', 'order_number', 'user', 'session_key', 'subtotal',
        'discount_total', 'total_price', 'total_items', 'created_at', 'updated_at'
    ]
    fieldsets = (
        ('Order Information', {
            'fields': (
                'id', 'order_number', 'status', 'payment_method', 'created_at', 'updated_at'
            )
        }),
        ('Customer Information', {
            'fields': (
                'user', 'session_key', 'full_name', 'contact_phone', 
                'delivery_address', 'notes'
            )
        }),
        ('Financial Details', {
            'fields': (
                'subtotal', 'discount_total', 'total_price', 'total_items'
            )
        }),
    )
    inlines = [OrderItemInline]
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    
    def customer_info(self, obj):
        """Display customer information"""
        if obj.user:
            user_link = reverse('admin:accounts_user_change', args=[obj.user.pk])
            return format_html(
                '<a href="{}">{}</a><br><small>{}</small>',
                user_link, obj.user.username, obj.full_name
            )
        return format_html(
            '<em>Anonymous</em><br><small>{}</small>',
            obj.full_name
        )
    customer_info.short_description = 'Customer'
    customer_info.admin_order_field = 'user__username'
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'pending': '#ffc107',     # yellow
            'paid': '#28a745',        # green
            'processing': '#17a2b8',  # blue
            'shipped': '#6f42c1',     # purple
            'delivered': '#28a745',   # green
            'canceled': '#dc3545',    # red
        }
        color = colors.get(obj.status, '#6c757d')  # default gray
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    status_badge.admin_order_field = 'status'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('user')
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of orders (for audit purposes)"""
        return False


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    """Admin configuration for OrderItem model"""
    
    list_display = [
        'order_link', 'product_name', 'quantity', 
        'unit_price', 'total_price', 'is_sale_price'
    ]
    list_filter = ['is_sale_price', 'order__status', 'order__created_at']
    search_fields = [
        'product_name', 'order__order_number', 'product__name_uz'
    ]
    readonly_fields = [
        'id', 'order', 'product', 'product_name', 'quantity',
        'unit_price', 'total_price', 'is_sale_price'
    ]
    ordering = ['-order__created_at']
    
    def order_link(self, obj):
        """Display link to order"""
        order_link = reverse('admin:order_order_change', args=[obj.order.pk])
        return format_html(
            '<a href="{}">{}</a>',
            order_link, obj.order.order_number
        )
    order_link.short_description = 'Order'
    order_link.admin_order_field = 'order__order_number'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        return super().get_queryset(request).select_related('order', 'product')
    
    def has_add_permission(self, request):
        """Prevent adding order items directly"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of order items"""
        return False
