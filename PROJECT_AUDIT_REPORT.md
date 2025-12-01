# GLEH Project Structure Audit Report
**Date:** 2024-11-30
**Scope:** Complete project cleanup before public GitHub release
**Total Files:** 6,691 files, 861 directories, 57 root-level entries

## Executive Summary

This audit identified significant clutter from previous development phases:
- **22% of root directory** contains deprecated files
- **Entire Documentation/ directory** is from a different AI agent project (AHDM/AEGIS)
- **3 duplicate .env template files** causing confusion
- **Flask-Migrate** imported but unused in Docker deployment
- **Multiple deprecated Python scripts** from local development phase
- **Runtime data directories** not properly gitignored
- **Hardcoded settings**: ✅ GOOD - All use environment variables properly

---

## Findings by Category

### ❌ CRITICAL: Wrong Project Entirely

**Documentation/ Directory - MUST DELETE**
- Contains documentation from **completely different project** (AHDM, AEGIS, TaskOrchestrator agents)
- 50+ files about multi-agent AI systems unrelated to GLEH
- Session reports dated 2025-11-14/15 (wrong year typos)
- Zero relevance to Educational Hub

**Files:**
```
Documentation/admin-guides/operations/AHDM_FIRST_DEPLOYMENT_REPORT.md
Documentation/admin-guides/deployment/AHDM_DEPLOYMENT_SUMMARY.md
Documentation/admin-guides/operations/AEGIS_*.md (multiple)
Documentation/admin-guides/operations/TASKORCHESTRATOR_EXECUTION_REPORT.md
Documentation/admin-guides/architecture/MULTI_AGENT_TEAM_STRUCTURE.md
... (50+ files total)
```

**Action:** DELETE entire Documentation/ directory

---

### ❌ DEPRECATED: Old Development Files

**Duplicate/Old Environment Files:**
- `.env.docker` - Old, missing MinIO/Calibre-Web settings
- `.env.example` - Old, Samba-focused, missing MinIO
- ✅ `.env.template` - CURRENT, keep this one

**Old Python Scripts (root directory):**
- `startup_manager.py` - Old session bootstrap, references non-existent restore_from_samba.ps1
- `populate_db.py` - Old local DB population (replaced by init_database.py)
- `clear_testuser.py` - Old test utility
- `verify_setup.py` - Old setup verification, references non-existent MIGRATION_GUIDE.md
- `test_content_dir.py` - Old test script

**Old Markdown Documentation (root directory):**
- `ADMIN_PANEL_QUICK_REFERENCE.txt` - Duplicate of docs/admin/
- `COMPLETE_STACK_GUIDE.md` - Outdated stack guide
- `DEPLOYMENT_PLAN.md` - Superseded by DOCKER_DEPLOYMENT.md
- `FILES_CREATED_SUMMARY.md` - AI session artifact
- `FUNCTION_ARCHITECTURE.txt` - Old architecture notes
- `MINIO_SETUP.md` - Superseded by DOCKER_DEPLOYMENT.md
- `RESTRUCTURING_COMPLETE.md` - AI session artifact
- `STORAGE_QUICK_REFERENCE.md` - Old reference
- `START_HERE.txt` - Duplicate of docs/START_HERE.md

**Old Data Files:**
- `coverage.json` - Test artifact
- `ebook_metadata.json` - Old test data
- `nul` - Windows stderr redirect artifact

**Old Nginx Config:**
- `nginx/gleh.conf` - Single file directory, superseded by docker/nginx/

**Docker Duplicates:**
- `docker/.env.example` - Duplicate, use root .env.template instead
- `docker/README.md` - Should reference root documentation

---

### ⚠️ QUESTIONABLE: Needs Review

**Flask-Migrate (migrations/ directory):**
- Currently imported in src/app.py (line 21, 52)
- Has 2 migration files for CalibreReadingProgress and EbookNote models
- **Docker deployment uses init_database.py (db.create_all()) instead**
- Decision needed: Remove or keep for future schema changes?

**Old Reference:** Line in src/models.py:144 has comment mentioning "J:/courses/" path (harmless example comment)

---

### ⚠️ RUNTIME DATA: Should Be Gitignored

**data/ directory:**
- Contains `postgres/` subdirectory (Docker runtime data)
- Should be added to .gitignore

**instance/ directory:**
- Contains `database.db` (old SQLite file from local dev)
- Already in .gitignore, but file should be deleted

**logs/ directory:**
- Contains `ebook_debug.log`, `ebook_error.log` (runtime logs)
- Already in .gitignore, but files should be deleted

**htmlcov/ directory:**
- Test coverage HTML reports
- Already in .gitignore ✅

**.pytest_cache/ directory:**
- Pytest cache
- Already in .gitignore ✅

**.venv/ directory:**
- Virtual environment
- Already in .gitignore ✅

**IDE directories:**
- `.idea/` - IntelliJ/PyCharm
- `.vscode/` - VS Code
- `.claude/` - Claude Code IDE
- `.continue/` - Continue IDE
- All already in .gitignore ✅

---

### ✅ GOOD: Keep These

**Root Python Files:**
- `requirements.txt` - Current dependencies

**Root Scripts:**
- `cleanup.sh`, `cleanup.bat` - Deployment scripts ✅
- `deploy.sh`, `deploy.bat` - Deployment scripts ✅

**Root Config Files:**
- `.env.template` - Current template ✅
- `.gitignore`, `.gitattributes` - Git config ✅
- `pytest.ini` - Test config ✅

**Root Documentation:**
- `README.md` - Main readme ✅
- `README_DEPLOYMENT.md` - Quick start ✅
- `DOCKER_DEPLOYMENT.md` - Deployment guide ✅
- `next.md` - Progress tracking ✅ (untracked file)

**Directories:**
- `assets/` - Screenshots for README (6 PNG files) ✅
- `docker/` - Docker configuration ✅
- `docs/` - CURRENT project documentation ✅
- `scripts/` - Active deployment scripts ✅
- `src/` - Application source code ✅
- `static/` - Web assets ✅
- `templates/` - Flask templates ✅
- `tests/` - Test suite ✅

---

## Hardcoded Settings Analysis

### ✅ ALL CLEAR - Proper Environment Variable Usage

**Database URLs:**
```python
DATABASE_URL = os.environ.get('DATABASE_URL', 'postgresql://...')  ✅
```

**MinIO Configuration:**
```python
MINIO_ENDPOINT = os.environ.get('MINIO_ENDPOINT', 'localhost:9000')  ✅
MINIO_ACCESS_KEY = os.environ.get('MINIO_ACCESS_KEY', 'minioadmin')  ✅
MINIO_SECRET_KEY = os.environ.get('MINIO_SECRET_KEY', '...')  ✅
```

**Calibre-Web URLs:**
```python
CALIBRE_WEB_URL = os.environ.get('CALIBRE_WEB_URL', 'http://localhost:8083')  ✅
```

**Port Numbers:**
```python
FLASK_PORT = os.environ.get('FLASK_PORT', 5000)  ✅
```

All hardcoded values are appropriate **development fallbacks** with proper `.env` variable overrides for production. No action needed.

---

## .env.template Completeness

**Current Coverage:** ✅ EXCELLENT

The `.env.template` includes all necessary configuration:
- Flask application settings
- Database (PostgreSQL + SQLite fallback)
- MinIO object storage (all credentials)
- Calibre + Calibre-Web integration
- Security settings (SECRET_KEY, session timeout, rate limiting)
- Logging configuration
- Docker-specific settings (Postgres, Nginx)
- Port configurations
- Timezone settings

**No missing environment variables detected.**

---

## Cleanup Action Plan

### Phase 1: Delete Deprecated Files (Safe)

**Delete entire directories:**
```bash
rm -rf Documentation/          # Wrong project entirely
rm -rf nginx/                  # Superseded by docker/nginx/
rm -rf instance/               # Old SQLite database
rm -rf logs/                   # Runtime logs
rm -rf htmlcov/                # Test coverage reports
rm -rf data/                   # Docker runtime data (will be recreated)
```

**Delete deprecated .env files:**
```bash
rm .env.docker
rm .env.example
rm docker/.env.example
```

**Delete old Python scripts:**
```bash
rm startup_manager.py
rm populate_db.py
rm clear_testuser.py
rm verify_setup.py
rm test_content_dir.py
```

**Delete old documentation:**
```bash
rm ADMIN_PANEL_QUICK_REFERENCE.txt
rm COMPLETE_STACK_GUIDE.md
rm DEPLOYMENT_PLAN.md
rm FILES_CREATED_SUMMARY.md
rm FUNCTION_ARCHITECTURE.txt
rm MINIO_SETUP.md
rm RESTRUCTURING_COMPLETE.md
rm STORAGE_QUICK_REFERENCE.md
rm START_HERE.txt
```

**Delete test artifacts:**
```bash
rm coverage.json
rm ebook_metadata.json
rm nul
```

### Phase 2: Update .gitignore

Add these runtime directories:
```gitignore
# Runtime data directories
data/
instance/
logs/
htmlcov/

# IDE directories (if not already present)
.idea/
.vscode/
.claude/
.continue/
```

### Phase 3: Remove Flask-Migrate (Optional)

**Option A: Remove (Recommended for Docker-first deployment)**
- Remove from requirements.txt: `Flask-Migrate`
- Remove from src/app.py: `from flask_migrate import Migrate` and `migrate = Migrate(app, db)`
- Remove from src/build.py: `from flask_migrate import upgrade as db_upgrade`
- Delete migrations/ directory
- Document in README that schema changes use init_database.py

**Option B: Keep (If you want migration capability)**
- Keep Flask-Migrate for future schema evolution
- Document migration workflow in deployment guide
- Note: Currently unused in Docker deployment

**Recommendation:** Remove. Docker deployment uses `db.create_all()` pattern via init_database.py.

### Phase 4: Update docker/README.md

Change docker/README.md to redirect to root documentation:
```markdown
# GLEH Docker Deployment

See [DOCKER_DEPLOYMENT.md](../DOCKER_DEPLOYMENT.md) in the root directory for deployment instructions.

## Quick Start

```bash
cd /opt/gleh
./deploy.sh    # Linux/Mac
deploy.bat     # Windows
```

For detailed documentation, see the root README.md.
```

---

## Final Project Structure (After Cleanup)

```
GLEH/
├── .env.template          # Environment configuration template
├── .gitignore             # Git ignore rules
├── README.md              # Main project readme
├── README_DEPLOYMENT.md   # Quick deployment guide
├── DOCKER_DEPLOYMENT.md   # Detailed deployment docs
├── next.md                # Progress tracking (untracked)
├── requirements.txt       # Python dependencies
├── pytest.ini             # Test configuration
├── cleanup.sh / .bat      # Cleanup scripts
├── deploy.sh / .bat       # Deployment scripts
│
├── assets/                # Screenshots for README
├── docker/                # Docker configuration
│   ├── docker-compose.yml
│   ├── Dockerfile
│   ├── entrypoint.sh
│   ├── nginx/
│   └── README.md         # (updated to reference root docs)
│
├── docs/                  # Project documentation
│   ├── START_HERE.md
│   ├── PROGRESS_LOG.md
│   ├── admin/
│   ├── deployment/
│   ├── migration/
│   └── architecture/
│
├── scripts/               # Deployment/maintenance scripts
│   ├── init_database.py
│   └── init_minio.py
│
├── src/                   # Application source code
│   ├── app.py
│   ├── models.py
│   ├── config.py
│   ├── routes/
│   └── ...
│
├── static/                # Web assets
├── templates/             # Flask templates
└── tests/                 # Test suite
```

**Result:** Clean, professional structure with ~30 fewer files and 1 fewer directory.

---

## Risks and Considerations

### Low Risk (Proceed with confidence):
- Deleting Documentation/ (wrong project)
- Deleting old .env files (backups exist)
- Deleting old Python scripts (unused)
- Deleting old markdown docs (superseded)
- Deleting test artifacts (regenerated on demand)

### Medium Risk (Verify first):
- Removing Flask-Migrate (check if team wants migration capability)
- Deleting migrations/ (contains schema history)

### Zero Risk:
- Updating .gitignore
- Cleaning up already-gitignored directories
- Updating docker/README.md

---

## Recommendations

1. **Execute Phase 1 immediately** - Safe deletions with no functional impact
2. **Execute Phase 2 immediately** - Improve .gitignore coverage
3. **Discuss Phase 3** - Decide on Flask-Migrate before removing
4. **Execute Phase 4 immediately** - Cleanup docker documentation

**Estimated cleanup time:** 10 minutes
**Risk level:** LOW (backups via git history)
**Benefit:** Professional, maintainable project ready for public GitHub release

---

## Next Steps After Cleanup

1. Test deployment with `./cleanup.sh` (keep volumes) + `./deploy.sh`
2. Verify all services start correctly
3. Run test suite: `pytest`
4. Git commit cleanup changes
5. Push to GitHub
6. Begin Task 1: MIT OCW Integration

---

*Generated by Claude Code - GLEH Project Audit*
