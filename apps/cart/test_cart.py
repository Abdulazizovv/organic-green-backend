"""
Test cases for Cart API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from apps.products.models import Product, ProductCategory
from apps.cart.models import Cart, CartItem
from decimal import Decimal
import uuid

User = get_user_model()

class CartAPITestCase(APITestCase):
    """Test cases for cart endpoints"""
    
    def setUp(self):
        """Set up test data"""
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test category
        self.category = ProductCategory.objects.create(
            name_uz='Test kategoriya',
            name_ru='Test category',
            name_en='Test category'
        )
        
        # Create test products
        self.product1 = Product.objects.create(
            name_uz='Test mahsulot 1',
            name_ru='Test product 1',
            name_en='Test product 1',
            description_uz='Test tavsif',
            price=Decimal('10000.00'),
            sale_price=Decimal('8000.00'),
            stock=100,
            category=self.category,
            is_active=True
        )
        
        self.product2 = Product.objects.create(
            name_uz='Test mahsulot 2',
            name_ru='Test product 2',
            name_en='Test product 2',
            description_uz='Test tavsif',
            price=Decimal('15000.00'),
            stock=50,
            category=self.category,
            is_active=True
        )
        
        # Cart URLs - router creates URLs with basename prefix
        self.cart_current_url = '/api/cart/current/'
        self.cart_add_item_url = '/api/cart/add_item/'
        self.cart_update_item_url = '/api/cart/update_item/'
        self.cart_remove_item_url = '/api/cart/remove_item/'
        self.cart_clear_url = '/api/cart/clear/'
        self.cart_summary_url = '/api/cart/summary/'
        self.cart_history_url = '/api/cart/history/'
    
    def authenticate_user(self):
        """Authenticate test user"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    
    def test_get_current_cart_anonymous(self):
        """Test getting current cart for anonymous user"""
        response = self.client.get(self.cart_current_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('items', response.data)
        self.assertEqual(response.data['total_items'], 0)
        self.assertTrue(response.data['is_empty'])
    
    def test_get_current_cart_authenticated(self):
        """Test getting current cart for authenticated user"""
        self.authenticate_user()
        
        response = self.client.get(self.cart_current_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['owner']['type'], 'registered')
        self.assertEqual(response.data['owner']['username'], 'testuser')
    
    def test_add_item_to_cart(self):
        """Test adding item to cart"""
        self.authenticate_user()  # Authenticate the user first
        
        data = {
            'product_id': str(self.product1.id),
            'quantity': 2
        }
        
        response = self.client.post(self.cart_add_item_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['item']['quantity'], 2)
        self.assertEqual(response.data['cart_summary']['total_items'], 2)
        
        # Check if item was created in database
        cart_items = CartItem.objects.filter(product=self.product1)
        self.assertEqual(cart_items.count(), 1)
        self.assertEqual(cart_items.first().quantity, 2)
    
    def test_add_item_invalid_product(self):
        """Test adding invalid product to cart"""
        data = {
            'product_id': str(uuid.uuid4()),
            'quantity': 1
        }
        
        response = self.client.post(self.cart_add_item_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)  # Changed from 404 to 400
        self.assertIn('product_id', response.data)  # Changed from 'error' to 'product_id'
    
    def test_add_item_insufficient_stock(self):
        """Test adding item with insufficient stock"""
        data = {
            'product_id': str(self.product2.id),
            'quantity': 1000  # More than available stock
        }
        
        response = self.client.post(self.cart_add_item_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data)  # Changed from 'error' to 'quantity'
    
    def test_add_same_item_twice(self):
        """Test adding same item twice (should set quantity, not add)"""
        self.authenticate_user()
        
        # Add item first time
        data = {
            'product_id': str(self.product1.id),
            'quantity': 2
        }
        self.client.post(self.cart_add_item_url, data)
        
        # Add same item again with different quantity (should set, not add)
        data['quantity'] = 3
        response = self.client.post(self.cart_add_item_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Mahsulot miqdori yangilandi')
        self.assertEqual(response.data['item']['quantity'], 3)  # Set to 3, not 2+3=5
        
        # Check database
        cart_item = CartItem.objects.get(product=self.product1)
        self.assertEqual(cart_item.quantity, 3)  # Should be 3, not 5
    
    def test_update_cart_item(self):
        """Test updating cart item quantity"""
        # First add item to cart
        self.client.post(self.cart_add_item_url, {
            'product_id': str(self.product1.id),
            'quantity': 2
        })
        
        cart_item = CartItem.objects.get(product=self.product1)
        
        # Update quantity
        data = {
            'item_id': str(cart_item.id),
            'quantity': 5
        }
        
        response = self.client.patch(self.cart_update_item_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item']['quantity'], 5)
        
        # Check database
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 5)
    
    def test_remove_cart_item(self):
        """Test removing item from cart"""
        # First add item to cart
        self.client.post(self.cart_add_item_url, {
            'product_id': str(self.product1.id),
            'quantity': 2
        })
        
        cart_item = CartItem.objects.get(product=self.product1)
        
        # Remove item
        response = self.client.delete(
            f"{self.cart_remove_item_url}?item_id={cart_item.id}"
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['cart_summary']['total_items'], 0)
        
        # Check if item was deleted
        self.assertFalse(CartItem.objects.filter(id=cart_item.id).exists())
    
    def test_clear_cart(self):
        """Test clearing all items from cart"""
        # Add multiple items to cart
        self.client.post(self.cart_add_item_url, {
            'product_id': str(self.product1.id),
            'quantity': 2
        })
        self.client.post(self.cart_add_item_url, {
            'product_id': str(self.product2.id),
            'quantity': 1
        })
        
        # Clear cart
        response = self.client.delete(self.cart_clear_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['cart_summary']['total_items'], 0)
        
        # Check if all items were deleted
        self.assertEqual(CartItem.objects.count(), 0)
    
    def test_cart_summary(self):
        """Test getting cart summary"""
        # Add items to cart
        self.client.post(self.cart_add_item_url, {
            'product_id': str(self.product1.id),
            'quantity': 2
        })
        self.client.post(self.cart_add_item_url, {
            'product_id': str(self.product2.id),
            'quantity': 1
        })
        
        response = self.client.get(self.cart_summary_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_items'], 3)
        self.assertEqual(response.data['items_count'], 2)
        self.assertGreater(float(response.data['total_price']), 0)  # Convert to float for comparison
        self.assertIn('items_summary', response.data)
        self.assertEqual(len(response.data['items_summary']), 2)
    
    def test_cart_with_sale_price(self):
        """Test cart calculations with sale prices"""
        # Product1 has sale price (8000 instead of 10000)
        self.client.post(self.cart_add_item_url, {
            'product_id': str(self.product1.id),
            'quantity': 1
        })
        
        response = self.client.get(self.cart_summary_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check if sale price is being used
        item_summary = response.data['items_summary'][0]
        self.assertTrue(item_summary['is_on_sale'])
        self.assertEqual(float(response.data['total_price']), 8000.0)
        self.assertEqual(float(response.data['total_discount']), 2000.0)  # 10000 - 8000
    
    def test_authenticated_user_cart_persistence(self):
        """Test that authenticated user's cart persists across sessions"""
        self.authenticate_user()
        
        # Add item to cart
        self.client.post(self.cart_add_item_url, {
            'product_id': str(self.product1.id),
            'quantity': 2
        })
        
        # Clear credentials (simulate logout)
        self.client.credentials()
        
        # Login again
        self.authenticate_user()
        
        # Check if cart is still there
        response = self.client.get(self.cart_current_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_items'], 2)
        
        # Check if the same cart exists in database
        cart = Cart.objects.get(user=self.user)
        self.assertEqual(cart.total_items, 2)
    
    def test_cart_validation_errors(self):
        """Test various validation errors"""
        # Test missing product_id
        response = self.client.post(self.cart_add_item_url, {'quantity': 1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test invalid quantity
        response = self.client.post(self.cart_add_item_url, {
            'product_id': str(self.product1.id),
            'quantity': 0
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test missing item_id for update
        response = self.client.patch(self.cart_update_item_url, {'quantity': 1})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Test missing item_id for remove
        response = self.client.delete(self.cart_remove_item_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_set_quantity_behavior(self):
        """Test that add_item sets quantity instead of adding"""
        self.authenticate_user()
        
        # Add item with quantity 5
        self.client.post(self.cart_add_item_url, {
            'product_id': str(self.product1.id),
            'quantity': 5
        })
        
        cart_item = CartItem.objects.get(product=self.product1)
        self.assertEqual(cart_item.quantity, 5)
        
        # "Add" same item with quantity 2 (should set to 2, not 5+2=7)
        response = self.client.post(self.cart_add_item_url, {
            'product_id': str(self.product1.id),
            'quantity': 2
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['message'], 'Mahsulot miqdori yangilandi')
        
        # Check that quantity is set to 2, not added
        cart_item.refresh_from_db()
        self.assertEqual(cart_item.quantity, 2)

    def test_stock_validation_proper_error(self):
        """Test that stock validation returns proper error format"""
        self.authenticate_user()
        
        # Try to add more than available stock
        data = {
            'product_id': str(self.product2.id),  # product2 has stock=50
            'quantity': 100  # More than available stock
        }
        
        response = self.client.post(self.cart_add_item_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('quantity', response.data)
        self.assertIn('Mahsulot omborda yetarli emas', response.data['quantity'][0])
        self.assertIn('50', response.data['quantity'][0])  # Should show available stock
