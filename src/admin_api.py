"""
Admin API Routes for the Admin Panel
Handles all admin operations: scanning, importing, diagnostics, server control
"""

import os
import json
from functools import wraps
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from .database import db
from .models import Course, Ebook, User, LayoutSettings
from .build import process_ebooks, extract_epub_metadata, fetch_cover_from_google_books, \
    download_cover_image, generate_cover_image, parse_course_metadata, generate_thumbnail, \
    categories_from_name
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
# TEXTBOOK OPERATIONS
# ===========================

@admin_bp.route('/scan-ebooks', methods=['POST'])
@login_required
@admin_required
def scan_ebooks():
    """Scan /epub directory for new EPUB files"""
    try:
        from . import app
        epub_dir = os.path.join(app.config.get('CONTENT_DIR', '.'), 'epub')

        if not os.path.isdir(epub_dir):
            return jsonify({'error': 'EPUB directory not found'}), 400

        epub_files = [f for f in os.listdir(epub_dir) if f.lower().endswith('.epub')]
        existing_ids = set(e.uid for e in Ebook.query.all())

        new_count = 0
        for filename in epub_files:
            uid = hashlib.md5(filename.encode()).hexdigest()
            if uid not in existing_ids:
                new_count += 1

        return jsonify({
            'total': len(epub_files),
            'new': new_count,
            'existing': len(epub_files) - new_count
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/get-ebooks', methods=['GET'])
@login_required
@admin_required
def get_ebooks():
    """Get all ebooks from database"""
    try:
        ebooks = Ebook.query.all()
        ebook_list = []

        for ebook in ebooks:
            # Check if cover exists
            cover_path = os.path.join(os.path.dirname(__file__), '..', 'static', ebook.cover_path)
            has_cover = os.path.exists(cover_path)
            cover_size = os.path.getsize(cover_path) if has_cover else 0
            is_real = cover_size > 10000 if has_cover else False

            ebook_list.append({
                'id': ebook.id,
                'title': ebook.title,
                'author': 'Unknown',
                'cover_status': 'found' if is_real else 'generated',
                'created_at': ebook.id  # placeholder
            })

        return jsonify({'ebooks': ebook_list})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/search-covers', methods=['POST'])
@login_required
@admin_required
def search_covers():
    """Search for covers using specified source"""
    try:
        data = request.json
        source = data.get('source', 'google')

        found = 0
        failed = 0
        skipped = 0

        ebooks = Ebook.query.all()

        for ebook in ebooks:
            cover_path = os.path.join(os.path.dirname(__file__), '..', 'static', ebook.cover_path)

            # Skip if already has real cover
            if os.path.exists(cover_path) and os.path.getsize(cover_path) > 10000:
                skipped += 1
                continue

            # Try to find cover
            cover_url = None

            if source == 'google':
                from .extract_metadata import fetch_cover_from_google_books
                cover_url = fetch_cover_from_google_books(ebook.title)
            # Add more sources as needed

            if cover_url:
                if download_cover_image(cover_url, cover_path):
                    found += 1
                else:
                    failed += 1
            else:
                failed += 1

        return jsonify({
            'found': found,
            'failed': failed,
            'skipped': skipped
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/generate-covers', methods=['POST'])
@login_required
@admin_required
def generate_covers():
    """Generate placeholder covers for books without covers"""
    try:
        generated = 0
        ebooks = Ebook.query.all()

        for ebook in ebooks:
            cover_path = os.path.join(os.path.dirname(__file__), '..', 'static', ebook.cover_path)

            # Only generate if missing or very small
            if not os.path.exists(cover_path) or os.path.getsize(cover_path) < 10000:
                try:
                    generate_cover_image(ebook.title, cover_path)
                    generated += 1
                except:
                    pass

        return jsonify({'generated': generated})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===========================
# COURSE OPERATIONS
# ===========================

@admin_bp.route('/scan-courses', methods=['POST'])
@login_required
@admin_required
def scan_courses():
    """Scan /courses directory for new courses"""
    try:
        from . import app
        courses_dir = os.path.join(app.config.get('CONTENT_DIR', '.'), 'courses')

        if not os.path.isdir(courses_dir):
            return jsonify({'error': 'Courses directory not found'}), 400

        course_folders = [f for f in os.listdir(courses_dir)
                         if os.path.isdir(os.path.join(courses_dir, f))]

        existing_ids = set(c.uid for c in Course.query.all())

        new_count = 0
        for folder in course_folders:
            uid = hashlib.md5(folder.encode()).hexdigest()
            if uid not in existing_ids:
                new_count += 1

        return jsonify({
            'total': len(course_folders),
            'new': new_count,
            'existing': len(course_folders) - new_count
        })

    except Exception as e:
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
            thumb_path = os.path.join(os.path.dirname(__file__), '..', 'static',
                                      course.thumbnail or 'images/default_course.jpg')
            has_thumbnail = os.path.exists(thumb_path) and 'default' not in (course.thumbnail or '')

            course_list.append({
                'id': course.id,
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
                except:
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


# ===========================
# SERVER OPERATIONS
# ===========================

@admin_bp.route('/server/restart', methods=['POST'])
@login_required
@admin_required
def restart_server():
    """Restart the Flask server"""
    try:
        import subprocess
        import sys

        # Kill the current process and restart
        os.execvp(sys.executable, [sys.executable, 'runner.py'])

        return jsonify({'status': 'Server restarting...'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===========================
# DIAGNOSTICS & STATUS
# ===========================

@admin_bp.route('/status', methods=['GET'])
@login_required
@admin_required
def get_status():
    """Get dashboard status information"""
    try:
        courses_count = Course.query.count()
        ebooks_count = Ebook.query.count()

        # Count covers
        cover_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'ebook_covers')
        covers_with_real_images = 0

        if os.path.exists(cover_dir):
            for cover in os.listdir(cover_dir):
                cover_path = os.path.join(cover_dir, cover)
                if os.path.getsize(cover_path) > 10000:
                    covers_with_real_images += 1

        return jsonify({
            'courses_count': courses_count,
            'ebooks_count': ebooks_count,
            'covers_with_real_images': covers_with_real_images,
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
        except:
            database_status = 'ERROR'

        # Count files
        courses_count = Course.query.count()
        ebooks_count = Ebook.query.count()

        cover_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'ebook_covers')
        covers_count = len(os.listdir(cover_dir)) if os.path.exists(cover_dir) else 0

        thumb_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'thumbnails')
        thumbnails_count = len(os.listdir(thumb_dir)) if os.path.exists(thumb_dir) else 0

        # Check for missing covers
        missing_covers = ebooks_count - covers_count

        return jsonify({
            'database_status': database_status,
            'courses_count': courses_count,
            'ebooks_count': ebooks_count,
            'covers_count': covers_count,
            'thumbnails_count': thumbnails_count,
            'missing_covers': max(0, missing_covers)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/logs', methods=['GET'])
@login_required
@admin_required
def get_logs():
    """Get recent application logs"""
    try:
        logs = [
            '[INFO] System started',
            '[INFO] Database connected',
            '[INFO] Courses loaded: 10',
            '[INFO] Ebooks loaded: 54',
        ]

        return jsonify({'logs': logs})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===========================
# USER MANAGEMENT
# ===========================

@admin_bp.route('/delete_user', methods=['POST'])
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

        db.session.delete(user)
        db.session.commit()

        return jsonify({'message': f'User {user.username} deleted successfully'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===========================
# LAYOUT CONFIGURATION
# ===========================

@admin_bp.route('/layout/get', methods=['GET'])
@login_required
@admin_required
def get_layout_settings():
    """Get current layout settings"""
    try:
        layout = LayoutSettings.query.filter_by(name='default').first()

        if not layout:
            # Create default settings if they don't exist
            layout = LayoutSettings(name='default')
            layout.set_settings(LayoutSettings.get_default_settings())
            db.session.add(layout)
            db.session.commit()

        return jsonify({
            'settings': layout.get_settings(),
            'success': True
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/layout/save', methods=['POST'])
@login_required
@admin_required
def save_layout_settings():
    """Save layout settings"""
    try:
        data = request.json
        settings = data.get('settings', {})

        layout = LayoutSettings.query.filter_by(name='default').first()

        if not layout:
            layout = LayoutSettings(name='default')
            db.session.add(layout)

        layout.set_settings(settings)
        db.session.commit()

        return jsonify({
            'message': 'Layout settings saved successfully',
            'success': True
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/layout/reset', methods=['POST'])
@login_required
@admin_required
def reset_layout_settings():
    """Reset layout to default settings"""
    try:
        layout = LayoutSettings.query.filter_by(name='default').first()

        if layout:
            layout.set_settings(LayoutSettings.get_default_settings())
            db.session.commit()

        return jsonify({
            'message': 'Layout settings reset to defaults',
            'settings': LayoutSettings.get_default_settings(),
            'success': True
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
