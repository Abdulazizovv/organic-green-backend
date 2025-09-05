"""
Tests for Admin API endpoints
"""
import pytest
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

# Models
from accounts.models import User
from apps.products.models import Product, ProductCategory, ProductTag
from apps.order.models import Order, OrderItem
from apps.course.models import Application as CourseApplication
from apps.franchise.models import FranchiseApplication
from apps.cart.models import Cart, CartItem
from apps.favorites.models import Favorite

User = get_user_model()


class BaseAdminAPITestCase(APITestCase):
    """Base test case for admin API tests"""
    
    def setUp(self):
        # Create admin user
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='adminpass123',
            is_staff=True,
            is_superuser=True
        )
        
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='userpass123'
        )
        
        # Generate admin token
        refresh = RefreshToken.for_user(self.admin_user)
        self.admin_token = str(refresh.access_token)
        
        # Generate regular user token
        refresh = RefreshToken.for_user(self.regular_user)
        self.user_token = str(refresh.access_token)
        
        self.client = APIClient()
    
    def authenticate_admin(self):
        """Authenticate as admin user"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token}')
    
    def authenticate_user(self):
        """Authenticate as regular user"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_token}')


class UserAdminAPITest(BaseAdminAPITestCase):
    """Test User Admin API"""
    
    def test_admin_can_list_users(self):
        """Test admin can list all users"""
        self.authenticate_admin()
        url = reverse('api:admin-users-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # admin + regular user
    
    def test_regular_user_cannot_access_admin_api(self):
        """Test regular user cannot access admin APIs"""
        self.authenticate_user()
        url = reverse('api:admin-users-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_unauthenticated_cannot_access_admin_api(self):
        """Test unauthenticated user cannot access admin APIs"""
        url = reverse('api:admin-users-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_admin_can_create_user(self):
        """Test admin can create new users"""
        self.authenticate_admin()
        url = reverse('api:admin-users-list')
        data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'first_name': 'New',
            'last_name': 'User',
            'is_active': True
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())
    
    def test_admin_can_update_user(self):
        """Test admin can update user details"""
        self.authenticate_admin()
        url = reverse('api:admin-users-detail', kwargs={'pk': self.regular_user.pk})
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'is_verified': True
        }
        response = self.client.patch(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.regular_user.refresh_from_db()
        self.assertEqual(self.regular_user.first_name, 'Updated')
        self.assertTrue(self.regular_user.is_verified)
    
    def test_user_activity_endpoint(self):
        """Test user activity statistics endpoint"""
        self.authenticate_admin()
        url = reverse('api:admin-users-activity')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('active_today', response.data)
        self.assertIn('total_users', response.data)


class ProductAdminAPITest(BaseAdminAPITestCase):
    """Test Product Admin API"""
    
    def setUp(self):
        super().setUp()
        # Create test category
        self.category = ProductCategory.objects.create(
            name_uz='Test Category',
            name_ru='Тест категория',
            name_en='Test Category'
        )
        
        # Create test product
        self.product = Product.objects.create(
            name_uz='Test Product',
            name_ru='Тест продукт',
            name_en='Test Product',
            slug='test-product',
            price=Decimal('10.00'),
            stock=100,
            category=self.category
        )
    
    def test_admin_can_list_products(self):
        """Test admin can list all products"""
        self.authenticate_admin()
        url = reverse('api:admin-products-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_admin_can_create_product(self):
        """Test admin can create products"""
        self.authenticate_admin()
        url = reverse('api:admin-products-list')
        data = {
            'name_uz': 'New Product',
            'name_ru': 'Новый продукт',
            'name_en': 'New Product',
            'slug': 'new-product',
            'price': '15.00',
            'stock': 50,
            'category': self.category.id,
            'is_active': True
        }
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Product.objects.filter(slug='new-product').exists())
    
    def test_product_soft_delete(self):
        """Test product soft delete functionality"""
        self.authenticate_admin()
        url = reverse('api:admin-products-detail', kwargs={'pk': self.product.pk})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.product.refresh_from_db()
        self.assertIsNotNone(self.product.deleted_at)
    
    def test_product_stats_endpoint(self):
        """Test product statistics endpoint"""
        self.authenticate_admin()
        url = reverse('api:admin-products-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_products', response.data)
        self.assertIn('active_products', response.data)


class DashboardStatsAPITest(BaseAdminAPITestCase):
    """Test Dashboard Statistics API"""
    
    def setUp(self):
        super().setUp()
        # Create test data
        self.category = ProductCategory.objects.create(
            name_uz='Test Category',
            name_ru='Тест категория',
            name_en='Test Category'
        )
        
        self.product = Product.objects.create(
            name_uz='Test Product',
            name_ru='Тест продукт',
            name_en='Test Product',
            slug='test-product',
            price=Decimal('10.00'),
            stock=100,
            category=self.category
        )
        
        # Create course application
        CourseApplication.objects.create(
            full_name='Test User',
            email='test@example.com',
            phone_number='+998901234567',
            course_name='Python Course'
        )
        
        # Create franchise application
        FranchiseApplication.objects.create(
            full_name='Franchise User',
            phone='+998901234567',
            city='Tashkent',
            investment_amount=Decimal('50000.00')
        )
    
    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        self.authenticate_admin()
        url = reverse('api:admin-dashboard')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response structure
        self.assertIn('users', response.data)
        self.assertIn('products', response.data)
        self.assertIn('orders', response.data)
        self.assertIn('courses', response.data)
        self.assertIn('franchises', response.data)
        self.assertIn('revenue', response.data)
        
        # Check user stats
        self.assertEqual(response.data['users']['total'], 2)  # admin + regular
        
        # Check product stats
        self.assertEqual(response.data['products']['total'], 1)
        
        # Check course stats
        self.assertEqual(response.data['courses']['total_applications'], 1)
        
        # Check franchise stats
        self.assertEqual(response.data['franchises']['total_applications'], 1)
    
    def test_applications_stats(self):
        """Test applications statistics endpoint"""
        self.authenticate_admin()
        url = reverse('api:admin-applications-stats')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check response structure
        self.assertIn('course_applications', response.data)
        self.assertIn('franchise_applications', response.data)
        
        # Check course applications
        self.assertEqual(response.data['course_applications']['total'], 1)
        self.assertEqual(response.data['course_applications']['pending'], 1)
        
        # Check franchise applications
        self.assertEqual(response.data['franchise_applications']['total'], 1)
        self.assertEqual(response.data['franchise_applications']['pending'], 1)


class FilteringAndSearchTest(BaseAdminAPITestCase):
    """Test filtering and search functionality"""
    
    def setUp(self):
        super().setUp()
        # Create test users with different attributes
        User.objects.create_user(
            username='verified_user',
            email='verified@test.com',
            password='pass123',
            is_verified=True
        )
        
        User.objects.create_user(
            username='staff_user',
            email='staff@test.com',
            password='pass123',
            is_staff=True
        )
    
    def test_user_filtering(self):
        """Test user filtering by various fields"""
        self.authenticate_admin()
        url = reverse('api:admin-users-list')
        
        # Filter by is_staff
        response = self.client.get(url, {'is_staff': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # admin + staff_user
        
        # Filter by is_verified
        response = self.client.get(url, {'is_verified': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)  # verified_user
    
    def test_user_search(self):
        """Test user search functionality"""
        self.authenticate_admin()
        url = reverse('api:admin-users-list')
        
        # Search by username
        response = self.client.get(url, {'search': 'verified'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Search by email
        response = self.client.get(url, {'search': 'staff@test.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_user_ordering(self):
        """Test user ordering functionality"""
        self.authenticate_admin()
        url = reverse('api:admin-users-list')
        
        # Order by username
        response = self.client.get(url, {'ordering': 'username'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        usernames = [user['username'] for user in response.data['results']]
        self.assertEqual(usernames, sorted(usernames))
        
        # Order by date_joined descending
        response = self.client.get(url, {'ordering': '-date_joined'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should return results (exact order checking depends on creation timing)


class PaginationTest(BaseAdminAPITestCase):
    """Test pagination functionality"""
    
    def setUp(self):
        super().setUp()
        # Create multiple users for pagination testing
        for i in range(25):
            User.objects.create_user(
                username=f'user{i}',
                email=f'user{i}@test.com',
                password='pass123'
            )
    
    def test_pagination(self):
        """Test pagination works correctly"""
        self.authenticate_admin()
        url = reverse('api:admin-users-list')
        
        # First page
        response = self.client.get(url, {'page': 1})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('count', response.data)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertIn('results', response.data)
        
        # Check total count
        self.assertEqual(response.data['count'], 27)  # 25 + admin + regular user
        
        # Check page size (default should be 20)
        self.assertEqual(len(response.data['results']), 20)
        
        # Second page
        response = self.client.get(url, {'page': 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 7)  # Remaining users


# Run tests
if __name__ == '__main__':
    pytest.main([__file__])
