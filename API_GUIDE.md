# Organic Green Backend API

Django loyihasi uchun JWT autentifikatsiya tizimi bilan REST API.

## Sozlash

1. Virtual muhit yarating va faollashtiring:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# yoki
venv\Scripts\activate  # Windows
```

2. Dependencylarni o'rnating:
```bash
pip install -r requirements.txt
```

3. Migratsiyalarni ishga tushiring:
```bash
python manage.py makemigrations
python manage.py migrate
```

4. Serverni ishga tushiring:
```bash
python manage.py runserver
```

## API Endpointlari

### Autentifikatsiya

#### 1. Oddiy ro'yxatdan o'tish
**POST** `/api/auth/register/simple/`

Faqat username va password bilan ro'yxatdan o'tish.

```json
{
    "username": "foydalanuvchi_nomi",
    "password": "parol123"
}
```

**Javob:**
```json
{
    "message": "Foydalanuvchi muvaffaqiyatli ro'yxatdan o'tdi",
    "user": {
        "id": 1,
        "username": "foydalanuvchi_nomi",
        "email": "foydalanuvchi_nomi@temp.com",
        "first_name": "",
        "last_name": "",
        "full_name": "",
        "is_active": true,
        "date_joined": "2025-08-26T12:00:00Z",
        "last_login": null
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### 2. To'liq ro'yxatdan o'tish
**POST** `/api/auth/register/`

Barcha ma'lumotlar bilan ro'yxatdan o'tish.

```json
{
    "username": "foydalanuvchi_nomi",
    "email": "email@example.com",
    "password": "parol123456",
    "password_confirm": "parol123456",
    "first_name": "Ism",
    "last_name": "Familiya"
}
```

#### 3. Tizimga kirish
**POST** `/api/auth/login/`

Username yoki email bilan tizimga kirish.

```json
{
    "username": "foydalanuvchi_nomi",  // yoki email
    "password": "parol123"
}
```

**Javob:**
```json
{
    "message": "Tizimga muvaffaqiyatli kirildi",
    "user": {
        "id": 1,
        "username": "foydalanuvchi_nomi",
        "email": "email@example.com",
        "first_name": "Ism",
        "last_name": "Familiya",
        "full_name": "Ism Familiya",
        "is_active": true,
        "date_joined": "2025-08-26T12:00:00Z",
        "last_login": "2025-08-26T12:30:00Z"
    },
    "tokens": {
        "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    }
}
```

#### 4. JWT Token olish
**POST** `/api/auth/token/`

```json
{
    "username": "foydalanuvchi_nomi",
    "password": "parol123"
}
```

#### 5. Token yangilash
**POST** `/api/auth/token/refresh/`

```json
{
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 6. Profil ma'lumotlari
**GET** `/api/auth/profile/`

Headers:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### 7. Profil yangilash
**PUT/PATCH** `/api/auth/profile/`

```json
{
    "first_name": "Yangi Ism",
    "last_name": "Yangi Familiya",
    "email": "yangi_email@example.com"
}
```

#### 8. Parol o'zgartirish
**POST** `/api/auth/change-password/`

```json
{
    "old_password": "eski_parol",
    "new_password": "yangi_parol",
    "new_password_confirm": "yangi_parol"
}
```

#### 9. Tizimdan chiqish
**POST** `/api/auth/logout/`

```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 10. Autentifikatsiya holati
**GET** `/api/auth/status/`

Foydalanuvchi autentifikatsiya holatini tekshirish.

### JWT Token haqida

- **Access token** - 60 daqiqa amal qiladi
- **Refresh token** - 7 kun amal qiladi
- Token yangilanganida eski refresh token bekor qilinadi (blacklist)

### Xatolar

API xatolar uchun standart HTTP status codelardan foydalanadi:

- `400 Bad Request` - Noto'g'ri ma'lumotlar
- `401 Unauthorized` - Autentifikatsiya talab qilinadi
- `403 Forbidden` - Ruxsat berilmagan
- `404 Not Found` - Topilmadi
- `500 Internal Server Error` - Server xatosi

**Xato misoli:**
```json
{
    "username": ["Bu foydalanuvchi nomi allaqachon band."],
    "password": ["Parol kamida 6 ta belgidan iborat bo'lishi kerak."]
}
```

### Testlar

Testlarni ishga tushirish:

```bash
python manage.py test api.test_auth --settings=core.test_settings -v 2
```

### API Documentation

Barcha mavjud endpointlarni ko'rish uchun:

**GET** `/api/`

### CORS

Frontend uchun CORS sozlangan:
- `http://localhost:3000`
- `http://127.0.0.1:3000`

### Throttling

API cheklovlari:
- Anonymous foydalanuvchilar: 100 so'rov/soat
- Autentifikatsiya qilingan foydalanuvchilar: 1000 so'rov/soat

## Misol foydalanish (JavaScript)

```javascript
// Ro'yxatdan o'tish
const register = async () => {
    const response = await fetch('http://localhost:8000/api/auth/register/simple/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            username: 'test_user',
            password: 'test123'
        })
    });
    
    const data = await response.json();
    
    if (response.ok) {
        localStorage.setItem('access_token', data.tokens.access);
        localStorage.setItem('refresh_token', data.tokens.refresh);
        console.log('Ro\'yxatdan o\'tish muvaffaqiyatli!', data.user);
    } else {
        console.error('Xato:', data);
    }
};

// API bilan ishlash
const apiCall = async (url, options = {}) => {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(`http://localhost:8000${url}`, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
            ...options.headers
        }
    });
    
    if (response.status === 401) {
        // Token yaroqsiz, yangilash
        await refreshToken();
        return apiCall(url, options); // Qayta urinish
    }
    
    return response;
};

// Token yangilash
const refreshToken = async () => {
    const refresh = localStorage.getItem('refresh_token');
    
    const response = await fetch('http://localhost:8000/api/auth/token/refresh/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            refresh: refresh
        })
    });
    
    if (response.ok) {
        const data = await response.json();
        localStorage.setItem('access_token', data.access);
    } else {
        // Refresh token ham yaroqsiz, qayta login qilish kerak
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
    }
};
```
