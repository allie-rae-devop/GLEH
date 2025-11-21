"""
Pytest configuration and shared fixtures for test suite.
Provides reusable fixtures for Flask app, database, CSRF tokens, and authentication.
"""
import pytest
import os
from src.app import app as flask_app
from src.app import db, auth_attempts
from src.models import User, Course, Ebook
from flask_wtf.csrf import generate_csrf


@pytest.fixture
def app():
    """
    Create and configure a new Flask app instance for each test.
    Uses in-memory SQLite database and testing configuration.
    """
    # Set testing configuration
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": True,  # CRITICAL: Keep CSRF enabled for security tests
        "SECRET_KEY": "test-secret-key-for-csrf-generation",
        "AUTH_RATE_LIMIT": 5,  # 5 attempts per minute
        "MAX_UPLOAD_SIZE": 5 * 1024 * 1024,  # 5MB
        "MIN_USERNAME_LENGTH": 3,
        "MAX_USERNAME_LENGTH": 64,
        "MIN_PASSWORD_LENGTH": 8,
    })

    # Create application context
    with flask_app.app_context():
        # Create all database tables
        db.create_all()

        # Create test data
        _create_test_data()

        yield flask_app

        # Cleanup: Drop all tables and clear rate limit tracking
        db.session.remove()
        db.drop_all()

        # Clear in-memory rate limiting data
        auth_attempts.clear()


@pytest.fixture
def client(app):
    """
    Provides a test client for making HTTP requests to the Flask app.
    Maintains session context for authentication flows.
    Uses use_cookies=True to preserve session/CSRF state across requests.
    """
    return app.test_client(use_cookies=True)


@pytest.fixture
def runner(app):
    """
    Provides a test CLI runner for testing Flask CLI commands.
    """
    return app.test_cli_runner()


@pytest.fixture
def csrf_token(client):
    """
    Fetches a valid CSRF token from the /csrf-token endpoint.
    Use this token in POST/PUT/DELETE requests to pass CSRF validation.

    Usage:
        response = client.post('/api/login',
                              json={'username': 'test', 'password': 'test123'},
                              headers={'X-CSRFToken': csrf_token})
    """
    response = client.get('/csrf-token')
    assert response.status_code == 200
    data = response.get_json()
    assert 'csrf_token' in data
    return data['csrf_token']


@pytest.fixture
def authenticated_user(app, client, csrf_token):
    """
    Creates a test user, logs them in, and returns the user object with session.
    Maintains Flask-Login session context.

    Returns:
        dict: {'user': User object, 'client': authenticated client}
    """
    with app.app_context():
        # Create test user
        user = User(username='authenticated_test_user')
        user.set_password('SecurePassword123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    # Login the user using the client
    login_response = client.post('/api/login',
                                 json={'username': 'authenticated_test_user',
                                       'password': 'SecurePassword123'},
                                 headers={'X-CSRFToken': csrf_token})

    assert login_response.status_code == 200, "Authentication failed in fixture"

    # Fetch user again in the app context
    with app.app_context():
        user = User.query.get(user_id)
        return {'user': user, 'client': client}


@pytest.fixture
def admin_user(app, client, csrf_token):
    """
    Creates an admin user, logs them in, and returns the user object with session.

    Returns:
        dict: {'user': User object, 'client': authenticated client}
    """
    with app.app_context():
        # Create admin user
        user = User(username='admin_test_user', is_admin=True)
        user.set_password('AdminPassword123')
        db.session.add(user)
        db.session.commit()
        user_id = user.id

    # Login the admin user
    login_response = client.post('/api/login',
                                 json={'username': 'admin_test_user',
                                       'password': 'AdminPassword123'},
                                 headers={'X-CSRFToken': csrf_token})

    assert login_response.status_code == 200, "Admin authentication failed in fixture"

    with app.app_context():
        user = User.query.get(user_id)
        return {'user': user, 'client': client}


@pytest.fixture
def sample_course(app):
    """
    Creates a sample course in the database for testing.

    Returns:
        Course: The created course object
    """
    with app.app_context():
        course = Course(
            uid='test-course-001',
            title='Test Course',
            description='A test course for testing purposes',
            categories='programming,testing',
            thumbnail='images/default_course.jpg'
        )
        db.session.add(course)
        db.session.commit()
        return course


@pytest.fixture
def sample_ebook(app):
    """
    Creates a sample ebook in the database for testing.

    Returns:
        Ebook: The created ebook object
    """
    with app.app_context():
        ebook = Ebook(
            uid='test-ebook-001',
            title='Test Ebook',
            path='/static/ebooks/test.epub',
            cover_path='images/default_ebook.jpg',
            categories='programming,testing'
        )
        db.session.add(ebook)
        db.session.commit()
        return ebook


@pytest.fixture
def mock_image_file():
    """
    Creates a mock image file for upload testing.
    Returns file data in the format Flask expects.
    """
    from io import BytesIO
    from PIL import Image

    # Create a simple test image (100x100 red square)
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return img_bytes


@pytest.fixture
def oversized_image_file():
    """
    Creates a mock oversized image for dimension validation testing.
    Creates a 5000x5000 pixel image (exceeds typical limits).
    """
    from io import BytesIO
    from PIL import Image

    # Create an oversized image (5000x5000 pixels, exceeds MAX_IMAGE_WIDTH/HEIGHT)
    img = Image.new('RGB', (5000, 5000), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    return img_bytes


@pytest.fixture
def image_bomb_file():
    """
    Creates a mock image bomb (extremely large dimensions, small file size).
    Simulates a decompression bomb attack.
    """
    from io import BytesIO
    from PIL import Image

    # Create a 10000x10000 white image (potential decompression bomb)
    # When compressed as PNG, this is small, but when loaded consumes massive memory
    img = Image.new('RGB', (10000, 10000), color='white')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG', compress_level=9)
    img_bytes.seek(0)

    return img_bytes


@pytest.fixture
def corrupted_image_file():
    """
    Creates a corrupted/invalid image file for validation testing.
    """
    from io import BytesIO

    # Create a file with invalid image data
    corrupted_data = BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00INVALID_DATA')
    corrupted_data.seek(0)

    return corrupted_data


def _create_test_data():
    """
    Internal helper to create test data in the database.
    Creates sample users, courses, and ebooks for testing.
    """
    # Create a default test user
    if not User.query.filter_by(username='testuser').first():
        user = User(username='testuser')
        user.set_password('TestPassword123')
        db.session.add(user)

    # Create sample courses
    if not Course.query.filter_by(uid='sample-course').first():
        course = Course(
            uid='sample-course',
            title='Sample Course',
            description='A sample course for testing',
            categories='testing',
            thumbnail='images/default_course.jpg'
        )
        db.session.add(course)

    # Create sample ebook
    if not Ebook.query.filter_by(uid='sample-ebook').first():
        ebook = Ebook(
            uid='sample-ebook',
            title='Sample Ebook',
            path='/static/ebooks/sample.epub',
            cover_path='images/default_ebook.jpg',
            categories='testing'
        )
        db.session.add(ebook)

    db.session.commit()


# Utility functions for tests

def get_csrf_headers(csrf_token):
    """
    Helper function to create headers dict with CSRF token.

    Args:
        csrf_token: CSRF token string

    Returns:
        dict: Headers dictionary with X-CSRFToken
    """
    return {'X-CSRFToken': csrf_token}


def make_csrf_request(client, method, path, csrf_token=None, **kwargs):
    """
    Helper function to make HTTP requests with CSRF token handling.
    Automatically includes CSRF token in headers if provided.

    Args:
        client: Flask test client
        method: HTTP method ('post', 'put', 'delete', etc.)
        path: URL path
        csrf_token: CSRF token string (optional)
        **kwargs: Additional arguments to pass to client method

    Returns:
        Response object
    """
    headers = kwargs.pop('headers', {})
    if csrf_token:
        headers['X-CSRFToken'] = csrf_token

    method_func = getattr(client, method)
    return method_func(path, headers=headers, **kwargs)


def create_test_user(username='testuser', password='TestPassword123', is_admin=False):
    """
    Helper function to create a test user in the database.
    Should be called within an app context.

    Args:
        username: Username for the test user
        password: Password for the test user
        is_admin: Whether the user should be an admin

    Returns:
        User: The created user object
    """
    user = User(username=username, is_admin=is_admin)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user
