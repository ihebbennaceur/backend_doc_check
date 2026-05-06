import os
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from django.db import connection
from django.utils.timezone import now

cursor = connection.cursor()

migrations = [
    ('auth', '0001_initial'),
    ('auth', '0002_alter_permission_name_max_length'),
    ('auth', '0003_alter_user_email_max_length'),
    ('auth', '0004_alter_user_username_opts'),
    ('auth', '0005_alter_user_last_login_null'),
    ('auth', '0006_require_contenttypes_0002'),
    ('auth', '0007_alter_validators_add_message_length'),
    ('auth', '0008_alter_user_username_max_length'),
    ('auth', '0009_alter_user_last_name_max_length'),
    ('auth', '0010_alter_group_name_max_length'),
    ('auth', '0011_update_proxy_permissions'),
    ('auth', '0012_alter_user_first_name_max_length'),
    ('doccheck', '0001_initial'),
    ('doccheck', '0002_docchecksession_is_portugal_resident_and_more'),
    ('docready', '0001_initial'),
    ('docready', '0002_fizboorder_whatsapp_opt_in'),
    ('docready', '0003_fizboorder_phone'),
    ('docready', '0004_alter_fizboorder_service_tier'),
    ('documents', '0001_initial'),
    ('operator', '0001_initial'),
    ('payments', '0001_initial'),
    ('payments', '0002_alter_payment_service_tier'),
    ('smartcma', '0001_initial'),
]

for app, name in migrations:
    try:
        cursor.execute(
            "INSERT INTO django_migrations (app, name, applied) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING;",
            [app, name, now()]
        )
        print(f"✓ {app}.{name}")
    except Exception as e:
        print(f"✗ {app}.{name}: {e}")

connection.commit()
print("\n✓ All migration records restored!")
