# Organic Green API - Authentication Documentation

## Kirish

Bu dokumentatsiya Organic Green API ning authentication qismini batafsil tushuntiradi. Barcha endpoint'lar, so'rov va javob formatlari haqiqiy ma'lumotlar bilan keltirilgan.

## Asosiy Ma'lumotlar

- **Base URL:** `http://localhost:8000/api/`
- **Authentication Type:** JWT (JSON Web Token)
- **Token Format:** Bearer Token
- **Ma'lumotlar formati:** JSON

---

## Foydalanuvchi Fieldlari

### Asosiy Ma'lumotlar
- **id** - Foydalanuvchi ID'si
- **username** - Foydalanuvchi nomi (noyob)
- **email** - Email manzili (noyob)
- **first_name** - Ism
- **last_name** - Familiya
- **phone** - Telefon raqami

### Qo'shimcha Ma'lumotlar
- **full_name** - To'liq ism (computed field)
- **display_name** - Ko'rsatish uchun ism (computed field)
- **avatar** - Avatar fayl yo'li
- **avatar_url** - Avatar ning to'liq URL'i

### Status Fieldlari
- **is_verified** - Hisob tasdiqlanganmi (default: false)
- **is_active** - Hisob faolmi (default: true)
- **is_staff** - Xodimmi (admin panel'ga kirish huquqi)
- **date_joined** - Ro'yxatdan o'tgan vaqt
- **last_login** - Oxirgi kirish vaqti

---

## 1. Foydalanuvchi Ro'yxatdan O'tishi

### 1.1 Oddiy Ro'yxatdan O'tish (Simple Registration)

**Endpoint:** `POST /auth/register/simple/`

**Tavsif:** Foydalanuvchini minimal ma'lumotlar bilan ro'yxatga olish.

**So'rov (Request):**
```json
{
    "username": "johndoe",
    "password": "mypass123"
}
```

**Muvaffaqiyatli Javob (201 Created):**
```json
{
    "user": {
        "id": 1,
        "username": "johndoe"
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjMzNzg2ODAwLCJpYXQiOjE2MzM3ODMyMDAsImp0aSI6IjEyMzQ1Njc4OTAiLCJ1c2VyX2lkIjoxLCJ1c2VybmFtZSI6ImpvaG5kb2UiLCJlbWFpbCI6ImpvaG5kb2VAdGVtcC5jb20iLCJmdWxsX25hbWUiOiJqb2huZG9lIiwicGhvbmUiOiIiLCJpc192ZXJpZmllZCI6ZmFsc2V9.abc123xyz789...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYzNDQ3NDQwMCwiaWF0IjoxNjMzNzgzMjAwLCJqdGkiOiI5ODc2NTQzMjEwIiwidXNlcl9pZCI6MX0.def456uvw789..."
    }
}
```

**Xato Javoblari:**

*Username allaqachon mavjud (400 Bad Request):*
```json
{
    "username": [
        "Bu foydalanuvchi nomi allaqachon band."
    ]
}
```

*Noto'g'ri ma'lumotlar (400 Bad Request):*
```json
{
    "username": [
        "Foydalanuvchi nomi kamida 3 ta belgidan iborat bo'lishi kerak."
    ],
    "password": [
        "Parol kamida 4 ta belgidan iborat bo'lishi kerak."
    ]
}
```

### 1.2 To'liq Ro'yxatdan O'tish (Full Registration)

**Endpoint:** `POST /auth/register/`

**Tavsif:** Foydalanuvchini barcha ma'lumotlar bilan ro'yxatga olish.

**So'rov (Request):**
```json
{
    "username": "alisher_uz",
    "email": "alisher@example.com",
    "password": "mypassword123",
    "password_confirm": "mypassword123",
    "first_name": "Alisher",
    "last_name": "Karimov",
    "phone": "+998901234567"
}
```

**Muvaffaqiyatli Javob (201 Created):**
```json
{
    "user": {
        "id": 2,
        "username": "alisher_uz",
        "email": "alisher@example.com",
        "first_name": "Alisher",
        "last_name": "Karimov",
        "full_name": "Alisher Karimov",
        "display_name": "Alisher Karimov",
        "phone": "+998901234567",
        "avatar": null,
        "avatar_url": null,
        "is_verified": false,
        "is_staff": false,
        "is_active": true,
        "date_joined": "2024-09-04T10:30:00.123456Z",
        "last_login": null
    },
    "tokens": {
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjMzNzg2ODAwLCJpYXQiOjE2MzM3ODMyMDAsImp0aSI6IjEyMzQ1Njc4OTEiLCJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6ImFsaXNoZXJfdXoiLCJlbWFpbCI6ImFsaXNoZXJAZXhhbXBsZS5jb20iLCJmdWxsX25hbWUiOiJBbGlzaGVyIEthcmltb3YiLCJwaG9uZSI6Iis5OTg5MDEyMzQ1NjciLCJpc192ZXJpZmllZCI6ZmFsc2V9.xyz789abc123...",
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYzNDQ3NDQwMCwiaWF0IjoxNjMzNzgzMjAwLCJqdGkiOiI5ODc2NTQzMjExIiwidXNlcl9pZCI6Mn0.uvw789def456..."
    }
}
```

**Xato Javoblari:**

*Parollar mos kelmadi (400 Bad Request):*
```json
{
    "password_confirm": [
        "Parollar mos kelmaydi."
    ]
}
```

*Email allaqachon mavjud (400 Bad Request):*
```json
{
    "email": [
        "Bu email allaqon ro'yxatdan o'tgan."
    ]
}
```

*Telefon raqam noto'g'ri (400 Bad Request):*
```json
{
    "phone": [
        "Telefon raqam '+' belgisi bilan boshlanishi kerak."
    ]
}
```

---

## 2. Kirish (Login)

### 2.1 Oddiy Kirish

**Endpoint:** `POST /auth/login/`

**Tavsif:** Foydalanuvchi nomi yoki email bilan kirish.

**So'rov (Request) - Username bilan:**
```json
{
    "username": "alisher_uz",
    "password": "mypassword123"
}
```

**So'rov (Request) - Email bilan:**
```json
{
    "username": "alisher@example.com",
    "password": "mypassword123"
}
```

**Muvaffaqiyatli Javob (200 OK):**
```json
{
    "user": {
        "id": 2,
        "username": "alisher_uz",
        "email": "alisher@example.com",
        "first_name": "Alisher",
        "last_name": "Karimov",
        "full_name": "Alisher Karimov",
        "display_name": "Alisher Karimov",
        "phone": "+998901234567",
        "avatar": null,
        "avatar_url": null,
        "is_verified": true,
        "is_staff": false,
        "is_active": true,
        "date_joined": "2024-09-04T10:30:00.123456Z",
        "last_login": "2024-09-04T12:45:30.987654Z"
    }
}
```

**Xato Javoblari:**

*Noto'g'ri ma'lumotlar (400 Bad Request):*
```json
{
    "non_field_errors": [
        "Foydalanuvchi nomi yoki parol noto'g'ri."
    ]
}
```

*Foydalanuvchi faol emas (400 Bad Request):*
```json
{
    "non_field_errors": [
        "Foydalanuvchi hisobi faol emas."
    ]
}
```

### 2.2 JWT Token Olish

**Endpoint:** `POST /auth/token/`

**Tavsif:** JWT access va refresh tokenlarni olish.

**So'rov (Request):**
```json
{
    "username": "alisher_uz",
    "password": "mypassword123"
}
```

**Muvaffaqiyatli Javob (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjMzNzg2ODAwLCJpYXQiOjE2MzM3ODMyMDAsImp0aSI6IjEyMzQ1Njc4OTIiLCJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6ImFsaXNoZXJfdXoiLCJlbWFpbCI6ImFsaXNoZXJAZXhhbXBsZS5jb20iLCJmdWxsX25hbWUiOiJBbGlzaGVyIEthcmltb3YiLCJwaG9uZSI6Iis5OTg5MDEyMzQ1NjciLCJpc192ZXJpZmllZCI6dHJ1ZSwiaXNfc3RhZmYiOmZhbHNlfQ.mno123pqr456...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYzNDQ3NDQwMCwiaWF0IjoxNjMzNzgzMjAwLCJqdGkiOiI5ODc2NTQzMjEyIiwidXNlcl9pZCI6Mn0.stu789vwx012...",
    "user": {
        "id": 2,
        "username": "alisher_uz",
        "email": "alisher@example.com",
        "first_name": "Alisher",
        "last_name": "Karimov",
        "full_name": "Alisher Karimov",
        "display_name": "Alisher Karimov",
        "phone": "+998901234567",
        "avatar": "/media/avatars/alisher_avatar.jpg",
        "avatar_url": "http://localhost:8000/media/avatars/alisher_avatar.jpg",
        "is_verified": true,
        "is_staff": false,
        "is_active": true,
        "date_joined": "2024-09-04T10:30:00.123456Z",
        "last_login": "2024-09-04T12:45:30.987654Z"
    }
}
```

---

## 3. Token Yangilash

### 3.1 Access Token Yangilash

**Endpoint:** `POST /auth/token/refresh/`

**Tavsif:** Refresh token yordamida yangi access token olish.

**So'rov (Request):**
```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYzNDQ3NDQwMCwiaWF0IjoxNjMzNzgzMjAwLCJqdGkiOiI5ODc2NTQzMjEyIiwidXNlcl9pZCI6Mn0.stu789vwx012..."
}
```

**Muvaffaqiyatli Javob (200 OK):**
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjMzNzkwNDAwLCJpYXQiOjE2MzM3ODY4MDAsImp0aSI6IjEyMzQ1Njc4OTMiLCJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6ImFsaXNoZXJfdXoiLCJlbWFpbCI6ImFsaXNoZXJAZXhhbXBsZS5jb20iLCJmdWxsX25hbWUiOiJBbGlzaGVyIEthcmltb3YiLCJwaG9uZSI6Iis5OTg5MDEyMzQ1NjciLCJpc192ZXJpZmllZCI6dHJ1ZX0.yz123abc456..."
}
```

**Xato Javob (401 Unauthorized):**
```json
{
    "detail": "Token is invalid or expired",
    "code": "token_not_valid"
}
```

### 3.2 Token Tekshirish

**Endpoint:** `POST /auth/token/verify/`

**Tavsif:** Token haqiqiyligini tekshirish.

**So'rov (Request):**
```json
{
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNjMzNzkwNDAwLCJpYXQiOjE2MzM3ODY4MDAsImp0aSI6IjEyMzQ1Njc4OTMiLCJ1c2VyX2lkIjoyLCJ1c2VybmFtZSI6ImFsaXNoZXJfdXoiLCJlbWFpbCI6ImFsaXNoZXJAZXhhbXBsZS5jb20iLCJmdWxsX25hbWUiOiJBbGlzaGVyIEthcmltb3YiLCJwaG9uZSI6Iis5OTg5MDEyMzQ1NjciLCJpc192ZXJpZmllZCI6dHJ1ZX0.yz123abc456..."
}
```

**Muvaffaqiyatli Javob (200 OK):**
```json
{}
```

**Xato Javob (401 Unauthorized):**
```json
{
    "detail": "Token is invalid or expired",
    "code": "token_not_valid"
}
```

---

## 4. Profil Boshqaruvi

### 4.1 Profil Ma'lumotlarini Olish

**Endpoint:** `GET /auth/profile/`

**Authentication:** Bearer Token talab qilinadi

**Header:**
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

**Muvaffaqiyatli Javob (200 OK):**
```json
{
    "id": 2,
    "username": "alisher_uz",
    "email": "alisher@example.com",
    "first_name": "Alisher",
    "last_name": "Karimov",
    "full_name": "Alisher Karimov",
    "display_name": "Alisher Karimov",
    "phone": "+998901234567",
    "avatar": "/media/avatars/alisher_avatar.jpg",
    "avatar_url": "http://localhost:8000/media/avatars/alisher_avatar.jpg",
    "is_verified": true,
    "is_staff": false,
    "is_active": true,
    "date_joined": "2024-09-04T10:30:00.123456Z",
    "last_login": "2024-09-04T12:45:30.987654Z"
}
```

### 4.2 Profil Ma'lumotlarini Yangilash

**Endpoint:** `PUT /auth/profile/` yoki `PATCH /auth/profile/`

**Authentication:** Bearer Token talab qilinadi

**So'rov (Request) - To'liq yangilash (PUT):**
```json
{
    "first_name": "Alisher",
    "last_name": "Karimov",
    "email": "alisher_new@example.com",
    "phone": "+998901234567"
}
```

**So'rov (Request) - Qisman yangilash (PATCH):**
```json
{
    "phone": "+998909876543"
}
```

**Muvaffaqiyatli Javob (200 OK):**
```json
{
    "id": 2,
    "username": "alisher_uz",
    "email": "alisher_new@example.com",
    "first_name": "Alisher",
    "last_name": "Karimov",
    "full_name": "Alisher Karimov",
    "display_name": "Alisher Karimov",
    "phone": "+998909876543",
    "avatar": "/media/avatars/alisher_avatar.jpg",
    "avatar_url": "http://localhost:8000/media/avatars/alisher_avatar.jpg",
    "is_verified": true,
    "is_staff": false,
    "is_active": true,
    "date_joined": "2024-09-04T10:30:00.123456Z",
    "last_login": "2024-09-04T12:45:30.987654Z"
}
```

**Xato Javob - Email allaqachon mavjud (400 Bad Request):**
```json
{
    "email": [
        "Bu email allaqon ro'yxatdan o'tgan."
    ]
}
```

---

## 5. Avatar Boshqaruvi

### 5.1 Avatar Yuklash

**Endpoint:** `POST /auth/upload-avatar/`

**Authentication:** Bearer Token talab qilinadi

**Content-Type:** `multipart/form-data`

**So'rov (Request):**
```
Content-Type: multipart/form-data

avatar: [fayl] (max 5MB, JPEG/PNG/GIF/WEBP)
```

**Muvaffaqiyatli Javob (200 OK):**
```json
{
    "message": "Avatar muvaffaqiyatli yuklandi",
    "avatar_url": "http://localhost:8000/media/avatars/alisher_uz_avatar_20240904_123456.jpg"
}
```

**Xato Javoblari:**

*Fayl hajmi katta (400 Bad Request):*
```json
{
    "avatar": [
        "Rasm hajmi 5MB dan oshmasligi kerak."
    ]
}
```

*Noto'g'ri fayl formati (400 Bad Request):*
```json
{
    "avatar": [
        "Faqat JPEG, PNG, GIF, WEBP formatidagi rasmlar qabul qilinadi."
    ]
}
```

### 5.2 Avatar O'chirish

**Endpoint:** `DELETE /auth/delete-avatar/`

**Authentication:** Bearer Token talab qilinadi

**Muvaffaqiyatli Javob (200 OK):**
```json
{
    "message": "Avatar muvaffaqiyatli o'chirildi"
}
```

**Xato Javob - Avatar mavjud emas (400 Bad Request):**
```json
{
    "error": "O'chiriladigan avatar mavjud emas"
}
```

---

## 6. Parol O'zgartirish

**Endpoint:** `POST /auth/change-password/`

**Authentication:** Bearer Token talab qilinadi

**So'rov (Request):**
```json
{
    "old_password": "mypassword123",
    "new_password": "mynewpassword456",
    "new_password_confirm": "mynewpassword456"
}
```

**Muvaffaqiyatli Javob (200 OK):**
```json
{
    "message": "Parol muvaffaqiyatli o'zgartirildi"
}
```

**Xato Javoblari:**

*Eski parol noto'g'ri (400 Bad Request):*
```json
{
    "old_password": [
        "Eski parol noto'g'ri."
    ]
}
```

*Yangi parollar mos kelmadi (400 Bad Request):*
```json
{
    "new_password_confirm": [
        "Yangi parollar mos kelmaydi."
    ]
}
```

---

## 7. Hisob Tasdiqlash

**Endpoint:** `POST /auth/verify/`

**Authentication:** Bearer Token talab qilinadi

**So'rov (Request):**
```json
{
    "verification_code": "123456"
}
```

**Muvaffaqiyatli Javob (200 OK):**
```json
{
    "message": "Hisob muvaffaqiyatli tasdiqlandi",
    "is_verified": true
}
```

**Xato Javob (400 Bad Request):**
```json
{
    "error": "Tasdiqlash kodi noto'g'ri yoki muddati tugagan"
}
```

---

## 8. Foydalanuvchi Statistikasi

**Endpoint:** `GET /auth/stats/`

**Authentication:** Bearer Token talab qilinadi

**Muvaffaqiyatli Javob (200 OK):**
```json
{
    "total_orders": 15,
    "completed_orders": 12,
    "pending_orders": 2,
    "cancelled_orders": 1,
    "total_spent": "1,250,500.00",
    "average_order_value": "83,366.67",
    "member_since": "2024-09-04",
    "last_order_date": "2024-09-03",
    "favorite_products_count": 8,
    "cart_items_count": 3
}
```

---

## 9. Chiqish (Logout)

**Endpoint:** `POST /auth/logout/`

**Authentication:** Bearer Token talab qilinadi

**So'rov (Request):**
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTYzNDQ3NDQwMCwiaWF0IjoxNjMzNzgzMjAwLCJqdGkiOiI5ODc2NTQzMjEyIiwidXNlcl9pZCI6Mn0.stu789vwx012..."
}
```

**Muvaffaqiyatli Javob (200 OK):**
```json
{
    "message": "Muvaffaqiyatli chiqildi"
}
```

---

## 10. Authentication Status

### 10.1 Authentication Holati

**Endpoint:** `GET /auth/status/`

**Authentication:** Bearer Token talab qilinadi

**Muvaffaqiyatli Javob (200 OK):**
```json
{
    "authenticated": true,
    "user_id": 2,
    "username": "alisher_uz"
}
```

**Xato Javob (401 Unauthorized):**
```json
{
    "authenticated": false,
    "detail": "Authentication credentials were not provided."
}
```

### 10.2 Authentication Ma'lumotlari

**Endpoint:** `GET /auth/`

**Javob (200 OK):**
```json
{
    "authentication_required": true,
    "token_type": "Bearer",
    "login_url": "/api/auth/login/",
    "register_url": "/api/auth/register/",
    "token_url": "/api/auth/token/",
    "refresh_url": "/api/auth/token/refresh/",
    "profile_url": "/api/auth/profile/"
}
```

---

## Xato Kodlari

### HTTP Status Kodlari

- **200 OK** - So'rov muvaffaqiyatli bajarildi
- **201 Created** - Yangi resurs yaratildi
- **400 Bad Request** - Noto'g'ri so'rov ma'lumotlari
- **401 Unauthorized** - Authentication talab qilinadi
- **403 Forbidden** - Ruxsat yo'q
- **404 Not Found** - Resurs topilmadi
- **429 Too Many Requests** - So'rovlar soni cheklangan
- **500 Internal Server Error** - Server xatosi

### Authentication Xatolari

**Token mavjud emas (401):**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**Token noto'g'ri (401):**
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

**Ruxsat yo'q (403):**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

---

## Amaliy Misollar

### JavaScript (Fetch API)

```javascript
// 1. Ro'yxatdan o'tish
async function register() {
    const response = await fetch('http://localhost:8000/api/auth/register/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: 'alisher_uz',
            email: 'alisher@example.com',
            password: 'mypassword123',
            password_confirm: 'mypassword123',
            first_name: 'Alisher',
            last_name: 'Karimov',
            phone: '+998901234567'
        })
    });
    
    const data = await response.json();
    
    if (response.ok) {
        // Tokenlarni saqlash
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('refresh_token', data.tokens.refresh);
        console.log('Ro\'yxatdan o\'tish muvaffaqiyatli!', data.user);
    } else {
        console.error('Xato:', data);
    }
}

// 2. Kirish
async function login() {
    const response = await fetch('http://localhost:8000/api/auth/token/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: 'alisher_uz',
            password: 'mypassword123'
        })
    });
    
    const data = await response.json();
    
    if (response.ok) {
        localStorage.setItem('access_token', data.access);
        localStorage.setItem('refresh_token', data.refresh);
        console.log('Kirish muvaffaqiyatli!', data.user);
    } else {
        console.error('Kirish xatosi:', data);
    }
}

// 3. Profil ma'lumotlarini olish
async function getProfile() {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch('http://localhost:8000/api/auth/profile/', {
        headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        }
    });
    
    if (response.ok) {
        const profile = await response.json();
        console.log('Profil:', profile);
    } else if (response.status === 401) {
        // Token yangilash
        await refreshToken();
        // So'rovni qaytarish
        return getProfile();
    }
}

// 4. Token yangilash
async function refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    
    const response = await fetch('http://localhost:8000/api/auth/token/refresh/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            refresh: refreshToken
        })
    });
    
    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access);
        return data.access;
    } else {
        // Refresh token ham noto'g'ri - foydalanuvchini login sahifasiga yo'naltirish
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
    }
}

// 5. Avatar yuklash
async function uploadAvatar(file) {
    const token = localStorage.getItem('access_token');
    const formData = new FormData();
    formData.append('avatar', file);
    
    const response = await fetch('http://localhost:8000/api/auth/upload-avatar/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${token}`,
        },
        body: formData
    });
    
    const data = await response.json();
    
    if (response.ok) {
        console.log('Avatar yuklandi:', data.avatar_url);
    } else {
        console.error('Avatar yuklash xatosi:', data);
    }
}
```

### React Hook

```javascript
import { useState, useEffect } from 'react';

function useAuth() {
    const [user, setUser] = useState(null);
    const [token, setToken] = useState(localStorage.getItem('access_token'));
    const [loading, setLoading] = useState(false);

    // Profil ma'lumotlarini olish
    const fetchProfile = async () => {
        if (!token) return;
        
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/api/auth/profile/', {
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json',
                }
            });
            
            if (response.ok) {
                const profile = await response.json();
                setUser(profile);
            } else if (response.status === 401) {
                await refreshToken();
            }
        } catch (error) {
            console.error('Profil olish xatosi:', error);
        } finally {
            setLoading(false);
        }
    };

    // Token yangilash
    const refreshToken = async () => {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) return logout();
        
        try {
            const response = await fetch('http://localhost:8000/api/auth/token/refresh/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ refresh: refreshToken })
            });
            
            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access);
                setToken(data.access);
                return data.access;
            } else {
                logout();
            }
        } catch (error) {
            console.error('Token yangilash xatosi:', error);
            logout();
        }
    };

    // Chiqish
    const logout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setToken(null);
        setUser(null);
    };

    // Kirish
    const login = async (username, password) => {
        setLoading(true);
        try {
            const response = await fetch('http://localhost:8000/api/auth/token/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });
            
            if (response.ok) {
                const data = await response.json();
                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);
                setToken(data.access);
                setUser(data.user);
                return { success: true, user: data.user };
            } else {
                const error = await response.json();
                return { success: false, error };
            }
        } catch (error) {
            return { success: false, error: { message: 'Tarmoq xatosi' } };
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (token) {
            fetchProfile();
        }
    }, [token]);

    return {
        user,
        token,
        loading,
        login,
        logout,
        refreshToken,
        isAuthenticated: !!token && !!user
    };
}

// Komponentda ishlatish
function App() {
    const { user, loading, login, logout, isAuthenticated } = useAuth();
    
    if (loading) return <div>Yuklanmoqda...</div>;
    
    if (!isAuthenticated) {
        return <LoginForm onLogin={login} />;
    }
    
    return (
        <div>
            <h1>Salom, {user.full_name}!</h1>
            <button onClick={logout}>Chiqish</button>
        </div>
    );
}
```

---

## Xavfsizlik Tavsiyalari

1. **Token Saqlash:**
   - Access token'ni `localStorage` yoki `sessionStorage` da saqlang
   - Refresh token'ni xavfsiz joyda saqlang
   - Production muhitida `httpOnly` cookie'lardan foydalaning

2. **Token Yangilash:**
   - Access token muddati tugaganda avtomatik yangilang
   - Refresh token ham noto'g'ri bo'lsa foydalanuvchini qayta kirishga majburlang

3. **Xato Boshqaruv:**
   - Barcha xatolarni to'g'ri ushlang va foydalanuvchiga tushunarli xabar bering
   - Network xatolarini ham hisobga oling

4. **Ma'lumotlar Validatsiyasi:**
   - Client tomonda ham validatsiya qo'shing
   - Server tomondan kelgan xatolarni ko'rsating

Bu dokumentatsiya Organic Green API ning authentication qismini to'liq qamrab oladi va real loyihada ishlatishga tayyor.
