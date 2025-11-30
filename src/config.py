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

    # All configuration should come from environment variables (.env file)
    # No hardcoded defaults - deployment environment must provide these values
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable must be set in .env file")

    # WORKAROUND: Windows paths with spaces break SQLite URL parsing
    # Build the database URI programmatically using absolute path
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        raise ValueError("DATABASE_URL environment variable must be set in .env file")

    # If it's a SQLite database, build the path manually to handle spaces
    if db_url.startswith('sqlite:///'):
        # Get absolute path to instance/database.db relative to this file
        basedir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(basedir, '..', 'instance', 'database.db')
        db_path = os.path.abspath(db_path)
        # Use file:/// URI scheme which properly handles spaces
        SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    else:
        SQLALCHEMY_DATABASE_URI = db_url

    CONTENT_DIR = os.environ.get('CONTENT_DIR')
    if not CONTENT_DIR:
        raise ValueError("CONTENT_DIR environment variable must be set in .env file")

    # Calibre-Web integration
    CALIBRE_WEB_URL = os.environ.get('CALIBRE_WEB_URL', 'http://localhost:8083')
    CALIBRE_LIBRARY_PATH = os.environ.get('CALIBRE_LIBRARY_PATH')


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False

    # All configuration should come from environment variables (.env file)
    # No hardcoded defaults - production must provide these values
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError(
            "SECRET_KEY environment variable must be set in production"
        )

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    if not SQLALCHEMY_DATABASE_URI:
        raise ValueError(
            "DATABASE_URL environment variable must be set in production"
        )

    CONTENT_DIR = os.environ.get('CONTENT_DIR')
    if not CONTENT_DIR:
        raise ValueError(
            "CONTENT_DIR environment variable must be set in production"
        )

    # Calibre-Web integration
    CALIBRE_WEB_URL = os.environ.get('CALIBRE_WEB_URL')
    if not CALIBRE_WEB_URL:
        raise ValueError(
            "CALIBRE_WEB_URL must be set in production .env file"
        )
    CALIBRE_LIBRARY_PATH = os.environ.get('CALIBRE_LIBRARY_PATH')

    # Session Security - Production Hardening (OWASP A02:2021, A07:2021)
    # Enforce HTTPS-only transmission (prevents MitM session hijacking)
    SESSION_COOKIE_SECURE = True
    # Prevent JavaScript access (already set in base, reinforced here)
    SESSION_COOKIE_HTTPONLY = True
    # CSRF protection (already set in base, reinforced here)
    SESSION_COOKIE_SAMESITE = 'Lax'
    # 1-hour timeout (least privilege principle)
    PERMANENT_SESSION_LIFETIME = 3600


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
