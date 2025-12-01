from .database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

class User(UserMixin, db.Model):
    """
    Represents a user in the system.
    Includes authentication fields and methods required by Flask-Login.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256))  # Increased for modern scrypt hashes
    is_admin = db.Column(db.Boolean, default=False, nullable=False)

    # Profile fields
    avatar = db.Column(db.String(512), default='default_avatar.png')
    about_me = db.Column(db.Text, default='')
    gender = db.Column(db.String(32), default='')  # male, female, non-binary
    pronouns = db.Column(db.String(32), default='')  # he/him, she/her, they/them, custom
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        """Hashes the provided password and stores it."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

class Course(db.Model):
    """
    Represents a single educational course.
    """
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(255), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(512))
    description = db.Column(db.Text)
    # Categories stored as a comma-separated string
    categories = db.Column(db.String(512))
    thumbnail = db.Column(db.String(512))

    @property
    def launch_url(self):
        """Convert absolute file path to web-accessible URL"""
        if not self.path:
            return None
        # Extract the relative path after 'courses/' from the absolute path
        # Example: J:/courses/CourseName/package/index.html -> CourseName/package/index.html
        import re
        # Match the path after 'courses/' (case insensitive for Windows)
        match = re.search(r'[/\\]courses[/\\](.+)', self.path, re.IGNORECASE)
        if match:
            relative_path = match.group(1).replace('\\', '/')
            return f'/courses/{relative_path}'
        return self.path

    def __repr__(self):
        return f'<Course {self.title}>'

class Ebook(db.Model):
    """
    Represents a single e-book/textbook.
    """
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(255), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(512))
    cover_path = db.Column(db.String(512))
    categories = db.Column(db.String(512))

    def __repr__(self):
        return f'<Ebook {self.title}>'

class CourseProgress(db.Model):
    """
    Tracks a user's progress for a specific course.
    This is a many-to-many association table between User and Course.
    """
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String(64), default='Not Started', nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    # Relationships for eager-loading to prevent N+1 queries
    course = db.relationship('Course', lazy='joined')

    # Ensure a user can only have one progress entry per course
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='_user_course_uc'),)

    def __repr__(self):
        return f'<CourseProgress User:{self.user_id} Course:{self.course_id} Status:{self.status}>'

class CourseNote(db.Model):
    """
    Stores a user's personal notes for a specific course.
    """
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    # Relationships for eager-loading to prevent N+1 queries
    course = db.relationship('Course', lazy='joined')

    # Ensure a user can only have one note entry per course
    __table_args__ = (db.UniqueConstraint('user_id', 'course_id', name='_user_course_note_uc'),)

    def __repr__(self):
        return f'<CourseNote User:{self.user_id} Course:{self.course_id}>'

class ReadingProgress(db.Model):
    """
    Tracks a user's reading progress for ebooks.
    Stores current location (CFI for EPUB, page number for PDF).
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ebook_id = db.Column(db.Integer, db.ForeignKey('ebook.id'), nullable=False)
    current_location = db.Column(db.String(512))  # CFI for EPUB or page# for PDF
    progress_percent = db.Column(db.Integer, default=0)  # 0-100
    last_read = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships for eager-loading to prevent N+1 queries
    ebook = db.relationship('Ebook', lazy='joined')

    # Ensure a user can only have one progress entry per ebook
    __table_args__ = (db.UniqueConstraint('user_id', 'ebook_id', name='_user_ebook_uc'),)

    def __repr__(self):
        return f'<ReadingProgress User:{self.user_id} Ebook:{self.ebook_id} {self.progress_percent}%>'

class EbookNote(db.Model):
    """
    Stores a user's personal notes for a specific ebook.
    Note: ebook_id is a string like 'calibre-4' since books come from Calibre-Web, not local database.
    """
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ebook_id = db.Column(db.String(255), nullable=False)  # e.g., 'calibre-4'

    # Ensure a user can only have one note entry per ebook
    __table_args__ = (db.UniqueConstraint('user_id', 'ebook_id', name='_user_ebook_note_uc'),)

    def __repr__(self):
        return f'<EbookNote User:{self.user_id} Ebook:{self.ebook_id}>'

class CalibreReadingProgress(db.Model):
    """
    Tracks a user's reading progress for Calibre-Web ebooks.
    Stores status (in_progress, completed) and last read timestamp.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    ebook_id = db.Column(db.String(255), nullable=False)  # e.g., 'calibre-4'
    status = db.Column(db.String(50), default='in_progress')  # 'in_progress' or 'completed'
    progress_percent = db.Column(db.Integer, default=0)  # 0-100 (optional, for future use)
    last_read = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Ensure a user can only have one progress entry per ebook
    __table_args__ = (db.UniqueConstraint('user_id', 'ebook_id', name='_user_calibre_ebook_uc'),)

    def __repr__(self):
        return f'<CalibreReadingProgress User:{self.user_id} Ebook:{self.ebook_id} Status:{self.status}>'

class LayoutSettings(db.Model):
    """
    Stores customizable layout settings for the homepage featured sections.
    Allows admin to configure card sizes, table widths, spacing, etc.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), default='default', unique=True)
    settings = db.Column(db.Text)  # JSON string
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_settings(self):
        """Parse and return the JSON settings dictionary"""
        if self.settings:
            return json.loads(self.settings)
        return self.get_default_settings()

    def set_settings(self, settings_dict):
        """Store settings as JSON string"""
        self.settings = json.dumps(settings_dict)

    @staticmethod
    def get_default_settings():
        """Returns default layout settings"""
        return {
            'featured_courses_width': '100%',
            'featured_courses_max_width': '600px',
            'featured_ebooks_width': '100%',
            'featured_ebooks_max_width': '600px',
            'table_row_height': 'auto',
            'table_padding': '12px',
            'course_image_width': '150px',
            'course_title_font_size': '1rem',
            'ebook_image_width': '120px',
            'ebook_image_height': '150px',
            'ebook_title_font_size': '1rem',
            'card_background': 'transparent',
            'card_border': 'none',
            'table_gap': '0.75rem',
        }

    def __repr__(self):
        return f'<LayoutSettings {self.name}>'
