"""
Tests for Order app
"""
import pytest
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from apps.products.models import Product, ProductCategory
from apps.cart.models import Cart, CartItem
from apps.order.models import Order, OrderItem, OrderStatus

User = get_user_model()

@pytest.fixture
def api_client():
    """API client fixture"""
    return APIClient()


@pytest.fixture
def user():
    """User fixture"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def category():
    """Product category fixture"""
    return ProductCategory.objects.create(
        name_uz='Test Category',
        name_ru='Тест Категория',
        name_en='Test Category'
    )


@pytest.fixture
def product(category):
    """Product fixture"""
    return Product.objects.create(
        name_uz='Test Product',
        name_ru='Тест Продукт',
        name_en='Test Product',
        description_uz='Test description',
        category=category,
        price=Decimal('10000.00'),
        stock=50,
        is_active=True
    )


@pytest.fixture
def product_with_sale(category):
    """Product with sale price fixture"""
    return Product.objects.create(
        name_uz='Sale Product',
        name_ru='Продукт со скидкой',
        name_en='Sale Product',
        description_uz='Sale description',
        category=category,
        price=Decimal('15000.00'),
        sale_price=Decimal('12000.00'),
        stock=30,
        is_active=True
    )


def create_cart_with_items(user=None, session_key=None, products_data=None):
    """Helper to create cart with items"""
    if products_data is None:
        products_data = []
    
    cart = Cart.objects.create(
        user=user,
        session_key=session_key
    )
    
    for product, quantity in products_data:
        unit_price = product.sale_price if product.sale_price else product.price
        CartItem.objects.create(
            cart=cart,
            product=product,
            quantity=quantity,
            unit_price=unit_price
        )
    
    return cart


@pytest.mark.django_db
class TestOrderCreationAnonymous:
    """Test order creation for anonymous users"""
    
    def test_anonymous_create_order_from_session_cart(self, api_client, product, product_with_sale):
        """Test creating order from session cart for anonymous user"""
        # Create session
        api_client.session.create()
        session_key = api_client.session.session_key
        
        # Create cart with items
        cart = create_cart_with_items(
            session_key=session_key,
            products_data=[
                (product, 2),
                (product_with_sale, 1)
            ]
        )
        
        # Order data
        order_data = {
            'full_name': 'Anonymous User',
            'contact_phone': '+998901112233',
            'delivery_address': 'Toshkent, Chilonzor tumani',
            'notes': 'Ertalab yetkazing',
            'payment_method': 'cod'
        }
        
        # Create order
        response = api_client.post('/api/orders/create_order/', order_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        
        order_data = response.data['order']
        assert order_data['full_name'] == 'Anonymous User'
        assert order_data['contact_phone'] == '+998901112233'
        assert order_data['status'] == 'pending'
        assert order_data['total_items'] == 3
        assert Decimal(order_data['total_price']) == Decimal('32000.00')  # 2*10000 + 1*12000
        
        # Verify order in database
        order = Order.objects.get(id=order_data['id'])
        assert order.session_key == session_key
        assert order.user is None
        assert order.items.count() == 2
        
        # Verify cart is cleared
        cart.refresh_from_db()
        assert cart.items.count() == 0
        
        # Verify stock reduction
        product.refresh_from_db()
        product_with_sale.refresh_from_db()
        assert product.stock == 48  # 50 - 2
        assert product_with_sale.stock == 29  # 30 - 1
    
    def test_anonymous_order_empty_cart_error(self, api_client):
        """Test creating order with empty cart returns error"""
        # Create session but no cart items
        api_client.session.create()
        
        order_data = {
            'full_name': 'Test User',
            'contact_phone': '+998901112233',
            'delivery_address': 'Toshkent',
            'payment_method': 'cod'
        }
        
        response = api_client.post('/api/orders/create_order/', order_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'cart' in response.data
        assert 'bo\'sh' in response.data['cart'][0].lower()


@pytest.mark.django_db
class TestOrderCreationAuthenticated:
    """Test order creation for authenticated users"""
    
    def test_authenticated_create_order_from_user_cart(self, api_client, user, product):
        """Test creating order from user cart for authenticated user"""
        # Authenticate user
        api_client.force_authenticate(user=user)
        
        # Create cart with items
        cart = create_cart_with_items(
            user=user,
            products_data=[(product, 3)]
        )
        
        # Order data (should use user's profile data)
        order_data = {
            'delivery_address': 'Samarqand, Registon ko\'chasi',
            'payment_method': 'click'
        }
        
        response = api_client.post('/api/orders/create_order/', order_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        
        order_data = response.data['order']
        assert order_data['full_name'] == 'Test User'  # From user profile
        assert order_data['user'] == user.id
        assert order_data['status'] == 'pending'
        assert order_data['payment_method'] == 'click'
        
        # Verify order in database
        order = Order.objects.get(id=order_data['id'])
        assert order.user == user
        assert order.session_key is None
    
    def test_authenticated_user_missing_profile_requires_contact_data(self, api_client, product):
        """Test that user without profile data must provide contact info"""
        # Create user without profile data
        user = User.objects.create_user(
            username='noname',
            password='testpass123'
        )
        api_client.force_authenticate(user=user)
        
        # Create cart
        create_cart_with_items(
            user=user,
            products_data=[(product, 1)]
        )
        
        # Try to create order without contact info
        order_data = {
            'delivery_address': 'Test address'
        }
        
        response = api_client.post('/api/orders/create_order/', order_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'full_name' in response.data or 'contact_phone' in response.data


@pytest.mark.django_db
class TestOrderStockValidation:
    """Test stock validation during order creation"""
    
    def test_prevent_create_if_insufficient_stock(self, api_client, user, product):
        """Test preventing order creation when insufficient stock"""
        api_client.force_authenticate(user=user)
        
        # Set low stock
        product.stock = 1
        product.save()
        
        # Create cart with more items than in stock
        create_cart_with_items(
            user=user,
            products_data=[(product, 5)]
        )
        
        order_data = {
            'delivery_address': 'Test address'
        }
        
        response = api_client.post('/api/orders/create_order/', order_data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'stock' in response.data
        assert product.name_uz in str(response.data['stock'])
    
    def test_stock_reduction_on_create(self, api_client, user, product):
        """Test that product stock is reduced when order is created"""
        api_client.force_authenticate(user=user)
        
        initial_stock = product.stock
        quantity_ordered = 5
        
        # Create cart
        create_cart_with_items(
            user=user,
            products_data=[(product, quantity_ordered)]
        )
        
        order_data = {
            'delivery_address': 'Test address'
        }
        
        response = api_client.post('/api/orders/create_order/', order_data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Check stock reduction
        product.refresh_from_db()
        assert product.stock == initial_stock - quantity_ordered


@pytest.mark.django_db
class TestOrderOperations:
    """Test order operations (list, retrieve, cancel)"""
    
    def test_cancel_allowed_and_forbidden(self, api_client, user, product):
        """Test order cancellation rules"""
        api_client.force_authenticate(user=user)
        
        # Create order
        order = Order.objects.create(
            user=user,
            order_number='OG-20250903-00001',
            full_name='Test User',
            contact_phone='+998901112233',
            delivery_address='Test address',
            status=OrderStatus.PENDING,
            subtotal=Decimal('10000.00'),
            total_price=Decimal('10000.00'),
            total_items=1
        )
        
        # Test cancel when pending - should work
        response = api_client.post(f'/api/orders/{order.id}/cancel/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'canceled'
        
        # Test cancel when already canceled - should fail
        response = api_client.post(f'/api/orders/{order.id}/cancel/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        # Test cancel when delivered - should fail
        order.status = OrderStatus.DELIVERED
        order.save()
        
        response = api_client.post(f'/api/orders/{order.id}/cancel/')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_owner_access_only(self, api_client, user, product):
        """Test that only order owners can access orders"""
        # Create two users
        user2 = User.objects.create_user(
            username='user2',
            password='testpass123'
        )
        
        # Create order for user1
        order = Order.objects.create(
            user=user,
            order_number='OG-20250903-00001',
            full_name='Test User',
            contact_phone='+998901112233',
            delivery_address='Test address',
            subtotal=Decimal('10000.00'),
            total_price=Decimal('10000.00'),
            total_items=1
        )
        
        # User1 should be able to access their order
        api_client.force_authenticate(user=user)
        response = api_client.get(f'/api/orders/{order.id}/')
        assert response.status_code == status.HTTP_200_OK
        
        # User2 should not be able to access user1's order
        api_client.force_authenticate(user=user2)
        response = api_client.get(f'/api/orders/{order.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND  # Filtered out by queryset
    
    def test_anonymous_session_access_only(self, api_client, product):
        """Test anonymous users can only access their session orders"""
        # Create session 1
        api_client.session.create()
        session_key1 = api_client.session.session_key
        
        # Create order for session 1
        order1 = Order.objects.create(
            session_key=session_key1,
            order_number='OG-20250903-00001',
            full_name='Anonymous User 1',
            contact_phone='+998901112233',
            delivery_address='Test address',
            subtotal=Decimal('10000.00'),
            total_price=Decimal('10000.00'),
            total_items=1
        )
        
        # Should be able to access own order
        response = api_client.get(f'/api/orders/{order1.id}/')
        assert response.status_code == status.HTTP_200_OK
        
        # Create new session (simulate different user)
        api_client.session.flush()
        api_client.session.create()
        
        # Should not be able to access other session's order
        response = api_client.get(f'/api/orders/{order1.id}/')
        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestOrderNumberGeneration:
    """Test order number generation"""
    
    def test_order_number_format(self, user):
        """Test order number format and uniqueness"""
        today = timezone.now().date()
        expected_prefix = f"OG-{today.strftime('%Y%m%d')}-"
        
        # Create first order
        order1 = Order.objects.create(
            user=user,
            full_name='Test User',
            contact_phone='+998901112233',
            delivery_address='Test address',
            subtotal=Decimal('10000.00'),
            total_price=Decimal('10000.00'),
            total_items=1
        )
        
        assert order1.order_number.startswith(expected_prefix)
        assert order1.order_number.endswith('-00001')
        
        # Create second order
        order2 = Order.objects.create(
            user=user,
            full_name='Test User 2',
            contact_phone='+998901112234',
            delivery_address='Test address 2',
            subtotal=Decimal('15000.00'),
            total_price=Decimal('15000.00'),
            total_items=2
        )
        
        assert order2.order_number.startswith(expected_prefix)
        assert order2.order_number.endswith('-00002')
        
        # Verify uniqueness
        assert order1.order_number != order2.order_number


@pytest.mark.django_db
class TestOrderStats:
    """Test order statistics"""
    
    def test_order_stats(self, api_client, user):
        """Test order statistics endpoint"""
        api_client.force_authenticate(user=user)
        
        # Create orders with different statuses
        Order.objects.create(
            user=user,
            order_number='OG-20250903-00001',
            full_name='Test User',
            contact_phone='+998901112233',
            delivery_address='Test address',
            status=OrderStatus.PENDING,
            subtotal=Decimal('10000.00'),
            total_price=Decimal('10000.00'),
            total_items=1
        )
        
        Order.objects.create(
            user=user,
            order_number='OG-20250903-00002',
            full_name='Test User',
            contact_phone='+998901112233',
            delivery_address='Test address',
            status=OrderStatus.DELIVERED,
            subtotal=Decimal('25000.00'),
            total_price=Decimal('25000.00'),
            total_items=2
        )
        
        response = api_client.get('/api/orders/stats/')
        assert response.status_code == status.HTTP_200_OK
        
        stats = response.data
        assert stats['total_orders'] == 2
        assert stats['pending_orders'] == 1
        assert stats['completed_orders'] == 1
        assert stats['cancelled_orders'] == 0
        assert Decimal(stats['total_spent']) == Decimal('25000.00')  # Only delivered orders
