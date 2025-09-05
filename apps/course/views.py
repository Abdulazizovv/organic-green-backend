"""
Course Application Views
"""
from django.db.models import Count
from django.utils import timezone
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import Application
from .serializers import (
    ApplicationCreateSerializer,
    ApplicationListSerializer,
    ApplicationDetailSerializer,
    ApplicationUpdateSerializer,
    ApplicationStatsSerializer
)


# Custom throttles
class ApplicationSubmissionThrottle(AnonRateThrottle):
    scope = 'course_application'


# PUBLIC API VIEWS

class ApplicationCreateView(generics.CreateAPIView):
    """
    Public API: Submit course application
    
    POST /api/course/applications/
    """
    serializer_class = ApplicationCreateSerializer
    throttle_classes = [ApplicationSubmissionThrottle]
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Create application with custom response"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save the application
        application = serializer.save()
        
        # Custom response with application number
        response_data = {
            'success': True,
            'message': 'Arizangiz muvaffaqiyatli yuborildi!',
            'application_number': application.application_number,
            'data': {
                'id': str(application.id),
                'application_number': application.application_number,
                'full_name': application.full_name,
                'course_name': application.course_name,
                'created_at': application.created_at.isoformat(),
                'status': 'Kutilmoqda'
            }
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)


# ADMIN API VIEWS

class ApplicationListView(generics.ListAPIView):
    """
    Admin API: List all applications with filtering
    
    GET /api/course/admin/applications/
    """
    permission_classes = [IsAdminUser]
    serializer_class = ApplicationListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['processed', 'course_name']
    search_fields = ['full_name', 'email', 'phone_number', 'course_name', 'application_number']
    ordering_fields = ['created_at', 'full_name', 'course_name']
    ordering = ['-created_at']
    
    def get_queryset(self):
        return Application.objects.all()


class ApplicationDetailView(generics.RetrieveUpdateAPIView):
    """
    Admin API: Get and update application details
    
    GET/PUT/PATCH /api/course/admin/applications/{id}/
    """
    permission_classes = [IsAdminUser]
    lookup_field = 'pk'
    
    def get_queryset(self):
        return Application.objects.all()
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ApplicationUpdateSerializer
        return ApplicationDetailSerializer


@api_view(['GET'])
@permission_classes([IsAdminUser])
def application_statistics_view(request):
    """
    Admin API: Get application statistics
    
    GET /api/course/admin/statistics/
    """
    today = timezone.now().date()
    
    # Basic statistics
    total_applications = Application.objects.count()
    processed_applications = Application.objects.filter(processed=True).count()
    pending_applications = Application.objects.filter(processed=False).count()
    today_applications = Application.objects.filter(created_at__date=today).count()
    
    # Popular courses
    popular_courses = list(
        Application.objects.values('course_name')
        .annotate(count=Count('id'))
        .order_by('-count')[:5]
    )
    
    # Recent applications
    recent_applications = Application.objects.order_by('-created_at')[:10]
    recent_serializer = ApplicationListSerializer(recent_applications, many=True)
    
    data = {
        'total_applications': total_applications,
        'processed_applications': processed_applications,
        'pending_applications': pending_applications,
        'today_applications': today_applications,
        'popular_courses': popular_courses,
        'recent_applications': recent_serializer.data
    }
    
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def bulk_update_status_view(request):
    """
    Admin API: Bulk update application status
    
    POST /api/course/admin/applications/bulk-update/
    Body: {
        "application_ids": ["uuid1", "uuid2", ...],
        "processed": true/false
    }
    """
    application_ids = request.data.get('application_ids', [])
    processed_status = request.data.get('processed')
    
    if not application_ids:
        return Response(
            {'error': 'application_ids is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if processed_status is None:
        return Response(
            {'error': 'processed status is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update applications
    updated_count = Application.objects.filter(
        id__in=application_ids
    ).update(processed=processed_status)
    
    status_text = "qayta ishlangan" if processed_status else "kutilmoqda"
    
    return Response({
        'success': True,
        'message': f'{updated_count} ta ariza {status_text} deb belgilandi',
        'updated_count': updated_count
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def export_applications_view(request):
    """
    Admin API: Export applications as JSON
    
    GET /api/course/admin/applications/export/
    """
    # Get query parameters for filtering
    processed = request.GET.get('processed')
    course_name = request.GET.get('course_name')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Build queryset based on filters
    queryset = Application.objects.all()
    
    if processed is not None:
        processed_bool = processed.lower() in ['true', '1', 'yes']
        queryset = queryset.filter(processed=processed_bool)
    
    if course_name:
        queryset = queryset.filter(course_name__icontains=course_name)
    
    if date_from:
        try:
            from datetime import datetime
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d').date()
            queryset = queryset.filter(created_at__date__gte=date_from_obj)
        except ValueError:
            pass
    
    if date_to:
        try:
            from datetime import datetime
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d').date()
            queryset = queryset.filter(created_at__date__lte=date_to_obj)
        except ValueError:
            pass
    
    # Serialize data
    serializer = ApplicationDetailSerializer(queryset, many=True)
    
    return Response({
        'success': True,
        'count': len(serializer.data),
        'applications': serializer.data
    })


# UTILITY VIEWS

@api_view(['GET'])
def application_check_view(request, application_number):
    """
    Public API: Check application status by application number
    
    GET /api/course/applications/check/{application_number}/
    """
    try:
        application = Application.objects.get(application_number=application_number)
        serializer = ApplicationDetailSerializer(application)
        
        return Response({
            'success': True,
            'application': serializer.data
        })
    except Application.DoesNotExist:
        return Response(
            {
                'success': False,
                'error': 'Ariza topilmadi. Ariza raqamini tekshiring.'
            },
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
def course_list_view(request):
    """
    Public API: Get list of available courses
    
    GET /api/course/courses/
    """
    # Get unique course names from applications
    course_names = Application.objects.values_list('course_name', flat=True).distinct()
    
    # Get course statistics
    course_stats = []
    for course_name in course_names:
        applications_count = Application.objects.filter(course_name=course_name).count()
        course_stats.append({
            'name': course_name,
            'applications_count': applications_count
        })
    
    # Sort by popularity
    course_stats.sort(key=lambda x: x['applications_count'], reverse=True)
    
    return Response({
        'success': True,
        'courses': course_stats
    })
