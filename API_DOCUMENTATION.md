# Seller Platform API Documentation

**Base URL:** `http://localhost:8000` (development) or `https://api.sellerplatform.com` (production)

**API Docs:** 
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI Schema: `/api/schema/`

---

## Table of Contents
1. [Authentication Endpoints](#authentication-endpoints)
2. [User Profile Endpoints](#user-profile-endpoints)
3. [Email Verification](#email-verification)
4. [Document Upload & Verification](#document-upload--verification)
5. [Admin User Management](#admin-user-management)
6. [Admin Document Management](#admin-document-management)
7. [Error Responses](#error-responses)

---

## Authentication Endpoints

### 1. Register User
**Endpoint:** `POST /api/accounts/register/`

**Description:** Create a new user account with a specific role.

**Request Body:**
```json
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "role": "seller"
}
```

**Role Options:**
- `seller` - Property seller
- `buyer` - Property buyer
- `agent` - Real estate agent
- `lawyer` - Legal professional
- `admin` - Platform administrator

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "role": "seller"
}
```

**Error (400 Bad Request):**
```json
{
  "username": ["A user with that username already exists."],
  "email": ["Enter a valid email address."],
  "password": ["This password is too common."],
  "role": ["\"invalid\" is not a valid choice."]
}
```

---

### 2. Login User
**Endpoint:** `POST /api/accounts/login/`

**Description:** Authenticate user and return JWT tokens.

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "username": "johndoe",
    "email": "john@example.com",
    "role": "seller"
  }
}
```

**Error (401 Unauthorized):**
```json
{
  "non_field_errors": ["Invalid username or password"]
}
```

---

### 3. Refresh Access Token
**Endpoint:** `POST /api/token/refresh/`

**Description:** Get a new access token using the refresh token.

**Request Body:**
```json
{
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Response (200 OK):**
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

---

## User Profile Endpoints

### 4. Get/Update User Profile
**Endpoint:** `PUT /api/accounts/profile/`

**Authentication:** Required (Bearer token)

**Description:** Update the current user's profile information.

**Request Body:**
```json
{
  "email": "newemail@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1-234-567-8900",
  "role": "seller"
}
```

**Response (200 OK):**
```json
{
  "email": "newemail@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "phone": "+1-234-567-8900",
  "role": "seller"
}
```

**Error (401 Unauthorized):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## Email Verification

### 5. Verify Email
**Endpoint:** `POST /api/accounts/verify-email/`

**Authentication:** Required (Bearer token)

**Description:** Mark a user's email as verified.

**Request Body:**
```json
{
  "email": "john@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Email verified successfully",
  "email": "john@example.com",
  "email_verified": true
}
```

**Error (400 Bad Request):**
```json
{
  "email": ["User with this email does not exist"]
}
```

---

## Document Upload & Verification

### 6. Upload Document
**Endpoint:** `POST /api/accounts/documents/upload/`

**Authentication:** Required (Bearer token)

**Description:** Upload a document for user verification.

**Content-Type:** `multipart/form-data`

**Request Body:**
```
document_type: "id"  // or "license", "proof_of_address", "other"
file: <binary_file>
```

**Document Types:**
- `id` - Government ID
- `license` - License
- `proof_of_address` - Proof of address
- `other` - Other documents

**Response (201 Created):**
```json
{
  "id": 1,
  "document_type": "id",
  "file": "http://localhost:8000/media/documents/2026/03/05/abc123.pdf",
  "status": "pending",
  "rejection_reason": null,
  "uploaded_at": "2026-03-05T10:30:00Z",
  "reviewed_at": null
}
```

**Error (400 Bad Request):**
```json
{
  "file": ["No file was submitted."],
  "document_type": ["\"invalid\" is not a valid choice."]
}
```

---

### 7. List User Documents
**Endpoint:** `GET /api/accounts/documents/`

**Authentication:** Required (Bearer token)

**Description:** Get all documents uploaded by the current user.

**Query Parameters:** None

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "document_type": "id",
    "file": "http://localhost:8000/media/documents/2026/03/05/abc123.pdf",
    "status": "pending",
    "rejection_reason": null,
    "uploaded_at": "2026-03-05T10:30:00Z",
    "reviewed_at": null
  },
  {
    "id": 2,
    "document_type": "proof_of_address",
    "file": "http://localhost:8000/media/documents/2026/03/05/xyz789.pdf",
    "status": "approved",
    "rejection_reason": null,
    "uploaded_at": "2026-03-05T11:45:00Z",
    "reviewed_at": "2026-03-05T12:00:00Z"
  }
]
```

---

## Admin User Management

### 8. List All Users (Admin Only)
**Endpoint:** `GET /api/accounts/admin/users/`

**Authentication:** Required (Bearer token with Admin role)

**Description:** Get a list of all users in the system.

**Query Parameters:**
- `search` - Search by username or email
- `role` - Filter by role (seller, buyer, agent, lawyer, admin)
- `is_active` - Filter by active status (true/false)

**Response (200 OK):**
```json
{
  "count": 15,
  "next": "http://localhost:8000/api/accounts/admin/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "johndoe",
      "email": "john@example.com",
      "role": "seller",
      "is_active": true,
      "email_verified": false,
      "created_at": "2026-03-05T10:00:00Z"
    },
    {
      "id": 2,
      "username": "jane_agent",
      "email": "jane@example.com",
      "role": "agent",
      "is_active": true,
      "email_verified": true,
      "created_at": "2026-03-04T15:30:00Z"
    }
  ]
}
```

**Error (403 Forbidden):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### 9. Get/Update User Details (Admin Only)
**Endpoint:** `GET/PUT /api/accounts/admin/users/<user_id>/`

**Authentication:** Required (Bearer token with Admin role)

**Description:** Retrieve or update a specific user's information, including role and verification status.

**Request Body (PUT):**
```json
{
  "role": "agent",
  "is_active": false,
  "email_verified": true
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "role": "agent",
  "is_active": false,
  "email_verified": true,
  "created_at": "2026-03-05T10:00:00Z"
}
```

**Error (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

---

## Admin Document Management

### 10. List All Documents (Admin Only)
**Endpoint:** `GET /api/accounts/admin/documents/`

**Authentication:** Required (Bearer token with Admin role)

**Description:** Get all documents pending review or with a specific status.

**Query Parameters:**
- `status` - Filter by status (pending, approved, rejected) - default: "pending"

**Response (200 OK):**
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "user_username": "johndoe",
      "document_type": "id",
      "status": "pending",
      "uploaded_at": "2026-03-05T10:30:00Z",
      "reviewed_at": null
    },
    {
      "id": 3,
      "user_username": "jane_agent",
      "document_type": "license",
      "status": "pending",
      "uploaded_at": "2026-03-05T11:15:00Z",
      "reviewed_at": null
    }
  ]
}
```

---

### 11. Approve/Reject Document (Admin Only)
**Endpoint:** `PUT /api/accounts/admin/documents/<document_id>/`

**Authentication:** Required (Bearer token with Admin role)

**Description:** Approve or reject a user's document for verification.

**Request Body (Approve):**
```json
{
  "status": "approved"
}
```

**Request Body (Reject):**
```json
{
  "status": "rejected",
  "rejection_reason": "Document is blurry and unreadable. Please upload a clear image."
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "user_username": "johndoe",
  "document_type": "id",
  "status": "approved",
  "uploaded_at": "2026-03-05T10:30:00Z",
  "reviewed_at": "2026-03-05T12:00:00Z"
}
```

**Error (400 Bad Request - Missing rejection reason):**
```json
{
  "non_field_errors": ["Rejection reason is required when rejecting a document"]
}
```

**Error (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

---

## Error Responses

### Common HTTP Status Codes

| Status Code | Meaning |
|-------------|---------|
| 200 | OK - Request succeeded |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid input |
| 401 | Unauthorized - Authentication required or invalid |
| 403 | Forbidden - Permission denied |
| 404 | Not Found - Resource not found |
| 500 | Server Error - Internal server error |

### Standard Error Format
```json
{
  "detail": "Error message",
  "field_name": ["Field-specific error message"]
}
```

---

## Authentication Header

For all protected endpoints, include the Authorization header:

```
Authorization: Bearer <access_token>
```

Example:
```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  http://localhost:8000/api/accounts/profile/
```

---

## Quick Reference Table

| Method | Endpoint | Auth | Role Required | Purpose |
|--------|----------|------|---------------|---------|
| POST | `/api/accounts/register/` | ❌ | - | Register new user |
| POST | `/api/accounts/login/` | ❌ | - | Login & get tokens |
| POST | `/api/token/refresh/` | ❌ | - | Refresh access token |
| PUT | `/api/accounts/profile/` | ✅ | Any | Update own profile |
| POST | `/api/accounts/verify-email/` | ✅ | Any | Verify email |
| POST | `/api/accounts/documents/upload/` | ✅ | Any | Upload document |
| GET | `/api/accounts/documents/` | ✅ | Any | List own documents |
| GET | `/api/accounts/admin/users/` | ✅ | Admin | List all users |
| GET/PUT | `/api/accounts/admin/users/<id>/` | ✅ | Admin | Manage user |
| GET | `/api/accounts/admin/documents/` | ✅ | Admin | List documents |
| PUT | `/api/accounts/admin/documents/<id>/` | ✅ | Admin | Review document |

---

## Testing with cURL

### Register
```bash
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123!",
    "role": "seller"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123!"
  }'
```

### Update Profile (with token)
```bash
curl -X PUT http://localhost:8000/api/accounts/profile/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newemail@example.com",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### Upload Document (with token)
```bash
curl -X POST http://localhost:8000/api/accounts/documents/upload/ \
  -H "Authorization: Bearer <access_token>" \
  -F "document_type=id" \
  -F "file=@/path/to/document.pdf"
```

---

**Last Updated:** March 5, 2026
**API Version:** 1.0.0
