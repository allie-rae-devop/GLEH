# GLEH Project Index

**Purpose:** Quick lookup table for active project files
**Last Updated:** November 19, 2025
**Workflow:** Bootstrap (Single Session)

---

## Active Files by Purpose

| Purpose | File | Location |
|---------|------|----------|
| **Status** | APPLICATION_STATUS_REPORT.md | Root directory |
| **Progress** | PROGRESS_LOG.md | Root directory |
| **Code** | src/app.py | src/ |
| **Config** | src/config.py | src/ |
| **Deployment** | DEPLOYMENT_GUIDE.md | Root directory |

---

## Quick Reference

### Status & Progress
- **APPLICATION_STATUS_REPORT.md** - Known issues, bugs, fixes needed
- **PROGRESS_LOG.md** - Session history, current phase, what's been done

### Source Code
- **src/app.py** - Main Flask application (3,300+ lines)
- **src/config.py** - Environment-based configuration
- **src/models.py** - Database models
- **src/database.py** - SQLAlchemy initialization
- **src/storage.py** - Unified storage abstraction (local/Samba)

### Deployment & Setup
- **DEPLOYMENT_GUIDE.md** - How to set up on new machines
- **README.md** - Comprehensive project overview
- **requirements.txt** - Python dependencies

### Scripts
- **backup_to_samba.ps1** - Push .env, database to Samba backup
- **restore_from_samba.ps1** - Pull .env, database from Samba backup
- **commit_and_push.ps1** - Backup to Samba + Git commit + Git push
- **startup_manager.py** - Session bootstrap automation

---

## Current Phase Information

**Phase:** 1.6 - Flask Development Testing
**Focus:** Fix ebook reader UX, test course launch, test admin panel
**Next Phase:** 1.7 - Docker Compose testing

For detailed phase information, see **PROGRESS_LOG.md**

---

**Version:** 1.0
**Created:** November 19, 2025
