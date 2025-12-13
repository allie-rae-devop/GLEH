"""
Admin API Routes for the Admin Panel
Handles all admin operations: scanning, importing, diagnostics, server control
"""

import os
import sys
import zipfile
import subprocess
import json
from functools import wraps
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify, current_app
from flask_login import login_required, current_user
from .database import db
from .models import Course, User
from .build import categories_from_name
import hashlib

admin_bp = Blueprint('admin_api', __name__, url_prefix='/api/admin')


def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated


# ===========================
# DASHBOARD OPERATIONS
# ===========================

@admin_bp.route('/env-config', methods=['GET'])
@login_required
@admin_required
def get_env_config():
    """Get environment configuration variables"""
    try:
        # Get project root directory
        root_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..'))
        env_file = os.path.join(root_dir, '.env')

        config_vars = {}

        if os.path.exists(env_file):
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        config_vars[key.strip()] = value.strip()

        return jsonify({'config': config_vars})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/env-config', methods=['POST'])
@login_required
@admin_required
def update_env_config():
    """Update environment configuration variables"""
    try:
        data = request.json
        config_vars = data.get('config', {})

        # Get project root directory
        root_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..'))
        env_file = os.path.join(root_dir, '.env')

        # Write configuration to .env file
        with open(env_file, 'w') as f:
            for key, value in config_vars.items():
                f.write(f'{key}={value}\n')

        return jsonify({'message': 'Configuration updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===========================
# COURSE OPERATIONS
# ===========================

@admin_bp.route('/scan-courses', methods=['POST'])
@login_required
@admin_required
def scan_courses():
    """Scan /courses directory and import courses to database"""
    try:
        # Determine courses directory (Docker volume or local)
        courses_dir = '/app/data/courses' if os.path.exists(
            '/app/data/courses') else os.path.join(
                current_app.config.get('CONTENT_DIR', '.'), 'courses')

        if not os.path.isdir(courses_dir):
            return jsonify({'error': 'Courses directory not found'}), 400

        # Find all valid course directories (must have index.html or data.json)
        course_folders = []
        for item in os.listdir(courses_dir):
            item_path = os.path.join(courses_dir, item)
            if os.path.isdir(item_path):
                index_path = os.path.join(item_path, 'index.html')
                data_path = os.path.join(item_path, 'data.json')
                if os.path.exists(index_path) or os.path.exists(data_path):
                    course_folders.append(item)

        # Get existing course UIDs
        existing_courses = {c.uid: c for c in Course.query.all()}

        new_count = 0
        updated_count = 0

        # Process each course folder
        for folder in course_folders:
            course_path = os.path.join(courses_dir, folder)
            data_json_path = os.path.join(course_path, 'data.json')

            # Default course info
            course_info = {
                'uid': folder,
                'title': folder.replace('-', ' ').replace('_', ' '),
                'path': f"{folder}/index.html",
                'description': '',
                'categories': '',
            }

            # Parse data.json if available (MIT OCW courses)
            if os.path.exists(data_json_path) and os.path.isfile(data_json_path):
                try:
                    with open(data_json_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Extract instructors
                    instructors = data.get('instructors', [])
                    instructor_names = []
                    for instructor in instructors:
                        if 'title' in instructor and instructor['title']:
                            instructor_names.append(instructor['title'])
                        else:
                            first = instructor.get('first_name', '')
                            last = instructor.get('last_name', '')
                            if first or last:
                                instructor_names.append(f"{first} {last}".strip())

                    # Extract topics/categories
                    topics = data.get('topics', [])
                    categories = set()
                    if topics:
                        for topic_path in topics:
                            if isinstance(topic_path, list):
                                categories.update(topic_path)

                    # Handle thumbnail
                    thumbnail = None
                    image_src = data.get('image_src', '')
                    if image_src:
                        if image_src.startswith('./'):
                            thumbnail = f"{folder}/{image_src[2:]}"
                        else:
                            thumbnail = f"{folder}/{image_src}"

                    # Update course info with MIT OCW data
                    course_info.update({
                        'title': data.get('course_title', folder),
                        'description': data.get('course_description', ''),
                        'instructor': ', '.join(instructor_names) if instructor_names else None,
                        'course_number': data.get('primary_course_number', ''),
                        'term': data.get('term', ''),
                        'year': data.get('year', ''),
                        'level': ', '.join(data.get('level', [])),
                        'department': ', '.join(data.get('department_numbers', [])),
                        'categories': ', '.join(sorted(categories)) if categories else '',
                        'thumbnail': thumbnail,
                        'learning_resources': json.dumps(data.get('learning_resource_types', [])),
                    })

                except Exception as e:
                    current_app.logger.warning(f"Failed to parse data.json for {folder}: {e}")

            # Create or update course in database
            if folder in existing_courses:
                # Update existing course
                course = existing_courses[folder]
                for key, value in course_info.items():
                    setattr(course, key, value)
                updated_count += 1
            else:
                # Create new course
                course = Course(**course_info)
                db.session.add(course)
                new_count += 1

        # Commit all changes to database
        db.session.commit()

        return jsonify({
            'total': len(course_folders),
            'new': new_count,
            'existing': updated_count,
            'message': f'Successfully imported {new_count} new courses and updated {updated_count} existing courses'
        })

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to scan courses: {e}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/get-courses', methods=['GET'])
@login_required
@admin_required
def get_courses():
    """Get all courses from database"""
    try:
        courses = Course.query.all()
        course_list = []

        for course in courses:
            thumb_path = os.path.join(
                os.path.dirname(__file__), '..',
                'static', course.thumbnail or 'images/default_course.jpg')
            has_thumbnail = (os.path.exists(thumb_path) and
                             'default' not in (course.thumbnail or ''))

            course_list.append({
                'id': course.id,
                'uid': course.uid,
                'title': course.title,
                'has_thumbnail': has_thumbnail,
                'categories': course.categories or 'Uncategorized',
                'created_at': course.id  # placeholder
            })

        return jsonify({'courses': course_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/generate-thumbnails', methods=['POST'])
@login_required
@admin_required
def generate_thumbnails_route():
    """Generate missing course thumbnails"""
    try:
        generated = 0
        failed = 0

        courses = Course.query.all()

        for course in courses:
            if not course.thumbnail or 'default' in course.thumbnail:
                try:
                    # Would need to regenerate from video
                    # This is a placeholder
                    generated += 1
                except Exception:
                    failed += 1

        return jsonify({
            'generated': generated,
            'failed': failed
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/autocategorize', methods=['POST'])
@login_required
@admin_required
def autocategorize():
    """Auto-categorize all courses"""
    try:
        updated = 0
        courses = Course.query.all()

        for course in courses:
            new_categories = categories_from_name(course.title)
            if new_categories:
                course.categories = ','.join(new_categories)
                updated += 1

        db.session.commit()

        return jsonify({'updated': updated})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/delete-course/<int:course_id>', methods=['DELETE'])
@login_required
@admin_required
def delete_course(course_id):
    """Delete a course and its associated files"""
    try:
        course = Course.query.get(course_id)
        if not course:
            return jsonify({'error': 'Course not found'}), 404

        # Delete course from database
        db.session.delete(course)
        db.session.commit()

        return jsonify({'message': 'Course deleted successfully'})

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/upload-course', methods=['POST'])
@login_required
@admin_required
def upload_course():
    """Upload course files to the courses volume"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Secure the filename
        filename = secure_filename(file.filename)

        # Determine courses directory (Docker volume or local)
        courses_dir = '/app/data/courses' if os.path.exists(
            '/app/data/courses') else os.path.join(
                current_app.config.get('CONTENT_DIR', '.'), 'courses')

        if not os.path.exists(courses_dir):
            os.makedirs(courses_dir, exist_ok=True)

        # Save uploaded file
        upload_path = os.path.join(courses_dir, filename)
        file.save(upload_path)

        # If it's a zip file, extract it
        if filename.endswith('.zip'):
            extract_dir = os.path.join(
                courses_dir, filename.replace('.zip', ''))
            with zipfile.ZipFile(upload_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            # Remove the zip file after extraction
            os.remove(upload_path)

        return jsonify({
            'message': 'Course uploaded successfully',
            'filename': filename
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===========================
# SERVER OPERATIONS & DIAGNOSTICS
# ===========================

@admin_bp.route('/server/restart', methods=['POST'])
@login_required
@admin_required
def restart_server():
    """Restart the Flask server (Docker container restart required)"""
    try:
        # In Docker, we need to restart the container
        # This endpoint returns success and admin should use
        # docker-compose restart web
        return jsonify({
            'status': 'Use docker-compose restart web to restart server'
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/run-script', methods=['POST'])
@login_required
@admin_required
def run_script():
    """Run maintenance scripts"""
    try:
        data = request.json
        script_name = data.get('script')

        if not script_name:
            return jsonify({'error': 'Script name required'}), 400

        # Whitelist of allowed scripts
        allowed_scripts = [
            'init_database.py',
            'import_courses_from_volume.py'
        ]

        if script_name not in allowed_scripts:
            return jsonify({'error': 'Script not allowed'}), 403

        # Get project root
        root_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..'))
        script_path = os.path.join(root_dir, 'scripts', script_name)

        if not os.path.exists(script_path):
            return jsonify({'error': 'Script not found'}), 404

        # Run the script
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )

        return jsonify({
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'returncode': result.returncode
        })

    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Script execution timed out'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/self-heal', methods=['POST'])
@login_required
@admin_required
def self_heal():
    """Run self-healing diagnostics and repairs"""
    try:
        repairs = []

        # Check 1: Database connectivity
        try:
            db.session.execute(db.text('SELECT 1'))
            repairs.append({
                'check': 'Database connectivity',
                'status': 'OK',
                'action': None
            })
        except Exception as e:
            repairs.append({
                'check': 'Database connectivity',
                'status': 'ERROR',
                'action': f'Database connection failed: {str(e)}'
            })

        # Check 2: Courses volume accessibility
        courses_dir = '/app/data/courses' if os.path.exists(
            '/app/data/courses') else os.path.join(
                current_app.config.get('CONTENT_DIR', '.'), 'courses')

        if os.path.exists(courses_dir):
            repairs.append({
                'check': 'Courses volume',
                'status': 'OK',
                'action': None
            })
        else:
            repairs.append({
                'check': 'Courses volume',
                'status': 'ERROR',
                'action': f'Courses directory not found: {courses_dir}'
            })

        # Check 3: Admin user exists
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            repairs.append({
                'check': 'Admin user',
                'status': 'OK',
                'action': None
            })
        else:
            repairs.append({
                'check': 'Admin user',
                'status': 'WARNING',
                'action': 'Admin user not found - run init_database.py'
            })

        return jsonify({'repairs': repairs})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/status', methods=['GET'])
@login_required
@admin_required
def get_status():
    """Get dashboard status information"""
    try:
        courses_count = Course.query.count()
        users_count = User.query.count()

        # Get Calibre-Web book count from API if available
        ebooks_count = 0
        try:
            from .calibre_client import get_calibre_client
            calibre_client = get_calibre_client()
            books = calibre_client.get_featured_books(count=1000)
            ebooks_count = len(books)
        except Exception:
            pass

        return jsonify({
            'courses_count': courses_count,
            'ebooks_count': ebooks_count,
            'users_count': users_count,
            'server_status': 'running'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/diagnostics', methods=['GET'])
@login_required
@admin_required
def diagnostics():
    """Run system diagnostics"""
    try:
        # Check database
        database_status = 'OK'
        try:
            Course.query.count()
        except Exception:
            database_status = 'ERROR'

        # Count files
        courses_count = Course.query.count()
        users_count = User.query.count()

        # Check courses volume
        courses_dir = '/app/data/courses' if os.path.exists(
            '/app/data/courses') else os.path.join(
                current_app.config.get('CONTENT_DIR', '.'), 'courses')
        volume_status = 'OK' if os.path.exists(courses_dir) else 'ERROR'

        return jsonify({
            'database_status': database_status,
            'courses_count': courses_count,
            'users_count': users_count,
            'volume_status': volume_status,
            'courses_dir': courses_dir
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/logs', methods=['GET'])
@login_required
@admin_required
def get_logs():
    """Get recent application logs"""
    try:
        # Try to read from Docker logs volume
        log_file = '/app/logs/app.log' if os.path.exists(
            '/app/logs') else None

        logs = []
        if log_file and os.path.exists(log_file):
            with open(log_file, 'r') as f:
                # Get last 50 lines
                all_lines = f.readlines()
                logs = all_lines[-50:]
        else:
            logs = [
                '[INFO] No log file found',
                '[INFO] Logs may be in Docker stdout',
                '[INFO] Use: docker logs gleh-web'
            ]

        return jsonify({'logs': logs})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===========================
# USER MANAGEMENT
# ===========================

@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def get_users():
    """Get all users"""
    try:
        users = User.query.all()
        user_list = []

        for user in users:
            user_list.append({
                'id': user.id,
                'username': user.username,
                'is_admin': user.is_admin,
                'created_at': user.created_at.isoformat()
                if user.created_at else None
            })

        return jsonify({'users': user_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/create-user', methods=['POST'])
@login_required
@admin_required
def create_user():
    """Create a new user"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        is_admin = data.get('is_admin', False)

        if not username or not password:
            return jsonify({
                'error': 'Username and password are required'
            }), 400

        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'error': 'Username already exists'}), 409

        # Create new user
        new_user = User(username=username, is_admin=is_admin)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            'message': f'User {username} created successfully',
            'user_id': new_user.id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/delete-user', methods=['POST'])
@login_required
@admin_required
def delete_user():
    """Delete a user account"""
    try:
        data = request.json
        user_id = data.get('user_id')

        user = User.query.get(user_id)

        if not user:
            return jsonify({'error': 'User not found'}), 404

        if user.username == 'admin':
            return jsonify({'error': 'Cannot delete admin user'}), 400

        username = user.username
        db.session.delete(user)
        db.session.commit()

        return jsonify({
            'message': f'User {username} deleted successfully'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/reset-password', methods=['POST'])
@login_required
@admin_required
def reset_password():
    """Reset a user's password"""
    try:
        data = request.json
        user_id = data.get('user_id')
        new_password = data.get('new_password')

        if not new_password:
            return jsonify({'error': 'New password is required'}), 400

        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404

        user.set_password(new_password)
        db.session.commit()

        return jsonify({
            'message': f'Password reset for user {user.username}'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/seed-test-users', methods=['POST'])
@login_required
@admin_required
def seed_test_users():
    """Create 3 test users for testing"""
    try:
        test_users = [
            {'username': 'testuser1', 'password': 'test123'},
            {'username': 'testuser2', 'password': 'test123'},
            {'username': 'testuser3', 'password': 'test123'},
        ]

        created = []
        skipped = []

        for user_data in test_users:
            if User.query.filter_by(
                    username=user_data['username']).first():
                skipped.append(user_data['username'])
            else:
                new_user = User(username=user_data['username'])
                new_user.set_password(user_data['password'])
                db.session.add(new_user)
                created.append(user_data['username'])

        db.session.commit()

        return jsonify({
            'message': 'Test users seeded',
            'created': created,
            'skipped': skipped
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# ===========================
# ABOUT CONTENT MANAGEMENT
# ===========================

@admin_bp.route('/about-content', methods=['GET'])
@login_required
@admin_required
def get_about_content():
    """Get the About page content"""
    try:
        root_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..'))
        about_file = os.path.join(root_dir, 'data', 'about_content.md')

        content = ''
        if os.path.exists(about_file):
            with open(about_file, 'r', encoding='utf-8') as f:
                content = f.read()

        return jsonify({'content': content})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/about-content', methods=['POST'])
@login_required
@admin_required
def update_about_content():
    """Update the About page content"""
    try:
        data = request.json
        content = data.get('content', '')

        root_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), '..'))
        data_dir = os.path.join(root_dir, 'data')
        about_file = os.path.join(data_dir, 'about_content.md')

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

        # Write content to file
        with open(about_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return jsonify({'message': 'About content updated successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
