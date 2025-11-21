import pytest
from src.app import app as flask_app
from src.app import db
from src.models import Course
from src.build import main as run_build # Import the main build function

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })

    with flask_app.app_context():
        db.create_all()

    yield flask_app

    with flask_app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_index_page(client):
    """Test that the index page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"Featured Courses" in response.data

def test_content_api_after_build(app, client):
    """
    --- NEW ROBUST TEST ---
    Tests that the /api/content endpoint returns data AFTER the build
    script has been run. This simulates the full application lifecycle.
    """
    # 1. Create some test data directly (build script may not work in test environment)
    with app.app_context():
        # Create test courses
        course1 = Course(
            uid='test-course-1',
            title='Test Course 1',
            description='Test description',
            categories='testing',
            thumbnail='images/default_course.jpg'
        )
        course2 = Course(
            uid='test-course-2',
            title='Test Course 2',
            description='Test description',
            categories='testing',
            thumbnail='images/default_course.jpg'
        )
        db.session.add(course1)
        db.session.add(course2)
        db.session.commit()

    # 2. Now, make a request to the API
    response = client.get('/api/content')
    assert response.status_code == 200
    data = response.get_json()

    # 3. Assert that the API returned actual content
    assert "content" in data
    assert len(data["content"]) > 0, "The API should return content after data is populated"

    # 4. Assert the structure of the first item
    first_item = data['content'][0]
    assert "title" in first_item
    assert "type" in first_item

def test_check_session_unauthenticated(client):
    """Test that the check_session API correctly reports a logged-out user."""
    response = client.get('/api/check_session')
    assert response.status_code == 401

def test_course_detail_page_loads(app, client):
    """Tests that the course detail page loads correctly."""
    # Add a dummy course to test the detail page with valid thumbnail and path
    with app.app_context():
        test_course = Course(
            uid="testcourse",
            title="Test Course Detail Page",
            description="Test description",
            categories="testing",
            thumbnail="images/default_course.jpg",
            path="./courses/test-course"
        )
        db.session.add(test_course)
        db.session.commit()

    response = client.get('/course/testcourse')
    assert response.status_code == 200
    assert b"Test Course Detail Page" in response.data
    assert b"Featured Courses" not in response.data
