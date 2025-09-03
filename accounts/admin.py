"""
Admin configuration for custom User model
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin with additional fields
    """
    list_display = [
        'username', 'avatar_preview', 'full_name', 'email', 
        'phone', 'is_verified', 'is_staff', 'date_joined'
    ]
    list_filter = [
        'is_staff', 'is_superuser', 'is_active', 'is_verified', 'date_joined'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering = ['-date_joined']
    
    # Add custom fields to the form
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Profile Information', {
            'fields': ('avatar', 'phone', 'is_verified')
        }),
    )
    
    # Add custom fields to add form
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Profile Information', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')
        }),
    )
    
    def avatar_preview(self, obj):
        """Display avatar preview in list"""
        if obj.avatar:
            return format_html(
                '<img src="{}" width="30" height="30" style="border-radius: 50%;" />',
                obj.avatar.url
            )
        return format_html(
            '<div style="width: 30px; height: 30px; background-color: #ddd; '
            'border-radius: 50%; display: flex; align-items: center; '
            'justify-content: center; font-size: 12px;">No</div>'
        )
    avatar_preview.short_description = 'Avatar'
    
    def full_name(self, obj):
        """Display full name"""
        return obj.full_name
    full_name.short_description = 'Full Name'
    full_name.admin_order_field = 'first_name'
