"""
Storage Management System for GLEH

Provides a unified interface for local and Samba storage paths.
Supports easy switching between local filesystem and remote Samba shares.

Usage:
    from storage import StorageManager

    storage = StorageManager()
    courses_dir = storage.get_courses_dir()
    ebooks_dir = storage.get_ebooks_dir()
    covers_dir = storage.get_covers_dir()
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class StorageManager:
    """
    Unified storage interface supporting local and Samba paths.

    Environment variables used:
        STORAGE_TYPE: 'local' or 'samba' (default: 'local')

        # Local storage
        LOCAL_COURSES_DIR: Path to courses directory
        LOCAL_EBOOKS_DIR: Path to e-books directory
        LOCAL_UPLOADS_DIR: Path to uploads directory (avatars, covers, etc)

        # Samba storage (optional, for future)
        SAMBA_HOST: Samba server hostname/IP
        SAMBA_SHARE_COURSES: Share name for courses
        SAMBA_SHARE_EBOOKS: Share name for e-books
        SAMBA_SHARE_UPLOADS: Share name for uploads
        SAMBA_USERNAME: Samba username
        SAMBA_PASSWORD: Samba password
        SAMBA_DOMAIN: Samba domain (optional)
        SAMBA_MOUNT_BASE: Base directory for Samba mounts (default: /mnt/samba)
    """

    def __init__(self):
        """Initialize StorageManager with configuration from environment."""
        self.storage_type = os.environ.get('STORAGE_TYPE', 'local').lower()
        self._validate_storage_type()

        if self.storage_type == 'local':
            self._init_local_storage()
        elif self.storage_type == 'samba':
            self._init_samba_storage()

    def _validate_storage_type(self):
        """Validate that storage type is supported."""
        if self.storage_type not in ['local', 'samba']:
            raise ValueError(
                f"Invalid STORAGE_TYPE '{self.storage_type}'. "
                "Must be 'local' or 'samba'"
            )

    def _init_local_storage(self):
        """Initialize local storage paths."""
        # Try to get CONTENT_DIR for backward compatibility
        content_dir = os.environ.get('CONTENT_DIR')

        # Otherwise, use individual LOCAL_* variables
        if content_dir:
            self.courses_dir = os.path.join(content_dir, 'courses')
            self.ebooks_dir = os.path.join(content_dir, 'ebooks')
            self.uploads_dir = os.path.join(content_dir, 'uploads')
        else:
            self.courses_dir = os.environ.get(
                'LOCAL_COURSES_DIR',
                os.path.expanduser(r'D:\GLEH Data\courses')
            )
            self.ebooks_dir = os.environ.get(
                'LOCAL_EBOOKS_DIR',
                os.path.expanduser(r'D:\GLEH Data\ebooks')
            )
            self.uploads_dir = os.environ.get(
                'LOCAL_UPLOADS_DIR',
                os.path.expanduser(r'D:\GLEH Data\uploads')
            )

        self._ensure_directories_exist()
        logger.info(f"Storage initialized (local): {self.courses_dir}")

    def _init_samba_storage(self):
        """Initialize Samba storage paths."""
        # This is configured but not yet mounted
        self.samba_host = os.environ.get('SAMBA_HOST')
        self.samba_username = os.environ.get('SAMBA_USERNAME')
        self.samba_password = os.environ.get('SAMBA_PASSWORD')
        self.samba_domain = os.environ.get('SAMBA_DOMAIN', '')
        self.samba_mount_base = os.environ.get('SAMBA_MOUNT_BASE', '/mnt/samba')

        self.samba_share_courses = os.environ.get('SAMBA_SHARE_COURSES', 'courses')
        self.samba_share_ebooks = os.environ.get('SAMBA_SHARE_EBOOKS', 'ebooks')
        self.samba_share_uploads = os.environ.get('SAMBA_SHARE_UPLOADS', 'uploads')

        # Set mount paths
        self.courses_dir = os.path.join(self.samba_mount_base, self.samba_share_courses)
        self.ebooks_dir = os.path.join(self.samba_mount_base, self.samba_share_ebooks)
        self.uploads_dir = os.path.join(self.samba_mount_base, self.samba_share_uploads)

        logger.info(f"Storage configured (samba): {self.samba_host}")

    def _ensure_directories_exist(self):
        """Create storage directories if they don't exist."""
        for path in [self.courses_dir, self.ebooks_dir, self.uploads_dir]:
            try:
                Path(path).mkdir(parents=True, exist_ok=True)
                logger.debug(f"Ensured directory exists: {path}")
            except Exception as e:
                logger.warning(f"Could not create directory {path}: {e}")

    def get_courses_dir(self) -> str:
        """Get the courses directory path."""
        return self.courses_dir

    def get_ebooks_dir(self) -> str:
        """Get the e-books directory path."""
        return self.ebooks_dir

    def get_uploads_dir(self) -> str:
        """Get the uploads directory path."""
        return self.uploads_dir

    def get_covers_subdir(self) -> str:
        """Get the covers subdirectory within uploads."""
        return os.path.join(self.uploads_dir, 'ebook_covers')

    def get_avatars_subdir(self) -> str:
        """Get the avatars subdirectory within uploads."""
        return os.path.join(self.uploads_dir, 'avatars')

    def get_thumbnails_subdir(self) -> str:
        """Get the thumbnails subdirectory within uploads."""
        return os.path.join(self.uploads_dir, 'thumbnails')

    def ensure_storage_ready(self) -> bool:
        """
        Verify storage is accessible and ready.
        Returns True if accessible, False otherwise.
        """
        try:
            if self.storage_type == 'local':
                return self._check_local_storage()
            elif self.storage_type == 'samba':
                return self._check_samba_storage()
        except Exception as e:
            logger.error(f"Storage health check failed: {e}")
            return False

    def _check_local_storage(self) -> bool:
        """Check if local storage is accessible."""
        try:
            for path in [self.courses_dir, self.ebooks_dir, self.uploads_dir]:
                if not os.path.exists(path):
                    logger.warning(f"Storage path does not exist: {path}")
                    # Try to create it
                    Path(path).mkdir(parents=True, exist_ok=True)
                if not os.path.isdir(path):
                    logger.error(f"Storage path is not a directory: {path}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Local storage check failed: {e}")
            return False

    def _check_samba_storage(self) -> bool:
        """Check if Samba storage is mounted and accessible."""
        try:
            for path in [self.courses_dir, self.ebooks_dir, self.uploads_dir]:
                if not os.path.exists(path):
                    logger.error(f"Samba mount point does not exist: {path}")
                    return False
                if not os.path.isdir(path):
                    logger.error(f"Samba path is not a directory: {path}")
                    return False
            return True
        except Exception as e:
            logger.error(f"Samba storage check failed: {e}")
            return False

    def get_storage_info(self) -> dict:
        """Get storage configuration information."""
        return {
            'type': self.storage_type,
            'courses_dir': self.courses_dir,
            'ebooks_dir': self.ebooks_dir,
            'uploads_dir': self.uploads_dir,
            'covers_dir': self.get_covers_subdir(),
            'avatars_dir': self.get_avatars_subdir(),
            'thumbnails_dir': self.get_thumbnails_subdir(),
            'is_ready': self.ensure_storage_ready(),
        }


# Singleton instance
_storage_instance: Optional[StorageManager] = None


def get_storage() -> StorageManager:
    """Get the global StorageManager instance."""
    global _storage_instance
    if _storage_instance is None:
        _storage_instance = StorageManager()
    return _storage_instance


def init_storage() -> StorageManager:
    """Initialize or reinitialize the global storage manager."""
    global _storage_instance
    _storage_instance = StorageManager()
    return _storage_instance
