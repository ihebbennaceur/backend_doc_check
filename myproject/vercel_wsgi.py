"""
WSGI config for Django on Vercel.
"""

import os
import django
from django.core.wsgi import get_wsgi_application
from whitenoise.middleware import WhiteNoiseMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# Run migrations on startup
if os.getenv('VERCEL_ENV') == 'production':
    django.setup()
    from django.core.management import call_command
    try:
        call_command('migrate', '--noinput', verbosity=0)
    except Exception as e:
        print(f"Migration warning: {e}")

application = get_wsgi_application()
application = WhiteNoiseMiddleware(application)
