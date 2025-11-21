# Samba Deployment Backup System

**Quick Reference for deploying GLEH on any machine**

---

## 🎯 The Problem

When you clone GLEH from GitHub, you don't get:
- `.env` (has your passwords - NOT in git)
- `database.db` (has your users/data - NOT in git)
- `instance/database.db` (Flask database - NOT in git)

**Solution:** Keep a backup copy on your Samba share!

---

## 📦 Backup Location

**All deployment files backed up to:**
```
\\10.0.10.61\project-data\DEPLOYMENT_BACKUP\
```

---

## 🚀 Quick Deploy on New Machine

```powershell
# 1. Clone from GitHub
git clone <your-repo> Gammons-Landing-Educational-Hub---GLEH
cd Gammons-Landing-Educational-Hub---GLEH

# 2. Copy deployment files from Samba
Copy-Item "\\10.0.10.61\project-data\DEPLOYMENT_BACKUP\.env" -Destination ".env"
Copy-Item "\\10.0.10.61\project-data\DEPLOYMENT_BACKUP\database.db" -Destination "database.db"
New-Item -ItemType Directory -Force -Path "instance"
Copy-Item "\\10.0.10.61\project-data\DEPLOYMENT_BACKUP\instance\database.db" -Destination "instance\database.db"

# 3. Install and run
pip install -r requirements.txt
python -m flask --app src/app run
```

---

## 💾 Update Backup (Automated)

### ✨ Smart Commit & Push (Recommended)
When you're done for the session:

```powershell
# One command does everything:
.\commit_and_push.ps1

# Or with a commit message:
.\commit_and_push.ps1 -CommitMessage "Add new feature"
```

**This automatically:**
1. ✅ Backs up `.env` and databases to Samba
2. ✅ Stages all Git changes
3. ✅ Commits to Git
4. ✅ Pushes to GitHub

**You never have to remember!** Just run the script when you're done working.

### 🔧 Manual Backup (If Needed)
```powershell
# Just backup without Git commit
.\backup_to_samba.ps1
```

---

## 📋 What's in Git vs Samba

### ✅ In Git (public/shared code):
- Source code (`src/`)
- Templates (`templates/`)
- Static files (`static/`)
- Tests (`tests/`)
- Documentation
- `.env.example` (template, no passwords)

### 🔒 On Samba (private/personal):
- `.env` (has your passwords)
- `database.db` (has your users)
- `instance/database.db` (Flask database)

---

## 🏠 Home Network Only

- Samba share only accessible on home network (10.0.10.61)
- If working remotely, use VPN
- Backup script checks network connectivity first

---

**See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions**
