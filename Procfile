release: cd myproject && python manage.py migrate --noinput && python manage.py collectstatic --noinput || true
web: cd myproject && gunicorn myproject.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --worker-class sync --timeout 300
