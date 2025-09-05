"""
Admin API Views - Complete admin interface for all project entities
"""
from decimal import Decimal
from django.db.models import Sum, Count, Q, F
from django.utils import timezone
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from datetime import datetime, timedelta

# Models
from accounts.models import User
from apps.products.models import Product, ProductCategory, ProductTag, ProductImage
from apps.order.models import Order, OrderItem
from apps.course.models import Application as CourseApplication
from apps.franchise.models import FranchiseApplication
from apps.cart.models import Cart, CartItem
from apps.favorites.models import Favorite

# Serializers
from api.admin_serializers import (
    UserAdminSerializer,
    UserDetailAdminSerializer,
    ProductAdminSerializer,
    ProductDetailAdminSerializer,
    ProductCategoryAdminSerializer,
    ProductTagAdminSerializer,
    OrderAdminSerializer,
    OrderDetailAdminSerializer,
    OrderItemAdminSerializer,
    CourseApplicationAdminSerializer,
    FranchiseApplicationAdminSerializer,
    CartAdminSerializer,
    FavoriteAdminSerializer,
)


class BaseAdminViewSet(viewsets.ModelViewSet):
    """Base admin viewset with common configurations"""
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # ordering = ['-created_at']
    
    def perform_destroy(self, instance):
        """Soft delete implementation"""
        if hasattr(instance, 'deleted_at'):
            instance.deleted_at = timezone.now()
            instance.save()
        elif hasattr(instance, 'is_active'):
            instance.is_active = False
            instance.save()
        else:
            # Hard delete if no soft delete fields
            instance.delete()


class UserAdminViewSet(BaseAdminViewSet):
    """Admin CRUD for Users"""
    queryset = User.objects.all()
    serializer_class = UserAdminSerializer
    filterset_fields = ['is_active', 'is_staff', 'is_superuser', 'is_verified']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'phone']
    ordering_fields = ['date_joined', 'last_login', 'username', 'email']
    ordering = ['-date_joined']
    
    def get_serializer_class(self):
        """Use detail serializer for retrieve"""
        if self.action == 'retrieve':
            return UserDetailAdminSerializer
        return UserAdminSerializer
    
    def get_queryset(self):
        """Add annotations for better performance"""
        return User.objects.select_related().prefetch_related(
            'orders', 'favorites', 'cart'
        )
    
    @action(detail=False, methods=['get'])
    def activity(self, request):
        """User activity statistics"""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        active_today = User.objects.filter(last_login__date=today).count()
        active_week = User.objects.filter(last_login__gte=week_ago).count()
        active_month = User.objects.filter(last_login__gte=month_ago).count()
        
        return Response({
            'active_today': active_today,
            'active_week': active_week,
            'active_month': active_month,
            'total_users': User.objects.count(),
            'verified_users': User.objects.filter(is_verified=True).count(),
            'staff_users': User.objects.filter(is_staff=True).count(),
        })


class ProductAdminViewSet(BaseAdminViewSet):
    """Admin CRUD for Products"""
    queryset = Product.objects.all()
    serializer_class = ProductAdminSerializer
    filterset_fields = ['is_active', 'is_featured', 'category', 'tags']
    search_fields = ['name_uz', 'name_ru', 'name_en', 'slug']
    ordering_fields = ['created_at', 'updated_at', 'price', 'stock']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use detail serializer for retrieve"""
        if self.action == 'retrieve':
            return ProductDetailAdminSerializer
        return ProductAdminSerializer
    
    def get_queryset(self):
        """Include soft deleted products and add optimizations"""
        return Product.objects.select_related('category').prefetch_related(
            'tags', 'images',
        )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Product statistics"""
        total = Product.objects.count()
        active = Product.objects.filter(is_active=True, deleted_at__isnull=True).count()
        featured = Product.objects.filter(is_featured=True, is_active=True).count()
        out_of_stock = Product.objects.filter(stock=0, is_active=True).count()
        
        return Response({
            'total_products': total,
            'active_products': active,
            'featured_products': featured,
            'out_of_stock': out_of_stock,
            'deleted_products': Product.objects.filter(deleted_at__isnull=False).count(),
        })
    
    def create(self, request, *args, **kwargs):
        """Override create to support multipart with nested images"""
        # Support both JSON and multipart
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['post'], url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload single image for existing product (supports multiple calls)"""
        product = self.get_object()
        files = request.FILES.getlist('image') or request.FILES.getlist('images')
        if not files:
            file_obj = request.FILES.get('image')
            if file_obj:
                files = [file_obj]
        if not files:
            return Response({'detail': 'Rasm yuborilmadi (image yoki images field).'}, status=400)

        alt_text_uz = request.data.get('alt_text_uz', '')
        alt_text_ru = request.data.get('alt_text_ru', '')
        alt_text_en = request.data.get('alt_text_en', '')
        is_primary = request.data.get('is_primary') in ['true', '1', True]

        created = []
        # Determine starting order
        existing_count = product.images.count()
        for index, f in enumerate(files):
            img = ProductImage.objects.create(
                product=product,
                image=f,
                alt_text_uz=alt_text_uz,
                alt_text_ru=alt_text_ru,
                alt_text_en=alt_text_en,
                is_primary=is_primary and index == 0,  # only first one can be primary in batch
                order=existing_count + index
            )
            created.append({
                'id': str(img.id),
                'image_url': request.build_absolute_uri(img.image.url) if img.image else None,
                'is_primary': img.is_primary,
                'order': img.order
            })
        return Response({'created': created, 'count': len(created)}, status=201)

    @action(detail=True, methods=['patch'], url_path='set-primary-image')
    def set_primary_image(self, request, pk=None):
        product = self.get_object()
        image_id = request.data.get('image_id')
        if not image_id:
            return Response({'detail': 'image_id talab qilinadi.'}, status=400)
        try:
            img = product.images.get(id=image_id)
        except ProductImage.DoesNotExist:
            return Response({'detail': 'Rasm topilmadi.'}, status=404)
        # Set as primary (save triggers unsetting others)
        img.is_primary = True
        img.save()
        return Response({'detail': 'Asosiy rasm yangilandi.'})

    @action(detail=True, methods=['delete'], url_path='delete-image')
    def delete_image(self, request, pk=None):
        product = self.get_object()
        image_id = request.data.get('image_id') or request.query_params.get('image_id')
        if not image_id:
            return Response({'detail': 'image_id talab qilinadi.'}, status=400)
        try:
            img = product.images.get(id=image_id)
        except ProductImage.DoesNotExist:
            return Response({'detail': 'Rasm topilmadi.'}, status=404)
        img.delete()
        return Response(status=204)


class ProductCategoryAdminViewSet(BaseAdminViewSet):
    """Admin CRUD for Product Categories"""
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategoryAdminSerializer
    search_fields = ['name_uz', 'name_ru', 'name_en']
    ordering_fields = ['created_at', 'name_uz']


class ProductTagAdminViewSet(BaseAdminViewSet):
    """Admin CRUD for Product Tags"""
    queryset = ProductTag.objects.all()
    serializer_class = ProductTagAdminSerializer
    search_fields = ['name_uz', 'name_ru', 'name_en']
    ordering_fields = ['created_at', 'name_uz']


class OrderAdminViewSet(BaseAdminViewSet):
    """Admin CRUD for Orders"""
    queryset = Order.objects.all()
    serializer_class = OrderAdminSerializer
    filterset_fields = ['status', 'created_at', 'user']
    search_fields = ['id', 'full_name', 'contact_phone']
    ordering_fields = ['created_at', 'updated_at', 'total_price']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use detail serializer for retrieve"""
        if self.action == 'retrieve':
            return OrderDetailAdminSerializer
        return OrderAdminSerializer
    
    def get_queryset(self):
        """Add optimizations for orders"""
        return Order.objects.select_related('user').prefetch_related(
            'items__product'
        )
    
    @action(detail=False, methods=['get'])
    def revenue(self, request):
        """Revenue statistics"""
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        today_revenue = Order.objects.filter(
            created_at__date=today,
            status='completed'
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        week_revenue = Order.objects.filter(
            created_at__gte=week_ago,
            status='completed'
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        month_revenue = Order.objects.filter(
            created_at__gte=month_ago,
            status='completed'
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        total_revenue = Order.objects.filter(
            status='completed'
        ).aggregate(total=Sum('total_price'))['total'] or 0
        
        return Response({
            'today_revenue': today_revenue,
            'week_revenue': week_revenue,
            'month_revenue': month_revenue,
            'total_revenue': total_revenue,
            'pending_orders': Order.objects.filter(status='pending').count(),
            'completed_orders': Order.objects.filter(status='completed').count(),
        })


class CourseApplicationAdminViewSet(BaseAdminViewSet):
    """Admin CRUD for Course Applications"""
    queryset = CourseApplication.objects.all()
    serializer_class = CourseApplicationAdminSerializer
    filterset_fields = ['processed', 'created_at']
    search_fields = ['full_name', 'email', 'phone_number', 'course_name', 'application_number']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Add optimizations"""
        return CourseApplication.objects.select_related()
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Application statistics"""
        return Response({
            'total_applications': CourseApplication.objects.count(),
            'pending_applications': CourseApplication.objects.filter(processed=False).count(),
            'processed_applications': CourseApplication.objects.filter(processed=True).count(),
        })


class FranchiseApplicationAdminViewSet(BaseAdminViewSet):
    """Admin CRUD for Franchise Applications"""
    queryset = FranchiseApplication.objects.all()
    serializer_class = FranchiseApplicationAdminSerializer
    filterset_fields = ['status', 'created_at']
    search_fields = ['full_name', 'phone', 'email', 'city']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Add optimizations"""
        return FranchiseApplication.objects.select_related()
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Franchise application statistics"""
        return Response({
            'total_applications': FranchiseApplication.objects.count(),
            'pending_applications': FranchiseApplication.objects.filter(status='pending').count(),
            'approved_applications': FranchiseApplication.objects.filter(status='approved').count(),
            'rejected_applications': FranchiseApplication.objects.filter(status='rejected').count(),
        })
    
    @action(detail=False, methods=['get'])
    def roi_stats(self, request):
        """ROI and investment statistics"""
        total_investment = FranchiseApplication.objects.filter(
            status='approved'
        ).aggregate(total=Sum('investment_amount'))['total'] or Decimal('0')
        
        avg_investment = FranchiseApplication.objects.filter(
            status='approved'
        ).aggregate(avg=Sum('investment_amount'))['avg'] or Decimal('0')
        
        return Response({
            'total_approved_investment': total_investment,
            'average_investment': avg_investment,
            'total_applications': FranchiseApplication.objects.count(),
            'pending_applications': FranchiseApplication.objects.filter(status='pending').count(),
            'approved_applications': FranchiseApplication.objects.filter(status='approved').count(),
            'rejected_applications': FranchiseApplication.objects.filter(status='rejected').count(),
        })


class CartAdminViewSet(BaseAdminViewSet):
    """Admin CRUD for Cart"""
    queryset = Cart.objects.all()
    serializer_class = CartAdminSerializer
    filterset_fields = ['user', 'created_at']
    search_fields = ['user__username', 'user__email', 'session_key']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """Add optimizations"""
        return Cart.objects.select_related('user').prefetch_related('items__product')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Cart statistics"""
        return Response({
            'total_carts': Cart.objects.count(),
            'active_carts': Cart.objects.filter(items__isnull=False).distinct().count(),
            'anonymous_carts': Cart.objects.filter(user__isnull=True).count(),
            'user_carts': Cart.objects.filter(user__isnull=False).count(),
        })


class FavoriteAdminViewSet(BaseAdminViewSet):
    """Admin CRUD for Favorites"""
    queryset = Favorite.objects.all()
    serializer_class = FavoriteAdminSerializer
    filterset_fields = ['user', 'product', 'created_at']
    search_fields = ['user__username', 'user__email', 'product__name_uz']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Add optimizations"""
        return Favorite.objects.select_related('user', 'product')
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Favorites statistics"""
        return Response({
            'total_favorites': Favorite.objects.count(),
            'unique_users': Favorite.objects.values('user').distinct().count(),
            'unique_products': Favorite.objects.values('product').distinct().count(),
        })


# Dashboard and Stats Views
@api_view(['GET'])
@permission_classes([IsAdminUser])
def dashboard_stats(request):
    """
    Complete dashboard statistics for admin panel
    GET /api/admin/dashboard/
    """
    today = timezone.now().date()
    
    # User stats
    user_stats = {
        'total': User.objects.count(),
        'active': User.objects.filter(is_active=True).count(),
        'admins': User.objects.filter(is_staff=True).count(),
        'verified': User.objects.filter(is_verified=True).count(),
        'new_today': User.objects.filter(date_joined__date=today).count(),
    }
    
    # Product stats
    product_stats = {
        'total': Product.objects.count(),
        'active': Product.objects.filter(is_active=True, deleted_at__isnull=True).count(),
        'featured': Product.objects.filter(is_featured=True).count(),
        'out_of_stock': Product.objects.filter(stock=0).count(),
    }
    
    # Order stats
    order_stats = {
        'total': Order.objects.count(),
        'pending': Order.objects.filter(status='pending').count(),
        'completed': Order.objects.filter(status='delivered').count(),
        'cancelled': Order.objects.filter(status='canceled').count(),
        'today': Order.objects.filter(created_at__date=today).count(),
    }
    
    # Course application stats
    course_stats = {
        'total_applications': CourseApplication.objects.count(),
        'pending': CourseApplication.objects.filter(processed=False).count(),
        'processed': CourseApplication.objects.filter(processed=True).count(),
        'today': CourseApplication.objects.filter(created_at__date=today).count(),
    }
    
    # Franchise application stats
    franchise_stats = {
        'total_applications': FranchiseApplication.objects.count(),
        'pending': FranchiseApplication.objects.filter(status='pending').count(),
        'approved': FranchiseApplication.objects.filter(status='approved').count(),
        'rejected': FranchiseApplication.objects.filter(status='rejected').count(),
    }
    
    # Revenue stats
    revenue_stats = {
        'today': Order.objects.filter(
            created_at__date=today
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0'),
        'this_month': Order.objects.filter(
            created_at__month=today.month, 
            created_at__year=today.year
        ).aggregate(total=Sum('total_amount'))['total'] or Decimal('0'),
    }
    
    return Response({
        'users': user_stats,
        'products': product_stats,
        'orders': order_stats,
        'courses': course_stats,
        'franchises': franchise_stats,
        'revenue': revenue_stats,
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def applications_stats(request):
    """
    Combined applications statistics (course + franchise)
    GET /api/admin/applications/stats/
    """
    # Course applications
    course_apps = {
        'total': CourseApplication.objects.count(),
        'pending': CourseApplication.objects.filter(processed=False).count(),
        'processed': CourseApplication.objects.filter(processed=True).count(),
        'today': CourseApplication.objects.filter(
            created_at__date=timezone.now().date()
        ).count(),
        'popular_courses': list(
            CourseApplication.objects.values('course_name')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
    }
    
    # Franchise applications
    franchise_apps = {
        'total': FranchiseApplication.objects.count(),
        'pending': FranchiseApplication.objects.filter(status='pending').count(),
        'approved': FranchiseApplication.objects.filter(status='approved').count(),
        'rejected': FranchiseApplication.objects.filter(status='rejected').count(),
        'total_investment': FranchiseApplication.objects.filter(
            status='approved'
        ).aggregate(total=Sum('investment_amount'))['total'] or Decimal('0'),
        'popular_cities': list(
            FranchiseApplication.objects.values('city')
            .annotate(count=Count('id'))
            .order_by('-count')[:5]
        )
    }
    
    return Response({
        'course_applications': course_apps,
        'franchise_applications': franchise_apps,
    })


# Dashboard Statistics Views
@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard_stats(request):
    """Admin dashboard statistics"""
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # User stats
    user_stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'new_users_today': User.objects.filter(date_joined__date=today).count(),
        'new_users_week': User.objects.filter(date_joined__gte=week_ago).count(),
    }
    
    # Product stats
    product_stats = {
        'total_products': Product.objects.count(),
        'active_products': Product.objects.filter(is_active=True, deleted_at__isnull=True).count(),
        'featured_products': Product.objects.filter(is_featured=True, is_active=True).count(),
        'out_of_stock': Product.objects.filter(stock=0, is_active=True).count(),
    }
    
    # Order stats
    order_stats = {
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'completed_orders': Order.objects.filter(status='completed').count(),
        'today_orders': Order.objects.filter(created_at__date=today).count(),
        'week_orders': Order.objects.filter(created_at__gte=week_ago).count(),
    }
    
    # Revenue stats
    revenue_stats = {
        'today_revenue': Order.objects.filter(
            created_at__date=today, status='completed'
        ).aggregate(total=Sum('total_price'))['total'] or 0,
        'week_revenue': Order.objects.filter(
            created_at__gte=week_ago, status='completed'
        ).aggregate(total=Sum('total_price'))['total'] or 0,
        'month_revenue': Order.objects.filter(
            created_at__gte=month_ago, status='completed'
        ).aggregate(total=Sum('total_price'))['total'] or 0,
    }
    
    # Application stats
    application_stats = {
        'course_applications': CourseApplication.objects.count(),
        'pending_course_applications': CourseApplication.objects.filter(processed=False).count(),
        'franchise_applications': FranchiseApplication.objects.count(),
        'pending_franchise_applications': FranchiseApplication.objects.filter(status='pending').count(),
    }
    
    return Response({
        'user_stats': user_stats,
        'product_stats': product_stats,
        'order_stats': order_stats,
        'revenue_stats': revenue_stats,
        'application_stats': application_stats,
        'generated_at': timezone.now().isoformat(),
    })
