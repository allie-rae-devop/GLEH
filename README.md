# Gammons Landing Educational Hub (GLEH)

## 🛠️ Methodology & Architecture
**Status:** Active Prototype / AI-Assisted Build

This project represents a **"Human-in-the-Loop" AI development workflow**.
* **Role:** As the Solutions Architect, I defined the feature requirements, data structure, and UI flow.
* **Implementation:** I utilized Large Language Models (LLMs) for rapid code generation and syntax handling.
* **Validation:** My focus was on logic verification, debugging integration errors, and code review to ensure the application met the specific constraints of my home lab environment.

*Note: This repository is a working prototype demonstrating rapid tool creation for personal utility.*

---
# GLEH - Gammons Landing Educational Hub

A production-ready Flask-based educational platform for managing courses and e-books (EPUB/PDF) with flexible storage configuration, Docker deployment, and comprehensive admin tools.

**Status:** 🟡 Phase 2 In Progress - Preparing for 1.0 Public Release
**Last Updated:** November 30, 2025
**Version:** 0.9-beta

---

## Changelog

### November 30, 2025 - Phase 1 Complete: Calibre-Web Integration ✅

**Major Milestone:** Transitioned from standalone ebook management to Calibre-Web OPDS API integration

**What Was Accomplished:**
- ✅ Created Calibre-Web OPDS API client ([src/calibre_client.py](src/calibre_client.py))
- ✅ Updated homepage to fetch books dynamically from Calibre-Web (http://10.0.10.75:8083)
- ✅ Replaced static Ebook model with dynamic OPDS feed fetching
- ✅ Created EbookNote model for textbook notes
- ✅ Created CalibreReadingProgress model for reading progress tracking
- ✅ Implemented automatic reading progress tracking on book visits
- ✅ Created textbook launch page with note-taking functionality
- ✅ Updated profile page to show ebook notes and reading progress
- ✅ Fixed profile page bugs (missing imports, old models)
- ✅ Organized scripts directory with batch file wrappers
- ✅ Database migrations completed

**Database Changes:**
- Added: `EbookNote` - User notes for ebooks
- Added: `CalibreReadingProgress` - Reading progress tracking
- Deprecated: `Ebook` - Replaced by Calibre-Web OPDS
- Deprecated: `ReadingProgress` - Replaced by CalibreReadingProgress

**Infrastructure Improvements:**
- Scripts directory organized with .bat wrappers for PowerShell scripts
- Samba backup/restore workflow maintained
- Development workflow streamlined

**Next Phase: 1.0 Public Release Preparation**
Five major tasks remaining:
1. MIT OCW Course Integration (replace copyright-protected courses)
2. File Hosting Solution (Docker volume mounts or MinIO)
3. Admin Panel Testing & Implementation
4. Portfolio About Page & First-Visit Modal
5. Docker Deployment & Beta Testing

**Target:** 1.0 Public Release by December 12-17, 2025

---

### November 19, 2025 - Phase 1.6: Flask Development Testing

**Database Migration:**
- ✅ Migrated database.db from local laptop to Samba network storage (J:\)
- ✅ Seeded database with 36 courses and 54 ebooks
- ✅ Verified Flask can read/write from network storage

**Bug Fixes:**
1. Flask .env loading - Added `load_dotenv()` to src/app.py
2. Cross-drive path validation - Added try/except for Windows path comparison
3. Avatar upload path - Fixed to use `app.static_folder`
4. EPUB metadata errors - Added file existence checks
5. CSRF tokens - Added inline CSRF helpers to JavaScript files

---

## Table of Contents

- [Quick Start](#quick-start)
- [Project Overview](#project-overview)
- [Architecture & Tech Stack](#architecture--tech-stack)
- [Project Structure](#project-structure)
- [Key Features](#key-features)
- [Setup & Configuration](#setup--configuration)
- [Common Commands](#common-commands)
- [Development](#development)
- [Database & Models](#database--models)
- [Known Issues & Fixes](#known-issues--fixes)
- [Admin Panel](#admin-panel)
- [Deployment](#deployment)
- [Testing](#testing)
- [Learning Resources](#learning-resources)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

Get GLEH running in 5 minutes:

### Option A: Local Flask Development (Fastest)

```bash
# 1. Install dependencies
cd app
pip install -r requirements.txt

# 2. Verify setup
python verify_setup.py

# 3. Start Flask development server
flask run

# Visit: http://localhost:5000
```

### Option B: Docker (Production-like)

```bash
# 1. Navigate to docker directory
cd docker

# 2. Start all services (Flask, PostgreSQL, Nginx)
docker-compose up

# Visit: http://localhost (Nginx on port 80)
```

### Option C: Verify Without Running

```bash
python verify_setup.py
```

This checks Python version, dependencies, configuration, storage setup, database, and Docker availability.

---

## Project Overview

### What is GLEH?

An educational platform that lets students:
- Browse and enroll in courses
- Track learning progress with notes and bookmarks
- Read e-books (EPUB/PDF) with persistent reading progress
- Manage personal profiles and learning history

**Use Case:** Similar to Udemy or Coursera, but for self-hosted, offline-capable educational content.

### Current Scope

- ✅ User authentication with roles (student, admin)
- ✅ Course browsing and enrollment
- ✅ E-book library with EPUB.js reader
- ✅ Reading progress tracking (current location in book)
- ✅ Course notes and bookmarks
- ✅ User profiles with avatars
- ✅ Admin panel (being built - see [Admin Panel](#admin-panel) section)
- ✅ Flexible storage (local filesystem, Samba-ready)
- ✅ Docker containerization
- ✅ Structured logging and monitoring
- ⏳ Advanced features (password reset, email verification, 2FA) - coming later

### Project Size

- ~3,300 lines of Flask code
- 50+ API endpoints
- 7 active database models (User, Course, CourseProgress, CourseNote, EbookNote, CalibreReadingProgress, LayoutSettings)
- 2 deprecated models (Ebook, ReadingProgress - replaced by Calibre-Web integration)
- 9 test files with 82 total tests
- 50+ configurable environment variables
- Calibre-Web OPDS integration for dynamic ebook management

---

## Architecture & Tech Stack

### Technology Stack

**Backend:**
- Flask 3.1.2 (Python web framework)
- SQLAlchemy (ORM for database)
- Flask-Login (session/authentication management)
- Flask-WTF (CSRF protection, form validation)
- Waitress (production WSGI server)
- structlog (structured JSON logging)

**Frontend:**
- HTML5, CSS3, JavaScript
- EPUB.js (e-book reader)
- Responsive Bootstrap-based UI

**Database:**
- SQLite (development)
- PostgreSQL (production via Docker)

**DevOps:**
- Docker & Docker Compose (containerization)
- Nginx (reverse proxy, rate limiting, static files)
- python-dotenv (environment configuration)

**Processing:**
- Pillow/PIL (image handling, cover generation)
- ebooklib & beautifulsoup4 (EPUB processing)
- ffmpeg-python (video thumbnail generation)

**Testing & Quality:**
- pytest (test framework)
- pytest-cov (coverage reporting)

### High-Level Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Web Browser                        │
│         (Student/Admin accessing GLEH)               │
└─────────────────────────────────────────────────────┘
                        │ HTTP/HTTPS
                        ▼
┌─────────────────────────────────────────────────────┐
│              Nginx Reverse Proxy                     │
│   - Rate limiting on auth endpoints                 │
│   - Serves static files (CSS, JS, covers)           │
│   - SSL/TLS termination (production)                │
└─────────────────────────────────────────────────────┘
                        │ WSGI
                        ▼
┌─────────────────────────────────────────────────────┐
│         Flask Application Server                    │
│                                                     │
│   ├─ Authentication & Authorization                │
│   │  └─ Session management via Flask-Login         │
│   │                                                 │
│   ├─ Route Handlers                                │
│   │  ├─ /courses → Course browsing & enrollment    │
│   │  ├─ /ebooks → E-book library & reader          │
│   │  ├─ /api/* → JSON API endpoints                │
│   │  └─ /admin → Admin panel (in development)      │
│   │                                                 │
│   ├─ Storage Manager                               │
│   │  └─ Unified interface (local/Samba/cloud)      │
│   │                                                 │
│   └─ Logging                                       │
│      └─ Structured JSON logs with request tracing  │
└─────────────────────────────────────────────────────┘
     │                      │                    │
     ▼                      ▼                    ▼
┌──────────────┐   ┌──────────────┐   ┌──────────────┐
│  SQLAlchemy  │   │   Storage    │   │   Image      │
│     ORM      │   │   Manager    │   │   Processing │
│  (Models)    │   │ (Local/Samba)│   │   (Pillow)   │
└──────────────┘   └──────────────┘   └──────────────┘
     │                      │
     ▼                      ▼
┌──────────────┐   ┌────────────────────┐
│  PostgreSQL  │   │   File Storage     │
│  (Production)│   │  ├─ D:\GLEH Data   │
│   or SQLite  │   │  │  ├─ courses/    │
│ (Development)│   │  │  ├─ ebooks/     │
└──────────────┘   │  │  └─ uploads/    │
                   │ (or Samba share)   │
                   └────────────────────┘
```

### Key Design Decisions

1. **Modular Flask Structure** - Separate files for routes, models, config, storage
2. **Environment-Based Configuration** - All settings via `.env`, no code changes needed
3. **Flexible Storage** - Abstracted storage layer supports local filesystem and will support Samba
4. **Structured Logging** - JSON logs with request IDs for debugging and monitoring
5. **CSRF Protection** - Every form/API change has CSRF token validation
6. **Rate Limiting** - Authentication endpoints limited to prevent brute force

---

## Project Structure

```
GLEH/
│
├── app/                               # Main Flask application
│   ├── src/                           # Source code (core logic)
│   │   ├── app.py                    # Main Flask app (3,300+ lines)
│   │   ├── models.py                 # Database models
│   │   ├── admin_api.py              # Admin endpoints (being expanded)
│   │   ├── storage.py                # Unified storage abstraction
│   │   ├── config.py                 # Configuration (Dev/Prod/Test)
│   │   ├── database.py               # SQLAlchemy initialization
│   │   ├── logging_config.py         # Structured logging setup
│   │   ├── build.py                  # Metadata extraction & processing
│   │   ├── extract_metadata.py       # E-book metadata extraction
│   │   ├── database.db               # SQLite database (development)
│   │   └── __init__.py
│   │
│   ├── static/                        # Static files (CSS, JS, images)
│   │   ├── css/                       # Stylesheets
│   │   ├── js/                        # JavaScript
│   │   ├── images/                    # Default images, icons
│   │   ├── favicon.ico
│   │   ├── robots.txt
│   │   └── 404.html
│   │
│   ├── templates/                     # HTML templates (Jinja2)
│   │   ├── index.html                 # Homepage (featured content)
│   │   ├── course.html                # Course detail page
│   │   ├── reader.html                # E-book reader interface
│   │   ├── admin.html                 # Admin dashboard
│   │   ├── profile.html               # User profile
│   │   └── base.html                  # Base template (layout)
│   │
│   ├── tests/                         # Test suite
│   │   ├── test_app.py                # Core app tests
│   │   ├── test_csrf.py               # CSRF protection tests
│   │   ├── test_rate_limiting.py      # Rate limiting tests
│   │   ├── test_logging_manual.py     # Logging tests
│   │   └── test_image_validation.py   # Image processing tests
│   │
│   ├── requirements.txt               # Python dependencies
│   └── pytest.ini                     # Pytest configuration
│
├── docker/                            # Docker configuration
│   ├── docker-compose.yml             # Multi-container orchestration
│   ├── Dockerfile                     # Flask container image
│   ├── entrypoint.sh                  # Container startup script
│   ├── nginx/
│   │   ├── nginx.conf                 # Nginx reverse proxy config
│   │   └── README.md                  # Docker usage guide
│   └── .env.example                   # Docker env template
│
├── .vscode/                           # VS Code team configuration
│   ├── settings.json                  # Editor settings
│   ├── extensions.json                # Recommended extensions
│   ├── launch.json                    # Debugging profiles
│   └── tasks.json                     # 20+ automated tasks
│
├── Documentation/                     # Documentation directory
│   ├── START_HERE.md                  # Quick start guide
│   ├── STORAGE_QUICK_REFERENCE.md     # Storage configuration
│   ├── MIGRATION_GUIDE.md             # Laptop/Samba migration
│   ├── RESTRUCTURING_COMPLETE.md      # Changes made
│   ├── APPLICATION_STATUS_REPORT.md   # Issues & fixes needed
│   └── ADMIN_PANEL_SPECIFICATION.md   # Admin panel design
│
├── .env                               # Your configuration (local)
├── .env.example                       # Configuration template
├── .gitignore
└── README.md                          # This file
```

### Important Files Explained

| File | Purpose | When to Read |
|------|---------|-------------|
| `.env` | **Your configuration** - paths, database, storage type | Every session - edit if paths change |
| `app/src/app.py` | Main Flask app with all routes and logic | Understanding the codebase |
| `app/src/models.py` | Database schema (User, Course, Ebook, etc) | Database structure |
| `app/src/storage.py` | Unified storage layer (local/Samba ready) | Understanding data persistence |
| `app/src/config.py` | Environment-based configuration | Configuration and environment |
| `docker-compose.yml` | Container orchestration | Using Docker |
| `START_HERE.md` | Quick start and overview | First time setup |
| `APPLICATION_STATUS_REPORT.md` | Issues that need fixing | Understanding what needs work |

---

## Key Features

### For Students

**Course Management:**
- Browse all available courses
- Enroll in courses
- Track completion progress
- Take and save notes within courses
- View learning history

**E-Book Reading:**
- Read EPUB and PDF files in browser
- Track reading position (persistent across sessions)
- Search within e-books
- Adjust font size and display settings
- Bookmark important sections

**Personal Learning:**
- Customize user profile with avatar and bio
- View personal learning statistics
- Access learning history

### For Administrators

**Content Management:**
- Scan and import courses automatically
- Scan and import e-books automatically
- Extract metadata (title, author, ISBN, etc)
- Generate or fetch book covers from multiple sources (Google Books, Open Library, Archive.org)
- Generate video thumbnails from course intros
- Auto-categorize content

**System Management:**
- Server status and control
- View application logs
- Database validation and repair
- Orphan file cleanup
- Import history tracking
- System diagnostics (CPU, memory, disk)

**Library Management:**
- View library statistics by category
- Export library manifest
- Backup and restore database
- Manage individual courses and e-books

### Technical Features

- **Session Management** - User login with remember-me functionality
- **CSRF Protection** - All forms/APIs protected with tokens
- **Rate Limiting** - Auth endpoints protected against brute force
- **Structured Logging** - JSON logs with request IDs for debugging
- **Database Connection Pooling** - Efficient database access
- **Content Security** - Input validation and sanitization
- **Responsive UI** - Works on desktop, tablet, mobile
- **Docker Ready** - Production deployment with containerization
- **Flexible Storage** - Local filesystem or network storage (Samba)

---

## 📸 Project Gallery

### 🏠 Central Hub
*The main dashboard providing quick access to featured content and recent activity.*
![Main Dashboard](assets/main.png)

### 📚 Content Libraries
*Organized grid views for browsing local courses and e-books.*
| Course Library | Textbook Library |
| :---: | :---: |
| ![Course Library](assets/courses.png) | ![Textbook Library](assets/textbook.png) |

### 🎓 Learning Experience
*Distraction-free video player with integrated note-taking and progress tracking.*
![Course Player](assets/course-launch.png)

### ⚙️ Management & Profiles
*User profiles for tracking personal stats, and a robust Admin Panel for server diagnostics.*
| User Profile | Admin Panel |
| :---: | :---: |
| ![User Profile](assets/user-profile.png) | ![Admin Panel](assets/admin-panel.png) |

---

## Setup & Configuration

### Environment Configuration

All configuration is done via `.env` file - no code changes needed!

#### Quick Setup (Windows)

```bash
# Copy the example file
copy .env.example .env

# Edit .env with your paths
# CONTENT_DIR=D:\GLEH Data  (your content location)
# STORAGE_TYPE=local        (local or samba)
```

#### Quick Setup (Mac/Linux)

```bash
cp .env.example .env

# Edit .env with your paths
# CONTENT_DIR=/Users/yourname/gleh_data
# STORAGE_TYPE=local
```

### Configuration Options

See `STORAGE_QUICK_REFERENCE.md` for complete configuration reference. Key variables:

```env
# Storage Configuration
STORAGE_TYPE=local                    # 'local' or 'samba'
CONTENT_DIR=D:\GLEH Data              # Where courses, ebooks, uploads are stored

# Application
FLASK_ENV=development                 # development, production, or testing
SECRET_KEY=your-secret-key-here       # Change this in production!
DATABASE_URL=sqlite:///database.db    # SQLite (dev) or postgresql://... (prod)

# Server
FLASK_HOST=127.0.0.1
FLASK_PORT=5000

# Logging
LOG_LEVEL=INFO                        # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=json                       # json or text

# Samba (if using network storage)
SAMBA_HOST=192.168.1.100
SAMBA_SHARE=shared_folder
SAMBA_USERNAME=your_user
SAMBA_PASSWORD=your_password
```

### Directory Structure GLEH Creates

GLEH automatically creates these folders in your `CONTENT_DIR`:

```
D:\GLEH Data\
├── courses/              # Course packages
│   └── course-name/
│       ├── index.html
│       ├── videos/
│       └── content/
├── ebooks/               # EPUB and PDF files
│   ├── book1.epub
│   └── book2.pdf
└── uploads/              # Generated files
    ├── covers/           # Book covers (real or generated)
    ├── thumbnails/       # Course video thumbnails
    └── avatars/          # User profile pictures
```

---

## Common Commands

### Verification & Setup

```bash
# Check everything is working
python verify_setup.py

# Initialize database (if needed)
cd app
python -c "from src.database import db; from src.app import app; app.app_context().push(); db.create_all()"

# Check storage configuration
python -c "from app.src.storage import get_storage; print(get_storage().get_storage_info())"
```

### Running the Application

```bash
# Development mode (with auto-reload, debug enabled)
cd app
flask run

# Development with custom host/port
flask run --host=0.0.0.0 --port=8000

# Production mode (using Waitress)
cd app
python -c "from waitress import serve; from src.app import app; serve(app, host='0.0.0.0', port=5000)"

# Docker mode
cd docker
docker-compose up

# Docker (background)
docker-compose up -d

# Stop Docker
docker-compose down
```

### Testing & Code Quality

```bash
# Run all tests
pytest app/tests -v

# Run specific test file
pytest app/tests/test_csrf.py -v

# Run with coverage report
pytest app/tests --cov=app/src --cov-report=html

# View coverage report
# Open app/htmlcov/index.html in browser

# Check test results summary
pytest app/tests -q
```

### Database Operations

```bash
# Export database as JSON (for backup)
sqlite3 app/src/database.db ".mode json" "SELECT * FROM user;" > user_backup.json

# Check database integrity
sqlite3 app/src/database.db "PRAGMA integrity_check;"

# View all tables
sqlite3 app/src/database.db ".tables"

# Query users
sqlite3 app/src/database.db "SELECT id, username, email FROM user;"
```

### Content Management

```bash
# Scan and import all e-books
cd app
python -c "from src.extract_metadata import process_all_ebooks; process_all_ebooks()"

# Extract EPUB metadata
python -c "from src.build import extract_epub_metadata; print(extract_epub_metadata('path/to/file.epub'))"

# Generate default cover image
python -c "from src.build import generate_cover_image; generate_cover_image('My Book Title')"

# Search for covers from Google Books
python -c "from src.build import fetch_cover_from_google_books; print(fetch_cover_from_google_books(isbn='9780123456789'))"
```

### Logging & Debugging

```bash
# View recent logs
tail -f app/logs/application.log  (Mac/Linux)
Get-Content app/logs/application.log -Tail 50  (PowerShell)

# Filter logs by level
grep ERROR app/logs/application.log  (Mac/Linux)
Select-String "ERROR" app/logs/application.log  (PowerShell)

# Parse JSON logs
cat app/logs/application.log | python -m json.tool | head -50  (Mac/Linux)
```

### Git & Version Control

```bash
# Check current status
git status

# See recent commits
git log --oneline -10

# View changes to files
git diff

# Stage and commit changes
git add .
git commit -m "Your message"

# Push to GitHub
git push origin main

# See what's different from main
git diff main
```

---

## Development

### Development Workflow

1. **Create a feature branch** (don't commit to main)
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make changes** to the code

3. **Test your changes**
   ```bash
   pytest app/tests -v
   ```

4. **Verify nothing broke**
   ```bash
   python verify_setup.py
   flask run  # Test manually
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Description of what you changed"
   ```

6. **Push and create PR** (or merge if solo)
   ```bash
   git push origin feature/your-feature-name
   ```

### Code Organization

**Where to add code:**

- **New API endpoints** → `app/src/app.py` (look for `@app.route`)
- **Database logic** → `app/src/models.py`
- **Admin operations** → `app/src/admin_api.py`
- **Storage/file operations** → `app/src/storage.py`
- **Logging** → Already integrated via `structlog`
- **HTML templates** → `app/templates/`
- **CSS/JavaScript** → `app/static/`

**Key imports you'll use:**

```python
from flask import Flask, request, jsonify, render_template
from flask_login import login_required, current_user
from app.src.models import User, Course, Ebook, db
from app.src.storage import get_storage
from app.src.logging_config import get_logger

log = get_logger(__name__)
```

### Example: Adding a New Endpoint

```python
# In app/src/app.py

@app.route('/api/my-feature', methods=['GET'])
@login_required
def my_feature():
    """Get my feature data"""
    try:
        # Your logic here
        result = some_operation()
        return jsonify({'data': result}), 200
    except Exception as e:
        log.error("my_feature_error", error=str(e))
        return jsonify({'error': 'Something went wrong'}), 500
```

### Example: Adding a Database Model

```python
# In app/src/models.py

class MyModel(db.Model):
    __tablename__ = 'my_model'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref='my_models')
```

### VS Code Integration

GLEH includes `.vscode/` configuration for the team:

```bash
# Recommended extensions are automatically suggested
# Debugging profiles available (F5 to start)
# 20+ automation tasks available (Ctrl+Shift+P → "Run Task")
```

---

## Database & Models

### Current Database Schema

```
user
├── id (int, primary key)
├── username (string, unique)
├── email (string, unique)
├── password_hash (string)
├── avatar_path (string, optional)
├── about_me (text, optional)
└── created_at (datetime)

course
├── id (int, primary key)
├── uid (string, unique)
├── title (string)
├── description (text)
├── categories (string, comma-separated)
├── intro_video_path (string)
├── thumbnail_path (string, optional)
└── created_at (datetime)

ebook_note
├── id (int, primary key)
├── user_id (int, foreign key)
├── ebook_id (string - e.g., 'calibre-4')
├── content (text)
├── created_at (datetime)
└── updated_at (datetime)

calibre_reading_progress
├── id (int, primary key)
├── user_id (int, foreign key)
├── ebook_id (string - e.g., 'calibre-4')
├── status (string - 'in_progress' or 'completed')
├── progress_percent (int, 0-100)
├── last_read (datetime)
└── unique constraint (user_id, ebook_id)

course_progress
├── id (int, primary key)
├── user_id (int, foreign key)
├── course_id (int, foreign key)
├── progress_percentage (float, 0-100)
├── completed (boolean)
└── last_accessed (datetime)

course_note
├── id (int, primary key)
├── user_id (int, foreign key)
├── course_id (int, foreign key)
├── content (text)
├── created_at (datetime)
└── updated_at (datetime)

layout_settings
├── id (int, primary key)
├── user_id (int, foreign key)
├── font_size (string - small/medium/large)
├── line_height (float)
├── text_alignment (string)
└── background_color (string - light/dark)
```

### Working with the Database

```python
# Add a new user
from app.src.models import User, db
from werkzeug.security import generate_password_hash

user = User(
    username='john',
    email='john@example.com',
    password_hash=generate_password_hash('password123')
)
db.session.add(user)
db.session.commit()

# Query users
users = User.query.all()
user = User.query.filter_by(username='john').first()

# Update user
user = User.query.get(1)
user.about_me = "My bio"
db.session.commit()

# Delete user
user = User.query.get(1)
db.session.delete(user)
db.session.commit()

# Query with relationships
from app.src.models import CourseProgress
progress = CourseProgress.query.filter_by(user_id=1).all()
for p in progress:
    print(f"{p.user.username} - {p.course.title}: {p.progress_percentage}%")
```

---

## Known Issues & Fixes

### Critical Issues (Must Fix Before Production)

#### 1. Hardcoded SECRET_KEY

**Location:** `app/src/config.py` line 49

**Problem:** Production config has hardcoded SECRET_KEY

**Risk:** Session hijacking, CSRF token forgery

**Fix:**
```python
# In app/src/config.py

class ProductionConfig(Config):
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY must be set in environment variables")
```

**Then add to `.env`:**
```env
SECRET_KEY=your-very-long-random-secret-key-here
```

#### 2. SQLite Fallback in Production

**Location:** `app/src/config.py` line 74

**Problem:** Falls back to SQLite if DATABASE_URL not set

**Risk:** Data loss, no concurrency, not scalable

**Fix:**
```python
class ProductionConfig(Config):
    DATABASE_URL = os.environ.get('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL required in production")
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
```

#### 3. API Returns Wrong Content-Type

**Endpoint:** `GET /api/profile`

**Problem:** Returns HTML instead of JSON

**Fix:** Add JSON response for unauthenticated API requests:
```python
@app.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    if not current_user:
        return jsonify({'error': 'Unauthorized'}), 401
    return jsonify({...user_profile...}), 200
```

#### 4. 404 Errors Return 500

**Problem:** Global exception handler catches 404s, logs them as 500 errors

**Fix:**
```python
@app.errorhandler(404)
def handle_not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(Exception)
def handle_exception_logging(e):
    if isinstance(e, HTTPException):
        return jsonify({'error': str(e)}), e.code
    log.error("unhandled_exception", error=str(e))
    return jsonify({'error': 'Internal server error'}), 500
```

### High-Priority Issues (Fix Before Deployment)

#### 5. No XSS Input Sanitization

User-generated content (notes, bio) not sanitized

**Fix:**
```bash
pip install bleach
```

```python
from bleach import clean

# In endpoints that accept user input:
data['about_me'] = clean(data['about_me'], tags=[], strip=True)
data['note'] = clean(data['note'], tags=['b', 'i', 'u'], strip=True)
```

#### 6. Missing Security Headers

**Fix:**
```python
@app.after_request
def set_security_headers(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'"
    return response
```

#### 7. Rate Limiting Spoofable

**Problem:** Uses IP address that can be spoofed via X-Forwarded-For

**Fix:**
```python
# Behind Nginx (production):
ip = request.headers.get('X-Real-IP', request.remote_addr)
```

### Low-Priority Issues (Enhancement)

- No password reset mechanism
- No email verification
- No two-factor authentication
- No audit timestamps (created_at/updated_at)

See `APPLICATION_STATUS_REPORT.md` for detailed analysis.

---

## Admin Panel

### Current Status

The admin panel is **in active development**. It will provide UI for:

**Content Management:**
- Scan and import courses/e-books
- Search and fetch book covers from multiple sources
- Generate placeholder covers
- Generate video thumbnails
- Auto-categorize content

**System Management:**
- Server status and control
- View application logs and diagnostics
- Database validation and repair
- File system checks

**Library Management:**
- View library statistics
- Export manifests
- Backup/restore database

### Admin Endpoints (In Progress)

```
POST /api/admin/scan-ebooks
POST /api/admin/search-covers
POST /api/admin/generate-covers
POST /api/admin/scan-courses
POST /api/admin/generate-thumbnails
POST /api/admin/autocategorize-courses
GET /api/admin/status
POST /api/admin/server/restart
GET /api/admin/diagnostics
POST /api/admin/validate-data
POST /api/admin/cleanup-orphans
GET /api/admin/statistics
```

### Example: Manual E-book Import

Until UI is ready:

```python
cd app
python -c "
from src.extract_metadata import process_all_ebooks
results = process_all_ebooks()
print(f'Found {len(results)} e-books')
for ebook in results:
    print(f'  - {ebook[\"title\"]} by {ebook.get(\"author\", \"Unknown\")}')
"
```

### Example: Manual Course Import

```python
cd app
python -c "
from src.build import main
main()
"
```

See `ADMIN_PANEL_SPECIFICATION.md` for complete planned functionality.

---

## Deployment

### Development Deployment (Flask)

```bash
cd app
python -c "from waitress import serve; from src.app import app; serve(app, host='127.0.0.1', port=5000)"
```

### Production Deployment (Docker)

```bash
cd docker
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f flask

# Stop services
docker-compose down
```

### Docker Services

- **Flask app** - Port 5000 (internal)
- **PostgreSQL** - Port 5432 (internal)
- **Nginx** - Port 80 (external)

### Configuration for Deployment

Edit `.env`:

```env
FLASK_ENV=production
SECRET_KEY=your-very-long-random-key
DATABASE_URL=postgresql://user:password@localhost:5432/gleh
STORAGE_TYPE=local
CONTENT_DIR=/data/gleh_content  # Mounted volume in Docker
```

### SSL/TLS (HTTPS)

In `docker/nginx/nginx.conf`, add SSL certificates:

```nginx
listen 443 ssl;
ssl_certificate /etc/nginx/certs/cert.pem;
ssl_certificate_key /etc/nginx/certs/key.pem;
ssl_protocols TLSv1.2 TLSv1.3;
```

Then map certs volume in `docker-compose.yml`:
```yaml
volumes:
  - ./certs:/etc/nginx/certs
```

---

## Testing

### Test Organization

```
app/tests/
├── test_app.py              # Core app tests (health, routes)
├── test_csrf.py             # CSRF protection (60+ tests)
├── test_rate_limiting.py    # Rate limiting tests
├── test_logging_manual.py   # Logging tests
└── test_image_validation.py # Image processing tests
```

### Running Tests

```bash
# All tests
pytest app/tests -v

# Specific test file
pytest app/tests/test_csrf.py -v

# Specific test function
pytest app/tests/test_csrf.py::test_csrf_token_validation -v

# With coverage
pytest app/tests --cov=app/src --cov-report=html

# Quick summary
pytest app/tests -q
```

### Test Coverage

Current coverage: **82 tests**
- CSRF protection: Excellent (60+ tests)
- Authentication: Good
- Content API: Good
- Error handling: Needs work

### Writing a New Test

```python
# In app/tests/test_something.py

import pytest
from app.src.app import app
from app.src.models import User, db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()

def test_my_feature(client):
    # Arrange
    user = User(username='test', email='test@test.com')
    db.session.add(user)
    db.session.commit()

    # Act
    response = client.get('/api/my-endpoint')

    # Assert
    assert response.status_code == 200
```

---

## Learning Resources

### Understanding the Codebase

1. **Start here:** `START_HERE.md` - Overview and quick start
2. **Architecture:** This README (you're reading it!)
3. **Storage:** `STORAGE_QUICK_REFERENCE.md` - How storage works
4. **Issues:** `APPLICATION_STATUS_REPORT.md` - What needs fixing
5. **Admin Panel:** `ADMIN_PANEL_SPECIFICATION.md` - What's being built
6. **Code:** `app/src/app.py` - Main application logic

### Key Concepts

**Flask Request Lifecycle:**
```
Request → Route Handler → Authentication → Business Logic → Database → Response
  ↓                           ↓                                        ↓
 Middleware           CSRF Token Validation                    JSON/HTML Render
 Logging              Rate Limiting
```

**E-book Reading:**
```
User opens /reader?ebook_id=123
  ↓
fetch_ebook_file() → Load EPUB from storage
  ↓
EPUB.js in browser renders book
  ↓
User scrolls → progress saved to database (reading_progress)
  ↓
Next session → user returns to last position
```

**Course Progress:**
```
User enrolls in course
  ↓
course_progress record created (0%)
  ↓
User watches videos, takes notes
  ↓
course_note records created
  ↓
Admin marks course complete → progress_percentage = 100%
```

### Common Questions

**Q: How do users get courses/e-books?**
A: Admin scans course/ebook directories and imports them via `build.py` and `extract_metadata.py`. Eventually UI will be in admin panel.

**Q: Where are course files stored?**
A: `CONTENT_DIR/courses/` on disk. Path configurable via `.env`.

**Q: Can I move to a different computer?**
A: Yes! Just copy `CONTENT_DIR` and update `.env` with new path. See `MIGRATION_GUIDE.md`.

**Q: How is reading progress saved?**
A: EPUB.js sends position (CFI - EPUB Canonical Fragment Identifier) to `/api/reading-progress`. Stored in database with timestamp.

**Q: Why SQLite in development, PostgreSQL in production?**
A: SQLite is fine for single-user dev. PostgreSQL handles concurrent users, better locking, more reliable.

**Q: How does authentication work?**
A: Flask-Login manages sessions. Password hashed with werkzeug. Login sets session cookie with CSRF token.

---

## Troubleshooting

### "Module not found" Errors

```bash
# Make sure you're in the right directory
cd app

# Make sure dependencies installed
pip install -r requirements.txt

# Verify setup
python verify_setup.py
```

### Database Errors

```bash
# Check if database exists
ls app/src/database.db

# Reinitialize if corrupted
rm app/src/database.db
python -c "from src.app import app; from src.database import db; app.app_context().push(); db.create_all()"
```

### Storage Path Issues

```bash
# Check configured paths
python -c "from app.src.storage import get_storage; print(get_storage().get_storage_info())"

# Verify directories exist
ls -la D:\GLEH\ Data\  # Windows
ls -la /Users/yourname/gleh_data/  # Mac
```

### Port Already in Use

```bash
# Find what's using port 5000
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Kill the process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows

# Or use a different port
flask run --port=5001
```

### Tests Failing

```bash
# Clear pytest cache
rm -rf app/.pytest_cache

# Run with verbose output
pytest app/tests -v -s

# Run one test at a time
pytest app/tests/test_csrf.py::test_specific_test -v
```

### Docker Issues

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs flask
docker-compose logs nginx
docker-compose logs postgres

# Rebuild containers
docker-compose down
docker-compose up --build

# Clean everything (WARNING: loses data)
docker-compose down -v
```

### Import Errors with E-books

```bash
# Check e-books directory
ls D:\GLEH\ Data\ebooks\  # Windows
ls /Users/yourname/gleh_data/ebooks/  # Mac

# Try importing manually
cd app
python -c "from src.extract_metadata import process_all_ebooks; results = process_all_ebooks(); print(results)"
```

---

## Contributing & Git Workflow

### Before You Commit

```bash
# 1. Verify everything works
python verify_setup.py

# 2. Run tests
pytest app/tests -v

# 3. Check what you changed
git diff

# 4. Make sure no secrets are being committed
# (Don't commit .env if it has real passwords!)

# 5. Commit with clear message
git add .
git commit -m "Clear description of what you changed"
```

### Commit Message Guidelines

```
❌ Bad:
git commit -m "fixed stuff"
git commit -m "updates"

✅ Good:
git commit -m "Fix CSRF token validation for API endpoints"
git commit -m "Add security headers to all responses"
git commit -m "Refactor storage layer to support Samba"
```

---

## Next Steps

### Immediate (Today/Tomorrow)
- [ ] Run `python verify_setup.py` to confirm setup
- [ ] Try `flask run` and visit http://localhost:5000
- [ ] Explore the code in `app/src/app.py`
- [ ] Read `APPLICATION_STATUS_REPORT.md` to understand issues

### Short-term (This Week)
- [ ] Fix critical issues from status report
- [ ] Run tests: `pytest app/tests -v`
- [ ] Try Docker: `cd docker && docker-compose up`
- [ ] Set up VS Code debugging

### Medium-term (Next Week)
- [ ] Implement admin panel UI
- [ ] Add missing security features
- [ ] Write documentation for your additions
- [ ] Deploy to test environment

---

## Related Documentation

- **`START_HERE.md`** - Quick start guide and overview
- **`STORAGE_QUICK_REFERENCE.md`** - Storage configuration reference
- **`MIGRATION_GUIDE.md`** - Moving to laptop or Samba storage
- **`APPLICATION_STATUS_REPORT.md`** - Detailed list of issues and fixes needed
- **`ADMIN_PANEL_SPECIFICATION.md`** - Admin panel design and features
- **`RESTRUCTURING_COMPLETE.md`** - What was restructured and why
- **`docker/README.md`** - Docker setup and deployment

---

## Project Statistics

| Metric | Value |
|--------|-------|
| Python Lines of Code | 3,300+ |
| Database Models | 6 |
| API Endpoints | 40+ |
| Test Files | 9 |
| Total Tests | 82 |
| Configuration Options | 50+ |
| Git Commits | 50+ |
| Documentation Files | 10 |

---

## License

See `Documentation/LICENSE.txt` for details.

---

## Questions?

- Check `STORAGE_QUICK_REFERENCE.md` for configuration questions
- Check `APPLICATION_STATUS_REPORT.md` for known issues
- Check `ADMIN_PANEL_SPECIFICATION.md` for planned features
- Read code comments in `app/src/` for implementation details
- Run `python verify_setup.py` to diagnose issues

---

**Version:** 0.9-beta (Phase 2 In Progress)
**Last Updated:** November 30, 2025
**Status:** 🟡 Preparing for 1.0 Public Release
**Next:** MIT OCW Integration → File Hosting → Admin Panel → About Page → Docker → Beta Testing
