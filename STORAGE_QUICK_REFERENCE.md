# Storage Configuration - Quick Reference

Simple guide for configuring GLEH's unified storage system.

## TL;DR - Just Want to Run It?

```bash
# 1. Copy .env template
cp .env.example .env

# 2. Edit .env and set your data path:
CONTENT_DIR=D:\GLEH Data

# 3. Done! Run:
flask run
# or
docker-compose up
```

The app will automatically find `D:\GLEH Data/courses`, `D:\GLEH Data/ebooks`, and `D:\GLEH Data/uploads`.

---

## Configuration Options

### Option 1: Simple Path (Recommended for Beginners)

```env
STORAGE_TYPE=local
CONTENT_DIR=D:\GLEH Data
```

**How it works:**
- App looks for:
  - `D:\GLEH Data\courses/`
  - `D:\GLEH Data\ebooks/`
  - `D:\GLEH Data\uploads/`

**When to use:**
- Single data directory with standard subdirectories
- Simple local development
- Don't want to think about individual paths

### Option 2: Individual Paths (for Advanced Users)

```env
STORAGE_TYPE=local
LOCAL_COURSES_DIR=D:\GLEH Data\courses
LOCAL_EBOOKS_DIR=D:\GLEH Data\ebooks
LOCAL_UPLOADS_DIR=D:\GLEH Data\uploads
```

**When to use:**
- Data split across different drives/locations
- Different paths for different content types
- More control

### Option 3: Samba Network Share (for Later)

```env
STORAGE_TYPE=samba
SAMBA_HOST=192.168.1.100
SAMBA_USERNAME=your_user
SAMBA_PASSWORD=your_password
SAMBA_DOMAIN=WORKGROUP
SAMBA_SHARE_COURSES=courses
SAMBA_SHARE_EBOOKS=ebooks
SAMBA_SHARE_UPLOADS=uploads
SAMBA_MOUNT_BASE=/mnt/samba  # Linux/Docker
```

**When to use:**
- Network storage on another machine
- Shared team resources
- Centralized backup

---

## Platform-Specific Examples

### Windows (Your Current Setup)

```env
STORAGE_TYPE=local
CONTENT_DIR=D:\GLEH Data

# Or individual paths:
LOCAL_COURSES_DIR=D:\GLEH Data\courses
LOCAL_EBOOKS_DIR=D:\GLEH Data\ebooks
LOCAL_UPLOADS_DIR=D:\GLEH Data\uploads
```

### Mac

```env
STORAGE_TYPE=local
CONTENT_DIR=/Users/yourname/gleh_data

# Or individual paths:
LOCAL_COURSES_DIR=/Users/yourname/gleh_data/courses
LOCAL_EBOOKS_DIR=/Users/yourname/gleh_data/ebooks
LOCAL_UPLOADS_DIR=/Users/yourname/gleh_data/uploads
```

### Linux

```env
STORAGE_TYPE=local
CONTENT_DIR=/home/yourname/gleh_data

# Or individual paths:
LOCAL_COURSES_DIR=/home/yourname/gleh_data/courses
LOCAL_EBOOKS_DIR=/home/yourname/gleh_data/ebooks
LOCAL_UPLOADS_DIR=/home/yourname/gleh_data/uploads
```

### Docker

```env
# Mount your data to /data/gleh in the container
STORAGE_TYPE=local
CONTENT_DIR=/data/gleh

# docker-compose.yml will mount:
# - ../data/gleh:/data/gleh
```

---

## How the System Works (Under the Hood)

```
Your .env File
    ↓
StorageManager reads STORAGE_TYPE
    ↓
    ├─→ If "local": Use LOCAL_COURSES_DIR, LOCAL_EBOOKS_DIR, LOCAL_UPLOADS_DIR
    │
    └─→ If "samba": Mount and use SAMBA_* paths
    ↓
App gets storage paths
    ↓
Operations (read courses, save covers, etc.)
```

### Example Flow

```python
# In your Flask app:
from app.src.storage import get_storage

storage = get_storage()
courses_dir = storage.get_courses_dir()
# Returns: D:\GLEH Data\courses (from .env CONTENT_DIR)

# App automatically handles all file operations:
for file in os.listdir(courses_dir):
    # Works seamlessly whether storage is local or Samba!
    process_course(file)
```

---

## Common Scenarios

### Scenario 1: Initial Setup (Windows Machine)

```env
# .env file
STORAGE_TYPE=local
CONTENT_DIR=D:\GLEH Data

# File structure:
# D:\GLEH Data\
#   ├─ courses\
#   │   ├─ Course 1\
#   │   ├─ Course 2\
#   │   ...
#   ├─ ebooks\
#   │   ├─ Book1.epub
#   │   ├─ Book2.epub
#   │   ...
#   └─ uploads\
#       └─ (auto-generated covers, avatars)
```

### Scenario 2: Migration to Laptop (Mac)

**Step 1:** Transfer data
```bash
# Copy D:\GLEH Data from Windows to Mac
# Put it at: /Users/yourname/gleh_data
```

**Step 2:** Update .env
```env
# Before (Windows):
# CONTENT_DIR=D:\GLEH Data

# After (Mac):
CONTENT_DIR=/Users/yourname/gleh_data
```

**Step 3:** Run
```bash
flask run
# App automatically finds /Users/yourname/gleh_data/courses, ebooks, uploads
```

### Scenario 3: Team Using Samba (Future)

**Prerequisites:**
- Samba server running at: 192.168.1.100
- Shares available: `courses`, `ebooks`, `uploads`

```env
STORAGE_TYPE=samba
SAMBA_HOST=192.168.1.100
SAMBA_USERNAME=john_doe
SAMBA_PASSWORD=secret123
SAMBA_DOMAIN=OFFICE
SAMBA_SHARE_COURSES=courses
SAMBA_SHARE_EBOOKS=ebooks
SAMBA_SHARE_UPLOADS=uploads
SAMBA_MOUNT_BASE=/mnt/samba
```

**Result:**
- App mounts shares automatically
- All team members see same data
- No need to copy files around
- Centralized backups

---

## Verification

### Check Your Configuration

```python
# Run this in Python or Flask shell:
from app.src.storage import get_storage
import json

storage = get_storage()
info = storage.get_storage_info()
print(json.dumps(info, indent=2))
```

**Output example:**
```json
{
  "type": "local",
  "courses_dir": "D:\\GLEH Data\\courses",
  "ebooks_dir": "D:\\GLEH Data\\ebooks",
  "uploads_dir": "D:\\GLEH Data\\uploads",
  "covers_dir": "D:\\GLEH Data\\uploads\\ebook_covers",
  "avatars_dir": "D:\\GLEH Data\\uploads\\avatars",
  "thumbnails_dir": "D:\\GLEH Data\\uploads\\thumbnails",
  "is_ready": true
}
```

### Troubleshooting

**Problem:** `"is_ready": false`

```bash
# Solution 1: Create missing directories
mkdir -p "D:\GLEH Data\courses"
mkdir -p "D:\GLEH Data\ebooks"
mkdir -p "D:\GLEH Data\uploads"

# Solution 2: Check file permissions
# Ensure Windows user can read/write to D:\GLEH Data

# Solution 3: Verify path in .env
# Check for typos in CONTENT_DIR or LOCAL_*_DIR
```

**Problem:** Can't find courses/ebooks

```bash
# 1. Verify files exist
ls -la D:\GLEH\ Data\courses\

# 2. Check case sensitivity (Linux/Mac)
# Paths are case-sensitive on Linux/Mac but not Windows

# 3. Check CONTENT_DIR in .env
cat .env | grep CONTENT_DIR
```

---

## Migration Checklist

### Before Migrating to Laptop
- [ ] All courses in `D:\GLEH Data\courses\`
- [ ] All ebooks in `D:\GLEH Data\ebooks\`
- [ ] Covers generated in `D:\GLEH Data\uploads\ebook_covers\`
- [ ] Database backed up (or regenerated easily)

### During Migration
- [ ] Transfer data files to laptop
- [ ] Install GLEH on laptop
- [ ] Update `.env` with new paths
- [ ] Verify storage config: `python storage_test.py`
- [ ] Test running locally: `flask run`
- [ ] Test Docker: `docker-compose up`

### Before Adding Samba
- [ ] Samba server configured and tested
- [ ] Shares accessible from your machine
- [ ] Credentials ready
- [ ] Choose SAMBA_MOUNT_BASE path
- [ ] All data copied to Samba shares
- [ ] Update `.env` with SAMBA_* variables
- [ ] Mount manually to test: `net use Z: \\server\courses`
- [ ] Test app with Samba: `STORAGE_TYPE=samba flask run`

---

## Key Concepts

### Storage Type
- **local:** Files on your computer or mounted drive
- **samba:** Files on a network server (SMB/CIFS protocol)

### What Gets Stored Where

| Type | Location | Example |
|------|----------|---------|
| **Courses** | courses_dir | D:\GLEH Data\courses\Python Basics\ |
| **E-books** | ebooks_dir | D:\GLEH Data\ebooks\*.epub |
| **Covers** | uploads_dir/ebook_covers | D:\GLEH Data\uploads\ebook_covers\*.jpg |
| **Avatars** | uploads_dir/avatars | D:\GLEH Data\uploads\avatars\*.jpg |
| **Thumbnails** | uploads_dir/thumbnails | D:\GLEH Data\uploads\thumbnails\*.jpg |

### Automatic Fallbacks
```
✓ CONTENT_DIR set        → Use it
✗ CONTENT_DIR not set    → Check LOCAL_*_DIR
✗ LOCAL_*_DIR not set    → Use defaults (Windows only)
✗ No config at all       → Error (prompt to configure)
```

---

## No Code Changes Needed!

The beauty of this system:

```
Windows Development
├─ CONTENT_DIR=D:\GLEH Data
└─ flask run ✓ Works!

↓ Transfer files to laptop ↓

Mac Development
├─ Update: CONTENT_DIR=/Users/you/gleh_data
└─ flask run ✓ Still works! No code changes!

↓ Add Samba server ↓

Team with Samba
├─ Update: STORAGE_TYPE=samba
├─ Update: SAMBA_* variables
└─ flask run ✓ Still works! No code changes!
```

---

## Need Help?

1. **Not working?** → Check `STORAGE_QUICK_REFERENCE.md` (this file)
2. **Detailed guide?** → See `MIGRATION_GUIDE.md`
3. **Docker-specific?** → See `docker/README.md`
4. **Code level?** → Check `app/src/storage.py`

---

**Version:** 1.0
**Last Updated:** 2024-11-17
