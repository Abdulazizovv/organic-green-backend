# Course Application API Documentation

## Umumiy ma'lumot

Course Application API foydalanuvchilarga kurs arizalarini yuborish va adminlarga ularni boshqarish imkonini beradi.

**Base URL:** `https://your-domain.com/api/course/`

## Authentication

- **Public endpoints:** Authentication talab etmaydi
- **Admin endpoints:** JWT Bearer token va admin huquqlari talab etiladi

## Rate Limiting

- **Course applications:** 10 ariza/soat (anonim foydalanuvchilar uchun)

---

## Public API Endpoints

### 1. Kurs arizasini yuborish

**POST** `/applications/`

Yangi kurs arizasini yuborish uchun.

#### Request

```json
{
    "full_name": "Abdulaziz Abdullayev",
    "email": "abdulaziz@example.com",
    "phone_number": "+998901234567",
    "course_name": "Python dasturlash kursi",
    "message": "Men bu kursga juda qiziqaman va o'rganishni xohlayman"
}
```

#### Request Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `full_name` | string | ✅ | To'liq ism va familiya (kamida 2 ta so'z) |
| `email` | string | ✅ | Email manzili |
| `phone_number` | string | ✅ | Telefon raqami (+998901234567 formatida) |
| `course_name` | string | ✅ | Kurs nomi |
| `message` | string | ❌ | Qo'shimcha xabar |

#### Response (201 Created)

```json
{
    "success": true,
    "message": "Arizangiz muvaffaqiyatli yuborildi!",
    "application_number": "KURS-20240904-00001",
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "application_number": "KURS-20240904-00001",
        "full_name": "Abdulaziz Abdullayev",
        "course_name": "Python dasturlash kursi",
        "created_at": "2024-09-04T10:30:00Z",
        "status": "Kutilmoqda"
    }
}
```

#### Error Response (400 Bad Request)

```json
{
    "full_name": ["Iltimos, ism va familiyangizni to'liq kiriting"],
    "phone_number": ["Telefon raqami to'g'ri formatda bo'lishi kerak. Masalan: +998901234567"],
    "email": ["Bu email manzili yaroqsiz."]
}
```

---

### 2. Ariza holatini tekshirish

**GET** `/applications/check/{application_number}/`

Ariza raqami orqali ariza holatini tekshirish.

#### Request

```
GET /api/course/applications/check/KURS-20240904-00001/
```

#### Response (200 OK)

```json
{
    "success": true,
    "application": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "application_number": "KURS-20240904-00001",
        "full_name": "Abdulaziz Abdullayev",
        "email": "abdulaziz@example.com",
        "phone_number": "+998901234567",
        "phone_clean": "998901234567",
        "course_name": "Python dasturlash kursi",
        "message": "Men bu kursga juda qiziqaman va o'rganishni xohlayman",
        "processed": false,
        "status_display": "Kutilmoqda",
        "created_at": "2024-09-04T10:30:00Z",
        "created_at_formatted": "04.09.2024 10:30",
        "application_age": 0
    }
}
```

#### Error Response (404 Not Found)

```json
{
    "success": false,
    "error": "Ariza topilmadi. Ariza raqamini tekshiring."
}
```

---

### 3. Mavjud kurslar ro'yxati

**GET** `/courses/`

Barcha mavjud kurslar ro'yxatini olish.

#### Response (200 OK)

```json
{
    "success": true,
    "courses": [
        {
            "name": "Python dasturlash kursi",
            "applications_count": 15
        },
        {
            "name": "JavaScript kursi",
            "applications_count": 12
        },
        {
            "name": "Django framework kursi",
            "applications_count": 8
        }
    ]
}
```

---

## Admin API Endpoints

> **⚠️ Diqqat:** Barcha admin endpoint'lar JWT Bearer token va admin huquqlarini talab qiladi.

### Authentication Header

```
Authorization: Bearer <your-jwt-token>
```

---

### 4. Barcha arizalar ro'yxati

**GET** `/admin/applications/`

Barcha arizalar ro'yxatini olish (filtrlash va qidiruv bilan).

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `processed` | boolean | Ariza holati bo'yicha filtrlash (true/false) |
| `course_name` | string | Kurs nomi bo'yicha filtrlash |
| `search` | string | Ism, email, telefon, kurs nomi bo'yicha qidirish |
| `ordering` | string | Tartiblash (-created_at, full_name, course_name) |
| `page` | integer | Sahifa raqami |

#### Request Examples

```
GET /api/course/admin/applications/
GET /api/course/admin/applications/?processed=false
GET /api/course/admin/applications/?course_name=Python
GET /api/course/admin/applications/?search=Abdulaziz
GET /api/course/admin/applications/?ordering=-created_at&page=2
```

#### Response (200 OK)

```json
{
    "count": 50,
    "next": "http://localhost:8000/api/course/admin/applications/?page=2",
    "previous": null,
    "results": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "application_number": "KURS-20240904-00001",
            "full_name": "Abdulaziz Abdullayev",
            "email": "abdulaziz@example.com",
            "phone_number": "+998901234567",
            "course_name": "Python dasturlash kursi",
            "message": "Men bu kursga juda qiziqaman",
            "processed": false,
            "status_display": "Kutilmoqda",
            "created_at": "2024-09-04T10:30:00Z",
            "created_at_formatted": "04.09.2024 10:30",
            "application_age": 0
        }
    ]
}
```

---

### 5. Ariza tafsilotlari

**GET** `/admin/applications/{id}/`

Muayyan arizaning to'liq ma'lumotlarini olish.

#### Response (200 OK)

```json
{
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "application_number": "KURS-20240904-00001",
    "full_name": "Abdulaziz Abdullayev",
    "email": "abdulaziz@example.com",
    "phone_number": "+998901234567",
    "phone_clean": "998901234567",
    "course_name": "Python dasturlash kursi",
    "message": "Men bu kursga juda qiziqaman va o'rganishni xohlayman",
    "processed": false,
    "status_display": "Kutilmoqda",
    "created_at": "2024-09-04T10:30:00Z",
    "created_at_formatted": "04.09.2024 10:30",
    "application_age": 0
}
```

---

### 6. Ariza holatini yangilash

**PATCH** `/admin/applications/{id}/`

Arizaning processed holatini yangilash.

#### Request

```json
{
    "processed": true
}
```

#### Response (200 OK)

```json
{
    "processed": true
}
```

---

### 7. Statistika

**GET** `/admin/statistics/`

Arizalar bo'yicha umumiy statistika.

#### Response (200 OK)

```json
{
    "total_applications": 150,
    "processed_applications": 120,
    "pending_applications": 30,
    "today_applications": 5,
    "popular_courses": [
        {
            "course_name": "Python dasturlash kursi",
            "count": 45
        },
        {
            "course_name": "JavaScript kursi",
            "count": 38
        },
        {
            "course_name": "Django framework kursi",
            "count": 25
        }
    ],
    "recent_applications": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "application_number": "KURS-20240904-00001",
            "full_name": "Abdulaziz Abdullayev",
            "email": "abdulaziz@example.com",
            "phone_number": "+998901234567",
            "course_name": "Python dasturlash kursi",
            "message": "Men bu kursga juda qiziqaman",
            "processed": false,
            "status_display": "Kutilmoqda",
            "created_at": "2024-09-04T10:30:00Z",
            "created_at_formatted": "04.09.2024 10:30",
            "application_age": 0
        }
    ]
}
```

---

### 8. Bir nechta arizani yangilash

**POST** `/admin/applications/bulk-update/`

Bir vaqtda bir nechta arizaning holatini yangilash.

#### Request

```json
{
    "application_ids": [
        "550e8400-e29b-41d4-a716-446655440000",
        "550e8400-e29b-41d4-a716-446655440001"
    ],
    "processed": true
}
```

#### Response (200 OK)

```json
{
    "success": true,
    "message": "2 ta ariza qayta ishlangan deb belgilandi",
    "updated_count": 2
}
```

#### Error Response (400 Bad Request)

```json
{
    "error": "application_ids is required"
}
```

---

### 9. Arizalarni eksport qilish

**GET** `/admin/applications/export/`

Arizalarni JSON formatida eksport qilish.

#### Query Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `processed` | boolean | Ariza holati bo'yicha filtrlash |
| `course_name` | string | Kurs nomi bo'yicha filtrlash |
| `date_from` | string | Boshlanish sanasi (YYYY-MM-DD) |
| `date_to` | string | Tugash sanasi (YYYY-MM-DD) |

#### Request Examples

```
GET /api/course/admin/applications/export/
GET /api/course/admin/applications/export/?processed=false
GET /api/course/admin/applications/export/?date_from=2024-09-01&date_to=2024-09-30
```

#### Response (200 OK)

```json
{
    "success": true,
    "count": 25,
    "applications": [
        {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "application_number": "KURS-20240904-00001",
            "full_name": "Abdulaziz Abdullayev",
            "email": "abdulaziz@example.com",
            "phone_number": "+998901234567",
            "phone_clean": "998901234567",
            "course_name": "Python dasturlash kursi",
            "message": "Men bu kursga juda qiziqaman",
            "processed": false,
            "status_display": "Kutilmoqda",
            "created_at": "2024-09-04T10:30:00Z",
            "created_at_formatted": "04.09.2024 10:30",
            "application_age": 0
        }
    ]
}
```

---

## Error Codes

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Muvaffaqiyatli so'rov |
| 201 | Created - Yangi resurs yaratildi |
| 400 | Bad Request - Noto'g'ri so'rov |
| 401 | Unauthorized - Autentifikatsiya talab etiladi |
| 403 | Forbidden - Ruxsat yo'q |
| 404 | Not Found - Resurs topilmadi |
| 429 | Too Many Requests - Juda ko'p so'rovlar |
| 500 | Internal Server Error - Server xatosi |

### Validation Errors

#### Full Name Validation

```json
{
    "full_name": ["Iltimos, ism va familiyangizni to'liq kiriting"]
}
```

#### Phone Number Validation

```json
{
    "phone_number": ["Telefon raqami to'g'ri formatda bo'lishi kerak. Masalan: +998901234567"]
}
```

#### Email Validation

```json
{
    "email": ["Bu email manzili yaroqsiz."]
}
```

#### Course Name Validation

```json
{
    "course_name": ["Kurs nomini kiritish majburiy"]
}
```

---

## JavaScript Misollari

### Ariza yuborish

```javascript
const submitApplication = async (applicationData) => {
    try {
        const response = await fetch('/api/course/applications/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(applicationData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            console.log('Ariza yuborildi:', data.application_number);
            return data;
        } else {
            console.error('Xatolik:', data);
            throw new Error('Ariza yuborishda xatolik');
        }
    } catch (error) {
        console.error('Network xatolik:', error);
        throw error;
    }
};

// Misol
const applicationData = {
    full_name: "Abdulaziz Abdullayev",
    email: "abdulaziz@example.com",
    phone_number: "+998901234567",
    course_name: "Python dasturlash kursi",
    message: "Men bu kursga qiziqaman"
};

submitApplication(applicationData);
```

### Ariza holatini tekshirish

```javascript
const checkApplicationStatus = async (applicationNumber) => {
    try {
        const response = await fetch(`/api/course/applications/check/${applicationNumber}/`);
        const data = await response.json();
        
        if (response.ok) {
            return data.application;
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Xatolik:', error);
        throw error;
    }
};

// Misol
checkApplicationStatus('KURS-20240904-00001')
    .then(application => {
        console.log('Ariza holati:', application.status_display);
    });
```

### Admin API (JWT bilan)

```javascript
const getApplications = async (token) => {
    try {
        const response = await fetch('/api/course/admin/applications/', {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            }
        });
        
        const data = await response.json();
        return data.results;
    } catch (error) {
        console.error('Xatolik:', error);
        throw error;
    }
};

const updateApplicationStatus = async (token, applicationId, processed) => {
    try {
        const response = await fetch(`/api/course/admin/applications/${applicationId}/`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ processed })
        });
        
        return await response.json();
    } catch (error) {
        console.error('Xatolik:', error);
        throw error;
    }
};
```

---

## Qo'shimcha ma'lumotlar

### Ariza raqami formati

Ariza raqamlari avtomatik ravishda quyidagi formatda yaratiladi:
- **Format:** `KURS-YYYYMMDD-XXXXX`
- **Misol:** `KURS-20240904-00001`

Bu yerda:
- `KURS` - ariza turi
- `YYYYMMDD` - sana (yil-oy-kun)
- `XXXXX` - kunlik ketma-ket raqam (5 xonali)

### Pagination

Admin API'larda pagination mavjud:
- **Default page size:** 20
- **Query parameter:** `page`
- **Response fields:** `count`, `next`, `previous`, `results`

### Filtering va Search

Admin API'larda quyidagi filtrlar mavjud:
- **processed:** `true`/`false`
- **course_name:** kurs nomi bo'yicha
- **search:** ism, email, telefon, kurs nomi bo'yicha qidirish
- **ordering:** `-created_at`, `full_name`, `course_name`

Bu dokumentatsiya Course Application API'ning to'liq qo'llanmasini o'z ichiga oladi.
