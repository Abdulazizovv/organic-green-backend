"""
Course Application Admin - Senior Developer Implementation
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse, path
from django.shortcuts import render, redirect
from django.contrib.admin import SimpleListFilter
from django.db.models import Count, Q
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
import csv
from datetime import datetime, timedelta

from .models import Application


class ProcessedFilter(SimpleListFilter):
    """Custom filter for processed applications"""
    title = 'Qayta ishlangan holati'
    parameter_name = 'processed_status'

    def lookups(self, request, model_admin):
        return (
            ('processed', '✅ Qayta ishlangan'),
            ('pending', '⏳ Kutilmoqda'),
            ('today', '🆕 Bugungi'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'processed':
            return queryset.filter(processed=True)
        elif self.value() == 'pending':
            return queryset.filter(processed=False)
        elif self.value() == 'today':
            return queryset.filter(created_at__date=timezone.now().date())
        return queryset


class CourseFilter(SimpleListFilter):
    """Filter by course name"""
    title = 'Kurs nomi'
    parameter_name = 'course_filter'

    def lookups(self, request, model_admin):
        courses = Application.objects.values_list('course_name', flat=True).distinct()
        return [(course, course) for course in courses if course]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(course_name=self.value())
        return queryset


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    """
    Enhanced Course Application Admin
    """
    list_display = [
        'application_info', 'contact_details', 'course_info', 
        'status_display', 'application_date', 'admin_actions'
    ]
    list_filter = [
        ProcessedFilter, CourseFilter, 'created_at'
    ]
    search_fields = [
        'application_number', 'full_name', 'email', 'phone_number', 
        'course_name', 'message'
    ]
    readonly_fields = [
        'id', 'application_number', 'created_at', 'application_summary'
    ]
    list_per_page = 25
    ordering = ['-created_at']
    date_hierarchy = 'created_at'
    actions = ['mark_as_processed', 'mark_as_pending', 'export_applications']
    
    fieldsets = (
        ('📋 Ariza ma\'lumotlari', {
            'fields': (
                'application_number', 'application_summary'
            ),
            'classes': ('wide',)
        }),
        ('👤 Shaxsiy ma\'lumotlar', {
            'fields': (
                ('full_name', 'email'),
                'phone_number',
            ),
            'classes': ('wide',)
        }),
        ('📚 Kurs ma\'lumotlari', {
            'fields': (
                'course_name', 'message'
            ),
            'classes': ('wide',)
        }),
        ('⚙️ Holati', {
            'fields': ('processed',),
            'classes': ('wide',)
        }),
        ('📊 Meta ma\'lumotlar', {
            'fields': (
                'id', 'created_at'
            ),
            'classes': ('collapse',)
        }),
    )
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('statistics/', self.admin_site.admin_view(self.statistics_view), name='application_statistics'),
            path('export-csv/', self.admin_site.admin_view(self.export_csv_view), name='application_export_csv'),
        ]
        return custom_urls + urls
    
    def application_info(self, obj):
        """Enhanced application information display"""
        status_color = '#28a745' if obj.processed else '#ffc107'
        status_icon = '✅' if obj.processed else '⏳'
        
        return format_html(
            '''
            <div style="min-width: 180px;">
                <div style="font-weight: bold; font-size: 14px; margin-bottom: 5px;">
                    📄 {}
                </div>
                <div style="color: {}; font-weight: bold; font-size: 12px;">
                    {} {}
                </div>
            </div>
            ''',
            obj.application_number,
            status_color,
            status_icon, 'Qayta ishlangan' if obj.processed else 'Kutilmoqda'
        )
    application_info.short_description = '📄 Ariza ma\'lumotlari'
    application_info.admin_order_field = 'application_number'
    
    def contact_details(self, obj):
        """Enhanced contact information display"""
        phone_clean = obj.phone_number.replace('+', '').replace(' ', '').replace('-', '')
        
        return format_html(
            '''
            <div style="min-width: 200px;">
                <div style="font-weight: bold; margin-bottom: 3px;">
                    👤 {}
                </div>
                <div style="margin-bottom: 3px;">
                    <a href="tel:{}" style="color: #28a745; text-decoration: none;">
                        📞 {}
                    </a>
                </div>
                <div>
                    <a href="mailto:{}" style="color: #17a2b8; text-decoration: none; font-size: 12px;">
                        ✉️ {}
                    </a>
                </div>
            </div>
            ''',
            obj.full_name,
            phone_clean, obj.phone_number,
            obj.email, obj.email[:30] + ('...' if len(obj.email) > 30 else '')
        )
    contact_details.short_description = '👤 Aloqa ma\'lumotlari'
    contact_details.admin_order_field = 'full_name'
    
    def course_info(self, obj):
        """Display course information"""
        message_preview = obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
        
        return format_html(
            '''
            <div style="min-width: 150px;">
                <div style="font-weight: bold; color: #007cba; margin-bottom: 5px;">
                    📚 {}
                </div>
                {}
            </div>
            ''',
            obj.course_name,
            f'<div style="color: #666; font-size: 12px; font-style: italic;">"{message_preview}"</div>' if obj.message else '<div style="color: #999; font-size: 12px;">Xabar yo\'q</div>'
        )
    course_info.short_description = '📚 Kurs ma\'lumotlari'
    course_info.admin_order_field = 'course_name'
    
    def status_display(self, obj):
        """Enhanced status display"""
        if obj.processed:
            config = {'color': '#28a745', 'icon': '✅', 'bg': '#d1eddb', 'text': 'QAYTA ISHLANGAN'}
        else:
            config = {'color': '#ffc107', 'icon': '⏳', 'bg': '#fff3cd', 'text': 'KUTILMOQDA'}
        
        return format_html(
            '''
            <div style="text-align: center; min-width: 120px;">
                <div style="background: {}; color: {}; padding: 8px 12px; border-radius: 15px; font-weight: bold; font-size: 11px;">
                    {} {}
                </div>
            </div>
            ''',
            config['bg'], config['color'],
            config['icon'], config['text']
        )
    status_display.short_description = '📊 Holati'
    status_display.admin_order_field = 'processed'
    
    def application_date(self, obj):
        """Display application date with relative time"""
        now = timezone.now()
        diff = now - obj.created_at
        
        if diff.days == 0:
            if diff.seconds < 3600:
                time_text = f"{diff.seconds // 60} daqiqa oldin"
            else:
                time_text = f"{diff.seconds // 3600} soat oldin"
        elif diff.days == 1:
            time_text = "Kecha"
        else:
            time_text = f"{diff.days} kun oldin"
        
        return format_html(
            '''
            <div style="min-width: 100px; text-align: center;">
                <div style="font-weight: bold; margin-bottom: 2px;">
                    {}
                </div>
                <div style="color: #666; font-size: 11px;">
                    {}
                </div>
                <div style="color: #999; font-size: 10px;">
                    {}
                </div>
            </div>
            ''',
            obj.created_at.strftime('%d.%m.%Y'),
            obj.created_at.strftime('%H:%M'),
            time_text
        )
    application_date.short_description = '📅 Ariza sanasi'
    application_date.admin_order_field = 'created_at'
    
    def admin_actions(self, obj):
        """Quick action buttons"""
        buttons = []
        
        # Status toggle button
        if obj.processed:
            buttons.append(f'''
                <button onclick="toggleStatus('{obj.pk}', false)" 
                        style="background: #ffc107; color: #212529; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; margin: 1px; font-size: 10px;">
                    ↩️ Qaytarish
                </button>
            ''')
        else:
            buttons.append(f'''
                <button onclick="toggleStatus('{obj.pk}', true)" 
                        style="background: #28a745; color: white; border: none; padding: 4px 8px; border-radius: 4px; cursor: pointer; margin: 1px; font-size: 10px;">
                    ✅ Qayta ishlash
                </button>
            ''')
        
        # Contact buttons
        phone_clean = obj.phone_number.replace('+', '').replace(' ', '').replace('-', '')
        buttons.extend([
            f'''<a href="tel:{phone_clean}" 
                   style="background: #17a2b8; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 10px; margin: 1px;">
                📞 Qo'ng'iroq
                </a>''',
            f'''<a href="mailto:{obj.email}" 
                   style="background: #6f42c1; color: white; padding: 4px 8px; border-radius: 4px; text-decoration: none; font-size: 10px; margin: 1px;">
                ✉️ Email
                </a>'''
        ])
        
        return format_html(''.join(buttons))
    admin_actions.short_description = '⚡ Amallar'
    
    def application_summary(self, obj):
        """Display application summary"""
        if not obj.pk:
            return "Arizani saqlang"
        
        summary_html = f'''
        <div style="background: #f8f9fa; padding: 15px; border-radius: 8px; margin: 10px 0;">
            <h4 style="margin-top: 0; color: #495057;">📊 Ariza xulosasi</h4>
            <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px;">
                <div>
                    <strong>Ariza raqami:</strong><br>
                    <span style="color: #007cba; font-family: monospace;">{obj.application_number}</span>
                </div>
                <div>
                    <strong>Yuborilgan vaqt:</strong><br>
                    {obj.created_at.strftime('%d.%m.%Y, %H:%M')}
                </div>
                <div>
                    <strong>Holati:</strong><br>
                    <span style="color: {'#28a745' if obj.processed else '#ffc107'};">
                        {'✅ Qayta ishlangan' if obj.processed else '⏳ Kutilmoqda'}
                    </span>
                </div>
                <div>
                    <strong>Kurs:</strong><br>
                    {obj.course_name}
                </div>
            </div>
        </div>
        '''
        return format_html(summary_html)
    application_summary.short_description = '📊 Ariza xulosasi'
    
    # Custom Actions
    def mark_as_processed(self, request, queryset):
        count = queryset.update(processed=True)
        self.message_user(request, f'{count} ta ariza qayta ishlangan deb belgilandi.', messages.SUCCESS)
    mark_as_processed.short_description = "✅ Tanlangan arizalarni qayta ishlangan deb belgilash"
    
    def mark_as_pending(self, request, queryset):
        count = queryset.update(processed=False)
        self.message_user(request, f'{count} ta ariza kutilmoqda deb belgilandi.', messages.SUCCESS)
    mark_as_pending.short_description = "⏳ Tanlangan arizalarni kutilmoqda deb belgilash"
    
    def export_applications(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="kurs_arizalari.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Ariza raqami', 'To\'liq ism', 'Email', 'Telefon', 
            'Kurs nomi', 'Xabar', 'Holati', 'Yuborilgan sana'
        ])
        
        for app in queryset:
            writer.writerow([
                app.application_number, app.full_name, app.email, app.phone_number,
                app.course_name, app.message, 
                'Qayta ishlangan' if app.processed else 'Kutilmoqda',
                app.created_at.strftime('%d.%m.%Y %H:%M')
            ])
        
        return response
    export_applications.short_description = "📄 Tanlangan arizalarni CSV ga eksport qilish"
    
    # Custom Views
    def statistics_view(self, request):
        """Statistics dashboard"""
        today = timezone.now().date()
        
        stats = {
            'total': Application.objects.count(),
            'processed': Application.objects.filter(processed=True).count(),
            'pending': Application.objects.filter(processed=False).count(),
            'today': Application.objects.filter(created_at__date=today).count(),
        }
        
        # Popular courses
        popular_courses = Application.objects.values('course_name').annotate(
            count=Count('id')
        ).order_by('-count')[:5]
        
        context = {
            'title': 'Arizalar statistikasi',
            'stats': stats,
            'popular_courses': popular_courses,
        }
        
        return render(request, 'admin/application_statistics.html', context)
    
    def export_csv_view(self, request):
        """Export all applications to CSV"""
        return self.export_applications(request, Application.objects.all())
    
    def changelist_view(self, request, extra_context=None):
        """Add statistics to changelist"""
        extra_context = extra_context or {}
        
        # Quick stats for the changelist
        extra_context['quick_stats'] = {
            'total': Application.objects.count(),
            'pending': Application.objects.filter(processed=False).count(),
            'today': Application.objects.filter(created_at__date=timezone.now().date()).count(),
        }
        
        return super().changelist_view(request, extra_context)

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
        js = ('admin/js/custom_admin.js',)


# Enhanced Admin Site Customization
admin.site.site_header = "🎓 Organic Green - Kurs Arizalari Boshqaruvi"
admin.site.site_title = "Kurs Arizalari Admin"
admin.site.index_title = "Kurs Arizalari Boshqaruv Tizimi"
