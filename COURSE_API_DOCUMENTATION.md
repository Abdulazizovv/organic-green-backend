# Course Management API Documentation

## Overview

Complete course management system with public and admin APIs supporting multilingual content (UZ/RU/EN), course applications, soft delete, audit trails, and comprehensive validation.

## Base URL
```
http://api.organicgreen.uz/api/course/
```

## Authentication

**Public API**: No authentication required for viewing courses and submitting applications
**Admin API**: Bearer token authentication required (`Authorization: Bearer <token>`)

## Rate Limiting

- **Course Applications**: 10 applications per hour per IP/user
- **General API**: Standard rate limits apply

---

## PUBLIC API

### 1. List Courses

**GET** `/courses/`

Get list of active courses with filtering and search capabilities.

#### Query Parameters:
- `search` (string): Search in course titles and descriptions
- `category` (string): Filter by course category
- `level` (string): Filter by level (`beginner`, `intermediate`, `advanced`)
- `format` (string): Filter by format (`online`, `offline`, `hybrid`)
- `language` (string): Filter by language (`uz`, `ru`, `en`)
- `min_price` (integer): Minimum price filter
- `max_price` (integer): Maximum price filter
- `has_seats` (boolean): Filter courses with available seats

#### Example Request:
```bash
curl -X GET "http://api.organicgreen.uz/api/course/courses/?search=python&level=beginner&has_seats=true"
```

#### Example Response:
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Python Programming Basics",
      "description": "Learn Python programming from scratch",
      "slug": "python-programming-basics",
      "category": "Programming",
      "level": "beginner",
      "format": "online",
      "language": "en",
      "price": 500000,
      "discount_percentage": 20,
      "price_final": 400000,
      "start_date": "2024-02-01",
      "duration_weeks": 8,
      "seats": 30,
      "applications_count": 15,
      "has_available_seats": true,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

### 2. Course Details

**GET** `/courses/{slug}/`

Get detailed information about a specific course.

#### Example Request:
```bash
curl -X GET "http://api.organicgreen.uz/api/course/courses/python-programming-basics/"
```

#### Example Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Python Programming Basics",
  "description": "Learn Python programming from scratch with hands-on projects",
  "content": "Complete Python course covering variables, functions, OOP...",
  "slug": "python-programming-basics",
  "category": "Programming",
  "level": "beginner",
  "format": "online",
  "language": "en",
  "price": 500000,
  "discount_percentage": 20,
  "price_final": 400000,
  "start_date": "2024-02-01",
  "end_date": "2024-03-28",
  "duration_weeks": 8,
  "schedule": "Mon, Wed, Fri 18:00-20:00",
  "seats": 30,
  "applications_count": 15,
  "has_available_seats": true,
  "is_active": true,
  "created_at": "2024-01-15T10:00:00Z"
}
```

### 3. Submit Course Application

**POST** `/applications/`

Submit an application for a course.

#### Request Body:
```json
{
  "course": "python-programming-basics",
  "full_name": "John Doe",
  "phone": "+998901234567",
  "email": "john@example.com",
  "city": "Tashkent",
  "investment_amount": 5000000,
  "referral_source": "social_media",
  "message": "I'm interested in learning Python programming"
}
```

#### Field Validation:
- `course` (required): Course slug
- `full_name` (required): Full name (2-100 characters)
- `phone` (required): E.164 format phone number
- `email` (optional): Valid email address
- `city` (required): City name (2-50 characters)
- `investment_amount` (optional): Investment amount (0-999,999,999)
- `referral_source` (optional): One of predefined choices
- `message` (optional): Additional message (max 1000 characters)

#### Example Request:
```bash
curl -X POST "http://api.organicgreen.uz/api/course/applications/" \
  -H "Content-Type: application/json" \
  -d '{
    "course": "python-programming-basics",
    "full_name": "John Doe",
    "phone": "+998901234567",
    "email": "john@example.com",
    "city": "Tashkent",
    "investment_amount": 5000000,
    "referral_source": "social_media"
  }'
```

#### Example Response:
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "course": "python-programming-basics",
  "full_name": "John Doe",
  "phone": "+998901234567",
  "email": "john@example.com",
  "city": "Tashkent",
  "investment_amount": 5000000,
  "referral_source": "social_media",
  "status": "pending",
  "created_at": "2024-01-20T14:30:00Z"
}
```

#### Validation Rules:
- **Duplicate Prevention**: Same phone number cannot apply for the same course within 14 days
- **Seat Availability**: Cannot apply if course is full
- **Phone Format**: Must be valid E.164 format (e.g., +998901234567)

---

## ADMIN API

**Authentication Required**: All admin endpoints require admin user authentication.

### 1. Admin Course List

**GET** `/admin/courses/`

Get all courses (including inactive) with admin features.

#### Query Parameters:
Same as public API plus:
- `is_active` (boolean): Filter by active status

#### Example Request:
```bash
curl -X GET "http://api.organicgreen.uz/api/course/admin/courses/" \
  -H "Authorization: Bearer <admin_token>"
```

### 2. Create Course

**POST** `/admin/courses/`

Create a new course.

#### Request Body:
```json
{
  "title_en": "Advanced Python Development",
  "title_uz": "Python'da ilg'or dasturlash",
  "title_ru": "Продвинутая разработка на Python",
  "description_en": "Advanced Python concepts and frameworks",
  "description_uz": "Python'ning ilg'or kontseptsiyalari",
  "description_ru": "Продвинутые концепции Python",
  "content_en": "Detailed course content...",
  "content_uz": "Batafsil kurs mazmuni...",
  "content_ru": "Подробное содержание курса...",
  "category": "Programming",
  "level": "advanced",
  "format": "hybrid",
  "language": "en",
  "price": 800000,
  "discount_percentage": 15,
  "start_date": "2024-03-01",
  "end_date": "2024-04-26",
  "duration_weeks": 8,
  "schedule": "Tue, Thu 19:00-21:00",
  "seats": 20,
  "is_active": true
}
```

### 3. Update Course

**PUT/PATCH** `/admin/courses/{slug}/`

Update an existing course.

### 4. Delete Course

**DELETE** `/admin/courses/{slug}/`

Soft delete a course (sets `is_deleted=True`).

### 5. List Applications

**GET** `/admin/applications/`

Get all course applications with filtering.

#### Query Parameters:
- `course` (string): Filter by course slug
- `course_id` (uuid): Filter by course ID
- `course_title` (string): Search in course titles
- `status` (string): Filter by status (`pending`, `approved`, `rejected`)
- `created_after` (datetime): Filter applications created after date
- `created_before` (datetime): Filter applications created before date
- `city` (string): Filter by city
- `referral_source` (string): Filter by referral source
- `phone` (string): Search by phone number
- `name` (string): Search by applicant name

#### Example Request:
```bash
curl -X GET "http://api.organicgreen.uz/api/course/admin/applications/?status=pending&course=python-programming-basics" \
  -H "Authorization: Bearer <admin_token>"
```

### 6. Update Application Status

**PATCH** `/admin/applications/{id}/`

Update application status and details.

#### Request Body:
```json
{
  "status": "approved",
  "admin_notes": "Approved after interview"
}
```

### 7. Course Statistics

**GET** `/admin/statistics/`

Get comprehensive course statistics.

#### Example Response:
```json
{
  "courses": {
    "total": 25,
    "active": 20,
    "inactive": 5
  },
  "applications": {
    "total": 150,
    "pending": 25,
    "approved": 100,
    "rejected": 25
  },
  "top_courses": [
    {
      "title_en": "Python Programming Basics",
      "applications_count": 45,
      "slug": "python-programming-basics"
    }
  ],
  "recent_applications": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "course__title_en": "Python Programming Basics",
      "full_name": "John Doe",
      "status": "pending",
      "created_at": "2024-01-20T14:30:00Z"
    }
  ]
}
```

### 8. Bulk Update Applications

**POST** `/admin/applications/bulk-update/`

Update status of multiple applications at once.

#### Request Body:
```json
{
  "application_ids": [
    "660e8400-e29b-41d4-a716-446655440001",
    "660e8400-e29b-41d4-a716-446655440002"
  ],
  "status": "approved"
}
```

---

## Data Models

### Course Model
- **ID**: UUID primary key
- **Multilingual Fields**: title, description, content (en/uz/ru)
- **Basic Info**: slug, category, level, format, language
- **Scheduling**: start_date, end_date, duration_weeks, schedule
- **Pricing**: price, discount_percentage
- **Capacity**: seats, applications_count
- **Status**: is_active
- **Audit**: created_at, updated_at, created_by, updated_by
- **Soft Delete**: is_deleted, deleted_at

### Application Model
- **ID**: UUID primary key
- **Course Reference**: Foreign key to Course
- **User Reference**: Optional foreign key to User
- **Personal Info**: full_name, phone, email, city
- **Additional**: investment_amount, referral_source, message
- **Status**: pending/approved/rejected
- **Admin**: admin_notes
- **Audit**: created_at, updated_at, created_by, updated_by
- **Soft Delete**: is_deleted, deleted_at

---

## Error Responses

### Validation Errors (400)
```json
{
  "field_name": ["Error message"],
  "phone": ["Enter a valid phone number in E.164 format."],
  "non_field_errors": ["You have already applied for this course recently."]
}
```

### Not Found (404)
```json
{
  "detail": "Not found."
}
```

### Permission Denied (403)
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### Rate Limited (429)
```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

---

## Usage Examples

### Frontend Integration

#### Course Listing Page
```javascript
// Fetch courses with search
const response = await fetch('/api/course/courses/?search=python&level=beginner');
const data = await response.json();
```

#### Course Application Form
```javascript
// Submit application
const applicationData = {
  course: 'python-programming-basics',
  full_name: 'John Doe',
  phone: '+998901234567',
  email: 'john@example.com',
  city: 'Tashkent',
  investment_amount: 5000000,
  referral_source: 'website'
};

const response = await fetch('/api/course/applications/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(applicationData)
});
```

#### Admin Dashboard
```javascript
// Get statistics
const stats = await fetch('/api/course/admin/statistics/', {
  headers: {
    'Authorization': `Bearer ${adminToken}`
  }
});

// Update application status
await fetch(`/api/course/admin/applications/${applicationId}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${adminToken}`,
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ status: 'approved' })
});
```

---

## Testing Endpoints

Use the provided test data and examples to verify the implementation. All endpoints support standard HTTP methods and return appropriate status codes with detailed error messages.
