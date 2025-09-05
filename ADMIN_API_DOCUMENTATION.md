# Admin API Documentation

## Umumiy ma'lumot

Admin API loyihaning barcha asosiy resurslarini boshqarish uchun to'liq CRUD operatsiyalarini taqdim etadi. Faqat admin huquqlariga ega foydalanuvchilar kirish imkoniyatiga ega.

**Base URL:** `https://your-domain.com/api/admin/`

## Authentication

- **Talab:** JWT Bearer token va `is_staff=True` yoki `is_superuser=True`
- **Header:** `Authorization: Bearer <admin-jwt-token>`

## Resurslar

### 1. Users Management

#### List Users
```
GET /api/admin/users/
```

**Query Parameters:**
- `is_active` (boolean): Faol foydalanuvchilar
- `is_staff` (boolean): Admin foydalanuvchilar
- `is_superuser` (boolean): Superuser'lar
- `is_verified` (boolean): Tasdiqlangan foydalanuvchilar
- `search` (string): Username, email, ism, familiya bo'yicha qidirish
- `ordering` (string): `date_joined`, `last_login`, `username`, `email`

**Response:**
```json
{
    "count": 150,
    "next": "http://localhost:8000/api/admin/users/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "john_doe",
            "email": "john@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
            "display_name": "John Doe",
            "phone": "+998901234567",
            "avatar": "/media/avatars/john.jpg",
            "is_active": true,
            "is_staff": false,
            "is_superuser": false,
            "is_verified": true,
            "date_joined": "2024-01-15T10:30:00Z",
            "last_login": "2024-09-04T14:20:00Z",
            "orders_count": 5,
            "total_spent": "125.50",
            "last_order_date": "2024-08-15T12:00:00Z"
        }
    ]
}
```

#### Create User
```
POST /api/admin/users/
```

**Request Body:**
```json
{
    "username": "new_user",
    "email": "new@example.com",
    "first_name": "New",
    "last_name": "User",
    "phone": "+998901234567",
    "is_active": true,
    "is_staff": false,
    "is_verified": false
}
```

#### Get User Details
```
GET /api/admin/users/{id}/
```

#### Update User
```
PATCH /api/admin/users/{id}/
```

#### Delete User (Soft Delete)
```
DELETE /api/admin/users/{id}/
```

#### User Activity Stats
```
GET /api/admin/users/activity/
```

**Response:**
```json
{
    "active_today": 25,
    "active_week": 150,
    "active_month": 500,
    "total_users": 1200,
    "verified_users": 1000,
    "staff_users": 10
}
```

---

### 2. Products Management

#### List Products
```
GET /api/admin/products/
```

**Query Parameters:**
- `is_active` (boolean): Faol mahsulotlar
- `is_featured` (boolean): Tavsiya etilgan mahsulotlar
- `category` (integer): Kategoriya ID
- `tags` (integer): Tag ID
- `search` (string): Nomi bo'yicha qidirish
- `ordering` (string): `created_at`, `updated_at`, `price`, `stock`

**Response:**
```json
{
    "count": 50,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name_uz": "Organik olma",
            "name_ru": "Органическое яблоко",
            "name_en": "Organic Apple",
            "slug": "organic-apple",
            "description_uz": "Tabiiy organik olma",
            "description_ru": "Натуральное органическое яблоко",
            "description_en": "Natural organic apple",
            "price": "5.00",
            "sale_price": "4.50",
            "stock": 100,
            "category": 1,
            "category_name": "Mevalar",
            "tags": [1, 2],
            "tags_list": ["Organik", "Yangi"],
            "is_active": true,
            "is_featured": true,
            "suggested_products": [],
            "created_at": "2024-01-15T10:30:00Z",
            "updated_at": "2024-09-04T14:20:00Z",
            "deleted_at": null,
            "images": [
                {
                    "id": "660e8400-e29b-41d4-a716-446655440001",
                    "image": "/media/products/apple.jpg",
                    "alt_text_uz": "Organik olma rasmi",
                    "alt_text_ru": "Изображение органического яблока",
                    "alt_text_en": "Organic apple image",
                    "is_primary": true,
                    "order": 1
                }
            ],
            "is_on_sale": true,
            "final_price": "4.50",
            "display_name": "Organik olma (Organic Apple)",
            "orders_count": 25
        }
    ]
}
```

#### Create Product
```
POST /api/admin/products/
```

#### Product Statistics
```
GET /api/admin/products/stats/
```

**Response:**
```json
{
    "total_products": 150,
    "active_products": 140,
    "featured_products": 25,
    "out_of_stock": 5,
    "deleted_products": 10
}
```

---

### 3. Categories Management

```
GET /api/admin/categories/
POST /api/admin/categories/
GET /api/admin/categories/{id}/
PATCH /api/admin/categories/{id}/
DELETE /api/admin/categories/{id}/
```

**Response Example:**
```json
{
    "id": 1,
    "name_uz": "Mevalar",
    "name_ru": "Фрукты",
    "name_en": "Fruits",
    "description_uz": "Turli xil mevalar",
    "description_ru": "Различные фрукты",
    "description_en": "Various fruits",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-09-04T14:20:00Z",
    "products_count": 25
}
```

---

### 4. Tags Management

```
GET /api/admin/tags/
POST /api/admin/tags/
GET /api/admin/tags/{id}/
PATCH /api/admin/tags/{id}/
DELETE /api/admin/tags/{id}/
```

---

### 5. Orders Management

#### List Orders
```
GET /api/admin/orders/
```

**Query Parameters:**
- `status` (string): Order status
- `payment_method` (string): Payment method
- `is_paid` (boolean): Payment status
- `search` (string): Order number, customer info bo'yicha qidirish

**Response:**
```json
{
    "results": [
        {
            "id": "770e8400-e29b-41d4-a716-446655440000",
            "order_number": "OG-20240904-00001",
            "user": 1,
            "customer_name": "John Doe",
            "customer_email": "john@example.com",
            "customer_phone": "+998901234567",
            "shipping_address": "Tashkent, Yunusobod 1-15-25",
            "billing_address": "Tashkent, Yunusobod 1-15-25",
            "status": "delivered",
            "status_display": "Yetkazildi",
            "payment_method": "payme",
            "payment_method_display": "Payme",
            "is_paid": true,
            "subtotal": "50.00",
            "shipping_cost": "5.00",
            "tax_amount": "2.75",
            "discount_amount": "0.00",
            "total_amount": "57.75",
            "notes": "Tez yetkazish",
            "created_at": "2024-09-04T10:30:00Z",
            "updated_at": "2024-09-04T15:45:00Z",
            "items": [
                {
                    "id": "880e8400-e29b-41d4-a716-446655440000",
                    "product": "550e8400-e29b-41d4-a716-446655440000",
                    "product_name": "Organik olma",
                    "product_slug": "organic-apple",
                    "quantity": 5,
                    "unit_price": "4.50",
                    "total_price": "22.50"
                }
            ],
            "items_count": 3
        }
    ]
}
```

#### Revenue Statistics
```
GET /api/admin/orders/revenue/
```

**Response:**
```json
{
    "today_revenue": "1250.00",
    "month_revenue": "25000.00",
    "last_month_revenue": "22000.00",
    "total_orders": 500,
    "paid_orders": 450,
    "pending_orders": 25
}
```

---

### 6. Course Applications Management

```
GET /api/admin/course-applications/
POST /api/admin/course-applications/
GET /api/admin/course-applications/{id}/
PATCH /api/admin/course-applications/{id}/
DELETE /api/admin/course-applications/{id}/
```

**Query Parameters:**
- `processed` (boolean): Qayta ishlangan arizalar
- `search` (string): Ism, email, telefon bo'yicha qidirish

**Response Example:**
```json
{
    "id": "990e8400-e29b-41d4-a716-446655440000",
    "application_number": "KURS-20240904-00001",
    "full_name": "Ali Valiyev",
    "email": "ali@example.com",
    "phone_number": "+998901234567",
    "course_name": "Python dasturlash kursi",
    "message": "Men bu kursga juda qiziqaman",
    "processed": false,
    "status_display": "Kutilmoqda",
    "created_at": "2024-09-04T10:30:00Z",
    "created_at_formatted": "04.09.2024 10:30",
    "updated_at": "2024-09-04T10:30:00Z",
    "application_age": 0
}
```

---

### 7. Franchise Applications Management

```
GET /api/admin/franchise-applications/
POST /api/admin/franchise-applications/
GET /api/admin/franchise-applications/{id}/
PATCH /api/admin/franchise-applications/{id}/
DELETE /api/admin/franchise-applications/{id}/
```

**Query Parameters:**
- `status` (string): Application status (pending, reviewed, approved, rejected)
- `search` (string): Ism, email, telefon, shahar bo'yicha qidirish

#### ROI Statistics
```
GET /api/admin/franchise-applications/roi_stats/
```

**Response:**
```json
{
    "total_approved_investment": "500000.00",
    "average_investment": "50000.00",
    "total_applications": 50,
    "pending_applications": 15,
    "approved_applications": 25,
    "rejected_applications": 10
}
```

---

### 8. Carts Management

```
GET /api/admin/carts/
GET /api/admin/carts/{id}/
DELETE /api/admin/carts/{id}/
```

**Response Example:**
```json
{
    "id": "aa0e8400-e29b-41d4-a716-446655440000",
    "user": 1,
    "user_name": "John Doe",
    "created_at": "2024-09-04T10:30:00Z",
    "updated_at": "2024-09-04T12:15:00Z",
    "items": [
        {
            "id": "bb0e8400-e29b-41d4-a716-446655440000",
            "product": "550e8400-e29b-41d4-a716-446655440000",
            "product_name": "Organik olma",
            "product_price": "4.50",
            "quantity": 3,
            "added_at": "2024-09-04T10:30:00Z"
        }
    ],
    "items_count": 2,
    "total_amount": "15.75"
}
```

---

### 9. Favorites Management

```
GET /api/admin/favorites/
GET /api/admin/favorites/{id}/
DELETE /api/admin/favorites/{id}/
```

---

### 10. Dashboard Statistics

#### Main Dashboard
```
GET /api/admin/dashboard/
```

**Response:**
```json
{
    "users": {
        "total": 1200,
        "active": 1150,
        "admins": 10,
        "verified": 1000,
        "new_today": 5
    },
    "products": {
        "total": 150,
        "active": 140,
        "featured": 25,
        "out_of_stock": 5
    },
    "orders": {
        "total": 500,
        "pending": 25,
        "completed": 450,
        "cancelled": 25,
        "today": 10
    },
    "courses": {
        "total_applications": 100,
        "pending": 30,
        "processed": 70,
        "today": 3
    },
    "franchises": {
        "total_applications": 50,
        "pending": 15,
        "approved": 25,
        "rejected": 10
    },
    "revenue": {
        "today": "1250.00",
        "this_month": "25000.00"
    }
}
```

#### Applications Statistics
```
GET /api/admin/applications/stats/
```

**Response:**
```json
{
    "course_applications": {
        "total": 100,
        "pending": 30,
        "processed": 70,
        "today": 3,
        "popular_courses": [
            {
                "course_name": "Python dasturlash kursi",
                "count": 25
            },
            {
                "course_name": "JavaScript kursi",
                "count": 20
            }
        ]
    },
    "franchise_applications": {
        "total": 50,
        "pending": 15,
        "approved": 25,
        "rejected": 10,
        "total_investment": "500000.00",
        "popular_cities": [
            {
                "city": "Tashkent",
                "count": 15
            },
            {
                "city": "Samarkand",
                "count": 10
            }
        ]
    }
}
```

---

## Filtrlash va Qidirish

### Umumiy filtrlar

Barcha admin endpoint'larda quyidagi filtrlar mavjud:

1. **Pagination:**
   - `page` - Sahifa raqami
   - Default: 20 ta element per page

2. **Ordering:**
   - `ordering` - Tartiblash maydoni
   - Masalan: `-created_at`, `name`, `price`

3. **Search:**
   - `search` - Qidirish so'zi
   - Har bir endpoint uchun mos maydonlarda qidiradi

4. **Filtering:**
   - Har bir resource uchun maxsus filtrlar
   - Boolean filtrlar: `true`, `false`, `1`, `0`
   - Date filtrlar: `YYYY-MM-DD` format

### Misol so'rovlar

```bash
# Faol foydalanuvchilarni qidirish
GET /api/admin/users/?is_active=true&search=john

# Oxirgi buyurtmalar
GET /api/admin/orders/?ordering=-created_at&status=pending

# Kategoriya bo'yicha mahsulotlar
GET /api/admin/products/?category=1&is_active=true

# Kurs arizalarini sanasi bo'yicha filtrlash
GET /api/admin/course-applications/?created_at__gte=2024-09-01
```

---

## Error Handling

### HTTP Status Codes

- `200` - OK
- `201` - Created
- `204` - No Content (Delete)
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden (Admin access required)
- `404` - Not Found
- `500` - Internal Server Error

### Error Response Format

```json
{
    "detail": "Authentication credentials were not provided."
}
```

```json
{
    "field_name": ["This field is required."],
    "non_field_errors": ["Invalid data provided."]
}
```

---

## JavaScript Client Example

```javascript
class AdminAPIClient {
    constructor(baseURL, token) {
        this.baseURL = baseURL;
        this.token = token;
    }
    
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}/api/admin/${endpoint}`;
        const config = {
            headers: {
                'Authorization': `Bearer ${this.token}`,
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        };
        
        const response = await fetch(url, config);
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    }
    
    // Users
    async getUsers(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`users/?${query}`);
    }
    
    async createUser(userData) {
        return this.request('users/', {
            method: 'POST',
            body: JSON.stringify(userData)
        });
    }
    
    async updateUser(userId, userData) {
        return this.request(`users/${userId}/`, {
            method: 'PATCH',
            body: JSON.stringify(userData)
        });
    }
    
    // Products
    async getProducts(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.request(`products/?${query}`);
    }
    
    async createProduct(productData) {
        return this.request('products/', {
            method: 'POST',
            body: JSON.stringify(productData)
        });
    }
    
    // Dashboard
    async getDashboardStats() {
        return this.request('dashboard/');
    }
    
    async getApplicationsStats() {
        return this.request('applications/stats/');
    }
}

// Usage
const adminAPI = new AdminAPIClient('https://api.organicgreen.uz', 'your-admin-token');

// Get dashboard stats
adminAPI.getDashboardStats().then(stats => {
    console.log('Dashboard stats:', stats);
});

// Get users with filtering
adminAPI.getUsers({ is_active: true, search: 'john' }).then(users => {
    console.log('Filtered users:', users);
});

// Create new product
adminAPI.createProduct({
    name_uz: 'Yangi mahsulot',
    name_ru: 'Новый продукт',
    name_en: 'New Product',
    slug: 'new-product',
    price: '10.00',
    stock: 100,
    category: 1,
    is_active: true
}).then(product => {
    console.log('Created product:', product);
});
```

Bu dokumentatsiya admin API'ning to'liq qo'llanmasini o'z ichiga oladi. Barcha endpoint'lar, parametrlar, javob formatlari va misol kodlar keltirilgan.
