# Swagger/OpenAPI Documentation

## Overview

The Seller Platform API includes comprehensive Swagger documentation for all endpoints, powered by `drf-spectacular`.

## Accessing the Documentation

### Swagger UI (Interactive)
- **Local Development**: http://localhost:8000/api/docs/
- **Production**: https://your-domain.com/api/docs/

Interactive interface where you can:
- Browse all API endpoints
- See request/response schemas
- Try out API calls directly
- View authentication methods
- Check error responses

### ReDoc (Alternative Documentation)
- **Local Development**: http://localhost:8000/api/redoc/
- **Production**: https://your-domain.com/api/redoc/

Alternative, read-only documentation format (better for mobile)

### OpenAPI Schema (JSON)
- **Local Development**: http://localhost:8000/api/schema/
- **Production**: https://your-domain.com/api/schema/

Raw OpenAPI 3.0 schema (useful for code generation)

## Authentication in Swagger

To test authenticated endpoints:

1. Go to **Swagger UI** (`/api/docs/`)
2. Click the **"Authorize"** button (top right)
3. Select **"Bearer"** authentication
4. Obtain a JWT token:
   - POST to `/api/token/` with credentials
   - Copy the access token
5. Paste token in the Bearer field: `Bearer <your_token>`
6. Click Authorize

## API Endpoints

### Authentication
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token

### Accounts & Users
- `GET/POST /api/user/` - User profile
- `POST /api/register/` - User registration
- `POST /api/login/` - User login

### Documents
- `GET/POST /api/documents/` - Document management
- `GET /api/documents/{id}/` - Document detail

### DocCheck (Document Verification)
- `GET/POST /api/doccheck/` - Document checking
- `GET /api/doccheck/cases/` - Verification cases

### DocReady (Document Preparation)
- `GET/POST /api/orders/` - Order management

### Payments
- `GET/POST /api/payments/` - Payment operations
- `GET /api/payments/{id}/` - Payment detail

### SmartCMA (Comparative Market Analysis)
- `GET/POST /api/cma/` - CMA reports

### Operator Management
- `GET/POST /api/operator/` - Operator operations

## Features

- ✅ Full OpenAPI 3.0 support
- ✅ JWT Bearer authentication
- ✅ Interactive request/response testing
- ✅ Schema auto-documentation
- ✅ Request/response examples
- ✅ Error code documentation
- ✅ Parameter descriptions
- ✅ Security scheme definitions

## Customizing Documentation

Edit `myproject/settings.py` → `SPECTACULAR_SETTINGS` to:
- Change title, description, version
- Add server URLs
- Configure authentication methods
- Customize schema preprocessing

## Exporting Documentation

To export OpenAPI schema for external tools:

```bash
python manage.py spectacular --file schema.json
```

This creates `schema.json` that can be imported into:
- Postman
- Insomnia
- Code generators
- API documentation platforms
