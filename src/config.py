import os

class Config:
    """Base configuration with default values."""
    # Security
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(24).hex()

    # Session settings
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

    # Database
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Database connection pooling and health (production hardening)
    # pool_pre_ping: Verify connections before use (prevents stale connection failures)
    # pool_recycle: Recycle connections after 1 hour (prevents database-side timeouts)
    # pool_size: Number of persistent connections to maintain in the pool
    # max_overflow: Maximum overflow connections when pool is exhausted
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,      # CRITICAL: Prevents stale connection failures in health checks
        'pool_recycle': 3600,       # Recycle connections after 1 hour (matches typical DB connection timeout)
        'pool_size': 10,            # Maintain 10 persistent connections
        'max_overflow': 20,         # Allow up to 20 additional connections during spikes
    }

    # Application
    APP_NAME = 'Gammons Landing Educational Hub'

    # Auth settings
    MIN_USERNAME_LENGTH = 3
    MAX_USERNAME_LENGTH = 64
    MIN_PASSWORD_LENGTH = 8

    # Rate limiting (requests per minute)
    AUTH_RATE_LIMIT = 5  # 5 login/register attempts per minute per IP

    # File upload settings
    MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB max file size

    # Content directory settings
    # CONTENT_DIR: Base directory containing 'courses' and 'ebooks' folders
    # Can be set via CONTENT_DIR environment variable for flexibility
    CONTENT_DIR = os.environ.get('CONTENT_DIR')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False
    # Use a fixed key for development so sessions persist across restarts
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-do-not-use-in-production'
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'database.db')

    # Development content directory (go up 1 level: src -> root)
    CONTENT_DIR = os.environ.get('CONTENT_DIR') or \
        os.path.abspath(os.path.join(basedir, '..'))


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False

    # In production, SECRET_KEY should be set via environment variable
    # If not set, will inherit from Config class (which generates a random key)
    # For production deployments, always set SECRET_KEY in environment!

    # Session Security - Production Hardening (OWASP A02:2021, A07:2021)
    SESSION_COOKIE_SECURE = True        # Enforce HTTPS-only transmission (prevents MitM session hijacking)
    SESSION_COOKIE_HTTPONLY = True      # Prevent JavaScript access (already set in base, reinforced here)
    SESSION_COOKIE_SAMESITE = 'Lax'     # CSRF protection (already set in base, reinforced here)
    PERMANENT_SESSION_LIFETIME = 3600   # 1-hour timeout (least privilege principle)

    # Production database
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        os.environ.get('PROD_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, '..', 'database.db')  # Fallback to dev DB

    # Production content directory (must be set via CONTENT_DIR environment variable)
    CONTENT_DIR = os.environ.get('CONTENT_DIR') or '/data/gleh'  # Docker/Proxmox path


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    # CSRF is now enabled for all configs - tests must include valid tokens


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
