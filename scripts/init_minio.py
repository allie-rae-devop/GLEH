"""
MinIO Bucket Initialization Script

This script initializes the MinIO storage by creating the required bucket
and folder structure for GLEH.

Run this script after starting MinIO for the first time, or use it
to reset the MinIO storage structure.

Usage:
    python scripts/init_minio.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path to import src modules
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(root_dir / '.env')

from src.minio_client import MinIOClient
from minio.error import S3Error


def init_minio_storage():
    """Initialize MinIO storage with required buckets and folder structure."""

    print("=" * 60)
    print("GLEH MinIO Storage Initialization")
    print("=" * 60)
    print()

    # Get MinIO configuration from environment
    endpoint = os.environ.get('MINIO_ENDPOINT', 'localhost:9000')
    access_key = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')
    secret_key = os.environ.get('MINIO_SECRET_KEY', 'minioadmin')
    bucket = os.environ.get('MINIO_BUCKET', 'gleh-storage')
    secure = os.environ.get('MINIO_SECURE', 'false').lower() == 'true'

    print(f"MinIO Configuration:")
    print(f"  Endpoint: {endpoint}")
    print(f"  Bucket: {bucket}")
    print(f"  Secure (HTTPS): {secure}")
    print()

    try:
        # Initialize MinIO client
        print("Connecting to MinIO...")
        minio_client = MinIOClient(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            bucket=bucket,
            secure=secure
        )
        print("✓ Connected to MinIO successfully")
        print()

        # Check if bucket exists
        if minio_client.client.bucket_exists(bucket):
            print(f"✓ Bucket '{bucket}' already exists")
        else:
            print(f"Creating bucket '{bucket}'...")
            minio_client.client.make_bucket(bucket)
            print(f"✓ Bucket '{bucket}' created successfully")
        print()

        # Create folder structure by uploading placeholder files
        # MinIO doesn't have folders per se, but we can create the structure
        # by uploading empty marker files
        print("Initializing folder structure...")

        folders = [
            'courses/',
            'uploads/',
            'uploads/avatars/'
        ]

        for folder in folders:
            marker_file = f"{folder}.keep"
            try:
                # Check if marker already exists
                if minio_client.file_exists(marker_file):
                    print(f"  ✓ {folder} (already exists)")
                else:
                    # Upload a small marker file to create the folder
                    import io
                    data = io.BytesIO(b'# MinIO folder marker')
                    minio_client.upload_file(
                        file_data=data,
                        object_name=marker_file,
                        content_type='text/plain'
                    )
                    print(f"  ✓ {folder} (created)")
            except S3Error as e:
                print(f"  ✗ {folder} (error: {e})")

        print()
        print("=" * 60)
        print("MinIO Initialization Complete!")
        print("=" * 60)
        print()
        print(f"Bucket structure:")
        print(f"  {bucket}/")
        print(f"    ├── courses/          # MIT OCW course materials")
        print(f"    └── uploads/          # User-uploaded files")
        print(f"        └── avatars/      # User avatar images")
        print()
        print(f"MinIO Web Console: http://{endpoint.split(':')[0]}:9001")
        print(f"  Username: {access_key}")
        print(f"  Password: {'*' * len(secret_key)}")
        print()

        return True

    except Exception as e:
        print()
        print("=" * 60)
        print("ERROR: MinIO Initialization Failed")
        print("=" * 60)
        print(f"Error: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Ensure MinIO is running:")
        print("     - Docker: docker-compose up -d minio")
        print("     - Standalone: minio server /data")
        print()
        print(f"  2. Check MinIO endpoint is accessible: {endpoint}")
        print()
        print("  3. Verify credentials in .env file:")
        print("     MINIO_ACCESS_KEY and MINIO_SECRET_KEY")
        print()
        return False


if __name__ == '__main__':
    success = init_minio_storage()
    sys.exit(0 if success else 1)
