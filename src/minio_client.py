"""
MinIO Object Storage Client

Provides a Python interface to interact with MinIO S3-compatible object storage.
Used for storing and retrieving course materials, user uploads, and other files.

MinIO Documentation: https://min.io/docs/minio/linux/developers/python/API.html
"""

import os
import io
import logging
from typing import Optional, BinaryIO, List, Dict
from datetime import timedelta
from minio import Minio
from minio.error import S3Error
from flask import current_app
from werkzeug.datastructures import FileStorage

logger = logging.getLogger(__name__)


class MinIOClient:
    """Client for interacting with MinIO object storage."""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
        bucket: Optional[str] = None,
        secure: Optional[bool] = None
    ):
        """
        Initialize MinIO client.

        Args:
            endpoint: MinIO server endpoint (e.g., 'minio:9000' or 'localhost:9000')
            access_key: MinIO access key (username)
            secret_key: MinIO secret key (password)
            bucket: Default bucket name for operations
            secure: Use HTTPS (True) or HTTP (False)
        """
        self.endpoint = endpoint or self._get_config('MINIO_ENDPOINT', 'localhost:9000')
        self.access_key = access_key or self._get_config('MINIO_ACCESS_KEY', 'minioadmin')
        self.secret_key = secret_key or self._get_config('MINIO_SECRET_KEY', 'minioadmin')
        self.bucket = bucket or self._get_config('MINIO_BUCKET', 'gleh-storage')
        self.secure = secure if secure is not None else self._get_config('MINIO_SECURE', 'false').lower() == 'true'

        logger.info(f"Initializing MinIO client: endpoint={self.endpoint}, bucket={self.bucket}, secure={self.secure}")

        try:
            self.client = Minio(
                endpoint=self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=self.secure
            )
            logger.info("MinIO client initialized successfully")

            # Ensure default bucket exists
            self._ensure_bucket_exists()

        except Exception as e:
            logger.error(f"Failed to initialize MinIO client: {e}")
            raise

    def _get_config(self, key: str, default: str = None) -> str:
        """
        Get configuration value from environment or Flask config.

        Args:
            key: Configuration key
            default: Default value if not found

        Returns:
            Configuration value
        """
        # Try environment variable first
        value = os.environ.get(key)
        if value:
            return value

        # Try Flask config if in app context
        try:
            if current_app:
                value = current_app.config.get(key)
                if value:
                    return value
        except RuntimeError:
            # Not in Flask app context
            pass

        return default

    def _ensure_bucket_exists(self, bucket_name: Optional[str] = None) -> None:
        """
        Ensure a bucket exists, create if it doesn't.

        Args:
            bucket_name: Bucket name (uses default if not specified)
        """
        bucket = bucket_name or self.bucket
        try:
            if not self.client.bucket_exists(bucket):
                logger.info(f"Creating bucket: {bucket}")
                self.client.make_bucket(bucket)
                logger.info(f"Bucket created: {bucket}")
            else:
                logger.debug(f"Bucket already exists: {bucket}")
        except S3Error as e:
            logger.error(f"Error ensuring bucket exists: {e}")
            raise

    def upload_file(
        self,
        file_data: BinaryIO,
        object_name: str,
        content_type: Optional[str] = None,
        bucket_name: Optional[str] = None
    ) -> str:
        """
        Upload a file to MinIO.

        Args:
            file_data: File object or bytes
            object_name: Object name in bucket (path/filename.ext)
            content_type: MIME type of file
            bucket_name: Target bucket (uses default if not specified)

        Returns:
            Object name (path) in bucket

        Raises:
            S3Error: If upload fails
        """
        bucket = bucket_name or self.bucket

        try:
            # Get file size
            file_data.seek(0, 2)  # Seek to end
            file_size = file_data.tell()
            file_data.seek(0)  # Reset to beginning

            # Upload to MinIO
            self.client.put_object(
                bucket_name=bucket,
                object_name=object_name,
                data=file_data,
                length=file_size,
                content_type=content_type or 'application/octet-stream'
            )

            logger.info(f"Uploaded file to MinIO: {bucket}/{object_name} ({file_size} bytes)")
            return object_name

        except S3Error as e:
            logger.error(f"Failed to upload file to MinIO: {e}")
            raise

    def upload_werkzeug_file(
        self,
        file: FileStorage,
        object_name: str,
        bucket_name: Optional[str] = None
    ) -> str:
        """
        Upload a Werkzeug FileStorage object (from Flask request.files).

        Args:
            file: Werkzeug FileStorage object
            object_name: Object name in bucket
            bucket_name: Target bucket (uses default if not specified)

        Returns:
            Object name (path) in bucket
        """
        return self.upload_file(
            file_data=file.stream,
            object_name=object_name,
            content_type=file.content_type,
            bucket_name=bucket_name
        )

    def download_file(
        self,
        object_name: str,
        bucket_name: Optional[str] = None
    ) -> bytes:
        """
        Download a file from MinIO.

        Args:
            object_name: Object name in bucket
            bucket_name: Source bucket (uses default if not specified)

        Returns:
            File contents as bytes

        Raises:
            S3Error: If download fails
        """
        bucket = bucket_name or self.bucket

        try:
            response = self.client.get_object(bucket, object_name)
            data = response.read()
            response.close()
            response.release_conn()

            logger.debug(f"Downloaded file from MinIO: {bucket}/{object_name}")
            return data

        except S3Error as e:
            logger.error(f"Failed to download file from MinIO: {e}")
            raise

    def get_file_stream(
        self,
        object_name: str,
        bucket_name: Optional[str] = None
    ):
        """
        Get a streaming response for a file (useful for large files).

        Args:
            object_name: Object name in bucket
            bucket_name: Source bucket (uses default if not specified)

        Returns:
            HTTPResponse object (remember to close it)
        """
        bucket = bucket_name or self.bucket

        try:
            response = self.client.get_object(bucket, object_name)
            return response
        except S3Error as e:
            logger.error(f"Failed to get file stream from MinIO: {e}")
            raise

    def delete_file(
        self,
        object_name: str,
        bucket_name: Optional[str] = None
    ) -> None:
        """
        Delete a file from MinIO.

        Args:
            object_name: Object name in bucket
            bucket_name: Source bucket (uses default if not specified)
        """
        bucket = bucket_name or self.bucket

        try:
            self.client.remove_object(bucket, object_name)
            logger.info(f"Deleted file from MinIO: {bucket}/{object_name}")
        except S3Error as e:
            logger.error(f"Failed to delete file from MinIO: {e}")
            raise

    def list_files(
        self,
        prefix: Optional[str] = None,
        bucket_name: Optional[str] = None
    ) -> List[Dict[str, any]]:
        """
        List files in a bucket (optionally with prefix filter).

        Args:
            prefix: Filter objects by prefix (e.g., 'courses/')
            bucket_name: Source bucket (uses default if not specified)

        Returns:
            List of file metadata dicts with keys: name, size, last_modified
        """
        bucket = bucket_name or self.bucket

        try:
            objects = self.client.list_objects(
                bucket,
                prefix=prefix,
                recursive=True
            )

            files = []
            for obj in objects:
                files.append({
                    'name': obj.object_name,
                    'size': obj.size,
                    'last_modified': obj.last_modified,
                    'etag': obj.etag
                })

            logger.debug(f"Listed {len(files)} files from MinIO: {bucket}/{prefix or ''}")
            return files

        except S3Error as e:
            logger.error(f"Failed to list files from MinIO: {e}")
            raise

    def get_presigned_url(
        self,
        object_name: str,
        expires: timedelta = timedelta(hours=1),
        bucket_name: Optional[str] = None
    ) -> str:
        """
        Generate a presigned URL for temporary file access.

        Args:
            object_name: Object name in bucket
            expires: URL expiration time (default: 1 hour)
            bucket_name: Source bucket (uses default if not specified)

        Returns:
            Presigned URL string
        """
        bucket = bucket_name or self.bucket

        try:
            url = self.client.presigned_get_object(
                bucket,
                object_name,
                expires=expires
            )
            logger.debug(f"Generated presigned URL for: {bucket}/{object_name}")
            return url
        except S3Error as e:
            logger.error(f"Failed to generate presigned URL: {e}")
            raise

    def file_exists(
        self,
        object_name: str,
        bucket_name: Optional[str] = None
    ) -> bool:
        """
        Check if a file exists in MinIO.

        Args:
            object_name: Object name in bucket
            bucket_name: Source bucket (uses default if not specified)

        Returns:
            True if file exists, False otherwise
        """
        bucket = bucket_name or self.bucket

        try:
            self.client.stat_object(bucket, object_name)
            return True
        except S3Error as e:
            if e.code == 'NoSuchKey':
                return False
            logger.error(f"Error checking file existence: {e}")
            raise

    def get_file_info(
        self,
        object_name: str,
        bucket_name: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Get metadata about a file.

        Args:
            object_name: Object name in bucket
            bucket_name: Source bucket (uses default if not specified)

        Returns:
            Dict with file metadata (size, content_type, last_modified, etc.)
        """
        bucket = bucket_name or self.bucket

        try:
            stat = self.client.stat_object(bucket, object_name)
            return {
                'name': object_name,
                'size': stat.size,
                'content_type': stat.content_type,
                'last_modified': stat.last_modified,
                'etag': stat.etag,
                'metadata': stat.metadata
            }
        except S3Error as e:
            logger.error(f"Failed to get file info: {e}")
            raise


# Singleton instance for easy import
_minio_client_instance = None


def get_minio_client() -> MinIOClient:
    """
    Get or create singleton MinIO client instance.

    Returns:
        MinIOClient instance
    """
    global _minio_client_instance
    if _minio_client_instance is None:
        _minio_client_instance = MinIOClient()
    return _minio_client_instance
