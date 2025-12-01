 GLEH Project Status Report - Pre-1.0 Release

Report Date: 2025-11-30

Current Version: 0.9 (Pre-release)

Target: 1.0 Public Release

Executive Summary

Phase 1 (Calibre-Web Integration): ✅ COMPLETE

Ebook management via Calibre-Web OPDS API

Reading progress tracking

Note-taking functionality

Profile page working

Phase 2 (MIT OCW Courses + 1.0 Prep): 🚧 IN PROGRESS

MIT OCW course integration needed

File hosting solution CRITICAL BLOCKER

Portfolio about page needed

Admin panel testing required

Docker deployment preparation

Remaining for 1.0: 5 major tasks + beta testing

Current System Architecture

Tech Stack

Backend: Flask 3.x (Python), SQLAlchemy ORM, Flask-Login

Database: SQLite (dev), PostgreSQL (Docker prod)

Ebook Management: Calibre-Web at http://10.0.10.75:8083 (Docker)

File Storage: Currently J:\ Samba share (\10.0.10.61\project-data)

Deployment: Docker Compose with nginx reverse proxy (configured, not active)

Data Models (Current)

# User Authentication

User (id, username, password_hash, is_admin, email, about, avatar_url, created_at)


# Calibre-Web Ebook Integration (NEW - Phase 1)

EbookNote (id, user_id, ebook_id, content, created_at)

CalibreReadingProgress (id, user_id, ebook_id, status, progress_percent, last_read)


# Legacy Course Models (Needs MIT OCW Update)

Course (id, uid, title, description, thumbnail_url, instructor, institution, created_at)

CourseProgress (id, user_id, course_id, completed, progress_percent, last_accessed)

CourseNote (id, user_id, course_id, content, created_at)


# DEPRECATED (Do not use)

Ebook (removed - replaced by Calibre-Web OPDS)

ReadingProgress (removed - replaced by CalibreReadingProgress)

API Endpoints Active

# Authentication

POST /api/register

POST /api/login

POST /api/logout

GET /api/check_session


# Profile

GET /api/profile

POST /api/profile


# Ebooks (Calibre-Web)

GET /api/textbooks (fetches from OPDS)

GET /textbook/<book_id> (launch page)

POST /api/textbook/note


# Courses (Needs MIT OCW update)

GET /api/courses

GET /course/<uid>

POST /api/course/progress

POST /api/course/note

File Structure

d:/AI Projects/GLEH/

├── src/

│ ├── app.py # Main Flask app

│ ├── models.py # Database models

│ ├── calibre_client.py # Calibre-Web OPDS API client

│ └── config.py

├── templates/ # Jinja2 templates

├── static/ # CSS, JS, images

├── scripts/ # Automation scripts (organized)

├── instance/

│ └── database.db # SQLite database

├── migrations/ # Alembic database migrations

├── .env # Configuration (NOT in git)

└── docker/ # Docker setup (ready, not active)

Phase 1 Complete: Calibre-Web Integration ✅

What Was Accomplished

✅ Removed standalone ebook scanning from build.py

✅ Created Calibre-Web OPDS API client (src/calibre_client.py)

✅ Updated homepage to fetch books dynamically from OPDS feed

✅ Fixed OPDS book ID extraction from XML link elements

✅ Created EbookNote model for textbook notes

✅ Created textbook launch page route and template

✅ Updated homepage to redirect to launch page on book click

✅ Ran database migration for EbookNote model

✅ Fixed profile page bugs (missing imports, old models)

✅ Created CalibreReadingProgress model

✅ Added automatic reading progress tracking on book visits

✅ Updated profile API to show reading progress

✅ Ran migration for CalibreReadingProgress

✅ Organized scripts directory with batch file wrappers

Key Changes Made

src/calibre_client.py - New file

OPDS API client for Calibre-Web integration

Functions: get_all_books(), get_book(book_id), get_book_cover_url(book_id)

Dynamic book fetching (no database import needed)

src/models.py - CalibreReadingProgress model

class CalibreReadingProgress(db.Model):

id = db.Column(db.Integer, primary_key=True)

user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

ebook_id = db.Column(db.String(255), nullable=False) # e.g., 'calibre-4'

status = db.Column(db.String(50), default='in_progress')

progress_percent = db.Column(db.Integer, default=0)

last_read = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

__table_args__ = (db.UniqueConstraint('user_id', 'ebook_id'),)

src/app.py - Key updates

Line 62: Added EbookNote, CalibreReadingProgress to imports

Lines 430-448: Auto-track reading progress on book launch page visits

Lines 761-788: Profile API fetches reading progress with book titles from Calibre-Web

scripts/ - Organized automation scripts

start_flask.bat - Start Flask dev server

kill_flask.bat - Kill Flask processes

backup_to_samba.bat/.ps1 - Backup .env and database to Samba

restore_from_samba.bat/.ps1 - Restore from Samba (for laptop migration)

commit_and_push.bat/.ps1 - Backup→commit→push workflow

README.md - Complete documentation

Test Users

admin / admin123 (is_admin=True)

testuser / test123 (is_admin=False)

Phase 2: What's Left for 1.0 Release

Task 1: MIT OCW Course Integration 🚧 PENDING

Current Status:

Old course scanner exists but has copyright-protected courses

Need to update for MIT OCW courses only

MIT OCW courses are open-licensed (CC BY-NC-SA)

Required Actions:

Update build.py course scanner (Phase 2A)

Remove old course scanning logic

Implement MIT OCW course fetching (likely via MIT OCW API or scraping)

Store course metadata in Course model

Download course materials to file storage location

Add MIT OCW attribution (Phase 2B)

Update templates with MIT OCW acknowledgment

Add "Powered by MIT OpenCourseWare" notices

Include license information (CC BY-NC-SA)

Link to original MIT OCW course pages

Comment out copyright-protected courses

Remove old courses from database (or mark as hidden)

Keep code for private fork (post-1.0)

Ensure only MIT OCW courses show in 1.0 public release

Files to Modify:

build.py - Course scanner

templates/index.html - Homepage (add MIT OCW attribution)

templates/course_detail.html - Course page (add attribution)

Database - Clear old courses, populate with MIT OCW

Estimated Time: 10-20 hours

Task 2: File Hosting Solution 🚨 CRITICAL BLOCKER

Current Problem:

Course files and ebook files currently on local Samba share (J:)

Not accessible to Docker containers or external deployment

1.0 release contingent on solving this

Current File Locations:

J:\courses\ # Course materials (videos, PDFs, etc.)

J:\ebooks\ # Ebooks (but now using Calibre-Web)

J:\uploads\ # User avatars, generated covers

J:\calibre-library # Calibre-Web library

Possible Solutions: Option A: Docker Volume Mounts

# docker/docker-compose.yml

services:

flask:

volumes:

- //10.0.10.61/project-data:/mnt/content:ro # Read-only mount

Pros: Simple, uses existing Samba share

Cons: Requires network access, may have permission issues

Option B: Object Storage (MinIO Docker Container)

services:

minio:

image: minio/minio

volumes:

- minio_data:/data

environment:

MINIO_ROOT_USER: admin

MINIO_ROOT_PASSWORD: password

Pros: Production-ready, S3-compatible, self-hosted

Cons: Requires data migration, additional container

Option C: Nginx Static File Server

services:

nginx:

volumes:

- //10.0.10.61/project-data/courses:/usr/share/nginx/html/courses:ro

Pros: Simple, efficient for static files

Cons: Still requires network mount

DECISION NEEDED: Which approach for 1.0? Required Actions:

Choose file hosting solution

Update .env configuration for new file paths

Update docker/docker-compose.yml with volume mounts

Test file access from Docker containers

Migrate existing files if needed

Update src/config.py for Docker file paths

Estimated Time: 4-12 hours

Task 3: Admin Account & Panel Testing 🧪 PENDING

Current Status:

Admin user exists (admin/admin123, is_admin=True)

Unknown what admin functionality exists

Need to verify admin panel works

Required Testing:

Admin Login

Verify admin user can log in

Check that is_admin flag is recognized

Admin Panel Functionality (Unknown if exists)

User management (view, edit, delete users)

Course management (add, edit, delete courses)

Content moderation (manage notes)

System settings

Admin Routes (Check if these exist)

/admin - Admin dashboard?

/admin/users - User management?

/admin/courses - Course management?

Action Items:

Search codebase for admin-specific routes

Test admin account in browser

Implement missing admin functionality if needed

Document admin panel features

Files to Check:

src/app.py - Search for @login_required and is_admin checks

templates/ - Search for admin templates

Estimated Time: 4-8 hours

Task 4: Portfolio About Page & First-Visit Modal 📄 PENDING

Purpose:

Professional portfolio presentation for employers

Explain project context, motivation, and technical approach

First impression for visitors to your public deployment

Current Status: Not implemented Required Components:

1. About Page Route & Template

Create new page at /about with portfolio content: Content Sections:

What is GLEH? - Project overview

Why I Built This - Motivation and use case

How I Built This - Technical stack and architecture

Flask/Python backend

SQLAlchemy ORM

Calibre-Web integration

MIT OCW course integration

Docker deployment

Nginx reverse proxy

Technologies Used - Full tech stack list

Challenges & Solutions - Development journey

Future Plans - Roadmap items

Contact/Portfolio Links - GitHub, LinkedIn, etc.

Files to Create:

templates/about.html - About page template

templates/about_content.html - Reusable content component

static/css/about.css - Custom styling (optional)

Route to Add (in app.py):

@app.route('/about')

def about():

return render_template('about.html')

2. First-Visit Modal System

Behavior Requirements: Testing Mode (Development):

Modal shows on EVERY page load for easy testing

OR shows only if URL parameter ?force_modal=1 is present

Controlled by environment variable: ABOUT_MODAL_MODE=always or testing

Production Mode (Deployment):

Modal shows ONCE per unique visitor

Never shows again after closing

Uses visitor tracking (cookie + localStorage)

Tracking Method (Cookie-based - Most Reliable):

Primary: HTTP Cookie

Set cookie: gleh_visited=true (expires in 1 year)

Secure, HttpOnly flags in production

Domain-wide cookie

Fallback: localStorage

JavaScript: localStorage.setItem('gleh_about_shown', 'true')

Persists across sessions

Per-browser storage

No IP/MAC tracking - Privacy concerns, unreliable

Environment Configuration (.env):

# About Modal Behavior

# Options: 'once' (production), 'always' (testing), 'never' (disabled)

ABOUT_MODAL_MODE=once

3. Implementation Details

Backend Route (app.py):

@app.route('/api/mark_about_seen', methods=['POST'])

def mark_about_seen():

"""Set cookie to mark About modal as seen"""

response = jsonify({'success': True})

# Set cookie for 1 year

response.set_cookie(

'gleh_visited',

'true',

max_age=31536000, # 1 year in seconds

secure=True if app.config['ENV'] == 'production' else False,

httponly=True,

samesite='Lax'

)

return response


@app.route('/')

def index():

# Check if user has seen the about modal

has_visited = request.cookies.get('gleh_visited')

modal_mode = os.getenv('ABOUT_MODAL_MODE', 'once')

# Force show in testing mode

force_modal = request.args.get('force_modal') == '1'

show_modal = (

force_modal or

modal_mode == 'always' or

(modal_mode == 'once' and not has_visited)

)

return render_template('index.html', show_about_modal=show_modal)

Frontend JavaScript (static/js/about_modal.js - NEW FILE):

// About Modal - First Visit Logic

document.addEventListener('DOMContentLoaded', () => {

const modalMode = '{{ config.ABOUT_MODAL_MODE }}'; // From backend

const showModal = {{ show_about_modal|tojson }}; // From backend

// Check localStorage as fallback

const hasSeenModal = localStorage.getItem('gleh_about_shown') === 'true';

// Show modal if backend says to and localStorage hasn't blocked it

if (showModal && !hasSeenModal) {

const aboutModal = new bootstrap.Modal(document.getElementById('aboutModal'));

aboutModal.show();

}

// When modal is closed, mark as seen

const aboutModalElement = document.getElementById('aboutModal');

if (aboutModalElement) {

aboutModalElement.addEventListener('hidden.bs.modal', async () => {

// Set localStorage

localStorage.setItem('gleh_about_shown', 'true');

// Set cookie via API

try {

await fetch('/api/mark_about_seen', { method: 'POST' });

} catch (error) {

console.error('Failed to mark about as seen:', error);

}

});

}

});

Modal Template (in templates/index.html or base.html):

<!-- About Modal - First Visit Pop-up -->

<div class="modal fade" id="aboutModal" tabindex="-1" aria-labelledby="aboutModalLabel" aria-hidden="true" data-bs-backdrop="static">

<div class="modal-dialog modal-lg modal-dialog-centered modal-dialog-scrollable">

<div class="modal-content">

<div class="modal-header bg-primary text-white">

<h5 class="modal-title" id="aboutModalLabel">Welcome to GLEH</h5>

<button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>

</div>

<div class="modal-body">

<!-- Include about content here or via include -->

{% include 'about_content.html' %}

</div>

<div class="modal-footer">

<a href="/about" class="btn btn-outline-primary me-auto">Read Full About Page</a>

<button type="button" class="btn btn-primary" data-bs-dismiss="modal">Get Started</button>

</div>

</div>

</div>

</div>

About Content Template (templates/about_content.html - NEW FILE):

<!-- Reusable about content for modal and /about page -->

<div class="about-content">

<h2>About GLEH</h2>

<p>Gammons Landing Educational Hub is a personal learning platform...</p>

<h3>Why I Built This</h3>

<p>As a developer and lifelong learner...</p>

<h3>How I Built This</h3>

<ul>

<li><strong>Backend:</strong> Python Flask 3.x, SQLAlchemy ORM</li>

<li><strong>Frontend:</strong> Bootstrap 5, vanilla JavaScript</li>

<li><strong>Ebook Management:</strong> Calibre-Web OPDS integration</li>

<li><strong>Course Content:</strong> MIT OpenCourseWare</li>

<li><strong>Deployment:</strong> Docker Compose, nginx, PostgreSQL</li>

</ul>

<h3>Technologies Used</h3>

<div class="row">

<div class="col-md-6">

<h5>Backend</h5>

<ul>

<li>Python 3.x</li>

<li>Flask 3.x</li>

<li>SQLAlchemy</li>

<li>Flask-Login</li>

<li>Flask-Migrate</li>

</ul>

</div>

<div class="col-md-6">

<h5>Frontend</h5>

<ul>

<li>Bootstrap 5</li>

<li>JavaScript ES6+</li>

<li>HTML5/CSS3</li>

</ul>

</div>

</div>

<h3>Contact</h3>

<p>

<a href="https://github.com/yourusername" target="_blank">GitHub</a> |

<a href="https://linkedin.com/in/yourprofile" target="_blank">LinkedIn</a>

</p>

</div>

Navbar Link (in templates/base.html or navigation):

<li class="nav-item">

<a class="nav-link" href="/about">About</a>

</li>

4. Testing Strategy

Development Testing (.env):

ABOUT_MODAL_MODE=always # Shows on every page load

Test modal appearance

Test modal styling

Test "Close" button

Test "Read Full About Page" link

Verify content displays correctly

Pre-Production Testing (.env):

ABOUT_MODAL_MODE=once # Shows once per visitor

Clear browser cookies and localStorage

Visit site → modal should show

Close modal

Refresh page → modal should NOT show

Clear cookies → visit site → modal should show again

Force Show for Testing:

http://localhost:5000/?force_modal=1

Shows modal even if already seen

Useful for testing changes to modal content

Production Mode (.env):

ABOUT_MODAL_MODE=once # Default for production

5. Action Items

Files to Create:

templates/about.html - Full about page

templates/about_content.html - Reusable content (for modal and page)

static/js/about_modal.js - Modal logic

static/css/about.css - Optional custom styling

Files to Modify:

src/app.py - Add routes for /about and /api/mark_about_seen

templates/base.html - Add modal markup and navbar link

templates/index.html - Include modal JavaScript

.env - Add ABOUT_MODAL_MODE configuration

src/config.py - Add config variable for modal mode

Testing Checklist:

Modal shows on first visit (testing mode)

Modal shows only once (production mode)

Cookie persists across sessions

localStorage persists across sessions

"Get Started" button closes modal

"Read Full About Page" link works

Navbar "About" link works

Modal is mobile-responsive

Content is professional and portfolio-ready

Force modal parameter works (?force_modal=1)

6. Content Writing

Portfolio Content Guidelines:

Professional Tone - Employer-facing

Technical Detail - Show your skills

Problem-Solving - Highlight challenges overcome

Clear Structure - Easy to scan

Call to Action - Link to GitHub, resume, contact

Example Structure:

Introduction

├─ What is GLEH?

├─ Live Demo Link

└─ Project Status (v1.0)


Motivation

├─ Why I built this

├─ Problem being solved

└─ Target audience


Technical Implementation

├─ Architecture Overview

├─ Technology Stack

├─ Key Features

│ ├─ Calibre-Web Integration

│ ├─ MIT OCW Courses

│ ├─ User Authentication

│ └─ Progress Tracking

└─ Deployment Strategy


Development Journey

├─ Challenges Faced

├─ Solutions Implemented

└─ Lessons Learned


Future Roadmap

├─ Planned Features

└─ Scaling Considerations


About the Developer

├─ Contact Information

├─ Portfolio Links

└─ Resume/CV Link

Estimated Time: 7-13 hours

Task 5: Docker Deployment Preparation 🐳 PENDING

Current Status:

Docker Compose setup exists in docker/ directory

Never been tested or deployed

Ready to move from Flask dev to production

Docker Setup Files:

docker/

├── docker-compose.yml # Multi-container orchestration

├── Dockerfile # Flask app container

├── entrypoint.sh # Container startup script

├── nginx/

│ └── nginx.conf # Reverse proxy config

├── .env.example # Docker environment template

└── README.md # Docker documentation

Required Actions:

Resolve File Hosting (Task 2 prerequisite)

Docker won't work without file access solution

Update Docker Configuration

Copy .env to docker/.env and adjust paths

Update DATABASE_URL for PostgreSQL

Update CONTENT_DIR for Docker volume mounts

Update CALIBRE_WEB_URL if needed

Test Docker Build

cd docker

docker-compose build

Test Docker Deployment

docker-compose up

Debug Issues

Database connection

File access

Calibre-Web connectivity

Nginx reverse proxy

Static file serving

Verify Functionality

Login works

Books load from Calibre-Web

Courses display (after MIT OCW integration)

File uploads work

Profile works

Environment Variables for Docker:

# docker/.env

FLASK_ENV=production

DATABASE_URL=postgresql://gleh_user:gleh_password@postgres:5432/gleh_db

CONTENT_DIR=/mnt/content # Or S3/MinIO path

CALIBRE_WEB_URL=http://10.0.10.75:8083

SECRET_KEY=<strong-random-key>

Estimated Time: 4-8 hours

Beta Testing Phase 🧪

Prerequisites:

✅ MIT OCW courses integrated

✅ File hostin 