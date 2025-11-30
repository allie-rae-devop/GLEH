# GLEH Scripts Directory

This directory contains automation scripts for development and deployment workflows.

## Flask Development Scripts

### start_flask.bat
Starts the Flask development server.
```batch
scripts\start_flask.bat
```
- Activates virtual environment
- Starts Flask on http://127.0.0.1:5000
- Press Ctrl+C to stop

### kill_flask.bat
Kills all running Flask/Python processes.
```batch
scripts\kill_flask.bat
```
- Useful when Flask doesn't stop cleanly
- Kills all Python processes
- Use before starting a fresh Flask instance

## Samba Backup/Deployment Scripts

These scripts support multi-device workflow by backing up non-git files (database, .env) to your Samba share.

### backup_to_samba.bat / .ps1
Backs up deployment files to Samba share.
```batch
scripts\backup_to_samba.bat
```
**What it backs up:**
- `.env` (your configuration)
- `database.db` (root location - legacy)
- `instance/database.db` (Flask instance database)
- `static/avatars/` (legacy avatar location)

**Backup location:** `\\SAMBA_HOST\SAMBA_SHARE\DEPLOYMENT_BACKUP`
(Reads SAMBA_HOST and SAMBA_SHARE from .env file)

### restore_from_samba.bat / .ps1
Restores deployment files from Samba backup.
```batch
scripts\restore_from_samba.bat
```
**Use when:**
- Setting up GLEH on a new device
- Recovering from backup
- Syncing database between desktop and laptop

**IMPORTANT:** After restoring, update DATABASE_URL in .env to match the new machine's path.

### commit_and_push.bat / .ps1
All-in-one workflow: backup → commit → push.
```batch
scripts\commit_and_push.bat
```
**What it does:**
1. Backs up to Samba (non-git files)
2. Shows git status
3. Prompts for commit message
4. Commits all changes
5. Pushes to GitHub (main branch)

**Usage:**
```batch
# Interactive (will prompt for commit message)
scripts\commit_and_push.bat

# With commit message
scripts\commit_and_push.bat "Your commit message here"
```

## Workflow Examples

### Daily Development Workflow
```batch
# Start working
scripts\start_flask.bat

# ... make changes ...

# Commit and push (backs up to Samba automatically)
scripts\commit_and_push.bat "Add new feature"
```

### Moving to Laptop
```batch
# On Desktop - backup first
scripts\backup_to_samba.bat
scripts\commit_and_push.bat "Latest changes"

# On Laptop - restore
git pull
scripts\restore_from_samba.bat
# Edit .env to update DATABASE_URL path
scripts\start_flask.bat
```

### Troubleshooting Flask

**Flask won't stop:**
```batch
scripts\kill_flask.bat
scripts\start_flask.bat
```

**Multiple Flask instances running:**
```batch
scripts\kill_flask.bat
# Wait 2 seconds
scripts\start_flask.bat
```

## File Types

- **`.bat` files** - Windows batch files (double-click to run)
- **`.ps1` files** - PowerShell scripts (run via .bat wrappers)

All .bat files automatically call their corresponding .ps1 files with proper execution policy.

## Calibre-Web Integration

**Note:** There is NO book import script needed for Calibre-Web!

Books are fetched dynamically from Calibre-Web via OPDS API:
- Add books to Calibre-Web at http://10.0.10.75:8083
- Refresh GLEH homepage - new books appear automatically
- No scan or import process required

The integration is real-time via the OPDS feed.

## Configuration

All scripts read configuration from `.env` file in project root:
- `SAMBA_HOST` - Samba server IP (e.g., 10.0.10.61)
- `SAMBA_SHARE` - Samba share name (e.g., project-data)
- `DATABASE_URL` - SQLite database path
- `CALIBRE_WEB_URL` - Calibre-Web server URL

## Notes

- Always run .bat files from project root or use absolute paths
- PowerShell scripts are cross-platform (Linux/Mac: just run .ps1 directly)
- Backup scripts won't commit sensitive files to git (.env is in .gitignore)
- commit_and_push.ps1 has hardcoded Samba path - could be improved to read from .env
