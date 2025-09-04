"""
Professional API Views
Comprehensive RESTful API with advanced features
"""
from rest_framework import generics, viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from api.throttling import AuthRateThrottle, LenientAnonRateThrottle
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Sum, F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model
from apps.products.models import Product, ProductCategory, ProductTag
from .serializers import (
    # Authentication serializers
    SimpleUserRegistrationSerializer, UserRegistrationSerializer, UserLoginSerializer, UserProfileSerializer,
    ChangePasswordSerializer, CustomTokenObtainPairSerializer, AvatarUploadSerializer,
    # Product serializers
    ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer,
    ProductCategorySerializer, ProductTagSerializer, ProductStatsSerializer
)
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

# Authentication Views

class SimpleUserRegistrationView(generics.CreateAPIView):
    """
    Simple user registration endpoint
    
    Register a new user with only username and password.
    Returns user data and JWT tokens upon successful registration.
    """
    queryset = User.objects.all()
    serializer_class = SimpleUserRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]  # Use auth throttle for registration
    
    def create(self, request, *args, **kwargs):
        """Create user and return tokens"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Prepare response data
        user_data = UserProfileSerializer(user).data
        
        response_data = {
            'message': 'Foydalanuvchi muvaffaqiyatli ro\'yxatdan o\'tdi',
            'user': user_data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }
        
        logger.info(f"New user registered (simple): {user.username}")
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint
    
    Register a new user with username, email, password, first_name, and last_name.
    Returns user data and JWT tokens upon successful registration.
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]  # Use auth throttle for registration
    
    def create(self, request, *args, **kwargs):
        """Create user and return tokens"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Prepare response data
        user_data = UserProfileSerializer(user).data
        
        response_data = {
            'message': 'Foydalanuvchi muvaffaqiyatli ro\'yxatdan o\'tdi',
            'user': user_data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }
        
        logger.info(f"New user registered: {user.username}")
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class UserLoginView(generics.GenericAPIView):
    """
    User login endpoint
    
    Login with username/email and password.
    Returns user data and JWT tokens upon successful authentication.
    """
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]  # Use auth throttle for login
    
    def post(self, request, *args, **kwargs):
        """Authenticate user and return tokens"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Update last login
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # Prepare response data
        user_data = UserProfileSerializer(user).data
        
        response_data = {
            'message': 'Tizimga muvaffaqiyatli kirildi',
            'user': user_data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }
        
        logger.info(f"User logged in: {user.username}")
        
        return Response(response_data, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view with additional user info"""
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile endpoint
    
    Get and update current user's profile information.
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Return current authenticated user"""
        return self.request.user
        
    def get_serializer_context(self):
        """Add request to serializer context"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
        
    def update(self, request, *args, **kwargs):
        """Update user profile"""
        response = super().update(request, *args, **kwargs)
        
        if response.status_code == 200:
            logger.info(f"User profile updated: {request.user.username}")
            response.data['message'] = 'Profil muvaffaqiyatli yangilandi'
            
        return response


class ChangePasswordView(generics.GenericAPIView):
    """
    Change password endpoint
    
    Change current user's password by providing old and new passwords.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """Change user password"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Save new password
        serializer.save()
        
        logger.info(f"Password changed for user: {request.user.username}")
        
        return Response({
            'message': 'Parol muvaffaqiyatli o\'zgartirildi'
        }, status=status.HTTP_200_OK)


class UserLogoutView(generics.GenericAPIView):
    """
    User logout endpoint
    
    Logout current user by blacklisting the refresh token.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """Logout user by blacklisting refresh token"""
        try:
            refresh_token = request.data.get('refresh_token')
            
            if not refresh_token:
                return Response({
                    'error': 'Refresh token kiritish majburiy'
                }, status=status.HTTP_400_BAD_REQUEST)
                
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            logger.info(f"User logged out: {request.user.username}")
            
            return Response({
                'message': 'Tizimdan muvaffaqiyatli chiqildi'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Logout error for user {request.user.username}: {str(e)}")
            return Response({
                'error': 'Noto\'g\'ri token'
            }, status=status.HTTP_400_BAD_REQUEST)


# Utility Views for Authentication

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_auth_status(request):
    """
    Check authentication status
    
    Returns current user information if authenticated.
    """
    user_data = UserProfileSerializer(request.user).data
    
    return Response({
        'authenticated': True,
        'user': user_data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def auth_info(request):
    """
    Get authentication information and endpoints
    
    Returns available authentication endpoints and their descriptions.
    """
    return Response({
        'title': 'Authentication API',
        'description': 'JWT-based authentication system',
        'endpoints': {
            'register': '/api/auth/register/ (POST)',
            'login': '/api/auth/login/ (POST)',
            'token': '/api/auth/token/ (POST)',
            'token_refresh': '/api/auth/token/refresh/ (POST)',
            'profile': '/api/auth/profile/ (GET, PUT, PATCH)',
            'change_password': '/api/auth/change-password/ (POST)',
            'logout': '/api/auth/logout/ (POST)',
            'check_status': '/api/auth/status/ (GET)',
        },
        'authentication': 'Bearer Token (JWT)',
        'token_lifetime': {
            'access': '60 minutes',
            'refresh': '7 days'
        }
    }, status=status.HTTP_200_OK)


class StandardResultsSetPagination(PageNumberPagination):
    """Custom pagination class"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'page_size': self.page_size,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'results': data
        })


class ProductFilter:
    """Custom filter for products"""
    
    @staticmethod
    def filter_queryset(queryset, request):
        """Apply custom filters to product queryset"""
        
        # Base filter - only active and non-deleted products for public API
        if not request.user.is_staff:
            queryset = queryset.filter(is_active=True, deleted_at__isnull=True)
        
        # Category filter
        category_id = request.query_params.get('category', None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Tags filter
        tags = request.query_params.getlist('tags')
        if tags:
            queryset = queryset.filter(tags__id__in=tags).distinct()
        
        # Price range filter
        min_price = request.query_params.get('min_price', None)
        max_price = request.query_params.get('max_price', None)
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        # Stock filter
        in_stock = request.query_params.get('in_stock', None)
        if in_stock and in_stock.lower() == 'true':
            queryset = queryset.filter(stock__gt=0)
        elif in_stock and in_stock.lower() == 'false':
            queryset = queryset.filter(stock=0)
        
        # Featured filter
        featured = request.query_params.get('featured', None)
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        # On sale filter
        on_sale = request.query_params.get('on_sale', None)
        if on_sale and on_sale.lower() == 'true':
            queryset = queryset.filter(sale_price__isnull=False, sale_price__lt=F('price'))
        
        # Search functionality
        search = request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name_uz__icontains=search) |
                Q(name_ru__icontains=search) |
                Q(name_en__icontains=search) |
                Q(description_uz__icontains=search) |
                Q(description_ru__icontains=search) |
                Q(description_en__icontains=search) |
                Q(category__name_uz__icontains=search) |
                Q(category__name_ru__icontains=search) |
                Q(category__name_en__icontains=search)
            ).distinct()
        
        # Ordering
        ordering = request.query_params.get('ordering', '-created_at')
        valid_orderings = [
            'created_at', '-created_at',
            'price', '-price',
            'name_uz', '-name_uz',
            'stock', '-stock',
            'is_featured', '-is_featured'
        ]
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)
        
        return queryset


class ProductCategoryViewSet(viewsets.ModelViewSet):
    """API for ProductCategory management"""
    
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name_uz', 'name_ru', 'name_en', 'description_uz', 'description_ru', 'description_en']
    ordering_fields = ['created_at', 'name_uz']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Optimize queryset with prefetch"""
        return ProductCategory.objects.prefetch_related('products').all()
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products for specific category"""
        category = self.get_object()
        products = Product.objects.filter(
            category=category,
            is_active=True,
            deleted_at__isnull=True
        ).select_related('category').prefetch_related('tags')
        
        # Apply language context
        language = request.query_params.get('lang', 'uz')
        serializer = ProductListSerializer(
            products, 
            many=True, 
            context={'language': language, 'request': request}
        )
        return Response(serializer.data)


class ProductTagViewSet(viewsets.ModelViewSet):
    """API for ProductTag management"""
    
    queryset = ProductTag.objects.all()
    serializer_class = ProductTagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name_uz', 'name_ru', 'name_en']
    ordering_fields = ['created_at', 'name_uz']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Optimize queryset with prefetch"""
        return ProductTag.objects.prefetch_related('products').all()
    
    @action(detail=True, methods=['get'])
    def products(self, request, pk=None):
        """Get products for specific tag"""
        tag = self.get_object()
        products = Product.objects.filter(
            tags=tag,
            is_active=True,
            deleted_at__isnull=True
        ).select_related('category').prefetch_related('tags')
        
        # Apply language context
        language = request.query_params.get('lang', 'uz')
        serializer = ProductListSerializer(
            products, 
            many=True, 
            context={'language': language, 'request': request}
        )
        return Response(serializer.data)


class ProductViewSet(viewsets.ModelViewSet):
    """
    Complete CRUD API for Products with advanced filtering and features
    """
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = StandardResultsSetPagination
    # throttle_classes = [UserRateThrottle, AnonRateThrottle]  # Removed throttling for better UX
    
    def get_queryset(self):
        """Optimized queryset with proper prefetching"""
        queryset = Product.objects.select_related('category').prefetch_related(
            'tags', 'suggested_products', 'suggested_products__category'
        )
        
        # Apply custom filters
        queryset = ProductFilter.filter_queryset(queryset, self.request)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return ProductListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return ProductCreateUpdateSerializer
        return ProductDetailSerializer
    
    def get_serializer_context(self):
        """Add language context to serializer"""
        context = super().get_serializer_context()
        context['language'] = self.request.query_params.get('lang', 'uz')
        return context
    
    def get_object(self):
        """
        Override get_object to support both UUID and slug lookup
        """
        queryset = self.filter_queryset(self.get_queryset())
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        lookup_value = self.kwargs[lookup_url_kwarg]
        
        # Try to get by UUID first (if it looks like a UUID)
        try:
            # Check if the lookup value is a valid UUID
            import uuid
            uuid.UUID(lookup_value)
            # If valid UUID, filter by ID
            filter_kwargs = {self.lookup_field: lookup_value}
        except (ValueError, AttributeError):
            # If not a UUID, assume it's a slug
            filter_kwargs = {'slug': lookup_value}
        
        obj = get_object_or_404(queryset, **filter_kwargs)
        
        # May raise a permission denied
        self.check_object_permissions(self.request, obj)
        
        return obj
    
    def list(self, request, *args, **kwargs):
        """Enhanced list view with caching"""
        # Create cache key based on query parameters
        cache_key = f"products_list_{hash(str(sorted(request.query_params.items())))}"
        
        # Try to get from cache
        cached_response = cache.get(cache_key)
        if cached_response and not request.user.is_staff:
            return Response(cached_response)
        
        # Get fresh data
        response = super().list(request, *args, **kwargs)
        
        # Cache for 15 minutes for non-staff users
        if not request.user.is_staff:
            cache.set(cache_key, response.data, 60 * 15)
        
        return response
    
    def retrieve(self, request, *args, **kwargs):
        """Enhanced retrieve view with view tracking"""
        instance = self.get_object()
        
        # Track product view (could be used for analytics)
        # Product.objects.filter(id=instance.id).update(view_count=F('view_count') + 1)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete instead of hard delete"""
        instance = self.get_object()
        if not instance.deleted_at:
            instance.delete()  # This calls our custom delete method (soft delete)
            return Response({'message': 'Mahsulot muvaffaqiyatli o\'chirildi.'}, 
                          status=status.HTTP_204_NO_CONTENT)
        return Response({'error': 'Mahsulot allaqachon o\'chirilgan.'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def restore(self, request, pk=None):
        """Restore soft-deleted product"""
        product = self.get_object()
        if product.deleted_at:
            product.restore()
            return Response({'message': 'Mahsulot muvaffaqiyatli tiklandi.'})
        return Response({'error': 'Mahsulot o\'chirilmagan.'}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured products"""
        featured_products = self.get_queryset().filter(is_featured=True)
        page = self.paginate_queryset(featured_products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context=self.get_serializer_context())
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(featured_products, many=True, context=self.get_serializer_context())
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def on_sale(self, request):
        """Get products on sale"""
        sale_products = self.get_queryset().filter(
            sale_price__isnull=False,
            sale_price__lt=F('price')
        )
        page = self.paginate_queryset(sale_products)
        if page is not None:
            serializer = ProductListSerializer(page, many=True, context=self.get_serializer_context())
            return self.get_paginated_response(serializer.data)
        
        serializer = ProductListSerializer(sale_products, many=True, context=self.get_serializer_context())
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """Get low stock products (admin only)"""
        if not request.user.is_staff:
            return Response({'error': 'Ruxsat yo\'q.'}, status=status.HTTP_403_FORBIDDEN)
        
        low_stock_products = Product.objects.filter(
            stock__lte=10,
            stock__gt=0,
            is_active=True,
            deleted_at__isnull=True
        ).select_related('category')
        
        serializer = ProductListSerializer(low_stock_products, many=True, context=self.get_serializer_context())
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """Get out of stock products (admin only)"""
        if not request.user.is_staff:
            return Response({'error': 'Ruxsat yo\'q.'}, status=status.HTTP_403_FORBIDDEN)
        
        out_of_stock_products = Product.objects.filter(
            stock=0,
            is_active=True,
            deleted_at__isnull=True
        ).select_related('category')
        
        serializer = ProductListSerializer(out_of_stock_products, many=True, context=self.get_serializer_context())
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def suggested(self, request, pk=None):
        """Get suggested products for a specific product"""
        product = self.get_object()
        suggested = product.suggested_products.filter(
            is_active=True,
            deleted_at__isnull=True
        ).select_related('category').prefetch_related('tags')
        
        serializer = ProductListSerializer(suggested, many=True, context=self.get_serializer_context())
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get product statistics (admin only)"""
        if not request.user.is_staff:
            return Response({'error': 'Ruxsat yo\'q.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Calculate statistics
        all_products = Product.objects.all()
        active_products = all_products.filter(is_active=True, deleted_at__isnull=True)
        
        stats = {
            'total_products': all_products.count(),
            'active_products': active_products.count(),
            'featured_products': active_products.filter(is_featured=True).count(),
            'out_of_stock': active_products.filter(stock=0).count(),
            'low_stock': active_products.filter(stock__lte=10, stock__gt=0).count(),
            'on_sale': active_products.filter(
                sale_price__isnull=False,
                sale_price__lt=F('price')
            ).count(),
            'categories_count': ProductCategory.objects.count(),
            'tags_count': ProductTag.objects.count(),
            'average_price': active_products.aggregate(avg_price=Avg('price'))['avg_price'] or 0,
            'total_stock_value': active_products.aggregate(
                total_value=Sum(F('price') * F('stock'))
            )['total_value'] or 0
        }
        
        serializer = ProductStatsSerializer(stats)
        return Response(serializer.data)


# User Management Views

class AvatarUploadView(generics.UpdateAPIView):
    """
    Avatar upload endpoint
    
    Upload or update user's profile avatar image.
    """
    serializer_class = AvatarUploadSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Return current authenticated user"""
        return self.request.user
        
    def update(self, request, *args, **kwargs):
        """Upload avatar"""
        response = super().update(request, *args, **kwargs)
        
        if response.status_code == 200:
            user = self.get_object()
            user_data = UserProfileSerializer(user, context={'request': request}).data
            
            logger.info(f"Avatar uploaded for user: {request.user.username}")
            
            return Response({
                'message': 'Avatar muvaffaqiyatli yuklandi',
                'user': user_data
            }, status=status.HTTP_200_OK)
            
        return response


class DeleteAvatarView(generics.GenericAPIView):
    """
    Delete avatar endpoint
    
    Remove user's profile avatar image.
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, *args, **kwargs):
        """Delete user avatar"""
        user = request.user
        
        if user.avatar and user.avatar.name != 'avatars/default.png':
            user.avatar.delete()
            user.avatar = 'avatars/default.png'
            user.save(update_fields=['avatar'])
            
        user_data = UserProfileSerializer(user, context={'request': request}).data
        
        logger.info(f"Avatar deleted for user: {request.user.username}")
        
        return Response({
            'message': 'Avatar o\'chirildi',
            'user': user_data
        }, status=status.HTTP_200_OK)


class VerifyAccountView(generics.GenericAPIView):
    """
    Account verification endpoint
    
    Verify user account (admin only feature for now).
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        """Verify user account"""
        user = request.user
        
        # For now, auto-verify. In production, you might want to implement
        # email verification or admin approval
        user.is_verified = True
        user.save(update_fields=['is_verified'])
        
        user_data = UserProfileSerializer(user, context={'request': request}).data
        
        logger.info(f"Account verified for user: {request.user.username}")
        
        return Response({
            'message': 'Hisob tasdiqlandi',
            'user': user_data
        }, status=status.HTTP_200_OK)


class UserStatsView(generics.GenericAPIView):
    """
    User statistics endpoint
    
    Get user's order and activity statistics.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, *args, **kwargs):
        """Get user statistics"""
        user = request.user
        
        # Import here to avoid circular imports
        from apps.order.models import Order
        from apps.cart.models import Cart
        from apps.favorites.models import Favorite
        
        stats = {
            'total_orders': Order.objects.filter(user=user).count(),
            'pending_orders': Order.objects.filter(user=user, status='pending').count(),
            'completed_orders': Order.objects.filter(user=user, status='delivered').count(),
            'cart_items': 0,
            'favorites_count': 0,
            'is_verified': user.is_verified,
            'account_age_days': (timezone.now() - user.date_joined).days,
        }
        
        # Get cart items count
        try:
            cart = Cart.objects.get(user=user)
            stats['cart_items'] = cart.total_items
        except Cart.DoesNotExist:
            pass
            
        # Get favorites count
        stats['favorites_count'] = Favorite.objects.filter(user=user).count()
        
        return Response({
            'message': 'Foydalanuvchi statistikasi',
            'stats': stats
        }, status=status.HTTP_200_OK)
    

@api_view(['GET'])
@permission_classes([])
def api_health_check(request):
    """API health check endpoint"""
    return Response({
        'status': 'healthy',
        'timestamp': timezone.now(),
        'version': '1.0.0',
        'message': 'Products API is running successfully'
    })


@api_view(['GET'])
@permission_classes([])
def api_documentation(request):
    """API documentation endpoint"""
    docs = {
        'title': 'Organic Green API',
        'version': '1.0.0',
        'description': 'Comprehensive REST API for organic products with JWT authentication',
        'authentication': {
            'type': 'JWT Bearer Token',
            'header': 'Authorization: Bearer <token>',
            'token_lifetime': {
                'access': '60 minutes',
                'refresh': '7 days'
            }
        },
        'endpoints': {
            'authentication': {
                'register_simple': {
                    'url': '/api/auth/register/simple/',
                    'method': 'POST',
                    'description': 'Oddiy ro\'yxatdan o\'tish (faqat username va password)',
                    'auth_required': False,
                    'fields': ['username', 'password']
                },
                'register': {
                    'url': '/api/auth/register/',
                    'method': 'POST',
                    'description': 'To\'liq ro\'yxatdan o\'tish',
                    'auth_required': False,
                    'fields': ['username', 'email', 'password', 'password_confirm', 'first_name', 'last_name']
                },
                'login': {
                    'url': '/api/auth/login/',
                    'method': 'POST',
                    'description': 'Tizimga kirish',
                    'auth_required': False,
                    'fields': ['username', 'password']
                },
                'token': {
                    'url': '/api/auth/token/',
                    'method': 'POST',
                    'description': 'Get JWT tokens',
                    'auth_required': False,
                    'fields': ['username', 'password']
                },
                'token_refresh': {
                    'url': '/api/auth/token/refresh/',
                    'method': 'POST',
                    'description': 'Refresh access token',
                    'auth_required': False,
                    'fields': ['refresh']
                },
                'profile': {
                    'url': '/api/auth/profile/',
                    'methods': ['GET', 'PUT', 'PATCH'],
                    'description': 'Get/update user profile',
                    'auth_required': True
                },
                'change_password': {
                    'url': '/api/auth/change-password/',
                    'method': 'POST',
                    'description': 'Change user password',
                    'auth_required': True,
                    'fields': ['old_password', 'new_password', 'new_password_confirm']
                },
                'logout': {
                    'url': '/api/auth/logout/',
                    'method': 'POST',
                    'description': 'Logout user (blacklist token)',
                    'auth_required': True,
                    'fields': ['refresh_token']
                },
                'status': {
                    'url': '/api/auth/status/',
                    'method': 'GET',
                    'description': 'Check authentication status',
                    'auth_required': True
                }
            },
            'products': {
                'list_create': {
                    'url': '/api/products/',
                    'methods': ['GET', 'POST'],
                    'description': 'List/create products with advanced filtering',
                    'auth_required': 'POST only'
                },
                'detail': {
                    'url': '/api/products/{id}/',
                    'methods': ['GET', 'PUT', 'PATCH', 'DELETE'],
                    'description': 'Product detail operations',
                    'auth_required': 'Modify only'
                },
                'featured': {
                    'url': '/api/products/featured/',
                    'method': 'GET',
                    'description': 'Get featured products',
                    'auth_required': False
                },
                'on_sale': {
                    'url': '/api/products/on_sale/',
                    'method': 'GET',
                    'description': 'Get products on sale',
                    'auth_required': False
                }
            },
            'categories': {
                'url': '/api/categories/',
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'description': 'CRUD operations for product categories',
                'auth_required': 'Modify only'
            },
            'tags': {
                'url': '/api/tags/',
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'description': 'CRUD operations for product tags',
                'auth_required': 'Modify only'
            }
        },
        'filters': {
            'category': 'Filter by category ID',
            'tags': 'Filter by tag IDs (multiple)',
            'min_price': 'Minimum price filter',
            'max_price': 'Maximum price filter',
            'in_stock': 'Filter by stock availability (true/false)',
            'featured': 'Filter featured products (true/false)',
            'on_sale': 'Filter products on sale (true/false)',
            'search': 'Search in product names and descriptions',
            'ordering': 'Order by: created_at, price, name_uz, stock, is_featured',
            'lang': 'Language for localized content (uz/ru/en)'
        }
    }
    return Response(docs)
