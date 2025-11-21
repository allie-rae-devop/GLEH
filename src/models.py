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
    password_hash = db.Column(db.String(128))
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
