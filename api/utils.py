"""
Utility functions for API
"""
from django.core.cache import cache
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from apps.products.models import Product
import hashlib


def generate_cache_key(prefix, params):
    """Generate cache key from parameters"""
    params_str = str(sorted(params.items()))
    params_hash = hashlib.md5(params_str.encode()).hexdigest()
    return f"{prefix}_{params_hash}"


def search_products(query, language='uz'):
    """
    Advanced product search functionality
    """
    if not query:
        return Product.objects.none()
    
    # Create search filter based on language
    if language == 'uz':
        search_filter = Q(name_uz__icontains=query) | Q(description_uz__icontains=query)
    elif language == 'ru':
        search_filter = Q(name_ru__icontains=query) | Q(description_ru__icontains=query)
    elif language == 'en':
        search_filter = Q(name_en__icontains=query) | Q(description_en__icontains=query)
    else:
        # Search in all languages
        search_filter = (
            Q(name_uz__icontains=query) | Q(description_uz__icontains=query) |
            Q(name_ru__icontains=query) | Q(description_ru__icontains=query) |
            Q(name_en__icontains=query) | Q(description_en__icontains=query)
        )
    
    # Also search in category and tag names
    search_filter |= (
        Q(category__name_uz__icontains=query) |
        Q(category__name_ru__icontains=query) |
        Q(category__name_en__icontains=query) |
        Q(tags__name_uz__icontains=query) |
        Q(tags__name_ru__icontains=query) |
        Q(tags__name_en__icontains=query)
    )
    
    return Product.objects.filter(
        search_filter,
        is_active=True,
        deleted_at__isnull=True
    ).distinct().select_related('category').prefetch_related('tags')


def get_similar_products(product, limit=5):
    """
    Get similar products based on category and tags
    """
    # Get products from same category
    similar_by_category = Product.objects.filter(
        category=product.category,
        is_active=True,
        deleted_at__isnull=True
    ).exclude(id=product.id)
    
    # Get products with similar tags
    product_tags = product.tags.all()
    if product_tags.exists():
        similar_by_tags = Product.objects.filter(
            tags__in=product_tags,
            is_active=True,
            deleted_at__isnull=True
        ).exclude(id=product.id).distinct()
        
        # Combine and deduplicate
        combined_ids = set(similar_by_category.values_list('id', flat=True)) | \
                      set(similar_by_tags.values_list('id', flat=True))
        
        similar_products = Product.objects.filter(
            id__in=combined_ids
        ).select_related('category').prefetch_related('tags')[:limit]
    else:
        similar_products = similar_by_category.select_related('category').prefetch_related('tags')[:limit]
    
    return similar_products


def validate_price_range(min_price, max_price):
    """
    Validate price range parameters
    """
    errors = {}
    
    if min_price is not None:
        try:
            min_price = float(min_price)
            if min_price < 0:
                errors['min_price'] = 'Minimum price cannot be negative'
        except (ValueError, TypeError):
            errors['min_price'] = 'Invalid minimum price format'
    
    if max_price is not None:
        try:
            max_price = float(max_price)
            if max_price < 0:
                errors['max_price'] = 'Maximum price cannot be negative'
        except (ValueError, TypeError):
            errors['max_price'] = 'Invalid maximum price format'
    
    if min_price is not None and max_price is not None and min_price > max_price:
        errors['price_range'] = 'Minimum price cannot be greater than maximum price'
    
    return errors if errors else None


def get_trending_products(limit=10):
    """
    Get trending products (featured + recently created)
    """
    cache_key = f"trending_products_{limit}"
    trending = cache.get(cache_key)
    
    if trending is None:
        # Get featured products and recently created products
        trending = Product.objects.filter(
            is_active=True,
            deleted_at__isnull=True
        ).filter(
            Q(is_featured=True) | Q(created_at__gte=timezone.now() - timedelta(days=7))
        ).select_related('category').prefetch_related('tags').order_by(
            '-is_featured', '-created_at'
        )[:limit]
        
        # Cache for 1 hour
        cache.set(cache_key, trending, 60 * 60)
    
    return trending


def format_api_response(data, message=None, status_code=200, errors=None):
    """
    Format standardized API response
    """
    response = {
        'success': 200 <= status_code < 300,
        'status_code': status_code,
        'data': data
    }
    
    if message:
        response['message'] = message
    
    if errors:
        response['errors'] = errors
    
    return response


def log_api_activity(user, action, resource, resource_id=None, extra_data=None):
    """
    Log API activity for analytics
    """
    # This could be implemented to log to database or external service
    pass
