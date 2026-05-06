release: python myproject/fix_migrations.py && python myproject/manage.py migrate --noinput
web: gunicorn -w 4 -b 0.0.0.0:$PORT myproject.wsgi:application
