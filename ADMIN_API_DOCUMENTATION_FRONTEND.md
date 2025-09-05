# Admin API Documentation

Bu dokumentatsiya Organic Green loyihasining Admin API'si uchun to'liq qo'llanma hisoblanadi. Barcha admin endpoint'lari JWT authentication talab qiladi va faqat admin foydalanuvchilar kirish huquqiga ega.

## Authentication

**Talab:** Barcha admin endpoint'lari JWT Bearer token va admin huquqlari talab qiladi.

**Header:**
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
```

**Admin huquqlari tekshiruvi:**
- Foydalanuvchi `is_staff=True` yoki `is_superuser=True` bo'lishi kerak

---

## 1. USERS ADMIN API

### 1.1 Foydalanuvchilar ro'yxati

**GET** `/api/admin/users/`

Barcha foydalanuvchilarni olish (pagination, filtering, search bilan).

#### Query Parameters:
| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Sahifa raqami |
| `page_size` | integer | Sahifadagi elementlar soni (default: 20) |
| `is_active` | boolean | Faol foydalanuvchilar filtri |
| `is_staff` | boolean | Admin foydalanuvchilar filtri |
| `is_superuser` | boolean | Superuser foydalanuvchilar filtri |
| `is_verified` | boolean | Tasdiqlangan foydalanuvchilar filtri |
| `search` | string | Qidirish (username, email, first_name, last_name, phone) |
| `ordering` | string | Tartiblash (-date_joined, username, email, last_login) |

#### Response (200 OK):
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
            "is_active": true,
            "is_staff": false,
            "is_superuser": false,
            "date_joined": "2024-01-15T10:30:00Z",
            "last_login": "2024-09-05T14:20:00Z",
            "orders_count": 5,
            "total_spent": 125000.0
        }
    ]
}
```

#### Errors:
- **401 Unauthorized:** Token yo'q yoki noto'g'ri
- **403 Forbidden:** Admin huquqlari yo'q

### 1.2 Foydalanuvchi tafsilotlari

**GET** `/api/admin/users/{id}/`

Bitta foydalanuvchining to'liq ma'lumotlarini olish.

#### Response (200 OK):
```json
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false,
    "date_joined": "2024-01-15T10:30:00Z",
    "last_login": "2024-09-05T14:20:00Z",
    "orders_count": 5,
    "total_spent": 125000.0,
    "recent_orders": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "order_number": "OG-20240905-00001",
            "total_price": 25000.0,
            "status": "completed",
            "created_at": "2024-09-05T10:00:00Z"
        }
    ],
    "recent_favorites": [
        {
            "product_id": "660e8400-e29b-41d4-a716-446655440001",
            "product_name": "Organik pomidor",
            "created_at": "2024-09-05T12:00:00Z"
        }
    ],
    "course_applications": 0,
    "franchise_applications": 0
}
```

#### Errors:
- **404 Not Found:** Foydalanuvchi topilmadi

### 1.3 Foydalanuvchini yangilash

**PUT/PATCH** `/api/admin/users/{id}/`

#### Request Body:
```json
{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "is_active": true,
    "is_staff": false,
    "is_superuser": false
}
```

#### Response (200 OK):
Yangilangan foydalanuvchi ma'lumotlari qaytariladi.

### 1.4 Foydalanuvchilar faolligi

**GET** `/api/admin/users/activity/`

Foydalanuvchilar faolligi statistikasi.

#### Response (200 OK):
```json
{
    "active_today": 25,
    "active_week": 120,
    "active_month": 450,
    "total_users": 1500,
    "verified_users": 1200,
    "staff_users": 5
}
```

---

## 2. PRODUCTS ADMIN API

### 2.1 Mahsulotlar ro'yxati

**GET** `/api/admin/products/`

#### Query Parameters:
| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Sahifa raqami |
| `is_active` | boolean | Faol mahsulotlar filtri |
| `is_featured` | boolean | Tavsiya etilgan mahsulotlar |
| `category` | integer | Kategoriya ID |
| `tags` | integer | Tag ID |
| `search` | string | Qidirish (name_uz, name_ru, name_en, slug) |
| `ordering` | string | Tartiblash (-created_at, price, stock) |

#### Response (200 OK):
```json
{
    "count": 500,
    "next": "http://localhost:8000/api/admin/products/?page=2",
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "name_uz": "Organik pomidor",
            "name_ru": "Органические помидоры",
            "name_en": "Organic Tomatoes",
            "slug": "organik-pomidor",
            "price": "15000.00",
            "sale_price": "12000.00",
            "stock": 100,
            "category": 1,
            "category_name": "Sabzavotlar",
            "is_active": true,
            "is_featured": true,
            "orders_count": 25,
            "favorites_count": 12,
            "image_url": "https://domain.com/media/products/550e.../img1.jpg",
            "primary_image_url": "https://domain.com/media/products/550e.../img1.jpg",
            "image_count": 2,
            "created_at": "2024-08-01T10:00:00Z",
            "updated_at": "2024-09-05T14:30:00Z"
        }
    ]
}
```

### 2.2 Mahsulot tafsilotlari

**GET** `/api/admin/products/{id}/`

(Yangi qo'shilgan maydonlar: `images_list`, `primary_image_url`, `image_count`)

#### Response (200 OK):
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name_uz": "Organik pomidor",
    "name_ru": "Органические помидоры",
    "name_en": "Organic Tomatoes",
    "slug": "organik-pomidor",
    "price": "15000.00",
    "sale_price": "12000.00",
    "stock": 100,
    "category": 1,
    "category_name": "Sabzavotlar",
    "is_active": true,
    "is_featured": true,
    "orders_count": 25,
    "favorites_count": 12,
    "total_sold": 150,
    "revenue_generated": 1800000.0,
    "stock_status": "In Stock",
    "images_list": [
        {
            "id": "770e8400-e29b-41d4-a716-446655440111",
            "image_url": "https://domain.com/media/products/550e.../img1.jpg",
            "alt_text_uz": "Pomidor",
            "alt_text_ru": "Помидор",
            "alt_text_en": "Tomato",
            "is_primary": true,
            "order": 0,
            "created_at": "2024-09-05T10:00:00Z"
        },
        {
            "id": "880e8400-e29b-41d4-a716-446655440222",
            "image_url": "https://domain.com/media/products/550e.../img2.jpg",
            "alt_text_uz": "Pomidor yon tomoni",
            "alt_text_ru": "Помидор сбоку",
            "alt_text_en": "Tomato side",
            "is_primary": false,
            "order": 1,
            "created_at": "2024-09-05T10:05:00Z"
        }
    ],
    "primary_image_url": "https://domain.com/media/products/550e.../img1.jpg",
    "image_count": 2,
    "recent_orders": [
        {
            "order_id": "660e8400-e29b-41d4-a716-446655440001",
            "order_number": "OG-20240905-00001",
            "quantity": 2,
            "price": 24000.0,
            "created_at": "2024-09-05T10:00:00Z"
        }
    ],
    "created_at": "2024-08-01T10:00:00Z",
    "updated_at": "2024-09-05T14:30:00Z"
}
```

### 2.3 Yangi mahsulot yaratish (oddiy JSON, rasmsiz)

**POST** `/api/admin/products/`

Content-Type: `application/json`

#### Request Body (rasmsiz):
```json
{
    "name_uz": "Yangi mahsulot",
    "name_ru": "Новый продукт",
    "name_en": "New Product",
    "slug": "yangi-mahsulot",
    "price": "20000.00",
    "sale_price": "18000.00",
    "stock": 50,
    "category": 1,
    "is_active": true,
    "is_featured": false
}
```

### 2.4 Yangi mahsulot yaratish (rasmlar bilan multipart)

Agar bir vaqtning o'zida rasmlar yubormoqchi bo'lsangiz `Content-Type: multipart/form-data` dan foydalaning.

Field nomlari (nested array): `images[0].image`, `images[0].alt_text_uz`, `images[0].is_primary`, `images[0].order`, va hokazo.

#### Form-Data misol (kalitlar):
```
name_uz: Yangi mahsulot
name_ru: Новый продукт
name_en: New Product
slug: yangi-mahsulot
price: 20000.00
sale_price: 18000.00
stock: 50
category: 1
is_active: true
is_featured: false
images[0].image: <FILE>
images[0].alt_text_uz: Asosiy rasm
images[0].is_primary: true
images[0].order: 0
images[1].image: <FILE>
images[1].alt_text_uz: Ikkinchi rasm
images[1].order: 1
```

#### Response (201 Created) (asosiy maydonlar + images_list qaytadi):
```json
{
  "id": "990e8400-e29b-41d4-a716-446655440999",
  "name_uz": "Yangi mahsulot",
  "slug": "yangi-mahsulot",
  "price": "20000.00",
  "sale_price": "18000.00",
  "stock": 50,
  "category": 1,
  "category_name": "Sabzavotlar",
  "is_active": true,
  "is_featured": false,
  "orders_count": 0,
  "favorites_count": 0,
  "created_at": "2025-09-05T12:00:00Z",
  "updated_at": "2025-09-05T12:00:00Z",
  "primary_image_url": "https://domain.com/media/products/990e.../main.jpg",
  "image_count": 2,
  "images_list": [
    {
      "id": "a70e8400-e29b-41d4-a716-446655440111",
      "image_url": "https://domain.com/media/products/990e.../main.jpg",
      "alt_text_uz": "Asosiy rasm",
      "alt_text_ru": "",
      "alt_text_en": "",
      "is_primary": true,
      "order": 0,
      "created_at": "2025-09-05T12:00:00Z"
    },
    {
      "id": "b80e8400-e29b-41d4-a716-446655440222",
      "image_url": "https://domain.com/media/products/990e.../second.jpg",
      "alt_text_uz": "Ikkinchi rasm",
      "alt_text_ru": "",
      "alt_text_en": "",
      "is_primary": false,
      "order": 1,
      "created_at": "2025-09-05T12:00:00Z"
    }
  ]
}
```

### 2.5 Mahsulotni yangilash

**PUT/PATCH** `/api/admin/products/{id}/`

#### Request Body:
```json
{
    "name_uz": "Yangilangan mahsulot",
    "price": "25000.00",
    "stock": 75,
    "is_featured": true
}
```

### 2.6 Mahsulotni o'chirish (soft delete)

**DELETE** `/api/admin/products/{id}/`

#### Response (204 No Content)

### 2.7 Mahsulotlar statistikasi

**GET** `/api/admin/products/stats/`

#### Response (200 OK):
```json
{
    "total_products": 500,
    "active_products": 450,
    "featured_products": 50,
    "out_of_stock": 15,
    "deleted_products": 25
}
```

### 2.8 Mavjud mahsulotga rasm yuklash

**POST** `/api/admin/products/{id}/upload-image/`

Bir yoki bir nechta rasmni keyinchalik alohida jo'natish. Content-Type: `multipart/form-data`.

#### Form-Data maydonlari:
| Field | Majburiy | Izoh |
|-------|----------|------|
| `image` yoki `images` | Ha | Bitta yoki bir nechta file. `image` birinchi file sifatida, `images` list sifatida ham qo'llab-quvvatlanadi |
| `alt_text_uz` | Yo'q | Alt matn (UZ) |
| `alt_text_ru` | Yo'q | Alt matn (RU) |
| `alt_text_en` | Yo'q | Alt text (EN) |
| `is_primary` | Yo'q | `true/false` (birinchi file primariga qo'yiladi agar true bo'lsa) |

#### Response (201 Created):
```json
{
  "created": [
    {
      "id": "c90e8400-e29b-41d4-a716-446655440333",
      "image_url": "https://domain.com/media/products/550e.../new1.jpg",
      "is_primary": false,
      "order": 2
    }
  ],
  "count": 1
}
```

#### Xatoliklar:
- 400: `{"detail": "Rasm yuborilmadi (image yoki images field)."}`
- 404: Mahsulot topilmadi

### 2.9 Asosiy rasmni o'rnatish

**PATCH** `/api/admin/products/{id}/set-primary-image/`

#### Request Body:
```json
{ "image_id": "c90e8400-e29b-41d4-a716-446655440333" }
```

#### Response (200 OK):
```json
{ "detail": "Asosiy rasm yangilandi." }
```

#### Xatoliklar:
- 400: `image_id talab qilinadi.`
- 404: `Rasm topilmadi.`

### 2.10 Rasmni o'chirish

**DELETE** `/api/admin/products/{id}/delete-image/?image_id=<uuid>`

Yoki body orqali:
```json
{ "image_id": "c90e8400-e29b-41d4-a716-446655440333" }
```

#### Response:
- 204 No Content

#### Xatoliklar:
- 400: `image_id talab qilinadi.`
- 404: `Rasm topilmadi.`

---

## 3. ORDERS ADMIN API

### 3.1 Buyurtmalar ro'yxati

**GET** `/api/admin/orders/`

#### Query Parameters:
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Buyurtma holati (pending, completed, cancelled) |
| `user` | integer | Foydalanuvchi ID |
| `created_at` | date | Sana filtri (YYYY-MM-DD) |
| `search` | string | Qidirish (id, full_name, contact_phone) |
| `ordering` | string | Tartiblash (-created_at, total_price) |

#### Response (200 OK):
```json
{
    "count": 200,
    "next": "http://localhost:8000/api/admin/orders/?page=2",
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "order_number": "OG-20240905-00001",
            "user": 1,
            "user_email": "john@example.com",
            "full_name": "John Doe",
            "contact_phone": "+998901234567",
            "delivery_address": "Toshkent, Mirobod tumani",
            "status": "pending",
            "payment_method": "cod",
            "total_price": "125000.00",
            "items_count": 3,
            "created_at": "2024-09-05T10:00:00Z",
            "updated_at": "2024-09-05T10:00:00Z"
        }
    ]
}
```

### 3.2 Buyurtma tafsilotlari

**GET** `/api/admin/orders/{id}/`

#### Response (200 OK):
```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "order_number": "OG-20240905-00001",
    "user": 1,
    "user_email": "john@example.com",
    "full_name": "John Doe",
    "contact_phone": "+998901234567",
    "delivery_address": "Toshkent, Mirobod tumani",
    "status": "pending",
    "payment_method": "cod",
    "total_price": "125000.00",
    "items_count": 3,
    "items": [
        {
            "id": 1,
            "product": "660e8400-e29b-41d4-a716-446655440001",
            "product_name": "Organik pomidor",
            "quantity": 2,
            "total_price": "24000.00",
            "unit_price": "12000.00"
        }
    ],
    "created_at": "2024-09-05T10:00:00Z",
    "updated_at": "2024-09-05T10:00:00Z"
}
```

### 3.3 Buyurtma holatini yangilash

**PATCH** `/api/admin/orders/{id}/`

#### Request Body:
```json
{
    "status": "completed"
}
```

### 3.4 Daromad statistikasi

**GET** `/api/admin/orders/revenue/`

#### Response (200 OK):
```json
{
    "today_revenue": 150000,
    "week_revenue": 1250000,
    "month_revenue": 5000000,
    "total_revenue": 25000000,
    "pending_orders": 15,
    "completed_orders": 185
}
```

---

## 4. COURSE APPLICATIONS ADMIN API

### 4.1 Kurs arizalari ro'yxati

**GET** `/api/admin/course-applications/`

#### Query Parameters:
| Parameter | Type | Description |
|-----------|------|-------------|
| `processed` | boolean | Qayta ishlangan arizalar |
| `created_at` | date | Sana filtri |
| `search` | string | Qidirish (full_name, email, phone_number, course_name, application_number) |
| `ordering` | string | Tartiblash (-created_at, updated_at) |

#### Response (200 OK):
```json
{
    "count": 75,
    "next": "http://localhost:8000/api/admin/course-applications/?page=2",
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "application_number": "KURS-20240905-00001",
            "full_name": "Abdulaziz Abdullayev",
            "email": "abdulaziz@example.com",
            "phone_number": "+998901234567",
            "course_name": "Python dasturlash kursi",
            "message": "Men bu kursga qiziqaman",
            "processed": false,
            "status_display": "Kutilmoqda",
            "created_at": "2024-09-05T10:00:00Z",
            "created_at_formatted": "05.09.2024 10:00",
            "updated_at": "2024-09-05T10:00:00Z",
            "application_age": 0
        }
    ]
}
```

### 4.2 Kurs arizasi tafsilotlari

**GET** `/api/admin/course-applications/{id}/`

Yuqoridagi response bilan bir xil.

### 4.3 Ariza holatini yangilash

**PATCH** `/api/admin/course-applications/{id}/`

#### Request Body:
```json
{
    "processed": true
}
```

### 4.4 Arizalar statistikasi

**GET** `/api/admin/course-applications/stats/`

#### Response (200 OK):
```json
{
    "total_applications": 75,
    "pending_applications": 25,
    "processed_applications": 50
}
```

---

## 5. FRANCHISE APPLICATIONS ADMIN API

### 5.1 Franshiza arizalari ro'yxati

**GET** `/api/admin/franchise-applications/`

#### Query Parameters:
| Parameter | Type | Description |
|-----------|------|-------------|
| `status` | string | Ariza holati (pending, reviewed, approved, rejected) |
| `created_at` | date | Sana filtri |
| `search` | string | Qidirish (full_name, phone, email, city) |
| `ordering` | string | Tartiblash (-created_at, updated_at) |

#### Response (200 OK):
```json
{
    "count": 30,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "full_name": "Jasur Karimov",
            "phone": "+998901234567",
            "email": "jasur@example.com",
            "city": "Toshkent",
            "investment_amount": "50000.00",
            "investment_amount_formatted": "$50,000.00",
            "formatted_investment_amount": "$50,000.00",
            "experience": "5 yillik biznes tajribam bor",
            "message": "Franshiza ochishga qiziqaman",
            "status": "pending",
            "status_display": "Yangi",
            "is_pending": true,
            "is_approved": false,
            "created_at": "2024-09-05T10:00:00Z",
            "created_at_formatted": "05.09.2024 10:00",
            "updated_at": "2024-09-05T10:00:00Z"
        }
    ]
}
```

### 5.2 Franshiza arizasi tafsilotlari

**GET** `/api/admin/franchise-applications/{id}/`

Yuqoridagi response bilan bir xil.

### 5.3 Ariza holatini yangilash

**PATCH** `/api/admin/franchise-applications/{id}/`

#### Request Body:
```json
{
    "status": "approved"
}
```

### 5.4 Franshiza arizalari statistikasi

**GET** `/api/admin/franchise-applications/stats/`

#### Response (200 OK):
```json
{
    "total_applications": 30,
    "pending_applications": 15,
    "approved_applications": 8,
    "rejected_applications": 7
}
```

---

## 6. CART ADMIN API

### 6.1 Savatlar ro'yxati

**GET** `/api/admin/carts/`

#### Query Parameters:
| Parameter | Type | Description |
|-----------|------|-------------|
| `user` | integer | Foydalanuvchi ID |
| `created_at` | date | Sana filtri |
| `search` | string | Qidirish (user__username, user__email, session_key) |

#### Response (200 OK):
```json
{
    "count": 50,
    "next": "http://localhost:8000/api/admin/carts/?page=2",
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "user": 1,
            "user_email": "john@example.com",
            "session_key": null,
            "items_count": 3,
            "total_value": 85000.0,
            "created_at": "2024-09-05T10:00:00Z",
            "updated_at": "2024-09-05T12:30:00Z"
        }
    ]
}
```

### 6.2 Savatlar statistikasi

**GET** `/api/admin/carts/stats/`

#### Response (200 OK):
```json
{
    "total_carts": 50,
    "active_carts": 35,
    "anonymous_carts": 10,
    "user_carts": 40
}
```

---

## 7. FAVORITES ADMIN API

### 7.1 Sevimlilar ro'yxati

**GET** `/api/admin/favorites/`

#### Query Parameters:
| Parameter | Type | Description |
|-----------|------|-------------|
| `user` | integer | Foydalanuvchi ID |
| `product` | string | Mahsulot ID |
| `created_at` | date | Sana filtri |
| `search` | string | Qidirish (user__username, user__email, product__name_uz) |

#### Response (200 OK):
```json
{
    "count": 120,
    "next": "http://localhost:8000/api/admin/favorites/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "user": 1,
            "user_email": "john@example.com",
            "product": "550e8400-e29b-41d4-a716-446655440000",
            "product_name": "Organik pomidor",
            "product_price": "12000.00",
            "created_at": "2024-09-05T10:00:00Z"
        }
    ]
}
```

### 7.2 Sevimlilar statistikasi

**GET** `/api/admin/favorites/stats/`

#### Response (200 OK):
```json
{
    "total_favorites": 120,
    "unique_users": 45,
    "unique_products": 25
}
```

---

## 8. CATEGORIES & TAGS ADMIN API

### 8.1 Kategoriyalar ro'yxati

**GET** `/api/admin/categories/`

#### Response (200 OK):
```json
{
    "count": 15,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name_uz": "Sabzavotlar",
            "name_ru": "Овощи",
            "name_en": "Vegetables",
            "description_uz": "Organik sabzavotlar",
            "description_ru": "Органические овощи",
            "description_en": "Organic vegetables",
            "products_count": 25,
            "created_at": "2024-08-01T10:00:00Z",
            "updated_at": "2024-08-01T10:00:00Z"
        }
    ]
}
```

### 8.2 Taglar ro'yxati

**GET** `/api/admin/tags/`

#### Response (200 OK):
```json
{
    "count": 20,
    "next": null,
    "previous": null,
    "results": [
        {
            "id": 1,
            "name_uz": "Organik",
            "name_ru": "Органический",
            "name_en": "Organic",
            "products_count": 45,
            "created_at": "2024-08-01T10:00:00Z",
            "updated_at": "2024-08-01T10:00:00Z"
        }
    ]
}
```

---

## 9. DASHBOARD STATISTICS

### 9.1 Umumiy statistika

**GET** `/api/admin/dashboard/`

#### Response (200 OK):
```json
{
    "user_stats": {
        "total_users": 1500,
        "active_users": 1450,
        "new_users_today": 25,
        "new_users_week": 180
    },
    "product_stats": {
        "total_products": 500,
        "active_products": 475,
        "featured_products": 50,
        "out_of_stock": 15
    },
    "order_stats": {
        "total_orders": 2500,
        "pending_orders": 45,
        "completed_orders": 2300,
        "today_orders": 12,
        "week_orders": 85
    },
    "revenue_stats": {
        "today_revenue": 750000,
        "week_revenue": 5250000,
        "month_revenue": 22500000
    },
    "application_stats": {
        "course_applications": 75,
        "pending_course_applications": 25,
        "franchise_applications": 30,
        "pending_franchise_applications": 15
    },
    "generated_at": "2024-09-05T14:30:00Z"
}
```

---

## XATOLIKLAR

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Muvaffaqiyatli so'rov |
| 201 | Created - Yangi resurs yaratildi |
| 204 | No Content - Muvaffaqiyatli o'chirildi |
| 400 | Bad Request - Noto'g'ri so'rov |
| 401 | Unauthorized - Autentifikatsiya talab qiladi |
| 403 | Forbidden - Admin huquqlari yo'q |
| 404 | Not Found - Resurs topilmadi |
| 500 | Internal Server Error - Server xatosi |

### Xatolik formati

```json
{
    "detail": "Authentication credentials were not provided."
}
```

yoki validation xatoliklari uchun:

```json
{
    "field_name": ["This field is required."],
    "another_field": ["Ensure this value is less than or equal to 100."]
}
```

---

## PAGINATION

Barcha ro'yxat endpoint'lari pagination ishlatadi:

#### Query Parameters:
- `page`: Sahifa raqami (default: 1)
- `page_size`: Sahifadagi elementlar soni (default: 20, max: 100)

#### Response format:
```json
{
    "count": 150,
    "next": "http://localhost:8000/api/admin/users/?page=3",
    "previous": "http://localhost:8000/api/admin/users/?page=1",
    "results": [...]
}
```

---

## FILTERING & SEARCH

Ko'pgina endpoint'larda qidirish va filtrlash imkoniyatlari mavjud:

#### Search:
`?search=qidiruv_so'zi` - Ko'rsatilgan fieldlarda qidiradi

#### Filtering:
`?field_name=value` - Aniq field bo'yicha filtrlaydi

#### Ordering:
`?ordering=field_name` - Ko'tarilish tartibida
`?ordering=-field_name` - Kamayish tartibida

Bu dokumentatsiya admin panel'i uchun frontend dasturchi tomonidan foydalanish uchun mo'ljallangan.
