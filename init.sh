#!/bin/bash
# Initialize the backend service on Railway
# This runs migrations and starts Gunicorn

set -e

echo "=================================="
echo "Django Backend Initialization"
echo "=================================="

# Navigate to the Django project
cd myproject

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

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
