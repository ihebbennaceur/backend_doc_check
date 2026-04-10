# Backend API Service

Django REST API backend for the Seller Platform.

## Quick Start

### Local Development

```bash
cd myproject
python manage.py migrate
python manage.py runserver
```

### Environment Variables

Create a `.env` file in the project root:

```
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@host:5432/dbname
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
AWS_STORAGE_BUCKET_NAME=your-bucket
AWS_S3_REGION_NAME=eu-west-1
```

### Docker

```bash
docker build -t backend .
docker run -p 8080:8080 -e DATABASE_URL=postgresql://... backend
```

### Railway Deployment

1. Push to GitHub
2. Connect repo to Railway
3. Add environment variables
4. Deploy

## API Documentation

- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`
- **OpenAPI Schema**: `/api/schema/`
- **Django Admin**: `/admin/`

## Services

- **Accounts**: User management and authentication
- **Documents**: Document management and processing
- **DocCheck**: Document verification
- **DocReady**: Document preparation
- **Operator**: Operator management
- **Payments**: Payment processing
- **SmartCMA**: CMA integration

## Tech Stack

- Django 6.0.3
- Django REST Framework
- drf-spectacular (Swagger/OpenAPI)
- PostgreSQL (Supabase)
- AWS S3
- Gunicorn

## Deploy Status

- ✅ Local development
- ✅ Docker containerization
- ⏳ Railway deployment
