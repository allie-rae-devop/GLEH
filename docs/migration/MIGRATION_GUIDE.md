# GLEH Migration Guide: Local → Docker Compose & Flexible Storage

## Overview

This guide walks you through the complete migration of GLEH from a local Flask development app to a Docker Compose-based service with flexible, configurable storage (local or Samba).

**What changed:**
- ✅ Unified storage configuration system (local paths via environment variables)
- ✅ Docker Compose setup ready for production
- ✅ VS Code integration with debugging, testing, and build tasks
- ✅ Easy switching between local and Samba storage (no code changes needed!)
- ✅ Structured project layout for team development

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Project Structure](#project-structure)
3. [Configuration System](#configuration-system)
4. [Running Locally](#running-locally)
5. [Docker Deployment](#docker-deployment)
6. [Migration to Laptop](#migration-to-laptop)
7. [Adding Samba Storage](#adding-samba-storage)
8. [VS Code Setup](#vs-code-setup)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### For Current Development (Windows Machine)

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env and set your data paths
# CONTENT_DIR=D:\GLEH Data
# (or use individual LOCAL_COURSES_DIR, LOCAL_EBOOKS_DIR, LOCAL_UPLOADS_DIR)

# 3. Install dependencies
pip install -r app/requirements.txt

# 4. Run Flask locally
flask run

# OR use Docker Compose locally
cd docker
docker-compose up
```

### For Laptop Migration

```bash
# Update .env with laptop paths
# LOCAL_COURSES_DIR=/Users/you/data/courses
# LOCAL_EBOOKS_DIR=/Users/you/data/ebooks
# LOCAL_UPLOADS_DIR=/Users/you/data/uploads

# Then run same commands as above
```

### For Samba Storage (Future)

```bash
# Update .env
# STORAGE_TYPE=samba
# SAMBA_HOST=192.168.1.100
# SAMBA_USERNAME=your_user
# SAMBA_PASSWORD=your_pass
# (and other SAMBA_* variables)

# Run - app automatically mounts and uses Samba!
flask run
# or
docker-compose up
```

---

## Project Structure

```
GLEH/
├── .env                          # ← Configuration (your data paths, secrets)
├── .env.example                  # ← Template (commit this)
├── .gitignore                    # Updated to ignore data/ and .env
│
├── .vscode/                      # VS Code team configuration
│   ├── settings.json            # Editor and tool settings
│   ├── extensions.json          # Recommended extensions
│   ├── launch.json              # Debug configurations
│   └── tasks.json               # Common development tasks
│
├── app/                          # Flask application (unchanged)
│   ├── src/
│   │   ├── app.py
│   │   ├── models.py
│   │   ├── config.py
│   │   ├── storage.py           # ← NEW: Unified storage manager
│   │   ├── build.py
│   │   └── ...
│   ├── static/
│   ├── templates/
│   ├── tests/
│   └── requirements.txt
│
├── docker/                       # Docker configuration
│   ├── docker-compose.yml       # Multi-container setup
│   ├── Dockerfile               # Flask container image
│   ├── entrypoint.sh            # Startup script
│   ├── .env.example             # Docker env template
│   └── nginx/
│       ├── nginx.conf           # Reverse proxy config
│       └── conf.d/              # Additional Nginx configs
│
├── data/                         # ← LOCAL STORAGE (git-ignored)
│   ├── gleh/
│   │   ├── courses/             # Course files
│   │   ├── ebooks/              # EPUB files
│   │   └── uploads/             # Generated covers, avatars, etc
│   └── postgres/                # Database files (if using Docker)
│
├── docs/                         # Documentation (existing)
│   └── ...
│
└── MIGRATION_GUIDE.md           # ← This file
```

---

## Configuration System

### How It Works

The new `StorageManager` class (`app/src/storage.py`) provides a unified interface for all file operations:

```python
from app.src.storage import get_storage

storage = get_storage()
courses_dir = storage.get_courses_dir()    # Returns: D:\GLEH Data\courses
ebooks_dir = storage.get_ebooks_dir()      # Returns: D:\GLEH Data\ebooks
covers_dir = storage.get_covers_subdir()   # Returns: D:\GLEH Data\uploads\ebook_covers
```

**Configuration priority** (highest to lowest):
1. Environment variables (`.env` file)
2. Defaults based on storage type

### Environment Variables

#### Option 1: Simple (CONTENT_DIR)

```env
STORAGE_TYPE=local
CONTENT_DIR=D:\GLEH Data
# App will create:
# - D:\GLEH Data\courses/
# - D:\GLEH Data\ebooks/
# - D:\GLEH Data\uploads/
```

#### Option 2: Individual Paths (recommended)

```env
STORAGE_TYPE=local
LOCAL_COURSES_DIR=D:\GLEH Data\courses
LOCAL_EBOOKS_DIR=D:\GLEH Data\ebooks
LOCAL_UPLOADS_DIR=D:\GLEH Data\uploads
```

#### Option 3: Samba (when ready)

```env
STORAGE_TYPE=samba
SAMBA_HOST=192.168.1.100
SAMBA_USERNAME=your_user
SAMBA_PASSWORD=your_password
SAMBA_DOMAIN=WORKGROUP
SAMBA_SHARE_COURSES=courses
SAMBA_SHARE_EBOOKS=ebooks
SAMBA_SHARE_UPLOADS=uploads
SAMBA_MOUNT_BASE=/mnt/samba  # Linux/Docker only
```

### Why This Matters

**No code changes needed!** The app automatically detects:
- If using local or Samba storage
- Available storage paths
- And handles all operations transparently

---

## Running Locally

### Prerequisites

- Python 3.11+
- PostgreSQL or SQLite (auto-used in dev)
- Your data in `D:\GLEH Data/` with subdirectories

### Development Setup

```bash
# 1. Clone/navigate to project
cd GLEH

# 2. Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # Mac/Linux

# 3. Copy and configure .env
cp .env.example .env
# Edit .env with your paths

# 4. Install dependencies
pip install -r app/requirements.txt

# 5. Initialize database
flask db upgrade
# or (if migrations not set up yet):
flask shell
>>> from app.src.database import db
>>> db.create_all()
>>> exit()

# 6. Optional: Scan and populate content
python app/src/build.py

# 7. Run development server
flask run
# Available at: http://localhost:5000
```

### Using VS Code Tasks

Press `Ctrl+Shift+D` and select:
- **Flask: Run Development Server** - Starts the app
- **Flask: Database Upgrade** - Runs migrations
- **Build: Scan & Populate Database** - Imports courses/ebooks
- **Test: Run All Tests** - Runs test suite

---

## Docker Deployment

### Prerequisites

- Docker & Docker Compose installed
- `D:\GLEH Data/` directory with content (or mapped volume)

### Local Development with Docker

```bash
# 1. Navigate to docker directory
cd docker

# 2. Copy and configure environment
cp .env.example .env
# Edit .env:
# - CONTENT_DIR=../data/gleh (relative to docker-compose.yml)
# - DATABASE settings (or use defaults)

# 3. Create data directories (Windows)
mkdir ..\data\gleh\courses
mkdir ..\data\gleh\ebooks
mkdir ..\data\gleh\uploads
mkdir ..\data\postgres

# 3b. Create data directories (Mac/Linux)
mkdir -p ../data/gleh/{courses,ebooks,uploads}
mkdir -p ../data/postgres

# 4. Copy existing course/ebook files to data/gleh/
# (or they'll be auto-discovered if already there)

# 5. Start services
docker-compose up

# Available at: http://localhost (or http://localhost:8080)
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web      # Flask app
docker-compose logs -f db       # Database
docker-compose logs -f nginx    # Web server
```

### Stop Services

```bash
docker-compose down            # Stop all
docker-compose down -v         # Stop + remove volumes
```

### Production Deployment

```bash
# Set environment variables before running
export FLASK_ENV=production
export SECRET_KEY=your-strong-random-key
export DATABASE_URL=postgresql://user:pass@your-db:5432/gleh

# Build and run
docker-compose build
docker-compose up -d
```

---

## Migration to Laptop

### Step 1: Transfer Data

**From Windows to Laptop:**

```bash
# Option A: Cloud sync (Dropbox, Google Drive, OneDrive)
# - Sync D:\GLEH Data/ to laptop

# Option B: External drive
# - Copy D:\GLEH Data/ to external USB drive
# - Transfer to laptop

# Option C: Network transfer
# - Use File Sharing or rsync
```

### Step 2: Update Configuration

```bash
# 1. Edit .env file
# Windows:
# LOCAL_COURSES_DIR=D:\GLEH Data\courses
# LOCAL_EBOOKS_DIR=D:\GLEH Data\ebooks
# LOCAL_UPLOADS_DIR=D:\GLEH Data\uploads

# Mac:
# LOCAL_COURSES_DIR=/Users/you/GLEH_Data/courses
# LOCAL_EBOOKS_DIR=/Users/you/GLEH_Data/ebooks
# LOCAL_UPLOADS_DIR=/Users/you/GLEH_Data/uploads

# Linux:
# LOCAL_COURSES_DIR=/home/you/gleh_data/courses
# LOCAL_EBOOKS_DIR=/home/you/gleh_data/ebooks
# LOCAL_UPLOADS_DIR=/home/you/gleh_data/uploads
```

### Step 3: Verify Setup

```bash
# Test local paths work
python -c "from app.src.storage import get_storage; s = get_storage(); print(s.get_storage_info())"

# Should show your paths and "is_ready": true
```

### Step 4: Run

```bash
flask run
# or
docker-compose up
```

---

## Adding Samba Storage

### Prerequisites

- Samba server running and accessible
- Share names: `courses`, `ebooks`, `uploads` (or custom)
- Credentials: username, password, domain (if any)

### For Windows/Mac (Direct Mount)

#### Windows

```powershell
# Create mount points
New-Item -ItemType Directory -Force -Path "D:\Mounts\samba"

# Mount Samba shares
net use D:\Mounts\samba\courses \\server\courses /user:domain\username password /persistent:yes
net use D:\Mounts\samba\ebooks \\server\ebooks /user:domain\username password /persistent:yes

# Update .env
# STORAGE_TYPE=samba
# SAMBA_HOST=192.168.1.100
# SAMBA_USERNAME=your_user
# SAMBA_SHARE_COURSES=courses
# SAMBA_MOUNT_BASE=D:\Mounts\samba
```

#### Mac/Linux

```bash
# Install Samba client
brew install samba  # Mac
sudo apt install cifs-utils  # Ubuntu/Debian

# Create mount points
sudo mkdir -p /mnt/samba/{courses,ebooks,uploads}

# Mount shares (temporary)
sudo mount -t cifs //server/courses /mnt/samba/courses -o user=username,password=password
# Or permanent (add to /etc/fstab):
# //server/courses /mnt/samba/courses cifs user=username,password=password,uid=1000 0 0

# Update .env
# STORAGE_TYPE=samba
# SAMBA_HOST=192.168.1.100
# SAMBA_USERNAME=your_user
# SAMBA_MOUNT_BASE=/mnt/samba
```

### For Docker

```bash
# docker-compose.yml already has commented sections for Samba mounting
# 1. Update .env with SAMBA_* variables
# 2. Uncomment volume sections in docker-compose.yml
# 3. Ensure Samba is mounted on host before starting Docker
# 4. Run: docker-compose up
```

### Verify Samba Connection

```python
from app.src.storage import get_storage

storage = get_storage()
print(storage.get_storage_info())
# Should show:
# - 'type': 'samba'
# - 'is_ready': true
```

---

## VS Code Setup

### Initial Setup

```bash
# 1. Open project in VS Code
code GLEH

# 2. Install recommended extensions
# Press Ctrl+Shift+X, click "Show Recommended Extensions"
# Install all recommended extensions

# 3. Select Python interpreter
# Ctrl+Shift+P > "Python: Select Interpreter"
# Choose: ./venv/Scripts/python.exe
```

### Using Tasks

Press `Ctrl+Shift+B` to see available tasks:

**Development:**
- Flask: Run Development Server
- Flask: Database Upgrade
- Build: Scan & Populate Database

**Testing:**
- Test: Run All Tests
- Test: Run with Coverage Report
- Test: Run Specific Test File

**Code Quality:**
- Lint: Check with Pylint
- Format: Black Code Formatter
- Format: Sort Imports (isort)

**Docker:**
- Docker: Build Images
- Docker: Start Services (Dev)
- Docker: Stop Services
- Docker: View Logs

### Debugging

Press `F5` or `Ctrl+Shift+D` and select:

- **Flask App (Development)** - Debug with breakpoints, watch variables
- **Python: Current File** - Debug active script
- **Run Tests (pytest)** - Debug tests
- **Build: Populate Database** - Debug import script

**Setting breakpoints:**
1. Click in the left gutter next to line numbers
2. A red dot appears
3. Run with `F5`
4. Execution pauses at breakpoint
5. Use Debug Console to inspect variables

---

## Troubleshooting

### Storage Issues

#### "CONTENT_DIR not configured" error

```bash
# Solution: Set environment variables
# Windows PowerShell:
$env:CONTENT_DIR = "D:\GLEH Data"

# Windows Command Prompt:
set CONTENT_DIR=D:\GLEH Data

# Mac/Linux:
export CONTENT_DIR=/path/to/gleh_data
```

#### "Storage path does not exist" warning

```bash
# The app will try to create directories automatically
# If it fails, manually create them:
mkdir -p "D:\GLEH Data\courses"
mkdir -p "D:\GLEH Data\ebooks"
mkdir -p "D:\GLEH Data\uploads"
```

### Docker Issues

#### Container won't start: "Database connection failed"

```bash
# 1. Check if db service is healthy
docker-compose ps

# 2. Check logs
docker-compose logs db

# 3. Wait a bit longer and retry
docker-compose up

# 4. Or use --wait flag (if your Docker version supports it)
docker-compose up --wait
```

#### "Port 80 already in use"

```bash
# Change port in docker/.env
NGINX_PORT=8080

# Or stop conflicting service
# Windows:
netstat -ano | findstr :80
taskkill /PID <pid> /F

# Mac/Linux:
sudo lsof -i :80
kill -9 <pid>
```

#### "Permission denied" mounting volumes

```bash
# Ensure file permissions allow Docker access
# Or run with sudo (not recommended):
sudo docker-compose up

# Better: Fix file permissions on host
chmod -R 755 ../data/
```

### Flask Issues

#### "ModuleNotFoundError: No module named 'app'"

```bash
# Make sure you're in the project root
cd GLEH

# And have activated venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Then install dependencies
pip install -r app/requirements.txt
```

#### Database migrations failing

```bash
# Check migration status
flask db current
flask db history

# If needed, reset database (⚠️ deletes data!)
rm app/src/database.db
flask db upgrade

# Or with PostgreSQL:
# DROP DATABASE gleh_db; CREATE DATABASE gleh_db;
```

### General Debugging

```bash
# Enable debug mode in .env
DEBUG=true
FLASK_ENV=development
LOG_LEVEL=DEBUG

# Check storage configuration
python -c "from app.src.storage import get_storage; import json; s = get_storage(); print(json.dumps(s.get_storage_info(), indent=2))"

# Run with verbose logging
FLASK_ENV=development python -u app/src/app.py

# Check database
flask shell
>>> from app.src.models import Course, Ebook
>>> print(f"Courses: {Course.query.count()}")
>>> print(f"Ebooks: {Ebook.query.count()}")
```

---

## Next Steps

### Immediate (Before Laptop Migration)

- [ ] Test local development with new storage config
- [ ] Verify Docker Compose setup works
- [ ] Run full test suite: `pytest app/tests -v`

### For Laptop Migration

- [ ] Decide on data transfer method (cloud, USB, rsync)
- [ ] Set up Samba if using network storage
- [ ] Update `.env` with laptop paths
- [ ] Verify storage with `python storage.py` test script

### For Production

- [ ] Set `FLASK_ENV=production`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure PostgreSQL database
- [ ] Set up SSL/TLS for HTTPS
- [ ] Configure Nginx properly
- [ ] Set up monitoring/logging

---

## Support & Questions

For issues or questions:

1. Check the **Troubleshooting** section above
2. Review **VS Code Debug** section for debugging
3. Check logs: `docker-compose logs -f`
4. Run health check: Visit `http://localhost/health`

---

## Summary of Key Changes

| What | Before | After |
|------|--------|-------|
| **Data Paths** | Hardcoded in code | Configurable via `.env` |
| **Storage Type** | Local only | Local or Samba (auto-detected) |
| **Deployment** | Flask dev server only | Docker Compose + production-ready |
| **IDE Support** | Minimal | Full VS Code integration |
| **Migration** | Manual code updates | Environment variables only |
| **Team Development** | Inconsistent setup | Standardized with `.vscode/` |

---

**Version:** 1.0
**Last Updated:** 2024-11-17
**Author:** GLEH Development Team
