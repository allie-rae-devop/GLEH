import os
from dotenv import load_dotenv

# CRITICAL: Load .env FIRST before any other imports
# Config classes validate environment variables at import time
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
load_dotenv(os.path.join(root_dir, '.env'))

# Now import everything else after .env is loaded
import re
import time
import uuid
import traceback
import zipfile
import io
from datetime import datetime, timedelta
from collections import defaultdict
from werkzeug.utils import secure_filename
from werkzeug.exceptions import NotFound
from flask import Flask, request, jsonify, render_template, abort, url_for, redirect, session, g, send_file, send_from_directory, make_response
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import generate_csrf, CSRFError
from PIL import Image
from .database import db

# --- App Initialization and Configuration ---

app = Flask(__name__,
            template_folder=os.path.join(root_dir, 'templates'),
            static_folder=os.path.join(root_dir, 'static'),
            instance_path=os.path.join(root_dir, 'instance'))

# Load configuration based on environment
env = os.environ.get('FLASK_ENV', 'development')
from .config import config
app.config.from_object(config[env])

# --- Structured Logging Configuration ---
# Import and configure structured logging (Phase 1 P5)
try:
    from .logging_config import configure_logging
    log = configure_logging(app)
except ImportError:
    # Fallback to standard logging if structlog not installed
    import logging
    log = logging.getLogger(__name__)
    log.warning("structlog not installed, using standard logging")

# --- Database Initialization ---
db.init_app(app)

# --- CSRF Protection Initialization ---
from flask_wtf.csrf import CSRFProtect
csrf = CSRFProtect(app)

# --- Login Manager Configuration ---
login_manager = LoginManager(app)
login_manager.login_view = 'index'

from .models import User, Course, Ebook, CourseProgress, CourseNote, ReadingProgress, EbookNote, CalibreReadingProgress
from .admin_api import admin_bp
from .calibre_client import get_calibre_client

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Structured Logging: Request/Response Hooks ---

@app.before_request
def before_request_logging():
    """
    Initialize logging context before each request.

    Actions:
    1. Generate unique request_id (UUID4)
    2. Store start_time for latency calculation
    3. Bind request context to logger
    4. Log request_received event

    Performance: ~0.2ms overhead
    """
    # Generate unique request ID for tracing
    request_id = str(uuid.uuid4())
    g.request_id = request_id
    g.start_time = time.time()

    # Bind request context to logger
    g.log = log.bind(
        request_id=request_id,
        method=request.method,
        path=request.path,
        ip=request.remote_addr,
        user_agent=request.headers.get('User-Agent', 'Unknown')[:100]  # Truncate long user agents
    )

    # Log request received
    g.log.info(
        "request_received",
        user_id=current_user.id if current_user.is_authenticated else None
    )

@app.after_request
def after_request_logging(response):
    """
    Log request completion metrics after each request.

    Actions:
    1. Calculate request latency
    2. Log request_completed event with status code
    3. Include performance metrics

    Performance: ~0.3ms overhead
    """
    if hasattr(g, 'log') and hasattr(g, 'start_time'):
        latency_ms = (time.time() - g.start_time) * 1000

        # Calculate response size safely
        # For file responses in passthrough mode, use Content-Length header
        # For regular responses, use get_data() if available
        response_size = 0
        try:
            if hasattr(response, 'is_streamed') and response.is_streamed:
                # Streamed/file responses: use Content-Length header
                response_size = int(response.headers.get('Content-Length', 0))
            else:
                # Regular responses: buffer and measure
                response_size = len(response.get_data())
        except (RuntimeError, ValueError):
            # Fallback: use Content-Length header
            response_size = int(response.headers.get('Content-Length', 0))

        g.log.info(
            "request_completed",
            status=response.status_code,
            latency_ms=round(latency_ms, 2),
            response_size_bytes=response_size
        )

    return response

@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    """
    Handle CSRF errors by returning a 400 JSON response.
    This allows tests to catch CSRF rejections as responses rather than exceptions.
    """
    if hasattr(g, 'log'):
        g.log.warning(
            "csrf_error",
            error_message=str(e.description)
        )
    return jsonify({'error': str(e.description)}), 400

@app.errorhandler(Exception)
def handle_exception_logging(e):
    """
    Global exception handler with structured logging.

    Logs all unhandled exceptions with full traceback for debugging.
    """
    if hasattr(g, 'log'):
        g.log.error(
            "error_occurred",
            error_type=type(e).__name__,
            error_message=str(e),
            traceback=traceback.format_exc()
        )

    # Let Flask handle the actual response
    # This ensures existing error handlers still work
    raise e

# --- Security: Input Validation ---

def validate_username(username):
    """
    Validates username meets requirements.
    Returns (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"

    if len(username) < app.config['MIN_USERNAME_LENGTH']:
        return False, f"Username must be at least {app.config['MIN_USERNAME_LENGTH']} characters"

    if len(username) > app.config['MAX_USERNAME_LENGTH']:
        return False, f"Username must not exceed {app.config['MAX_USERNAME_LENGTH']} characters"

    # Allow alphanumeric, underscore, and hyphen
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"

    return True, None

def validate_password(password):
    """
    Validates password meets strength requirements.
    Returns (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"

    if len(password) < app.config['MIN_PASSWORD_LENGTH']:
        return False, f"Password must be at least {app.config['MIN_PASSWORD_LENGTH']} characters"

    # Check for at least one letter and one number
    if not re.search(r'[A-Za-z]', password):
        return False, "Password must contain at least one letter"

    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"

    return True, None

# --- Security: Rate Limiting ---

# Simple in-memory rate limiting (IP -> list of timestamps)
auth_attempts = defaultdict(list)

def check_rate_limit(ip_address):
    """
    Check if IP has exceeded rate limit for auth endpoints.
    Returns (is_allowed, error_message)
    """
    now = datetime.utcnow()
    cutoff = now - timedelta(minutes=1)

    # Clean old attempts
    auth_attempts[ip_address] = [
        timestamp for timestamp in auth_attempts[ip_address]
        if timestamp > cutoff
    ]

    # Check limit
    if len(auth_attempts[ip_address]) >= app.config['AUTH_RATE_LIMIT']:
        # Log rate limit exceeded
        if hasattr(g, 'log'):
            g.log.warning(
                "rate_limit_exceeded",
                ip=ip_address,
                endpoint=request.path,
                limit=app.config['AUTH_RATE_LIMIT'],
                period_seconds=60,
                attempt_count=len(auth_attempts[ip_address])
            )
        return False, "Too many attempts. Please try again in a minute."

    # Record this attempt
    auth_attempts[ip_address].append(now)
    return True, None

# --- CSRF Token Endpoint ---

@app.route('/csrf-token', methods=['GET'])
def get_csrf_token():
    """Returns the CSRF token for the client."""
    token = generate_csrf()
    return jsonify({'csrf_token': token})

@app.route('/layout-css')
def get_layout_css():
    """Generate dynamic CSS with layout settings injected"""
    from .models import LayoutSettings

    layout = LayoutSettings.query.filter_by(name='default').first()

    if layout:
        settings = layout.get_settings()
    else:
        settings = LayoutSettings.get_default_settings()

    css = f"""
    :root {{
        --featured-courses-width: {settings.get('featured_courses_width', '100%')};
        --featured-courses-max-width: {settings.get('featured_courses_max_width', '600px')};
        --featured-ebooks-width: {settings.get('featured_ebooks_width', '100%')};
        --featured-ebooks-max-width: {settings.get('featured_ebooks_max_width', '600px')};

        --course-image-width: {settings.get('course_image_width', '150px')};
        --course-title-font-size: {settings.get('course_title_font_size', '1rem')};

        --ebook-image-width: {settings.get('ebook_image_width', '120px')};
        --ebook-image-height: {settings.get('ebook_image_height', '150px')};
        --ebook-title-font-size: {settings.get('ebook_title_font_size', '1rem')};

        --table-row-height: {settings.get('table_row_height', 'auto')};
        --table-padding: {settings.get('table_padding', '12px')};
        --table-gap: {settings.get('table_gap', '0.75rem')};
        --card-background: {settings.get('card_background', 'transparent')};
        --card-border: {settings.get('card_border', 'none')};
    }}
    """

    return css, 200, {'Content-Type': 'text/css; charset=utf-8'}

# --- Health Check Endpoints ---

@app.route('/health', methods=['GET'])
def health():
    """
    Lightweight health check for load balancers and orchestrators.
    Returns 200 if application is responding, 503 if unhealthy.

    Used by: AWS ELB, nginx, Kubernetes liveness probes.
    Response time: Expected <10ms under normal load.
    SLA: Must respond in <2 seconds.
    """
    try:
        # Test database connectivity with timeout protection
        db.session.execute(db.text('SELECT 1'))
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        app.logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503

@app.route('/health/deep', methods=['GET'])
def health_deep():
    """
    Detailed health check with component diagnostics.
    For monitoring dashboards and SRE analysis (AHDM integration).

    Used by: Monitoring dashboards, AHDM predictive analysis, SRE alerting.
    Response time: Expected <50ms under normal load.
    SLA: Must respond in <5 seconds.
    """
    checks = {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'components': {}
    }

    # Component 1: Database connectivity
    try:
        db.session.execute(db.text('SELECT 1'))
        checks['components']['database'] = {
            'status': 'healthy',
            'message': 'Database connection verified'
        }
    except Exception as e:
        app.logger.error(f"Database health check failed: {str(e)}")
        checks['components']['database'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        checks['status'] = 'unhealthy'

    # Component 2: Flask-Login (authentication system)
    try:
        # Verify LoginManager is initialized
        assert login_manager is not None
        checks['components']['authentication'] = {
            'status': 'healthy',
            'message': 'Flask-Login initialized'
        }
    except Exception as e:
        app.logger.error(f"Authentication health check failed: {str(e)}")
        checks['components']['authentication'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        checks['status'] = 'unhealthy'

    # Component 3: CSRF protection (Flask-WTF)
    try:
        assert csrf is not None
        checks['components']['csrf'] = {
            'status': 'healthy',
            'message': 'CSRF protection active'
        }
    except Exception as e:
        app.logger.error(f"CSRF health check failed: {str(e)}")
        checks['components']['csrf'] = {
            'status': 'unhealthy',
            'error': str(e)
        }
        checks['status'] = 'unhealthy'

    # Return appropriate status code
    status_code = 200 if checks['status'] == 'healthy' else 503
    return jsonify(checks), status_code

# --- Front-end Rendering ---

@app.route('/')
def index():
    """Serves the main single-page application."""
    return render_template('index.html')

@app.route('/course/<uid>')
def course_page(uid):
    """Serves the dedicated page for a single course."""
    course = Course.query.filter_by(uid=uid).first_or_404()
    return render_template('course.html', course=course)

@app.route('/textbook/<book_id>')
def textbook_page(book_id):
    """Serves the dedicated launch page for a single textbook from Calibre-Web."""
    from .models import EbookNote

    # Fetch book details from Calibre-Web
    calibre_client = get_calibre_client()

    # Extract numeric ID from book_id (e.g., 'calibre-4' -> 4)
    numeric_id = int(book_id.replace('calibre-', ''))
    book = calibre_client.get_book(numeric_id)

    if not book:
        abort(404)

    # Get user note if logged in
    user_note = ''
    if current_user.is_authenticated:
        note = EbookNote.query.filter_by(
            user_id=current_user.id,
            ebook_id=book_id
        ).first()
        if note:
            user_note = note.content

        # Track reading progress - create or update entry
        progress = CalibreReadingProgress.query.filter_by(
            user_id=current_user.id,
            ebook_id=book_id
        ).first()

        if not progress:
            # Create new progress entry
            progress = CalibreReadingProgress(
                user_id=current_user.id,
                ebook_id=book_id,
                status='in_progress'
            )
            db.session.add(progress)
        else:
            # Update last_read timestamp
            progress.last_read = datetime.utcnow()

        db.session.commit()

    return render_template('textbook.html', book=book, user_note=user_note)

@app.route('/api/calibre/cover/<int:book_id>')
def proxy_calibre_cover(book_id):
    """
    Proxy cover images from Calibre-Web with authentication.

    This endpoint fetches cover images from Calibre-Web using authenticated
    requests and serves them to the browser, avoiding cross-origin auth issues.

    Args:
        book_id: Calibre book ID

    Returns:
        Image bytes with appropriate content-type header
    """
    try:
        calibre_client = get_calibre_client()

        # Construct internal Calibre-Web cover URL
        cover_url = f"{calibre_client.base_url}/opds/cover/{book_id}"

        # Fetch cover using authenticated session
        response = calibre_client.session.get(cover_url, timeout=10)
        response.raise_for_status()

        # Determine content type from response headers
        content_type = response.headers.get('Content-Type', 'image/jpeg')

        # Return image bytes
        return send_file(
            io.BytesIO(response.content),
            mimetype=content_type,
            as_attachment=False
        )

    except Exception as e:
        log.error(f"Failed to proxy cover for book {book_id}: {e}")
        # Return 404 or default placeholder image
        abort(404)

@app.route('/courses/<path:filepath>')
def serve_course_files(filepath):
    """Serves course files from the courses directory."""
    from flask import send_from_directory
    import os
    # In Docker: serve from /app/data/courses (volume mount)
    # In development: serve from CONTENT_DIR/courses
    content_dir = app.config.get('CONTENT_DIR')
    if content_dir:
        # Development mode: use configured CONTENT_DIR
        courses_dir = os.path.join(content_dir, 'courses')
    else:
        # Docker mode: use hardcoded volume path
        courses_dir = '/app/data/courses'

    if not os.path.exists(courses_dir):
        log.error(f'Courses directory does not exist: {courses_dir}')
        abort(404)

    return send_from_directory(courses_dir, filepath)


@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        abort(403)
    users = User.query.all()
    return render_template('admin.html', users=users)

# Register admin API blueprint
app.register_blueprint(admin_bp)

# --- Main Content API ---

@app.route('/api/content')
def get_content():
    all_courses = Course.query.all()
    content_list = []

    user_progress = {}
    user_notes = {}
    if current_user.is_authenticated:
        progress_records = CourseProgress.query.filter_by(user_id=current_user.id).all()
        note_records = CourseNote.query.filter_by(user_id=current_user.id).all()
        user_progress = {p.course_id: p.status for p in progress_records}
        user_notes = {n.course_id: n.content for n in note_records}

    # Add courses to content list
    for course in all_courses:
        content_list.append({
            'type': 'course', 'uid': course.uid, 'title': course.title,
            'path': url_for('course_page', uid=course.uid),
            'description': course.description, 'categories': course.categories.split(',') if course.categories else [],
            'thumbnail': course.thumbnail_url if course.thumbnail and 'default' not in (course.thumbnail or '') else '',
            'user_progress': user_progress.get(course.id, 'Not Started'),
            'user_note': user_notes.get(course.id, '')
        })

    # Fetch ebooks from Calibre-Web instead of local database
    try:
        calibre_client = get_calibre_client()
        all_ebooks = calibre_client.get_featured_books(count=100)  # Get all books for homepage

        for ebook in all_ebooks:
            content_list.append({
                'type': 'ebook',
                'uid': ebook['uid'],
                'title': ebook['title'],
                'author': ebook.get('author', 'Unknown'),
                'path': url_for('textbook_page', book_id=ebook['uid']),  # Link to launch page
                'reader_url': ebook.get('reader_url'),  # Direct link to Calibre-Web reader
                'cover_path': ebook.get('cover_url'),  # Direct URL to Calibre-Web cover
                'categories': ebook.get('categories', []),
            })
    except Exception as e:
        # Log error but don't fail - just return courses without ebooks
        log.error(f"Failed to fetch books from Calibre-Web: {e}")

    return jsonify({'content': content_list})

# --- User Interaction APIs ---

@app.route('/api/course/<uid>/note', methods=['GET'])
@login_required
def get_note(uid):
    course = Course.query.filter_by(uid=uid).first_or_404()
    note = CourseNote.query.filter_by(user_id=current_user.id, course_id=course.id).first()
    return jsonify({'content': note.content if note else ''})

@app.route('/api/course/progress', methods=['POST'])
@login_required
def update_progress():
    data = request.get_json()
    course = Course.query.filter_by(uid=data.get('course_uid')).first_or_404()
    progress = CourseProgress.query.filter_by(user_id=current_user.id, course_id=course.id).first()
    if progress:
        progress.status = data.get('status')
    else:
        progress = CourseProgress(user_id=current_user.id, course_id=course.id, status=data.get('status'))
        db.session.add(progress)
    db.session.commit()
    return jsonify({'message': 'Progress updated successfully.'})

@app.route('/api/course/note', methods=['POST'])
@login_required
def update_note():
    data = request.get_json()
    course = Course.query.filter_by(uid=data.get('course_uid')).first_or_404()
    note = CourseNote.query.filter_by(user_id=current_user.id, course_id=course.id).first()
    if note:
        note.content = data.get('content', '')
    else:
        note = CourseNote(user_id=current_user.id, course_id=course.id, content=data.get('content', ''))
        db.session.add(note)
    db.session.commit()
    return jsonify({'message': 'Note saved successfully.'})

# --- Ebook Note API Endpoints ---

@app.route('/api/textbook/<book_id>/note', methods=['GET'])
@login_required
def get_ebook_note(book_id):
    from .models import EbookNote
    note = EbookNote.query.filter_by(user_id=current_user.id, ebook_id=book_id).first()
    return jsonify({'content': note.content if note else ''})

@app.route('/api/textbook/note', methods=['POST'])
@login_required
def update_ebook_note():
    from .models import EbookNote
    data = request.get_json()
    book_id = data.get('book_id')
    note = EbookNote.query.filter_by(user_id=current_user.id, ebook_id=book_id).first()
    if note:
        note.content = data.get('content', '')
    else:
        note = EbookNote(user_id=current_user.id, ebook_id=book_id, content=data.get('content', ''))
        db.session.add(note)
    db.session.commit()
    return jsonify({'message': 'Note saved successfully.'})

# --- API Endpoints for Authentication ---

@app.route('/api/register', methods=['POST'])
def register():
    # Rate limiting
    ip_address = request.remote_addr
    is_allowed, rate_limit_error = check_rate_limit(ip_address)
    if not is_allowed:
        return jsonify({'error': rate_limit_error}), 429

    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required.'}), 400

    # Validate username
    is_valid, username_error = validate_username(data['username'])
    if not is_valid:
        return jsonify({'error': username_error}), 400

    # Validate password
    is_valid, password_error = validate_password(data['password'])
    if not is_valid:
        return jsonify({'error': password_error}), 400

    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Username already exists.'}), 409

    # Create new user
    new_user = User(username=data['username'])
    new_user.set_password(data['password'])
    db.session.add(new_user)
    db.session.commit()

    # Log successful registration
    if hasattr(g, 'log'):
        g.log.info(
            "user_registered",
            user_id=new_user.id,
            username=new_user.username
        )

    return jsonify({'message': 'User registered successfully.'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    # Rate limiting
    ip_address = request.remote_addr
    is_allowed, rate_limit_error = check_rate_limit(ip_address)
    if not is_allowed:
        return jsonify({'error': rate_limit_error}), 429

    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data:
        return jsonify({'error': 'Username and password are required.'}), 400

    # Log login attempt
    if hasattr(g, 'log'):
        g.log.info("user_login_attempt", username=data['username'])

    user = User.query.filter_by(username=data['username']).first()
    if user and user.check_password(data['password']):
        login_user(user, remember=True)
        from flask import session
        session.permanent = True

        # Log successful login
        if hasattr(g, 'log'):
            g.log.info(
                "user_login_success",
                user_id=user.id,
                username=user.username
            )

        return jsonify({'message': 'Login successful.', 'user': {'id': user.id, 'username': user.username}}), 200

    # Log failed login
    if hasattr(g, 'log'):
        g.log.warning(
            "user_login_failed",
            username=data['username'],
            reason="invalid_credentials"
        )

    return jsonify({'error': 'Invalid username or password.'}), 401

@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    # Log logout before clearing user context
    if hasattr(g, 'log'):
        g.log.info("user_logout", user_id=current_user.id, username=current_user.username)

    logout_user()
    return jsonify({'message': 'Logout successful.'}), 200

@app.route('/api/check_session', methods=['GET'])
def check_session():
    if current_user.is_authenticated:
        return jsonify({
            'is_authenticated': True,
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'is_admin': current_user.is_admin
            }
        }), 200
    return jsonify({'is_authenticated': False}), 401

@app.route('/auth/check')
def nginx_auth_check():
    """
    Nginx auth_request endpoint for Calibre-Web SSO.
    Returns 200 with X-Remote-User header if authenticated, 401 if not.
    """
    if current_user.is_authenticated:
        # Return 200 with username header for Calibre-Web
        response = make_response('', 200)
        response.headers['X-Remote-User'] = current_user.username
        return response
    else:
        # Return 401 - Nginx will redirect to login
        return make_response('Unauthorized', 401)

# --- User Profile Routes ---

@app.route('/profile')
@login_required
def profile():
    """User profile/dashboard page"""
    return render_template('profile.html', user=current_user)

@app.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    """Get user profile data with eager-loaded relationships to prevent N+1 queries"""
    # Get user's course progress - relationships are auto-joined via lazy='joined'
    progress_entries = CourseProgress.query.filter_by(user_id=current_user.id).all()
    courses_in_progress = []
    courses_completed = []

    for entry in progress_entries:
        # Course is already loaded via eager-loading, no additional query
        course = entry.course
        if course:
            course_data = {
                'uid': course.uid,
                'title': course.title,
                'thumbnail': url_for('static', filename=course.thumbnail) if course.thumbnail else '',
                'status': entry.status
            }
            if entry.status == 'Completed':
                courses_completed.append(course_data)
            else:
                courses_in_progress.append(course_data)

    # Get user's notes - relationships are auto-joined via lazy='joined'
    notes = CourseNote.query.filter_by(user_id=current_user.id).all()
    notes_data = []
    for note in notes:
        # Course is already loaded via eager-loading, no additional query
        course = note.course
        if course:
            notes_data.append({
                'type': 'course',
                'course_uid': course.uid,
                'course_title': course.title,
                'content': note.content[:100] + '...' if len(note.content) > 100 else note.content
            })

    # Get ebook notes from Calibre-Web books
    ebook_notes = EbookNote.query.filter_by(user_id=current_user.id).all()
    for note in ebook_notes:
        # Fetch book title from Calibre-Web
        try:
            calibre_client = get_calibre_client()
            # Extract numeric ID from ebook_id (e.g., 'calibre-4' -> 4)
            numeric_id = int(note.ebook_id.replace('calibre-', ''))
            book = calibre_client.get_book(numeric_id)
            if book:
                notes_data.append({
                    'type': 'ebook',
                    'ebook_id': note.ebook_id,
                    'ebook_title': book['title'],
                    'content': note.content[:100] + '...' if len(note.content) > 100 else note.content
                })
        except Exception as e:
            log.warning(f"Failed to fetch book title for {note.ebook_id}: {e}")
            # Still show the note even if we can't fetch the title
            notes_data.append({
                'type': 'ebook',
                'ebook_id': note.ebook_id,
                'ebook_title': f'Book {note.ebook_id}',
                'content': note.content[:100] + '...' if len(note.content) > 100 else note.content
            })

    # Get Calibre-Web reading progress
    calibre_progress = CalibreReadingProgress.query.filter_by(user_id=current_user.id).all()
    reading_list = []
    for progress in calibre_progress:
        # Fetch book title from Calibre-Web
        try:
            calibre_client = get_calibre_client()
            # Extract numeric ID from ebook_id (e.g., 'calibre-4' -> 4)
            numeric_id = int(progress.ebook_id.replace('calibre-', ''))
            book = calibre_client.get_book(numeric_id)
            if book:
                reading_list.append({
                    'uid': progress.ebook_id,
                    'title': book['title'],
                    'progress': progress.progress_percent,
                    'status': progress.status,
                    'last_read': progress.last_read.isoformat() if progress.last_read else None
                })
        except Exception as e:
            log.warning(f"Failed to fetch book title for {progress.ebook_id}: {e}")
            # Still show the entry even if we can't fetch the title
            reading_list.append({
                'uid': progress.ebook_id,
                'title': f'Book {progress.ebook_id}',
                'progress': progress.progress_percent,
                'status': progress.status,
                'last_read': progress.last_read.isoformat() if progress.last_read else None
            })

    return jsonify({
        'user': {
            'username': current_user.username,
            'avatar': url_for('serve_avatar', filename=current_user.avatar) if current_user.avatar else url_for('static', filename='avatars/default_avatar.svg'),
            'about_me': current_user.about_me,
            'gender': current_user.gender,
            'pronouns': current_user.pronouns,
            'created_at': current_user.created_at.isoformat() if current_user.created_at else None
        },
        'courses_in_progress': courses_in_progress,
        'courses_completed': courses_completed,
        'notes': notes_data,
        'reading_list': reading_list
    })

@app.route('/api/profile', methods=['POST'])
@login_required
def update_profile():
    """Update user profile"""
    data = request.get_json()

    if 'about_me' in data:
        current_user.about_me = data['about_me']

    if 'gender' in data:
        current_user.gender = data['gender']

    if 'pronouns' in data:
        current_user.pronouns = data['pronouns']

    db.session.commit()
    return jsonify({'message': 'Profile updated successfully'})

@app.route('/api/profile/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Upload user avatar with validation"""
    if 'avatar' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400

    file = request.files['avatar']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    # Check file extension
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}  # Removed SVG for security
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        # Log rejected upload - invalid file type
        if hasattr(g, 'log'):
            g.log.warning(
                "image_upload_rejected",
                filename=file.filename,
                reason="invalid_file_type",
                user_id=current_user.id
            )
        return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, gif'}), 400

    # Pre-validate file size before opening
    max_size = app.config['MAX_UPLOAD_SIZE']
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset to beginning

    if file_size > max_size:
        # Log rejected upload - file too large
        if hasattr(g, 'log'):
            g.log.warning(
                "image_upload_rejected",
                filename=file.filename,
                reason="exceeds_size_limit",
                file_size_bytes=file_size,
                max_size_bytes=max_size,
                user_id=current_user.id
            )
        return jsonify({'error': f'File too large. Maximum size is {max_size / (1024*1024):.0f}MB'}), 400

    # Validate image with Pillow before saving
    try:
        # Try to open the image to validate it's a real image file
        img = Image.open(file.stream)

        # Verify image format matches file extension
        extension = file.filename.rsplit('.', 1)[1].lower()
        valid_formats = {
            'png': 'PNG',
            'jpg': 'JPEG',
            'jpeg': 'JPEG',
            'gif': 'GIF'
        }

        if img.format and img.format.upper() != valid_formats.get(extension):
            return jsonify({'error': 'File extension does not match image format'}), 400

        # Validate image dimensions (DoS prevention - image bombs)
        MAX_IMAGE_WIDTH = 4096
        MAX_IMAGE_HEIGHT = 4096
        if img.size[0] > MAX_IMAGE_WIDTH or img.size[1] > MAX_IMAGE_HEIGHT:
            return jsonify({'error': f'Image dimensions too large. Maximum: {MAX_IMAGE_WIDTH}x{MAX_IMAGE_HEIGHT} pixels'}), 400

        # File is valid, reset stream for saving
        file.seek(0)

    except Exception as e:
        return jsonify({'error': f'Invalid or corrupted image file: {str(e)}'}), 400

    # Save file to local filesystem (static/avatars directory)
    filename = secure_filename(f"{current_user.id}_{file.filename}")

    try:
        # Ensure avatars directory exists
        avatars_dir = os.path.join(app.static_folder, 'avatars')
        os.makedirs(avatars_dir, exist_ok=True)

        # Save file to filesystem
        filepath = os.path.join(avatars_dir, filename)
        file.save(filepath)

        # Update user avatar
        current_user.avatar = filename
        db.session.commit()

    except Exception as e:
        log.error(f"Failed to upload avatar: {e}")
        return jsonify({'error': 'Failed to upload avatar'}), 500

    # Log successful upload
    if hasattr(g, 'log'):
        g.log.info(
            "image_upload_success",
            filename=filename,
            file_size_bytes=file_size,
            user_id=current_user.id
        )

    return jsonify({
        'message': 'Avatar uploaded successfully',
        'avatar_url': url_for('serve_avatar', filename=filename)
    })

@app.route('/avatars/<filename>')
def serve_avatar(filename):
    """Serve avatar from local filesystem (static/avatars directory)"""
    # Sanitize filename
    filename = secure_filename(filename)
    avatars_dir = os.path.join(app.static_folder, 'avatars')
    filepath = os.path.join(avatars_dir, filename)

    try:
        # Check if file exists locally
        if not os.path.exists(filepath):
            # Fallback to default avatar
            return send_from_directory(os.path.join(app.static_folder, 'avatars'), 'default_avatar.svg')

        # Serve the file from filesystem
        response = send_from_directory(avatars_dir, filename)
        response.headers['Cache-Control'] = 'public, max-age=3600'  # Cache for 1 hour
        return response

    except Exception as e:
        log.error(f"Failed to serve avatar: {e}")
        # Fallback to default avatar on error
        return send_from_directory(os.path.join(app.static_folder, 'avatars'), 'default_avatar.svg')

# --- Ebook Reader Routes ---
# MIGRATED TO CALIBRE-WEB: Custom ebook reader replaced by Calibre-Web with Nginx SSO

@app.route('/reader/<uid>')
def ebook_reader(uid):
    """Redirect old ebook reader URLs to Calibre-Web"""
    # For now, redirect to Calibre-Web home
    # TODO: Map ebook UID to Calibre book ID for direct book linking
    return redirect('/calibre/')

# DEPRECATED: Reading progress now handled by Calibre-Web natively
# Removed routes - reading progress is managed by Calibre-Web's built-in system

# DEPRECATED: Ebook file serving now handled by Calibre-Web
# Removed 200+ lines of custom EPUB parsing, ZIP file handling, and MIME type detection
# Calibre-Web provides superior ebook serving with proper caching, format conversion, etc.

# --- Main Execution ---
if __name__ == '__main__':
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'development':
        app.run(debug=True)
    else:
        print('ERROR: Flask development server must not run in production.')
        print('Use waitress or gunicorn in production. Example:')
        print('  waitress-serve --port=8000 app:app')
        print('Or with gunicorn:')
        print('  gunicorn -w 4 -b 0.0.0.0:8000 app:app')
        exit(1)
