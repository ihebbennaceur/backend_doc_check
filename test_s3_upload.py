#!/usr/bin/env python
"""
Script to test S3 upload functionality
"""
import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
sys.path.insert(0, str(Path(__file__).resolve().parent))

django.setup()

from django.core.files.base import ContentFile
from django.conf import settings
import boto3

def test_s3_upload():
    """Test uploading a file to S3"""
    print("=" * 60)
    print("Testing S3 Upload Configuration")
    print("=" * 60)
    
    # Check if S3 credentials are set
    print("\n1. Checking AWS credentials...")
    aws_key = os.getenv('AWS_ACCESS_KEY_ID')
    aws_secret = os.getenv('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.getenv('AWS_STORAGE_BUCKET_NAME', 'doc-check-iheb')
    region = os.getenv('AWS_S3_REGION_NAME', 'eu-west-1')
    
    if not aws_key or not aws_secret:
        print("   ❌ AWS credentials not found in environment variables!")
        return False
    
    print(f"   ✓ AWS_ACCESS_KEY_ID: {aws_key[:10]}...")
    print(f"   ✓ AWS_STORAGE_BUCKET_NAME: {bucket_name}")
    print(f"   ✓ AWS_S3_REGION_NAME: {region}")
    
    # Check Django storage configuration
    print("\n2. Checking Django storage configuration...")
    print(f"   DEFAULT_FILE_STORAGE: {settings.DEFAULT_FILE_STORAGE}")
    print(f"   MEDIA_URL: {settings.MEDIA_URL}")
    
    # Test S3 connection
    print("\n3. Testing S3 connection...")
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_key,
            aws_secret_access_key=aws_secret,
            region_name=region
        )
        
        # List buckets to verify connection
        response = s3_client.list_buckets()
        buckets = [b['Name'] for b in response['Buckets']]
        print(f"   ✓ Connected to S3. Buckets found: {buckets}")
        
        if bucket_name not in buckets:
            print(f"   ⚠ Warning: Bucket '{bucket_name}' not found in your account!")
            return False
        
    except Exception as e:
        print(f"   ❌ Error connecting to S3: {e}")
        return False
    
    # Test upload
    print("\n4. Testing file upload to S3...")
    try:
        from django.core.files.storage import default_storage
        
        # Create test content
        test_content = ContentFile(b"Test file for S3 upload")
        test_filename = f"test-{django.utils.timezone.now().timestamp()}.txt"
        
        # Upload
        uploaded_path = default_storage.save(test_filename, test_content)
        print(f"   ✓ File uploaded successfully!")
        print(f"   ✓ Uploaded path: {uploaded_path}")
        
        # Get URL
        file_url = default_storage.url(uploaded_path)
        print(f"   ✓ File URL: {file_url}")
        
        # Verify file exists
        if default_storage.exists(uploaded_path):
            print(f"   ✓ File verified in S3!")
        else:
            print(f"   ❌ File not found in S3!")
            return False
        
        print("\n" + "=" * 60)
        print("✅ S3 Configuration is working correctly!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"   ❌ Error uploading file: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_s3_upload()
    sys.exit(0 if success else 1)
