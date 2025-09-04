# Organic Green API Documentation / Dokumentatsiya

## Mundarija / Table of Contents
1. [Authentication (Foydalanuvchi Autentifikatsiyasi)](#authentication--user-management)
2. [Product Management (Mahsulot Boshqaruvi)](#product-management)
3. [Order Management (Buyurtma Boshqaruvi)](#order-management)
4. [Error Handling (Xatolarni Boshqarish)](#error-handling)
5. [Code Examples (Kod Misollari)](#code-examples)

## Base URL / Asosiy URL
```
http://localhost:8000/api/
```

**Muhim:** To'liq authentication dokumentatsiyasi uchun [AUTHENTICATION_DOCS.md](./AUTHENTICATION_DOCS.md) faylini ko'ring.

---

## Authentication & User Management

### User Registration

#### Simple Registration
**Endpoint:** `POST /auth/register/`
**Description:** Basic user registration with minimal fields

**Request Body:**
```json
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123"
}
```

**Response (201 Created):**
```json
{
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "",
        "last_name": "",
        "avatar_url": null,
        "phone": "",
        "is_verified": false,
        "date_joined": "2024-01-15T10:30:00Z"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### Full Registration
**Endpoint:** `POST /auth/register-full/`
**Description:** Complete user registration with all available fields

**Request Body:**
```json
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123",
    "password_confirm": "securepassword123",
    "first_name": "John",
    "last_name": "Doe",
    "phone": "+1234567890"
}
```

**Response (201 Created):**
```json
{
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "avatar_url": null,
        "phone": "+1234567890",
        "is_verified": false,
        "full_name": "John Doe",
        "display_name": "John Doe",
        "date_joined": "2024-01-15T10:30:00Z"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

### User Login

**Endpoint:** `POST /auth/login/`
**Description:** User authentication

**Request Body:**
```json
{
    "username": "johndoe",
    "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "avatar_url": "http://api.organicgreen.uz/media/avatars/johndoe_avatar.jpg",
        "phone": "+1234567890",
        "is_verified": true,
        "full_name": "John Doe",
        "display_name": "John Doe"
    }
}
```

### JWT Token Refresh

**Endpoint:** `POST /auth/token/`
**Description:** Get new access token using refresh token

**Request Body:**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "avatar_url": "http://api.organicgreen.uz/media/avatars/johndoe_avatar.jpg",
        "phone": "+1234567890",
        "is_verified": true
    }
}
```

### User Profile

#### Get Profile
**Endpoint:** `GET /auth/profile/`
**Authentication:** Bearer Token Required

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "avatar_url": "http://api.organicgreen.uz/media/avatars/johndoe_avatar.jpg",
    "phone": "+1234567890",
    "is_verified": true,
    "full_name": "John Doe",
    "display_name": "John Doe",
    "date_joined": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-16T08:15:00Z"
}
```

#### Update Profile
**Endpoint:** `PUT /auth/profile/` or `PATCH /auth/profile/`
**Authentication:** Bearer Token Required

**Request Body (PUT - all fields required):**
```json
{
    "first_name": "John",
    "last_name": "Smith",
    "email": "johnsmith@example.com",
    "phone": "+1234567890"
}
```

**Request Body (PATCH - partial update):**
```json
{
    "first_name": "John",
    "phone": "+9876543210"
}
```

**Response (200 OK):**
```json
{
    "id": 1,
    "username": "johndoe",
    "email": "johnsmith@example.com",
    "first_name": "John",
    "last_name": "Smith",
    "avatar_url": "http://api.organicgreen.uz/media/avatars/johndoe_avatar.jpg",
    "phone": "+9876543210",
    "is_verified": true,
    "full_name": "John Smith",
    "display_name": "John Smith",
    "date_joined": "2024-01-15T10:30:00Z"
}
```

### Avatar Management

#### Upload Avatar
**Endpoint:** `POST /auth/upload-avatar/`
**Authentication:** Bearer Token Required
**Content-Type:** `multipart/form-data`

**Request Body:**
```
avatar: [image file] (max 5MB, supported formats: jpg, jpeg, png, gif, webp)
```

**Response (200 OK):**
```json
{
    "message": "Avatar uploaded successfully",
    "avatar_url": "http://api.organicgreen.uz/media/avatars/johndoe_avatar.jpg"
}
```

**Error Response (400 Bad Request):**
```json
{
    "avatar": ["File size exceeds 5MB limit"]
}
```

#### Delete Avatar
**Endpoint:** `DELETE /auth/delete-avatar/`
**Authentication:** Bearer Token Required

**Response (200 OK):**
```json
{
    "message": "Avatar deleted successfully"
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "No avatar to delete"
}
```

### Account Verification

**Endpoint:** `POST /auth/verify/`
**Authentication:** Bearer Token Required

**Request Body:**
```json
{
    "verification_code": "123456"
}
```

**Response (200 OK):**
```json
{
    "message": "Account verified successfully",
    "is_verified": true
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "Invalid verification code"
}
```

### User Statistics

**Endpoint:** `GET /auth/stats/`
**Authentication:** Bearer Token Required

**Response (200 OK):**
```json
{
    "total_orders": 15,
    "completed_orders": 12,
    "pending_orders": 2,
    "cancelled_orders": 1,
    "total_spent": "1250.50",
    "average_order_value": "83.37",
    "member_since": "2024-01-15",
    "last_order_date": "2024-01-16"
}
```

### Change Password

**Endpoint:** `POST /auth/change-password/`
**Authentication:** Bearer Token Required

**Request Body:**
```json
{
    "old_password": "currentpassword123",
    "new_password": "newpassword456"
}
```

**Response (200 OK):**
```json
{
    "message": "Password changed successfully"
}
```

### Logout

**Endpoint:** `POST /auth/logout/`
**Authentication:** Bearer Token Required

**Request Body:**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

**Response (200 OK):**
```json
{
    "message": "Successfully logged out"
}
```

### Authentication Status Check

**Endpoint:** `GET /auth/check/`
**Authentication:** Bearer Token Required

**Response (200 OK):**
```json
{
    "authenticated": true,
    "user_id": 1,
    "username": "johndoe"
}
```

### Authentication Info

**Endpoint:** `GET /auth/info/`

**Response (200 OK):**
```json
{
    "authentication_required": true,
    "token_type": "Bearer",
    "login_url": "/api/auth/login/",
    "register_url": "/api/auth/register/"
}
```

---

## Product Management

### List Products

**Endpoint:** `GET /products/`

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)
- `category`: Filter by category ID
- `tag`: Filter by tag ID
- `search`: Search in name and description
- `min_price`: Minimum price filter
- `max_price`: Maximum price filter
- `in_stock`: Filter by stock availability (true/false)
- `ordering`: Sort order (name, -name, price, -price, created_at, -created_at)

**Example Request:**
```
GET /products/?category=1&min_price=10&max_price=100&ordering=-created_at&page=1&page_size=10
```

**Response (200 OK):**
```json
{
    "count": 150,
    "next": "http://api.organicgreen.uz/api/products/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Organic Apples",
            "description": "Fresh organic apples from local farms",
            "price": "5.99",
            "category": {
                "id": 1,
                "name": "Fruits",
                "description": "Fresh organic fruits"
            },
            "tags": [
                {
                    "id": 1,
                    "name": "Organic"
                },
                {
                    "id": 2,
                    "name": "Local"
                }
            ],
            "images": [
                {
                    "id": 1,
                    "image": "http://api.organicgreen.uz/media/products/apples.jpg",
                    "alt_text": "Organic Apples"
                }
            ],
            "stock_quantity": 50,
            "is_available": true,
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-01-16T08:15:00Z"
        }
    ]
}
```

### Get Single Product

**Endpoint:** `GET /products/{id}/`

**Response (200 OK):**
```json
{
    "id": 1,
    "name": "Organic Apples",
    "description": "Fresh organic apples from local farms. Grown without pesticides and harvested at peak ripeness.",
    "price": "5.99",
    "category": {
        "id": 1,
        "name": "Fruits",
        "description": "Fresh organic fruits"
    },
    "tags": [
        {
            "id": 1,
            "name": "Organic"
        },
        {
            "id": 2,
            "name": "Local"
        }
    ],
    "images": [
        {
            "id": 1,
            "image": "http://api.organicgreen.uz/media/products/apples.jpg",
            "alt_text": "Organic Apples"
        }
    ],
    "stock_quantity": 50,
    "is_available": true,
    "nutritional_info": {
        "calories_per_100g": 52,
        "protein": "0.3g",
        "carbs": "14g",
        "fiber": "2.4g"
    },
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-16T08:15:00Z"
}
```

### Product Categories

**Endpoint:** `GET /categories/`

**Response (200 OK):**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Fruits",
            "description": "Fresh organic fruits",
            "product_count": 25
        },
        {
            "id": 2,
            "name": "Vegetables",
            "description": "Organic vegetables",
            "product_count": 40
        }
    ]
}
```

### Product Tags

**Endpoint:** `GET /tags/`

**Response (200 OK):**
```json
{
    "count": 8,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name": "Organic",
            "product_count": 75
        },
        {
            "id": 2,
            "name": "Local",
            "product_count": 50
        }
    ]
}
```

---

## Order Management

### Create Order

**Endpoint:** `POST /orders/`
**Authentication:** Bearer Token Required

**Request Body:**
```json
{
    "shipping_address": "123 Main St, City, State 12345",
    "items": [
        {
            "product": 1,
            "quantity": 3
        },
        {
            "product": 5,
            "quantity": 2
        }
    ]
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "order_number": "ORD-2024-0001",
    "user": {
        "id": 1,
        "username": "johndoe",
        "full_name": "John Doe"
    },
    "status": "pending",
    "total_amount": "29.95",
    "shipping_address": "123 Main St, City, State 12345",
    "items": [
        {
            "id": 1,
            "product": {
                "id": 1,
                "name": "Organic Apples",
                "price": "5.99"
            },
            "quantity": 3,
            "price": "5.99",
            "total_price": "17.97"
        },
        {
            "id": 2,
            "product": {
                "id": 5,
                "name": "Organic Bananas",
                "price": "3.99"
            },
            "quantity": 2,
            "price": "3.99",
            "total_price": "7.98"
        }
    ],
    "created_at": "2024-01-16T10:30:00Z",
    "updated_at": "2024-01-16T10:30:00Z"
}
```

### List User Orders

**Endpoint:** `GET /orders/`
**Authentication:** Bearer Token Required

**Query Parameters:**
- `status`: Filter by order status (pending, processing, shipped, delivered, cancelled)
- `page`: Page number
- `page_size`: Items per page

**Response (200 OK):**
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "order_number": "ORD-2024-0001",
            "status": "delivered",
            "total_amount": "29.95",
            "created_at": "2024-01-16T10:30:00Z",
            "items_count": 2
        }
    ]
}
```

### Get Single Order

**Endpoint:** `GET /orders/{id}/`
**Authentication:** Bearer Token Required

**Response (200 OK):**
```json
{
    "id": 1,
    "order_number": "ORD-2024-0001",
    "user": {
        "id": 1,
        "username": "johndoe",
        "full_name": "John Doe"
    },
    "status": "delivered",
    "total_amount": "29.95",
    "shipping_address": "123 Main St, City, State 12345",
    "tracking_number": "TRK123456789",
    "items": [
        {
            "id": 1,
            "product": {
                "id": 1,
                "name": "Organic Apples",
                "price": "5.99",
                "image": "http://api.organicgreen.uz/media/products/apples.jpg"
            },
            "quantity": 3,
            "price": "5.99",
            "total_price": "17.97"
        }
    ],
    "created_at": "2024-01-16T10:30:00Z",
    "updated_at": "2024-01-18T14:20:00Z",
    "shipped_at": "2024-01-17T09:15:00Z",
    "delivered_at": "2024-01-18T14:20:00Z"
}
```

### Cancel Order

**Endpoint:** `POST /orders/{id}/cancel/`
**Authentication:** Bearer Token Required

**Response (200 OK):**
```json
{
    "message": "Order cancelled successfully",
    "status": "cancelled"
}
```

**Error Response (400 Bad Request):**
```json
{
    "error": "Order cannot be cancelled as it has already been shipped"
}
```

---

## Error Handling

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Access denied
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

### Error Response Format

**Validation Errors (400):**
```json
{
    "field_name": ["Error message for this field"],
    "another_field": ["Another error message"]
}
```

**Authentication Errors (401):**
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

**Permission Errors (403):**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

**Not Found Errors (404):**
```json
{
    "detail": "Not found."
}
```

---

## Code Examples

### JavaScript/Fetch API

#### Authentication Setup
```javascript
class ApiClient {
    constructor(baseURL = 'http://api.organicgreen.uz/api/') {
        this.baseURL = baseURL;
        this.token = localStorage.getItem('access_token');
    }

    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers,
            },
            ...options,
        };

        if (this.token && !config.headers.Authorization) {
            config.headers.Authorization = `Bearer ${this.token}`;
        }

        try {
            const response = await fetch(url, config);
            
            if (response.status === 401) {
                // Token expired, try to refresh
                await this.refreshToken();
                config.headers.Authorization = `Bearer ${this.token}`;
                return fetch(url, config);
            }
            
            return response;
        } catch (error) {
            console.error('API request failed:', error);
            throw error;
        }
    }

    async refreshToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            throw new Error('No refresh token available');
        }

        const response = await fetch(`${this.baseURL}auth/token/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ refresh: refreshToken }),
        });

        if (response.ok) {
            const data = await response.json();
            this.token = data.access;
            localStorage.setItem('access_token', data.access);
        } else {
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            throw new Error('Token refresh failed');
        }
    }
}

const api = new ApiClient();
```

#### User Registration
```javascript
async function registerUser(userData) {
    try {
        const response = await api.request('auth/register-full/', {
            method: 'POST',
            body: JSON.stringify(userData),
        });

        if (response.ok) {
            const data = await response.json();
            localStorage.setItem('access_token', data.tokens.access);
            localStorage.setItem('refresh_token', data.tokens.refresh);
            return data;
        } else {
            const errors = await response.json();
            throw new Error(JSON.stringify(errors));
        }
    } catch (error) {
        console.error('Registration failed:', error);
        throw error;
    }
}

// Usage
const newUser = {
    username: 'johndoe',
    email: 'john@example.com',
    password: 'securepassword123',
    password_confirm: 'securepassword123',
    first_name: 'John',
    last_name: 'Doe',
    phone: '+1234567890'
};

registerUser(newUser);
```

#### Avatar Upload
```javascript
async function uploadAvatar(file) {
    const formData = new FormData();
    formData.append('avatar', file);

    try {
        const response = await api.request('auth/upload-avatar/', {
            method: 'POST',
            headers: {}, // Don't set Content-Type for FormData
            body: formData,
        });

        if (response.ok) {
            return await response.json();
        } else {
            const errors = await response.json();
            throw new Error(JSON.stringify(errors));
        }
    } catch (error) {
        console.error('Avatar upload failed:', error);
        throw error;
    }
}

// Usage with file input
document.getElementById('avatar-input').addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (file) {
        try {
            const result = await uploadAvatar(file);
            console.log('Avatar uploaded:', result.avatar_url);
        } catch (error) {
            console.error('Upload error:', error);
        }
    }
});
```

#### Product Listing with Pagination
```javascript
async function getProducts(page = 1, filters = {}) {
    const params = new URLSearchParams({
        page,
        page_size: 20,
        ...filters,
    });

    try {
        const response = await api.request(`products/?${params}`);
        
        if (response.ok) {
            return await response.json();
        } else {
            throw new Error('Failed to fetch products');
        }
    } catch (error) {
        console.error('Error fetching products:', error);
        throw error;
    }
}

// Usage
async function loadProducts() {
    try {
        const products = await getProducts(1, {
            category: 1,
            min_price: 5,
            max_price: 50,
            ordering: '-created_at'
        });
        
        console.log('Products:', products.results);
        console.log('Total count:', products.count);
    } catch (error) {
        console.error('Failed to load products:', error);
    }
}
```

#### Order Creation
```javascript
async function createOrder(orderData) {
    try {
        const response = await api.request('orders/', {
            method: 'POST',
            body: JSON.stringify(orderData),
        });

        if (response.ok) {
            return await response.json();
        } else {
            const errors = await response.json();
            throw new Error(JSON.stringify(errors));
        }
    } catch (error) {
        console.error('Order creation failed:', error);
        throw error;
    }
}

// Usage
const orderData = {
    shipping_address: '123 Main St, City, State 12345',
    items: [
        { product: 1, quantity: 3 },
        { product: 5, quantity: 2 }
    ]
};

createOrder(orderData);
```

### React Hook Example

```javascript
import { useState, useEffect } from 'react';

function useApi() {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const apiCall = async (endpoint, options = {}) => {
        setLoading(true);
        setError(null);

        try {
            const response = await api.request(endpoint, options);
            const data = await response.json();
            
            if (response.ok) {
                return data;
            } else {
                throw new Error(data.detail || 'API call failed');
            }
        } catch (err) {
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    };

    return { apiCall, loading, error };
}

// Usage in component
function UserProfile() {
    const [user, setUser] = useState(null);
    const { apiCall, loading, error } = useApi();

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const userData = await apiCall('auth/profile/');
                setUser(userData);
            } catch (err) {
                console.error('Failed to fetch profile:', err);
            }
        };

        fetchProfile();
    }, []);

    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error}</div>;
    if (!user) return null;

    return (
        <div>
            <h1>{user.full_name}</h1>
            <p>Email: {user.email}</p>
            <p>Phone: {user.phone}</p>
            {user.avatar_url && (
                <img src={user.avatar_url} alt="Avatar" width="100" />
            )}
        </div>
    );
}
```

### Axios Example

```javascript
import axios from 'axios';

const apiClient = axios.create({
    baseURL: 'http://api.organicgreen.uz/api/',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Response interceptor for token refresh
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
                try {
                    const response = await axios.post(
                        'http://api.organicgreen.uz/api/auth/token/',
                        { refresh: refreshToken }
                    );
                    
                    const { access } = response.data;
                    localStorage.setItem('access_token', access);
                    
                    // Retry original request
                    error.config.headers.Authorization = `Bearer ${access}`;
                    return apiClient.request(error.config);
                } catch (refreshError) {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    window.location.href = '/login';
                }
            }
        }
        return Promise.reject(error);
    }
);

// API functions
export const authAPI = {
    login: (credentials) => apiClient.post('auth/login/', credentials),
    register: (userData) => apiClient.post('auth/register-full/', userData),
    getProfile: () => apiClient.get('auth/profile/'),
    updateProfile: (data) => apiClient.patch('auth/profile/', data),
    uploadAvatar: (file) => {
        const formData = new FormData();
        formData.append('avatar', file);
        return apiClient.post('auth/upload-avatar/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
    },
    deleteAvatar: () => apiClient.delete('auth/delete-avatar/'),
    changePassword: (data) => apiClient.post('auth/change-password/', data),
    logout: (refreshToken) => apiClient.post('auth/logout/', { refresh_token: refreshToken }),
};

export const productAPI = {
    getProducts: (params) => apiClient.get('products/', { params }),
    getProduct: (id) => apiClient.get(`products/${id}/`),
    getCategories: () => apiClient.get('categories/'),
    getTags: () => apiClient.get('tags/'),
};

export const orderAPI = {
    createOrder: (orderData) => apiClient.post('orders/', orderData),
    getOrders: (params) => apiClient.get('orders/', { params }),
    getOrder: (id) => apiClient.get(`orders/${id}/`),
    cancelOrder: (id) => apiClient.post(`orders/${id}/cancel/`),
};
```

---

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Authentication endpoints**: 5 requests per minute per IP
- **General API endpoints**: 100 requests per minute per authenticated user
- **Anonymous requests**: 20 requests per minute per IP

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1642684800
```

---

## API Health Check

**Endpoint:** `GET /health/`

**Response (200 OK):**
```json
{
    "status": "healthy",
    "timestamp": "2024-01-16T10:30:00Z",
    "version": "1.0.0",
    "database": "connected"
}
```

---

## Support

For technical support or questions about the API, please contact:
- Email: support@organicgreen.com
- Documentation: http://api.organicgreen.uz/api/docs/
- API Status: http://api.organicgreen.uz/api/health/
