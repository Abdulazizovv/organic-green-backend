"""
Admin configuration for Favorites
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.favorites.models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Admin interface for managing user favorites
    """
    list_display = [
        'id', 'user_link', 'product_link', 'product_price', 
        'product_category', 'created_at'
    ]
    list_filter = [
        'created_at', 'product__category', 'product__is_featured',
        'product__is_active'
    ]
    search_fields = [
        'user__username', 'user__email', 'product__name_uz',
        'product__name_ru', 'product__name_en'
    ]
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    # Optimize database queries
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'user', 'product', 'product__category'
        ).prefetch_related('product__images')
    
    def user_link(self, obj):
        """Display user with link to user admin"""
        return format_html(
            '<a href="/admin/auth/user/{}/change/">{}</a>',
            obj.user.id,
            obj.user.username
        )
    user_link.short_description = 'Foydalanuvchi'
    user_link.admin_order_field = 'user__username'
    
    def product_link(self, obj):
        """Display product with link to product admin"""
        return format_html(
            '<a href="/admin/products/product/{}/change/">{}</a>',
            obj.product.id,
            obj.product.name_uz
        )
    product_link.short_description = 'Mahsulot'
    product_link.admin_order_field = 'product__name_uz'
    
    def product_price(self, obj):
        """Display product price"""
        if obj.product.sale_price:
            return format_html(
                '<span style="text-decoration: line-through;">{}</span> '
                '<span style="color: red; font-weight: bold;">{}</span>',
                obj.product.price,
                obj.product.sale_price
            )
        return obj.product.price
    product_price.short_description = 'Narx'
    product_price.admin_order_field = 'product__price'
    
    def product_category(self, obj):
        """Display product category"""
        return obj.product.category.name_uz if obj.product.category else '-'
    product_category.short_description = 'Kategoriya'
    product_category.admin_order_field = 'product__category__name_uz'
    
    # Custom actions
    actions = ['remove_selected_favorites']
    
    def remove_selected_favorites(self, request, queryset):
        """Remove selected favorites"""
        count = queryset.count()
        queryset.delete()
        self.message_user(
            request,
            f'{count} ta sevimli mahsulot o\'chirildi.'
        )
    remove_selected_favorites.short_description = "Tanlangan sevimlilarni o'chirish"
