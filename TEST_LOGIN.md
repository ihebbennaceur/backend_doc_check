# Login Test Guide

## Available Test Accounts

Here are the users in your database:

| Username | Email | Role | Password | Status |
|----------|-------|------|----------|--------|
| iheb | ihebbennaceur6@gmail.com | (none) | ❓ Need to set | ❓ |
| iheb_seller | iheb_seller@email.com | seller | ❓ Need to set | ✅ Active |
| iheb_lawyer | iheb_laywer@email.com | lawyer | ❓ Need to set | ✅ Active |
| iheb_agent | iheb_agent@email.com | agent | ❓ Need to set | ✅ Active |
| iheb_buyer | iheb_buyer@email.com | buyer | ❓ Need to set | ✅ Active |
| iheb_testing | iheb_testing@email.com | seller | ❓ Need to set | ✅ Active |

## Common Login Issues

### Issue: "Invalid username or password"
**Cause:** Wrong password or user doesn't exist
**Solution:** 
1. Try one of the usernames above
2. Check the password you used during registration
3. If you forgot, use Django shell to reset:

```bash
cd backend_django/backend_seller_platform/myproject
python manage.py shell
```

Then in the shell:
```python
from accounts.models import User
user = User.objects.get(username='iheb_seller')
user.set_password('newpassword123')
user.save()
exit()
```

## Test with cURL

```bash
curl -X POST http://localhost:8000/api/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "iheb_seller",
    "password": "password123"
  }'
```

## Test with Frontend

1. Go to http://localhost:3000/auth/login
2. Enter credentials
3. If successful, you'll get:
   - `access` token (short-lived)
   - `refresh` token (long-lived)
   - User info

## Set Password for Test User

Run this Django shell command:

```python
from accounts.models import User
from django.contrib.auth.hashers import make_password

user = User.objects.get(username='iheb_seller')
user.set_password('test123456')  # Set your desired password
user.save()

# Verify it works
from django.contrib.auth import authenticate
test = authenticate(username='iheb_seller', password='test123456')
print("Login works:", test is not None)
```

## Next Steps

1. Set a password for one of the test users above
2. Try logging in with that username and password
3. You should receive JWT tokens
4. Use the access token for authenticated requests
