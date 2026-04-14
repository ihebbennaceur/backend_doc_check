release: bash -c 'cd myproject && python manage.py migrate --noinput -v 2 && python manage.py collectstatic --noinput --clear 2>&1 || true'
web: bash -c 'cd myproject && gunicorn myproject.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --worker-class sync --timeout 300'
