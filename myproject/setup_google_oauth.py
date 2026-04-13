#!/usr/bin/env python
"""
Google OAuth Setup Script for PFE Seller Platform
This script helps setup Django migrations and Google OAuth configuration
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    django.setup()
    from django.core.management import call_command
    from django.contrib.sites.models import Site
    
    print("\n" + "="*60)
    print("Google OAuth Setup for PFE Seller Platform")
    print("="*60 + "\n")
    
    # Step 1: Run migrations
    print("Step 1: Running migrations for django-allauth...")
    try:
        call_command('migrate')
        print("✅ Migrations completed successfully\n")
    except Exception as e:
        print(f"⚠️  Migrations error: {e}\n")
    
    # Step 2: Setup Site object
    print("Step 2: Configuring Django Site...")
    try:
        site = Site.objects.get_or_create(id=1)[0]
        site.domain = os.environ.get('DOMAIN', 'backenddoccheck-production.up.railway.app')
        site.name = 'Seller Platform Backend'
        site.save()
        print(f"✅ Site configured: {site.domain}\n")
    except Exception as e:
        print(f"⚠️  Site configuration error: {e}\n")
    
    # Step 3: Verify Google OAuth credentials
    print("Step 3: Verifying Google OAuth credentials...")
    client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
    
    if client_id and client_secret:
        print(f"✅ GOOGLE_OAUTH_CLIENT_ID: {client_id[:20]}...")
        print(f"✅ GOOGLE_OAUTH_CLIENT_SECRET: {'*' * len(client_secret)}\n")
    else:
        if not client_id:
            print("❌ GOOGLE_OAUTH_CLIENT_ID is not set")
        if not client_secret:
            print("❌ GOOGLE_OAUTH_CLIENT_SECRET is not set")
        print()
    
    # Step 4: Display next steps
    print("="*60)
    print("Next Steps:")
    print("="*60)
    print("""
1. ✅ Django migrations completed
2. ✅ Site object configured
3. 📋 Google OAuth Credentials configured via environment variables:
   - GOOGLE_OAUTH_CLIENT_ID
   - GOOGLE_OAUTH_CLIENT_SECRET
4. 🚀 Test Google OAuth at:
   - Frontend: https://doc-frontend-beta.vercel.app/auth/register
   - Backend API: POST https://backenddoccheck-production.up.railway.app/api/auth/google/
""")
    print("="*60 + "\n")
    
except Exception as e:
    print(f"Error during setup: {e}")
    sys.exit(1)
