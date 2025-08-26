"""
Comprehensive tests for Products API
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.products.models import Product, ProductCategory, ProductTag
from decimal import Decimal


class ProductAPITestCase(APITestCase):
    """Test cases for Product API"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        
        # Create test category
        self.category = ProductCategory.objects.create(
            name_uz='Test Category',
            name_ru='Тест Категория',
            name_en='Test Category',
            description_uz='Test description'
        )
        
        # Create test tags
        self.tag1 = ProductTag.objects.create(
            name_uz='Tag 1',
            name_ru='Тег 1',
            name_en='Tag 1'
        )
        
        self.tag2 = ProductTag.objects.create(
            name_uz='Tag 2',
            name_ru='Тег 2',
            name_en='Tag 2'
        )
        
        # Create test products
        self.product1 = Product.objects.create(
            name_uz='Test Product 1',
            name_ru='Тест Продукт 1',
            name_en='Test Product 1',
            description_uz='Test description 1',
            price=Decimal('10.00'),
            stock=100,
            category=self.category,
            is_active=True
        )
        self.product1.tags.add(self.tag1)
        
        self.product2 = Product.objects.create(
            name_uz='Test Product 2',
            name_ru='Тест Продукт 2',
            name_en='Test Product 2',
            description_uz='Test description 2',
            price=Decimal('20.00'),
            sale_price=Decimal('15.00'),
            stock=50,
            category=self.category,
            is_featured=True,
            is_active=True
        )
        self.product2.tags.add(self.tag1, self.tag2)
        
        # Create inactive product
        self.inactive_product = Product.objects.create(
            name_uz='Inactive Product',
            name_ru='Неактивный Продукт',
            name_en='Inactive Product',
            price=Decimal('5.00'),
            stock=10,
            category=self.category,
            is_active=False
        )
        
        self.client = APIClient()
    
    def get_jwt_token(self, user):
        """Get JWT token for user"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def test_product_list_public(self):
        """Test public access to product list"""
        url = reverse('api:product-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('results', response.data)
        # Should only show active products
        self.assertEqual(len(response.data['results']), 2)
    
    def test_product_list_with_language(self):
        """Test product list with language parameter"""
        url = reverse('api:product-list')
        response = self.client.get(url, {'lang': 'ru'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check if Russian names are returned
        product = response.data['results'][0]
        self.assertIn('name_ru', product)
    
    def test_product_detail_public(self):
        """Test public access to product detail"""
        url = reverse('api:product-detail', kwargs={'pk': self.product1.pk})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name_uz'], 'Test Product 1')
    
    def test_product_create_authenticated(self):
        """Test product creation with authentication"""
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('api:product-list')
        data = {
            'name_uz': 'New Product',
            'name_ru': 'Новый Продукт',
            'name_en': 'New Product',
            'description_uz': 'New description',
            'price': '25.00',
            'stock': 75,
            'category_id': self.category.id,
            'tag_ids': [self.tag1.id],
            'is_active': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Product.objects.count(), 4)  # 3 existing + 1 new
    
    def test_product_create_unauthenticated(self):
        """Test product creation without authentication"""
        url = reverse('api:product-list')
        data = {
            'name_uz': 'New Product',
            'price': '25.00',
            'stock': 75,
            'category_id': self.category.id
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_product_update_authenticated(self):
        """Test product update with authentication"""
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('api:product-detail', kwargs={'pk': self.product1.pk})
        data = {
            'name_uz': 'Updated Product',
            'name_ru': 'Обновленный Продукт',
            'name_en': 'Updated Product',
            'price': '15.00',
            'stock': 200,
            'category_id': self.category.id
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.product1.refresh_from_db()
        self.assertEqual(self.product1.name_uz, 'Updated Product')
    
    def test_product_delete_soft(self):
        """Test soft delete of product"""
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('api:product-detail', kwargs={'pk': self.product1.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.product1.refresh_from_db()
        self.assertIsNotNone(self.product1.deleted_at)
    
    def test_featured_products(self):
        """Test featured products endpoint"""
        url = reverse('api:product-featured')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check paginated response
        featured_count = sum(1 for p in response.data['results'] if p['is_featured'])
        self.assertGreaterEqual(featured_count, 1)  # At least one featured product
    
    def test_on_sale_products(self):
        """Test on sale products endpoint"""
        url = reverse('api:product-on-sale')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check paginated response  
        sale_count = sum(1 for p in response.data['results'] if p['is_on_sale'])
        self.assertGreaterEqual(sale_count, 1)  # At least one product on sale
    
    def test_product_search(self):
        """Test product search functionality"""
        url = reverse('api:product-list')
        response = self.client.get(url, {'search': 'Test Product 1'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name_uz'], 'Test Product 1')
    
    def test_product_filter_by_category(self):
        """Test filtering products by category"""
        url = reverse('api:product-list')
        response = self.client.get(url, {'category': self.category.id})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_product_filter_by_tags(self):
        """Test filtering products by tags"""
        url = reverse('api:product-list')
        response = self.client.get(url, {'tags': [self.tag1.id]})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
    
    def test_product_price_range_filter(self):
        """Test filtering products by price range"""
        url = reverse('api:product-list')
        response = self.client.get(url, {'min_price': '15', 'max_price': '25'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['name_uz'], 'Test Product 2')
    
    def test_product_stats_admin_only(self):
        """Test product statistics endpoint (admin only)"""
        url = reverse('api:product-stats')
        
        # Test without authentication
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test with regular user
        token = self.get_jwt_token(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Test with admin user
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response structure
        expected_fields = [
            'total_products', 'active_products', 'featured_products',
            'out_of_stock', 'low_stock', 'on_sale', 'categories_count',
            'tags_count', 'average_price', 'total_stock_value'
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_api_health_check(self):
        """Test API health check endpoint"""
        url = reverse('api:api-health')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'healthy')
    
    def test_api_documentation(self):
        """Test API documentation endpoint"""
        url = reverse('api:api-documentation')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('title', response.data)
        self.assertIn('endpoints', response.data)


class CategoryAPITestCase(APITestCase):
    """Test cases for Category API"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        
        self.category = ProductCategory.objects.create(
            name_uz='Test Category',
            name_ru='Тест Категория',
            name_en='Test Category'
        )
        
        self.client = APIClient()
    
    def get_jwt_token(self, user):
        """Get JWT token for user"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def test_category_list_public(self):
        """Test public access to category list"""
        url = reverse('api:category-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_category_create_authenticated(self):
        """Test category creation with authentication"""
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('api:category-list')
        data = {
            'name_uz': 'New Category',
            'name_ru': 'Новая Категория',
            'name_en': 'New Category'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductCategory.objects.count(), 2)


class TagAPITestCase(APITestCase):
    """Test cases for Tag API"""
    
    def setUp(self):
        """Set up test data"""
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@example.com',
            password='adminpass123',
            is_staff=True
        )
        
        self.tag = ProductTag.objects.create(
            name_uz='Test Tag',
            name_ru='Тест Тег',
            name_en='Test Tag'
        )
        
        self.client = APIClient()
    
    def get_jwt_token(self, user):
        """Get JWT token for user"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)
    
    def test_tag_list_public(self):
        """Test public access to tag list"""
        url = reverse('api:tag-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_tag_create_authenticated(self):
        """Test tag creation with authentication"""
        token = self.get_jwt_token(self.admin_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        url = reverse('api:tag-list')
        data = {
            'name_uz': 'New Tag',
            'name_ru': 'Новый Тег',
            'name_en': 'New Tag'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ProductTag.objects.count(), 2)
