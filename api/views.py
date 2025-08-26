"""
Professional API Views for Products
Comprehensive RESTful API with advanced features
"""
from rest_framework import generics, viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg, Sum, F
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core.cache import cache
from apps.products.models import Product, ProductCategory, ProductTag
from .serializers import (
    ProductListSerializer, ProductDetailSerializer, ProductCreateUpdateSerializer,
    ProductCategorySerializer, ProductTagSerializer, ProductStatsSerializer
)
import logging

logger = logging.getLogger(__name__)


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
    throttle_classes = [UserRateThrottle, AnonRateThrottle]
    
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
        'title': 'Organic Green Products API',
        'version': '1.0.0',
        'description': 'Comprehensive REST API for managing organic products',
        'endpoints': {
            'categories': {
                'url': '/api/categories/',
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'description': 'CRUD operations for product categories'
            },
            'tags': {
                'url': '/api/tags/',
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'description': 'CRUD operations for product tags'
            },
            'products': {
                'url': '/api/products/',
                'methods': ['GET', 'POST', 'PUT', 'PATCH', 'DELETE'],
                'description': 'CRUD operations for products with advanced filtering'
            },
            'featured_products': {
                'url': '/api/products/featured/',
                'methods': ['GET'],
                'description': 'Get featured products'
            },
            'on_sale_products': {
                'url': '/api/products/on_sale/',
                'methods': ['GET'],
                'description': 'Get products on sale'
            },
            'product_stats': {
                'url': '/api/products/stats/',
                'methods': ['GET'],
                'description': 'Get product statistics (admin only)'
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
