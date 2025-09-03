# 🛒 Organic Green API - Test Data & Endpoints Summary

## ✅ Successfully Created Test Data

### 👥 Test Users
- **testuser1**: Anvar Karimov (verified user) - Password: `testpass123`
- **testuser2**: Malika Nazarova (unverified user) - Password: `testpass123`  
- **admin**: Superuser - Password: `admin` (simple password for testing)

### 📦 Product Categories (4 categories)
1. **Mevalar** (Fruits) - Fresh and delicious fruits
2. **Sabzavotlar** (Vegetables) - Organic vegetables  
3. **Yashilliklar** (Greens) - Fresh greens and herbs
4. **Yong'oqlar** (Nuts) - Dried fruits and nuts

### 🥬 Products (10 products)
#### Fruits:
- **Olma** (Apple) - 15,000 UZS (Sale: 12,000 UZS) - Stock: 100
- **Banan** (Banana) - 18,000 UZS - Stock: 80
- **Apelsin** (Orange) - 20,000 UZS (Sale: 17,000 UZS) - Stock: 60

#### Vegetables:
- **Kartoshka** (Potato) - 8,000 UZS - Stock: 200
- **Sabzi** (Carrot) - 10,000 UZS (Sale: 8,500 UZS) - Stock: 150
- **Pomidor** (Tomato) - 12,000 UZS - Stock: 120

#### Greens:
- **Jambil** (Dill) - 5,000 UZS - Stock: 50
- **Kashnich** (Cilantro) - 4,000 UZS (Sale: 3,500 UZS) - Stock: 40

#### Nuts:
- **Yong'oq** (Walnut) - 45,000 UZS (Sale: 40,000 UZS) - Stock: 30
- **Bodom** (Almond) - 55,000 UZS - Stock: 25

### 📋 Sample Orders (5 orders)
- Orders with different statuses: pending, paid, processing, shipped, delivered
- Mix of authenticated and anonymous users
- Various payment methods: cod, click, payme, card
- Order numbers in format: `OG-20250903-00002` to `OG-20250903-00006`

## 🌐 Available API Endpoints

### 🔗 Base URL: `http://localhost:8000/api`

### 📦 Products API
- `GET /products/` - List all products (paginated)
- `GET /products/{id}/` - Get product details
- `GET /products/categories/` - List all categories
- `GET /products/categories/{id}/` - Get category details

### 🛒 Cart API  
- `GET /cart/` - Get current cart
- `POST /cart/add_item/` - Add item to cart
- `PUT /cart/update_item/` - Update cart item quantity
- `DELETE /cart/remove_item/` - Remove item from cart
- `DELETE /cart/clear/` - Clear entire cart

### 📋 Orders API
- `GET /orders/` - List user's orders (paginated)
- `GET /orders/{id}/` - Get order details
- `POST /orders/create_order/` - Create order from cart
- `POST /orders/{id}/cancel/` - Cancel order
- `GET /orders/stats/` - Get order statistics
- `GET /orders/info/` - API information

### ❤️ Favorites API
- `GET /favorites/` - List user's favorites
- `POST /favorites/add/` - Add product to favorites
- `DELETE /favorites/remove/` - Remove from favorites

## 🧪 Testing Your APIs

### 1. Start the Development Server
```bash
docker exec django_og python3 manage.py runserver 0.0.0.0:8000
```

### 2. Test Anonymous User Flow

#### Get Products:
```bash
curl -X GET "http://localhost:8000/api/products/" \\
  -H "Content-Type: application/json"
```

#### Add Item to Cart (Anonymous):
```bash
curl -X POST "http://localhost:8000/api/cart/add_item/" \\
  -H "Content-Type: application/json" \\
  -H "X-Session-Key: test_session_123" \\
  -d '{"product_id": "PRODUCT_UUID_HERE", "quantity": 2}'
```

#### View Cart:
```bash
curl -X GET "http://localhost:8000/api/cart/" \\
  -H "X-Session-Key: test_session_123"
```

#### Create Order (Anonymous):
```bash
curl -X POST "http://localhost:8000/api/orders/create_order/" \\
  -H "Content-Type: application/json" \\
  -H "X-Session-Key: test_session_123" \\
  -d '{
    "full_name": "John Doe",
    "contact_phone": "+998901112233", 
    "delivery_address": "Tashkent, Chilonzor",
    "payment_method": "cod"
  }'
```

### 3. Test Authenticated User Flow

#### Login to get JWT token:
```bash
curl -X POST "http://localhost:8000/api/auth/login/" \\
  -H "Content-Type: application/json" \\
  -d '{"username": "testuser1", "password": "testpass123"}'
```

#### Use JWT token for authenticated requests:
```bash
curl -X GET "http://localhost:8000/api/orders/" \\
  -H "Authorization: Bearer YOUR_JWT_TOKEN_HERE"
```

### 4. Admin Interface
- URL: `http://localhost:8000/admin/`
- Login: `admin` / `admin`
- Manage orders, products, categories, and users

## 🔧 Available Management Commands

### Create Test Data:
```bash
docker exec django_og python3 manage.py create_test_data [--clear]
```

### Create Sample Orders:
```bash
docker exec django_og python3 manage.py create_sample_orders [--count 10]
```

### Other Useful Commands:
```bash
# Check system
docker exec django_og python3 manage.py check

# Create superuser
docker exec django_og python3 manage.py createsuperuser

# View migrations
docker exec django_og python3 manage.py showmigrations

# Collect static files
docker exec django_og python3 manage.py collectstatic --noinput
```

## 🎯 Key Features Implemented

### ✅ Multi-language Support
- All products and categories have Uzbek, Russian, and English names
- API responses include all language variants

### ✅ Anonymous User Support  
- Cart and favorites work without authentication
- Session-based tracking using `X-Session-Key` header
- Orders can be created by anonymous users

### ✅ Authenticated User Support
- JWT-based authentication
- User profile integration
- Order history and management

### ✅ Advanced Order Management
- Unique order numbers (OG-YYYYMMDD-00001 format)
- Order status tracking
- Payment method support
- Stock validation and reduction
- Order cancellation with business rules

### ✅ Professional Admin Interface
- Enhanced order management with inlines
- Customer information links
- Status badges and filtering
- Search and export capabilities

### ✅ Database Optimizations
- Proper indexing for performance
- Select/prefetch related for efficient queries
- UUID primary keys for security

## 🚀 Ready for Production

Your Orders API is now fully functional with:
- ✅ Complete CRUD operations
- ✅ Business logic validation  
- ✅ Security measures
- ✅ Test data for development
- ✅ Professional admin interface
- ✅ Comprehensive error handling
- ✅ Performance optimizations

The system is ready for frontend integration and production deployment!
