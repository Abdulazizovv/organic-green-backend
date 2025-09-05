"""
Course Application URLs
"""
from django.urls import path
from . import views

app_name = 'course'

urlpatterns = [
    # PUBLIC API ENDPOINTS
    
    # Submit course application
    path('applications/', views.ApplicationCreateView.as_view(), name='application-create'),
    
    # Check application status by application number
    path('applications/check/<str:application_number>/', views.application_check_view, name='application-check'),
    
    # Get available courses list
    path('list/', views.course_list_view, name='course-list'),
    
    
    # ADMIN API ENDPOINTS
    
    # List all applications with filtering
    path('admin/applications/', views.ApplicationListView.as_view(), name='admin-application-list'),
    
    # Get/Update specific application
    path('admin/applications/<uuid:pk>/', views.ApplicationDetailView.as_view(), name='admin-application-detail'),
    
    # Application statistics
    path('admin/statistics/', views.application_statistics_view, name='admin-statistics'),
    
    # Bulk update application status
    path('admin/applications/bulk-update/', views.bulk_update_status_view, name='admin-bulk-update'),
    
    # Export applications
    path('admin/applications/export/', views.export_applications_view, name='admin-export'),
]
