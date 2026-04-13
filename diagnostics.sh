#!/bin/bash
# Diagnostic script for Railway backend
# This will show us what's wrong with the API

cd myproject

echo "=================================="
echo "Django Diagnostics"
echo "=================================="

echo ""
echo "1. Testing Django setup..."
python manage.py check

echo ""
echo "2. Testing database connection..."
python manage.py shell << EOF
from django.db import connection
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✓ Database connection OK")
except Exception as e:
    print(f"✗ Database error: {e}")
EOF

echo ""
echo "3. Testing Swagger/drf-spectacular..."
python manage.py shell << EOF
try:
    from drf_spectacular.generators import SchemaGenerator
    print("✓ drf-spectacular loaded")
    try:
        generator = SchemaGenerator()
        schema = generator.get_schema()
        print("✓ Schema generated successfully")
    except Exception as e:
        print(f"✗ Schema generation error: {e}")
        import traceback
        traceback.print_exc()
except Exception as e:
    print(f"✗ drf-spectacular error: {e}")
EOF

echo ""
echo "4. Checking REST_FRAMEWORK settings..."
python manage.py shell << EOF
from django.conf import settings
print(f"REST_FRAMEWORK['DEFAULT_SCHEMA_CLASS']: {settings.REST_FRAMEWORK.get('DEFAULT_SCHEMA_CLASS')}")
print(f"INSTALLED_APPS: {[app for app in settings.INSTALLED_APPS if 'drf' in app or 'spectacular' in app or 'rest' in app]}")
EOF

echo ""
echo "=================================="
echo "Diagnostics Complete"
echo "=================================="
