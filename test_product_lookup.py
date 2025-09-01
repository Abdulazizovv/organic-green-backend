#!/usr/bin/env python
"""
Test script to verify product lookup by both UUID and slug
"""
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append('/home/abdulazizov/myProjects/djangoProjects/organic-green')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from apps.products.models import Product, ProductCategory
from django.test import RequestFactory
from api.views import ProductViewSet

def test_product_lookup():
    """Test product lookup by UUID and slug"""
    
    # Create test data if doesn't exist
    category, _ = ProductCategory.objects.get_or_create(
        name_uz="Test Category",
        defaults={
            'name_ru': 'Test Category',
            'name_en': 'Test Category',
            'slug': 'test-category'
        }
    )
    
    product, created = Product.objects.get_or_create(
        slug='test-product',
        defaults={
            'name_uz': 'Test Product',
            'name_ru': 'Test Product',
            'name_en': 'Test Product',
            'price': 10000,
            'category': category,
            'stock': 10
        }
    )
    
    print(f"Product created: {created}")
    print(f"Product ID: {product.id}")
    print(f"Product slug: {product.slug}")
    
    # Create request factory
    factory = RequestFactory()
    
    # Test lookup by UUID
    request = factory.get(f'/api/products/{product.id}/')
    view = ProductViewSet()
    view.setup(request, pk=str(product.id))
    view.kwargs = {'pk': str(product.id)}
    
    try:
        obj_by_id = view.get_object()
        print(f"✅ Lookup by UUID successful: {obj_by_id.name_uz}")
    except Exception as e:
        print(f"❌ Lookup by UUID failed: {e}")
    
    # Test lookup by slug
    request = factory.get(f'/api/products/{product.slug}/')
    view = ProductViewSet()
    view.setup(request, pk=product.slug)
    view.kwargs = {'pk': product.slug}
    
    try:
        obj_by_slug = view.get_object()
        print(f"✅ Lookup by slug successful: {obj_by_slug.name_uz}")
    except Exception as e:
        print(f"❌ Lookup by slug failed: {e}")

if __name__ == '__main__':
    test_product_lookup()
