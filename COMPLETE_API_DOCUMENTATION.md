# Organic Green API - Complete Documentation

**Production-Ready REST API Documentation for Frontend Development**  
*Version 1.0.0 - Professional Backend API with Comprehensive Features*

## Base URLs
```
URL: http://api.organicgreen.uz/api/
```

## Quick Start for Frontend Developers

### 1. Authentication Flow
```javascript
// 1. Register user
const register = await fetch('http://api.organicgreen.uz/api/auth/register/simple/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username: 'user123', password: 'password123' })
});

// 2. Get tokens from response
const { tokens, user } = await register.json();
localStorage.setItem('access_token', tokens.access);
localStorage.setItem('refresh_token', tokens.refresh);

// 3. Use token in subsequent requests
const response = await fetch('http://api.organicgreen.uz/api/products/', {
    headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` }
});
```

### 2. Basic Product Fetching
```javascript
// Get all products with pagination
const products = await fetch('http://api.organicgreen.uz/api/products/');
const data = await products.json();

// Response structure:
{
    "count": 150,
    "next": "http://api.organicgreen.uz/api/products/?page=2",
    "previous": null,
    "results": [...products array...]
}
```

---

## Core Features

- **JWT Authentication** with automatic token refresh
- **Pagination** on all list endpoints (20 items per page, configurable)
- **Multi-language Support** (Uzbek, Russian, English)
- **Advanced Filtering & Search** capabilities
- **Professional Error Handling** with detailed messages
- **Rate Limiting** and request throttling
- **CORS Enabled** for cross-origin requests
- **Session-based Cart** for anonymous users
- **Favorites/Wishlist** system for authenticated users

---

## Authentication System

### JWT Token Structure
- **Access Token**: Valid for 60 minutes
- **Refresh Token**: Valid for 7 days
- **Header Format**: `Authorization: Bearer <access_token>`

### 1. Simple Registration
**POST** `http://api.organicgreen.uz/api/auth/register/simple/`

**Request Body:**
```json
{
    "username": "johndoe",
    "password": "password123"
}
```

**Success Response (201):**
```json
{
    "message": "Foydalanuvchi muvaffaqiyatli ro'yxatdan o'tdi",
    "user": {
        "id": 15,
        "username": "johndoe",
        "email": "",
        "first_name": "",
        "last_name": "",
        "date_joined": "2025-01-15T10:30:00Z"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### 2. Full Registration
**POST** `http://api.organicgreen.uz/api/auth/register/`

**Request Body:**
```json
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "John",
    "last_name": "Doe"
}
```

### 3. Login
**POST** `http://api.organicgreen.uz/api/auth/login/`

**Request Body:**
```json
{
    "username": "johndoe",
    "password": "password123"
}
```

**Success Response (200):**
```json
{
    "message": "Tizimga muvaffaqiyatli kirildi",
    "user": {
        "id": 15,
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### 4. Token Refresh
**POST** `http://api.organicgreen.uz/api/auth/token/refresh/`

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 5. User Profile
**GET** `http://api.organicgreen.uz/api/auth/profile/`
**Authentication Required**

**Success Response (200):**
```json
{
    "id": 15,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "date_joined": "2025-01-15T10:30:00Z",
    "last_login": "2025-01-15T14:20:00Z"
}
```

### 6. Update Profile
**PUT/PATCH** `http://api.organicgreen.uz/api/auth/profile/`
**Authentication Required**

### 7. Change Password
**POST** `http://api.organicgreen.uz/api/auth/change-password/`
**Authentication Required**

**Request Body:**
```json
{
    "old_password": "oldpassword123",
    "new_password": "newpassword123",
    "new_password_confirm": "newpassword123"
}
```

### 8. Logout
**POST** `http://api.organicgreen.uz/api/auth/logout/`
**Authentication Required**

**Request Body:**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### 9. Check Auth Status
**GET** `http://api.organicgreen.uz/api/auth/status/`
**Authentication Required**

---

## Products API

### Pagination System
All list endpoints use **PageNumberPagination**:

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

**Pagination Response:**
```json
{
    "count": 150,
    "next": "http://api.organicgreen.uz/api/products/?page=2",
    "previous": null,
    "page_size": 20,
    "total_pages": 8,
    "current_page": 1,
    "results": [...]
}
```

### 1. List Products (with Advanced Filtering)
**GET** `http://api.organicgreen.uz/api/products/`

**Query Parameters:**
- `page`: Page number
- `page_size`: Items per page (max 100)
- `search`: Search in product names and descriptions
- `category`: Filter by category ID
- `tags`: Filter by tag IDs (multiple: `tags=1,2,3`)
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter
- `in_stock`: Filter by stock availability (`true`/`false`)
- `featured`: Filter featured products (`true`/`false`)
- `on_sale`: Filter products on sale (`true`/`false`)
- `ordering`: Order by (`created_at`, `price`, `name_uz`, `stock`, `is_featured`)
- `lang`: Language for localized content (`uz`/`ru`/`en`)

**Example Request:**
```
GET http://api.organicgreen.uz/api/products/?category=1&featured=true&lang=uz&page=1
```

**Success Response (200):**
```json
{
    "count": 25,
    "next": "http://api.organicgreen.uz/api/products/?page=2",
    "previous": null,
    "page_size": 20,
    "total_pages": 2,
    "current_page": 1,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "slug": "organic-tomatoes",
            "name_uz": "Organik pomidorlar",
            "name_ru": "Органические помидоры",
            "name_en": "Organic Tomatoes",
            "category": "Vegetables",
            "category_name": "Sabzavotlar",
            "price": "25000.00",
            "sale_price": "20000.00",
            "final_price": "20000.00",
            "is_on_sale": true,
            "stock": 100,
            "available_stock": 100,
            "tags": [
                {
                    "id": 1,
                    "name": "Organik"
                }
            ],
            "is_featured": true,
            "primary_image": {
                "id": 1,
                "image": "http://api.organicgreen.uz/media/products/tomatoes.jpg",
                "alt_text_uz": "Organik pomidorlar"
            },
            "images_count": 3,
            "created_at": "2025-01-15T10:30:00Z"
        }
    ]
}
```

### 2. Get Product Details
**GET** `http://api.organicgreen.uz/api/products/{id}/`
**GET** `http://api.organicgreen.uz/api/products/{slug}/`

**Success Response (200):**
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "slug": "organic-tomatoes",
    "name_uz": "Organik pomidorlar",
    "name_ru": "Органические помидоры",
    "name_en": "Organic Tomatoes",
    "localized_name": "Organik pomidorlar",
    "description_uz": "Eng sifatli organik pomidorlar...",
    "description_ru": "Лучшие органические помидоры...",
    "description_en": "The finest organic tomatoes...",
    "localized_description": "Eng sifatli organik pomidorlar...",
    "category": {
        "id": 1,
        "name": "Vegetables",
        "description": "Fresh organic vegetables"
    },
    "localized_category_name": "Sabzavotlar",
    "tags": [
        {
            "id": 1,
            "name": "Organic"
        }
    ],
    "localized_tags": ["Organik"],
    "price": "25000.00",
    "sale_price": "20000.00",
    "final_price": "20000.00",
    "is_on_sale": true,
    "stock": 100,
    "available_stock": 100,
    "is_active": true,
    "is_featured": true,
    "suggested_products": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "name_uz": "Organik bodring",
            "slug": "organic-cucumber",
            "price": "15000.00"
        }
    ],
    "images": [
        {
            "id": 1,
            "image": "http://api.organicgreen.uz/media/products/tomatoes.jpg",
            "image_url": "http://api.organicgreen.uz/media/products/tomatoes.jpg",
            "alt_text_uz": "Organik pomidorlar",
            "is_primary": true,
            "order": 1
        }
    ],
    "primary_image": {
        "id": 1,
        "image": "http://api.organicgreen.uz/media/products/tomatoes.jpg",
        "alt_text_uz": "Organik pomidorlar"
    },
    "images_count": 3,
    "display_name": "Organik pomidorlar",
    "created_at": "2025-01-15T10:30:00Z",
    "updated_at": "2025-01-15T12:45:00Z"
}
```

### 3. Create Product (Admin Only)
**POST** `http://api.organicgreen.uz/api/products/`
**Authentication Required: Admin**

**Request Body:**
```json
{
    "name_uz": "Yangi mahsulot",
    "name_ru": "Новый продукт",
    "name_en": "New Product",
    "description_uz": "Mahsulot tavsifi...",
    "description_ru": "Описание продукта...",
    "description_en": "Product description...",
    "category_id": 1,
    "tag_ids": [1, 2],
    "price": "25000.00",
    "sale_price": "20000.00",
    "stock": 100,
    "is_active": true,
    "is_featured": false
}
```

### 4. Featured Products
**GET** `http://api.organicgreen.uz/api/products/featured/`

### 5. Products On Sale
**GET** `http://api.organicgreen.uz/api/products/on_sale/`

### 6. Product Statistics (Admin Only)
**GET** `http://api.organicgreen.uz/api/products/stats/`
**Authentication Required: Admin**

**Success Response (200):**
```json
{
    "total_products": 150,
    "active_products": 145,
    "featured_products": 25,
    "out_of_stock": 5,
    "low_stock": 12,
    "on_sale": 18,
    "categories_count": 8,
    "tags_count": 15,
    "average_price": 35000.00,
    "total_stock_value": 5250000.00
}
```

### 7. Suggested Products
**GET** `http://api.organicgreen.uz/api/products/{id}/suggested/`

---

## Categories API

### 1. List Categories
**GET** `http://api.organicgreen.uz/api/categories/`

**Query Parameters:**
- `page`: Page number
- `page_size`: Items per page
- `search`: Search in category names
- `ordering`: Order by (`created_at`, `name_uz`)

**Success Response (200):**
```json
{
    "count": 8,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Vegetables",
            "description": "Fresh organic vegetables",
            "image": "http://api.organicgreen.uz/media/categories/vegetables.jpg",
            "is_active": true,
            "products_count": 45,
            "created_at": "2025-01-15T10:30:00Z"
        }
    ]
}
```

### 2. Category Details
**GET** `http://api.organicgreen.uz/api/categories/{id}/`

### 3. Category Products
**GET** `http://api.organicgreen.uz/api/categories/{id}/products/`

**Query Parameters:**
- `page`: Page number
- `page_size`: Items per page
- `lang`: Language (`uz`/`ru`/`en`)

---

## Tags API

### 1. List Tags
**GET** `http://api.organicgreen.uz/api/tags/`

### 2. Tag Products
**GET** `http://api.organicgreen.uz/api/tags/{id}/products/`

---

## Cart API (Shopping Cart)

### Features
- **Session-based** for anonymous users
- **User-associated** for authenticated users
- **Automatic migration** from session to user cart on login
- **Stock validation** before adding items
- **Price calculation** with discounts

### 1. Get Current Cart
**GET** `http://api.organicgreen.uz/api/cart/current/`

**Success Response (200):**
```json
{
    "id": 123,
    "items": [
        {
            "id": 456,
            "product": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name_uz": "Organik pomidorlar",
                "price": "25000.00",
                "sale_price": "20000.00",
                "final_price": "20000.00",
                "image": "http://api.organicgreen.uz/media/products/tomatoes.jpg",
                "stock": 100
            },
            "quantity": 2,
            "unit_price": "20000.00",
            "total_price": "40000.00",
            "added_at": "2025-01-15T10:30:00Z"
        }
    ],
    "total_items": 2,
    "total_amount": "40000.00",
    "created_at": "2025-01-15T10:00:00Z",
    "updated_at": "2025-01-15T10:30:00Z"
}
```

### 2. Add Item to Cart
**POST** `http://api.organicgreen.uz/api/cart/add_item/`

**Request Body:**
```json
{
    "product_id": "550e8400-e29b-41d4-a716-446655440000",
    "quantity": 2
}
```

**Success Response (201):**
```json
{
    "message": "Mahsulot savatga qo'shildi",
    "item": {
        "id": 456,
        "product": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name_uz": "Organik pomidorlar"
        },
        "quantity": 2,
        "unit_price": "20000.00",
        "total_price": "40000.00"
    },
    "cart_total": "40000.00"
}
```

### 3. Update Item Quantity
**PATCH** `http://api.organicgreen.uz/api/cart/update_item/`

**Request Body:**
```json
{
    "item_id": 456,
    "quantity": 3
}
```

### 4. Remove Item from Cart
**DELETE** `http://api.organicgreen.uz/api/cart/remove_item/`

**Request Body:**
```json
{
    "item_id": 456
}
```

### 5. Clear Cart
**DELETE** `http://api.organicgreen.uz/api/cart/clear/`

### 6. Cart Summary
**GET** `http://api.organicgreen.uz/api/cart/summary/`

**Success Response (200):**
```json
{
    "total_items": 3,
    "total_amount": "85000.00",
    "total_savings": "15000.00",
    "items_count": 2
}
```

### 7. Cart History
**GET** `http://api.organicgreen.uz/api/cart/history/`
**Authentication Required**

---

## Favorites API (Wishlist)

### Features
- **User-specific** favorites list
- **Duplicate prevention** (unique constraint)
- **Bulk operations** support
- **Statistics tracking**
- **Product availability** checking

### 1. List User Favorites
**GET** `http://api.organicgreen.uz/api/favorites/`
**Authentication Required**

**Query Parameters:**
- `page`: Page number
- `page_size`: Items per page
- `search`: Search in favorite product names
- `category`: Filter by product category
- `available_only`: Show only available products (`true`/`false`)

**Success Response (200):**
```json
{
    "count": 15,
    "next": "http://api.organicgreen.uz/api/favorites/?page=2",
    "previous": null,
    "results": [
        {
            "id": 789,
            "product": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "name_uz": "Organik pomidorlar",
                "name_ru": "Органические помидоры",
                "name_en": "Organic Tomatoes",
                "slug": "organic-tomatoes",
                "price": "25000.00",
                "sale_price": "20000.00",
                "final_price": "20000.00",
                "stock": 100,
                "is_active": true,
                "is_featured": true,
                "image": "http://api.organicgreen.uz/media/products/tomatoes.jpg",
                "category_name": "Sabzavotlar",
                "is_on_sale": true,
                "created_at": "2025-01-15T10:30:00Z"
            },
            "created_at": "2025-01-15T14:20:00Z"
        }
    ]
}
```

### 2. Add to Favorites
**POST** `http://api.organicgreen.uz/api/favorites/`
**Authentication Required**

**Request Body:**
```json
{
    "product_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Success Response (201):**
```json
{
    "message": "Mahsulot sevimlilarga qo'shildi",
    "favorite": {
        "id": 789,
        "product": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name_uz": "Organik pomidorlar",
            "final_price": "20000.00"
        },
        "created_at": "2025-01-15T14:20:00Z"
    }
}
```

### 3. Remove from Favorites
**DELETE** `http://api.organicgreen.uz/api/favorites/{id}/`
**Authentication Required**

**Success Response (204):**
```json
{
    "message": "Mahsulot sevimlilardan o'chirildi"
}
```

### 4. Check if Product is Favorited
**GET** `http://api.organicgreen.uz/api/favorites/check/?product_id={product_id}`
**Authentication Required**

**Success Response (200):**
```json
{
    "is_favorited": true,
    "favorite_id": 789,
    "created_at": "2025-01-15T14:20:00Z"
}
```

### 5. Toggle Favorite Status
**POST** `http://api.organicgreen.uz/api/favorites/toggle/`
**Authentication Required**

**Request Body:**
```json
{
    "product_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Success Response (200):**
```json
{
    "action": "added",
    "message": "Mahsulot sevimlilarga qo'shildi",
    "is_favorited": true,
    "favorite_id": 789
}
```

### 6. Clear All Favorites
**DELETE** `http://api.organicgreen.uz/api/favorites/clear/`
**Authentication Required**

**Success Response (200):**
```json
{
    "message": "Barcha sevimli mahsulotlar o'chirildi",
    "deleted_count": 15
}
```

### 7. Favorites Statistics
**GET** `http://api.organicgreen.uz/api/favorites/stats/`
**Authentication Required**

**Success Response (200):**
```json
{
    "total_favorites": 15,
    "available_favorites": 12,
    "out_of_stock_favorites": 3,
    "on_sale_favorites": 5,
    "total_value": "375000.00",
    "average_price": "25000.00",
    "categories": {
        "Vegetables": 8,
        "Fruits": 4,
        "Herbs": 3
    }
}
```

### 8. Bulk Add to Favorites
**POST** `http://api.organicgreen.uz/api/favorites/bulk_add/`
**Authentication Required**

**Request Body:**
```json
{
    "product_ids": [
        "550e8400-e29b-41d4-a716-446655440000",
        "550e8400-e29b-41d4-a716-446655440001",
        "550e8400-e29b-41d4-a716-446655440002"
    ]
}
```

### 9. Move Favorites to Cart
**POST** `http://api.organicgreen.uz/api/favorites/move_to_cart/`
**Authentication Required**

**Request Body:**
```json
{
    "favorite_ids": [789, 790, 791],
    "remove_from_favorites": true
}
```

---

## Error Handling

### Error Response Format
All API errors follow this consistent format:

```json
{
    "error": "Brief error message",
    "detail": "Detailed error description",
    "field_errors": {
        "field_name": ["Field-specific error message"]
    },
    "status_code": 400
}
```

### HTTP Status Codes
- **200 OK**: Successful GET/PUT/PATCH
- **201 Created**: Successful POST
- **204 No Content**: Successful DELETE
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **403 Forbidden**: Permission denied
- **404 Not Found**: Resource not found
- **429 Too Many Requests**: Rate limit exceeded
- **500 Internal Server Error**: Server error

### Authentication Errors
```json
{
    "detail": "Given token not valid for any token type",
    "code": "token_not_valid",
    "messages": [
        {
            "token_class": "AccessToken",
            "token_type": "access",
            "message": "Token is invalid or expired"
        }
    ]
}
```

### Validation Errors
```json
{
    "username": ["Bu nom allaqachon mavjud."],
    "password": ["Parol juda qisqa."],
    "email": ["Email format noto'g'ri."]
}
```

---

## Rate Limiting

### Limits by User Type
- **Anonymous Users**: 100 requests per hour
- **Authenticated Users**: 1000 requests per hour
- **Admin Users**: Unlimited

### Rate Limit Headers
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642694400
```

---

## Language Support

### Supported Languages
- **uz**: Uzbek (default)
- **ru**: Russian
- **en**: English

### Usage
Add `lang` parameter to any request:
```
GET http://api.organicgreen.uz/api/products/?lang=ru
```

### Localized Fields
All products, categories, and tags have localized fields:
- `name_uz`, `name_ru`, `name_en`
- `description_uz`, `description_ru`, `description_en`

---

## Frontend Integration Examples

### React Hook for API Calls
```javascript
import { useState, useEffect } from 'react';

const useApi = (url, options = {}) => {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchData = async () => {
            try {
                const token = localStorage.getItem('access_token');
                const response = await fetch(`http://api.organicgreen.uz${url}`, {
                    ...options,
                    headers: {
                        'Content-Type': 'application/json',
                        ...(token && { 'Authorization': `Bearer ${token}` }),
                        ...options.headers
                    }
                });

                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }

                const result = await response.json();
                setData(result);
            } catch (err) {
                setError(err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [url]);

    return { data, loading, error };
};

// Usage
const ProductList = () => {
    const { data, loading, error } = useApi('/api/products/');
    
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    
    return (
        <div>
            {data.results.map(product => (
                <div key={product.id}>{product.name_uz}</div>
            ))}
        </div>
    );
};
```

### API Service Class
```javascript
class OrganicGreenAPI {
    constructor() {
        this.baseURL = 'http://api.organicgreen.uz/api';
        this.token = localStorage.getItem('access_token');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...(this.token && { 'Authorization': `Bearer ${this.token}` })
            },
            ...options
        };

        const response = await fetch(url, config);
        
        if (response.status === 401) {
            // Token expired, try refresh
            await this.refreshToken();
            return this.request(endpoint, options);
        }

        return response.json();
    }

    async refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            window.location.href = '/login';
            return;
        }

        const response = await fetch(`${this.baseURL}/auth/token/refresh/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken })
        });

        if (response.ok) {
            const { access } = await response.json();
            localStorage.setItem('access_token', access);
            this.token = access;
        } else {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
        }
    }

    // Products
    async getProducts(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`/products/?${query}`);
    }

    async getProduct(id) {
        return this.request(`/products/${id}/`);
    }

    // Favorites
    async getFavorites() {
        return this.request('/favorites/');
    }

    async addToFavorites(productId) {
        return this.request('/favorites/', {
            method: 'POST',
            body: JSON.stringify({ product_id: productId })
        });
    }

    async removeFromFavorites(favoriteId) {
        return this.request(`/favorites/${favoriteId}/`, {
            method: 'DELETE'
        });
    }

    // Cart
    async getCart() {
        return this.request('/cart/current/');
    }

    async addToCart(productId, quantity = 1) {
        return this.request('/cart/add_item/', {
            method: 'POST',
            body: JSON.stringify({ product_id: productId, quantity })
        });
    }
}

// Usage
const api = new OrganicGreenAPI();

// Get products
const products = await api.getProducts({ category: 1, featured: true });

// Add to favorites
await api.addToFavorites('550e8400-e29b-41d4-a716-446655440000');

// Add to cart
await api.addToCart('550e8400-e29b-41d4-a716-446655440000', 2);
```

### Pagination Component
```javascript
const PaginationComponent = ({ data, onPageChange }) => {
    const { count, next, previous, current_page, total_pages } = data;

    return (
        <div className="pagination">
            <span>Showing {data.results.length} of {count} items</span>
            
            {previous && (
                <button onClick={() => onPageChange(current_page - 1)}>
                    Previous
                </button>
            )}
            
            <span>Page {current_page} of {total_pages}</span>
            
            {next && (
                <button onClick={() => onPageChange(current_page + 1)}>
                    Next
                </button>
            )}
        </div>
    );
};
```

---

## Testing Endpoints

### Health Check
**GET** `http://api.organicgreen.uz/api/health/`

```json
{
    "status": "healthy",
    "timestamp": "2025-01-15T12:45:00Z",
    "version": "1.0.0",
    "message": "Products API is running successfully"
}
```

### API Documentation
**GET** `http://api.organicgreen.uz/api/`

Returns complete API documentation in JSON format.

---

## Security & Best Practices

### Security Headers
- **http Only** in production
- **Secure Cookie** settings
- **CORS** properly configured
- **Content Security Policy** enabled

### Authentication Best Practices
- Store tokens in **httpOnly cookies** (recommended) or **localStorage**
- Implement **automatic token refresh**
- Handle **401 errors** gracefully
- **Logout** on token expiration

### Error Handling
```javascript
const handleApiError = (error) => {
    if (error.status === 401) {
        // Redirect to login
        window.location.href = '/login';
    } else if (error.status === 403) {
        // Show permission denied message
        alert('Sizda bu amalni bajarish uchun ruxsat yo\'q');
    } else if (error.status >= 500) {
        // Show server error message
        alert('Server xatosi. Iltimos, keyinroq urinib ko\'ring');
    }
};
```

---

## Performance Optimization

### Caching
- **Response caching**: 15 minutes for product lists
- **Browser caching**: Enabled for static assets
- **Database optimization**: Proper indexing and query optimization

### Pagination
- Use **page_size** parameter to control response size
- Maximum **100 items per page**
- **count** field shows total items

### Image Optimization
- Product images are **automatically optimized**
- **Multiple sizes** available for different use cases
- **WebP format** support for modern browsers

---

## Contact & Support

### Base URL
- **Production**: `http://api.organicgreen.uz/api/`
- **Documentation**: `http://api.organicgreen.uz/api/`

### API Version
- **Current Version**: 1.0.0
- **Versioning**: Not yet implemented (will use URL versioning in future)

### Support
For API support and questions, please contact the development team.

---

*This documentation is designed for frontend developers integrating with the Organic Green e-commerce backend API. All endpoints are production-ready and follow REST API best practices.*
