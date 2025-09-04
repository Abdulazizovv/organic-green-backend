# Franchise API Documentation

## Overview

The Franchise API allows users to submit franchise applications and provides administrative endpoints for managing these applications. The API follows REST principles and uses JSON for data exchange.

## Base URL
```
http://api.organicgreen.uz/api/franchise/
```

## Authentication

- **Public Access**: Anyone can submit franchise applications
- **Admin Access**: Only staff/admin users can view, update, and delete applications
- **Authentication Method**: JWT Bearer Token for admin endpoints

---

## Endpoints

### 1. Submit Franchise Application

**Endpoint:** `POST /applications/`  
**Access:** Public (No authentication required)  
**Description:** Submit a new franchise application

#### Request Body
```json
{
    "full_name": "string (required, max 255 chars)",
    "phone": "string (required, max 20 chars)",
    "email": "string (optional, valid email format)",
    "city": "string (required, max 100 chars)",
    "investment_amount": "decimal (required, 0.01 - 10,000,000.00)",
    "experience": "string (optional, text field)",
    "message": "string (optional, text field)"
}
```

#### Example Request
```json
{
    "full_name": "Alisher Karimov",
    "phone": "+998901234567",
    "email": "alisher@example.com",
    "city": "Toshkent",
    "investment_amount": "50000.00",
    "experience": "5 yillik restoran biznesida tajriba",
    "message": "Organic Green franshizasini ochishga juda qiziqaman"
}
```

#### Success Response (201 Created)
```json
{
    "message": "Franchise application submitted successfully",
    "application_id": 1,
    "status": "pending"
}
```

#### Error Responses

**Validation Error (400 Bad Request):**
```json
{
    "full_name": ["This field is required."],
    "phone": ["Phone number must be at least 10 digits."],
    "investment_amount": ["Investment amount must be greater than 0."]
}
```

**Field-specific validation errors:**
- `full_name`: Required, minimum 2 characters
- `phone`: Required, minimum 10 digits (supports +, -, (), spaces)
- `email`: Must be valid email format if provided
- `city`: Required, minimum 2 characters
- `investment_amount`: Required, between $0.01 and $10,000,000
- `experience`: Optional text
- `message`: Optional text

---

### 2. List Franchise Applications (Admin Only)

**Endpoint:** `GET /applications/list/`  
**Access:** Admin/Staff only  
**Authentication:** Bearer Token required  
**Description:** Get paginated list of all franchise applications

#### Query Parameters
- `status`: Filter by status (`pending`, `reviewed`, `approved`, `rejected`)
- `city`: Filter by city name
- `search`: Search in full_name, phone, email, city
- `ordering`: Sort by fields (`created_at`, `-created_at`, `investment_amount`, `-investment_amount`, `full_name`, `-full_name`)
- `page`: Page number for pagination
- `page_size`: Number of items per page

#### Example Request
```
GET /applications/list/?status=pending&ordering=-created_at&page=1
```

#### Success Response (200 OK)
```json
{
    "count": 25,
    "next": "http://api.organicgreen.uz/api/franchise/applications/list/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "full_name": "Alisher Karimov",
            "phone": "+998901234567",
            "city": "Toshkent",
            "investment_amount": "50000.00",
            "formatted_investment_amount": "$50,000.00",
            "status": "pending",
            "is_pending": true,
            "is_approved": false,
            "created_at": "2024-09-04T10:30:00.123456Z"
        },
        {
            "id": 2,
            "full_name": "Madina Nazarova",
            "phone": "+998901111111",
            "city": "Samarqand",
            "investment_amount": "75000.00",
            "formatted_investment_amount": "$75,000.00",
            "status": "reviewed",
            "is_pending": false,
            "is_approved": false,
            "created_at": "2024-09-03T15:20:00.654321Z"
        }
    ]
}
```

#### Error Responses

**Unauthorized (401 Unauthorized):**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**Forbidden (403 Forbidden):**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

---

### 3. Get Franchise Application Details (Admin Only)

**Endpoint:** `GET /applications/{id}/`  
**Access:** Admin/Staff only  
**Authentication:** Bearer Token required  
**Description:** Get detailed information about a specific franchise application

#### Path Parameters
- `id`: Integer, application ID

#### Example Request
```
GET /applications/1/
```

#### Success Response (200 OK)
```json
{
    "id": 1,
    "full_name": "Alisher Karimov",
    "phone": "+998901234567",
    "email": "alisher@example.com",
    "city": "Toshkent",
    "investment_amount": "50000.00",
    "formatted_investment_amount": "$50,000.00",
    "experience": "5 yillik restoran biznesida tajriba",
    "message": "Organic Green franshizasini ochishga juda qiziqaman",
    "status": "pending",
    "is_pending": true,
    "is_approved": false,
    "created_at": "2024-09-04T10:30:00.123456Z",
    "updated_at": "2024-09-04T10:30:00.123456Z"
}
```

#### Error Responses

**Not Found (404 Not Found):**
```json
{
    "detail": "Not found."
}
```

**Unauthorized (401 Unauthorized):**
```json
{
    "detail": "Authentication credentials were not provided."
}
```

**Forbidden (403 Forbidden):**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

---

### 4. Update Franchise Application (Admin Only)

**Endpoint:** `PATCH /applications/{id}/update/`  
**Access:** Admin/Staff only  
**Authentication:** Bearer Token required  
**Description:** Update franchise application (typically used to change status)

#### Path Parameters
- `id`: Integer, application ID

#### Request Body (Partial Update)
```json
{
    "status": "approved",
    "message": "Updated admin notes"
}
```

#### Available Status Values
- `pending`: Yangi (New)
- `reviewed`: Ko'rib chiqilgan (Reviewed)
- `approved`: Ma'qullangan (Approved)
- `rejected`: Rad etilgan (Rejected)

#### Example Request
```json
{
    "status": "approved"
}
```

#### Success Response (200 OK)
```json
{
    "id": 1,
    "full_name": "Alisher Karimov",
    "phone": "+998901234567",
    "email": "alisher@example.com",
    "city": "Toshkent",
    "investment_amount": "50000.00",
    "formatted_investment_amount": "$50,000.00",
    "experience": "5 yillik restoran biznesida tajriba",
    "message": "Organic Green franshizasini ochishga juda qiziqaman",
    "status": "approved",
    "is_pending": false,
    "is_approved": true,
    "created_at": "2024-09-04T10:30:00.123456Z",
    "updated_at": "2024-09-04T12:45:30.987654Z",
    "message": "Application status changed from pending to approved"
}
```

#### Error Responses

**Validation Error (400 Bad Request):**
```json
{
    "status": ["Invalid status value."]
}
```

**Not Found (404 Not Found):**
```json
{
    "detail": "Not found."
}
```

---

### 5. Delete Franchise Application (Admin Only)

**Endpoint:** `DELETE /applications/{id}/delete/`  
**Access:** Admin/Staff only  
**Authentication:** Bearer Token required  
**Description:** Delete a franchise application

#### Path Parameters
- `id`: Integer, application ID

#### Example Request
```
DELETE /applications/1/delete/
```

#### Success Response (200 OK)
```json
{
    "message": "Franchise application 1 deleted successfully"
}
```

#### Error Responses

**Not Found (404 Not Found):**
```json
{
    "detail": "Not found."
}
```

**Forbidden (403 Forbidden):**
```json
{
    "detail": "You do not have permission to perform this action."
}
```

---

## Data Models

### FranchiseApplication

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | Integer | Auto | Unique identifier |
| full_name | String(255) | Yes | Applicant's full name |
| phone | String(20) | Yes | Phone number |
| email | Email | No | Email address |
| city | String(100) | Yes | City for franchise location |
| investment_amount | Decimal(12,2) | Yes | Available investment ($0.01 - $10M) |
| experience | Text | No | Previous business experience |
| message | Text | No | Additional comments |
| status | Choice | Auto | Application status (default: pending) |
| created_at | DateTime | Auto | Submission timestamp |
| updated_at | DateTime | Auto | Last update timestamp |

### Computed Fields

| Field | Type | Description |
|-------|------|-------------|
| formatted_investment_amount | String | Investment amount formatted as currency |
| is_pending | Boolean | True if status is 'pending' |
| is_approved | Boolean | True if status is 'approved' |

---

## Status Workflow

1. **pending** (Yangi) - Initial status when application is submitted
2. **reviewed** (Ko'rib chiqilgan) - Application has been reviewed by admin
3. **approved** (Ma'qullangan) - Application approved for franchise
4. **rejected** (Rad etilgan) - Application rejected

---

## Error Handling

### HTTP Status Codes

- `200 OK` - Request successful
- `201 Created` - Application created successfully
- `400 Bad Request` - Validation errors
- `401 Unauthorized` - Authentication required
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Common Error Response Format

```json
{
    "field_name": ["Error message for this field"],
    "non_field_errors": ["General error message"]
}
```

---

## Usage Examples

### JavaScript/Fetch API

#### Submit Application (Public)
```javascript
const submitApplication = async (applicationData) => {
    const response = await fetch('http://api.organicgreen.uz/api/franchise/applications/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(applicationData)
    });
    
    if (response.ok) {
        const result = await response.json();
        console.log('Application submitted:', result);
        return result;
    } else {
        const errors = await response.json();
        console.error('Submission failed:', errors);
        throw errors;
    }
};

// Usage
const applicationData = {
    full_name: "Alisher Karimov",
    phone: "+998901234567",
    email: "alisher@example.com",
    city: "Toshkent",
    investment_amount: "50000.00",
    experience: "5 yillik restoran biznesida tajriba",
    message: "Organic Green franshizasini ochishga juda qiziqaman"
};

submitApplication(applicationData);
```

#### List Applications (Admin)
```javascript
const getApplications = async (filters = {}) => {
    const token = localStorage.getItem('access_token');
    const params = new URLSearchParams(filters);
    
    const response = await fetch(
        `http://api.organicgreen.uz/api/franchise/applications/list/?${params}`,
        {
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            }
        }
    );
    
    if (response.ok) {
        return await response.json();
    } else {
        throw new Error('Failed to fetch applications');
    }
};

// Usage
getApplications({ status: 'pending', ordering: '-created_at' });
```

#### Update Application Status (Admin)
```javascript
const updateApplicationStatus = async (applicationId, status) => {
    const token = localStorage.getItem('access_token');
    
    const response = await fetch(
        `http://api.organicgreen.uz/api/franchise/applications/${applicationId}/update/`,
        {
            method: 'PATCH',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ status })
        }
    );
    
    if (response.ok) {
        return await response.json();
    } else {
        throw new Error('Failed to update application');
    }
};

// Usage
updateApplicationStatus(1, 'approved');
```

---

## Notes

1. **Validation**: All fields are validated on the server side
2. **Permissions**: Public users can only create applications; admin access required for all other operations
3. **Pagination**: List endpoint supports pagination with customizable page size
4. **Filtering**: Multiple filtering options available for admin list view
5. **Status Tracking**: Applications maintain creation and update timestamps
6. **Investment Limits**: Investment amount must be between $0.01 and $10,000,000
7. **Phone Validation**: Phone numbers must contain at least 10 digits
8. **Localization**: Status choices are available in Uzbek language
