# GLEH Deployment Guide

**For setting up GLEH on a new machine (laptop, desktop, etc.)**

This guide explains how to deploy GLEH when you clone from GitHub, since certain files are NOT committed to git for security reasons.

---

## 🔐 Files NOT in Git (Security/Privacy)

These files are excluded via `.gitignore`:
- `.env` - Your personal configuration (passwords, paths)
- `database.db` - Your local SQLite database
- `instance/database.db` - Flask's database instance
- `logs/` - Application logs
- `.venv/` - Python virtual environment
- `__pycache__/` - Python cache files

---

## 📦 Backup Location on Samba

**All deployment files are backed up to:**
```
smb://10.0.10.61/project-data/DEPLOYMENT_BACKUP/
```

This folder contains:
```
DEPLOYMENT_BACKUP/
├── .env                    ← Your configured .env file
├── database.db             ← Your working database with users/data
├── instance/
│   └── database.db         ← Flask instance database
└── README.txt              ← This deployment guide
```

---

## 🚀 Quick Setup on New Machine

### Step 1: Clone from GitHub
```bash
cd "C:\Users\Allie\Desktop\AI Projects"
git clone <your-github-repo-url> Gammons-Landing-Educational-Hub---GLEH
cd Gammons-Landing-Educational-Hub---GLEH
```

### Step 2: Copy Deployment Files from Samba
```powershell
# Copy .env configuration
Copy-Item "\\10.0.10.61\project-data\DEPLOYMENT_BACKUP\.env" -Destination ".env"

# Copy database files
Copy-Item "\\10.0.10.61\project-data\DEPLOYMENT_BACKUP\database.db" -Destination "database.db"
New-Item -ItemType Directory -Force -Path "instance"
Copy-Item "\\10.0.10.61\project-data\DEPLOYMENT_BACKUP\instance\database.db" -Destination "instance\database.db"
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Verify Setup
```bash
python verify_setup.py
```

### Step 5: Start Flask
```bash
python -m flask --app src/app run
```

**Visit:** http://localhost:5000

---

## 🔄 Keeping Deployment Backup Updated

Whenever you make significant changes to `.env` or the database, update the backup:

```powershell
# Update .env backup
Copy-Item ".env" -Destination "\\10.0.10.61\project-data\DEPLOYMENT_BACKUP\.env"

# Update database backups
Copy-Item "database.db" -Destination "\\10.0.10.61\project-data\DEPLOYMENT_BACKUP\database.db"
Copy-Item "instance\database.db" -Destination "\\10.0.10.61\project-data\DEPLOYMENT_BACKUP\instance\database.db"
```

**Or use the automated backup script** (see below)

---

## 🤖 Automated Backup Script

Create `backup_to_samba.ps1`:
```powershell
# Backup GLEH deployment files to Samba
$BACKUP_PATH = "\\10.0.10.61\project-data\DEPLOYMENT_BACKUP"

Write-Host "Backing up deployment files to Samba..." -ForegroundColor Cyan

# Ensure backup directory exists
New-Item -ItemType Directory -Force -Path $BACKUP_PATH | Out-Null
New-Item -ItemType Directory -Force -Path "$BACKUP_PATH\instance" | Out-Null

# Backup .env
Copy-Item ".env" -Destination "$BACKUP_PATH\.env" -Force
Write-Host "[OK] .env backed up" -ForegroundColor Green

# Backup databases
Copy-Item "database.db" -Destination "$BACKUP_PATH\database.db" -Force
Write-Host "[OK] database.db backed up" -ForegroundColor Green

Copy-Item "instance\database.db" -Destination "$BACKUP_PATH\instance\database.db" -Force
Write-Host "[OK] instance/database.db backed up" -ForegroundColor Green

Write-Host "`nBackup complete! Files saved to: $BACKUP_PATH" -ForegroundColor Cyan
```

**Run backup anytime:**
```powershell
.\backup_to_samba.ps1
```

---

## 📝 What Gets Committed to Git

**These files ARE in version control:**
- All source code (`src/`)
- Templates (`templates/`)
- Static files (`static/`)
- Configuration templates (`.env.example`)
- Documentation (`README.md`, etc.)
- Tests (`tests/`)
- Docker configuration (`docker/`)

**These files are NOT in version control:**
- Personal configuration (`.env`)
- Databases (`*.db`)
- Logs (`logs/`)
- Virtual environments (`.venv/`)
- Python cache (`__pycache__/`)

---

## 🔒 Security Notes

1. **Never commit `.env` to GitHub** - it contains passwords
2. **Never commit `database.db` to GitHub** - it contains user data
3. **Samba backup is private** - only accessible on your home network
4. **GitHub repo is public/shared** - only contains code, no secrets

---

## 🌐 Network Requirements

- Must be on same network as `10.0.10.61` to access Samba share
- If working remotely, consider VPN to home network
- Samba credentials in `.env` file

---

## 🆘 Troubleshooting

### "Cannot access Samba share"
- Check you're on home network
- Verify server `10.0.10.61` is running
- Test with: `Test-Path "\\10.0.10.61\project-data"`

### "Database tables missing"
- Copy database from Samba backup
- Or run: `python -c "from src.database import db; from src.app import app; app.app_context().push(); db.create_all()"`

### ".env file missing"
- Copy from Samba: `Copy-Item "\\10.0.10.61\project-data\DEPLOYMENT_BACKUP\.env" -Destination ".env"`
- Or copy from `.env.example` and configure manually

---

**Version:** 1.0
**Last Updated:** November 19, 2025
**Author:** Allie (with Claude Code assistance)
