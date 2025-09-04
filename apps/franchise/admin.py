"""
Franchise application admin configuration
"""
from django.contrib import admin
from apps.franchise.models import FranchiseApplication


@admin.register(FranchiseApplication)
class FranchiseApplicationAdmin(admin.ModelAdmin):
    """
    Admin interface for franchise applications
    """
    list_display = [
        'id',
        'full_name',
        'phone',
        'city',
        'formatted_investment_amount',
        'status',
        'created_at',
    ]
    list_filter = [
        'status',
        'city',
        'created_at',
        'updated_at',
    ]
    search_fields = [
        'full_name',
        'phone',
        'email',
        'city',
    ]
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'formatted_investment_amount',
    ]
    
    fieldsets = (
        ('Application Information', {
            'fields': (
                'id',
                'full_name',
                'phone',
                'email',
                'city',
            )
        }),
        ('Investment Details', {
            'fields': (
                'investment_amount',
                'formatted_investment_amount',
            )
        }),
        ('Additional Information', {
            'fields': (
                'experience',
                'message',
            ),
            'classes': ('collapse',),
        }),
        ('Status & Timestamps', {
            'fields': (
                'status',
                'created_at',
                'updated_at',
            )
        }),
    )
    
    ordering = ['-created_at']
    list_per_page = 25
    
    actions = ['mark_as_reviewed', 'mark_as_approved', 'mark_as_rejected']
    
    def mark_as_reviewed(self, request, queryset):
        """Mark selected applications as reviewed"""
        updated = queryset.update(status='reviewed')
        self.message_user(request, f'{updated} applications marked as reviewed.')
    mark_as_reviewed.short_description = 'Mark selected applications as reviewed'
    
    def mark_as_approved(self, request, queryset):
        """Mark selected applications as approved"""
        updated = queryset.update(status='approved')
        self.message_user(request, f'{updated} applications marked as approved.')
    mark_as_approved.short_description = 'Mark selected applications as approved'
    
    def mark_as_rejected(self, request, queryset):
        """Mark selected applications as rejected"""
        updated = queryset.update(status='rejected')
        self.message_user(request, f'{updated} applications marked as rejected.')
    mark_as_rejected.short_description = 'Mark selected applications as rejected'
