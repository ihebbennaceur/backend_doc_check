#!/bin/bash
# Initialize the backend service on Railway
# This runs migrations and starts Gunicorn

set -e

echo "=================================="
echo "Django Backend Initialization"
echo "=================================="
echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"
echo "Django version: $(python -c 'import django; print(django.VERSION)')"

# Navigate to the Django project
cd myproject
echo "Changed to: $(pwd)"

# Check database connection
echo ""
echo "Checking database connection..."
python manage.py shell << EOF
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✓ Database connection successful")
except Exception as e:
    print(f"✗ Database connection failed: {e}")
EOF

echo ""
echo "Running database migrations..."
python manage.py migrate --noinput -v 2

echo ""
echo "Creating admin user (if needed)..."
python manage.py shell << EOF
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("✓ Admin user created")
else:
    print("✓ Admin user already exists")
EOF

echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput 2>&1 || true

echo ""
echo "=================================="
echo "Starting Gunicorn"
echo "=================================="

# Start Gunicorn
gunicorn myproject.wsgi:application \
    --bind 0.0.0.0:8080 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
