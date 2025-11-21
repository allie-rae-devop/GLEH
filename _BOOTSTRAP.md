# GLEH WORKFLOW BOOTSTRAP
**Project:** Gammons Landing Educational Hub (GLEH)
**System:** Flask 3.1.2 / Samba (J:\) / Docker
**Docs:** PROJECT_INDEX.md, APPLICATION_STATUS_REPORT.md, PROGRESS_LOG.md

---

## 🚀 HOW TO USE THIS FILE (FRESH CLAUDE SESSION)

**SIMPLEST METHOD (One Word!):**

1. Open this file (`_BOOTSTRAP.md`) in VS Code
2. Start new Claude Code session
3. Type: **`read`**

That's it! Claude will see this file is open, read it, and execute `/startup` automatically.

**Alternative (if file not open):**
Type: `Read _BOOTSTRAP.md and execute /startup`

**Either way, Claude will:**
1. Read this file to learn the workflow
2. Run the `/startup` command (defined below)
3. Load project context
4. Report "Ready to work"

---

## 🎯 CURRENT FOCUS
**Active Phase:** Phase 1.6 - Flask Development Testing
**Immediate Goal:** Fix eBook Reader UX (Pagination vs Scroll) & Test Course Launch
**Constraints:**
- Do NOT optimize UI (Phase 2) yet
- Watch for `ValueError` on cross-drive paths (Samba J:\ vs Local C:\)
- Ensure `.env` is loaded before accessing `CONTENT_DIR`

---

## ⚡ SESSION COMMANDS

### 🟢 /startup
**Trigger:** Run this command when you open the project.
**Action:**
1.  **Run Manager:** Execute `python startup_manager.py` in the terminal.
    - *Goal:* This checks for the `.env` file. If missing, it triggers the "New Device" protocol (calling `restore_from_samba.ps1`).
2.  **Load Index:** Read `PROJECT_INDEX.md`.
3.  **Selective Read:** Based on the **Immediate Goal** defined above, read *only* the relevant documentation.
    - *Example:* If working on Reader, read `templates/reader.html` and `APPLICATION_STATUS_REPORT.md`.
    - *Always:* Read the last entry of `PROGRESS_LOG.md` to sync memory.
4.  **Report:** "Environment checked. Context loaded for [Goal]. Ready."

### 🔴 /shutdown
**Trigger:** Run this command when ending the session.
**Action:**
1.  **Log Update:**
    - Update `PROGRESS_LOG.md` with tonight's progress.
    - Update `APPLICATION_STATUS_REPORT.md` if bugs were fixed/found.
2.  **Execute Backup:**
    - **Run:** `.\commit_and_push.ps1`
    - *Note:* This script handles the Git commit/push AND backs up the `.env` and databases to the Samba share (`\\10.0.10.61\project-data\DEPLOYMENT_BACKUP`).
3.  **Report:** "Progress logged. Samba backup secure. GitHub synced. Session closed."

---

## 🧠 CONTEXT RULES
1.  **Samba Awareness:**
    - `restore_from_samba.ps1` pulls sensitive data (Down).
    - `commit_and_push.ps1` pushes sensitive data (Up).
    - *Never* commit `.env` or `.db` to Git.
2.  **Device Switching:**
    - If `startup_manager.py` warns of a missing `.env`, assume we are on a new machine.
    - **CRITICAL:** Paths (J:\ vs D:\) may change between devices. Trust the `.env` `CONTENT_DIR` variable over hardcoded assumptions.
3.  **Documentation Authority:**
    - `PROGRESS_LOG.md` is the single source of truth for "Where did we leave off?"
    - Ignore any files referencing "AEGIS" or "AHDM"—these are deprecated.

---

## 📋 SESSION WORKFLOW

### Starting a Session
1. User opens project in VS Code
2. User types: "Run /startup"
3. Claude executes startup_manager.py
4. Claude loads PROJECT_INDEX.md
5. Claude reads relevant docs based on current goal
6. Claude reports: "Ready to work on [Current Goal]"

### During Work
- Focus on **Immediate Goal** only
- Update TODO list as tasks progress
- Test changes incrementally
- Document issues in APPLICATION_STATUS_REPORT.md

### Ending a Session
1. User types: "Run /shutdown"
2. Claude updates PROGRESS_LOG.md with session summary
3. Claude updates APPLICATION_STATUS_REPORT.md if needed
4. Claude runs commit_and_push.ps1
5. Claude reports: "Session closed. Ready for next session."

---

## 🔧 COMMON OPERATIONS

### Device Switch Protocol
**Scenario:** Pulling repo on different computer (laptop ↔ desktop)

**Steps:**
1. `git pull origin master` - Get latest code
2. `python startup_manager.py` - Detects missing .env
3. Script offers to run `restore_from_samba.ps1`
4. Confirm restoration
5. Edit .env DATABASE_URL path for current user
6. `python -m flask --app src/app run` - Start Flask
7. Verify everything works

### Committing Changes
**Quick commit:**
```powershell
.\commit_and_push.ps1
```
This handles: Samba backup → Git add → Git commit → Git push

**Manual commit:**
```bash
git add .
git commit -m "Your message"
git push origin master
.\backup_to_samba.ps1  # Don't forget!
```

### Testing Changes
```bash
# Start Flask
python -m flask --app src/app run

# In browser
http://localhost:5000

# Hard refresh after code changes
Ctrl + Shift + R
```

---

## 📚 KEY FILES REFERENCE

**Session Management:**
- `_BOOTSTRAP.md` - This file (workflow guide)
- `PROJECT_INDEX.md` - File lookup table
- `PROGRESS_LOG.md` - Session history and current phase
- `APPLICATION_STATUS_REPORT.md` - Known issues and bugs

**Scripts:**
- `startup_manager.py` - Session bootstrap automation
- `restore_from_samba.ps1` - Pull config/data from Samba
- `backup_to_samba.ps1` - Push config/data to Samba
- `commit_and_push.ps1` - Backup + Git commit + Push

**Core Application:**
- `src/app.py` - Main Flask application
- `src/config.py` - Environment configuration
- `src/models.py` - Database models
- `templates/` - HTML templates
- `static/` - CSS, JS, images

**Deployment:**
- `.env` - Configuration (NOT in Git)
- `database.db` - SQLite database (NOT in Git)
- `instance/database.db` - Flask instance database (NOT in Git)
- `requirements.txt` - Python dependencies

---

## ⚠️ IMPORTANT REMINDERS

### Security
- ❌ **NEVER** commit `.env` to Git
- ❌ **NEVER** commit `*.db` files to Git
- ✅ **ALWAYS** use Samba backup for sensitive files
- ✅ **ALWAYS** run backup before pushing code

### Device Switching
- Check `startup_manager.py` output carefully
- Update DATABASE_URL in `.env` for current user path
- Verify Samba J:\ drive is accessible
- Hard refresh browser after code changes (Ctrl+Shift+R)

### Development
- Test changes incrementally
- Update PROGRESS_LOG.md regularly
- Mark TODOs as completed immediately
- Document bugs in APPLICATION_STATUS_REPORT.md

---

## 🎓 PHASE INFORMATION

**Current Phase:** 1.6 - Flask Development Testing
**Status:** In Progress
**Goal:** Test all features, fix bugs, prepare for Docker

**Completed:**
- ✅ Phase 1: Initial migration and testing
- ✅ Phase 1.5: Directory restructuring (155GB → 54MB)
- ✅ Phase 1.5.1: Samba integration
- ✅ Phase 1.5.2: Database migration to Samba

**Next Phases:**
- Phase 1.7: Docker Compose test environment
- Phase 1.8: Production deployment to Samba server
- Phase 2: Beautiful templates with Tailwind CSS

**For detailed phase history:** See `PROGRESS_LOG.md`

---

## 📊 SESSION HEALTH

**Token Management:**
- Monitor token usage throughout session
- Around 80% (160K tokens): Pause and summarize
- Around 90% (180K tokens): Stop and start new session
- If session resets: Read PROGRESS_LOG.md to resume

**Session Reset Recovery:**
1. Read `_BOOTSTRAP.md` (this file)
2. Read `PROGRESS_LOG.md` (last entry)
3. Read `PROJECT_INDEX.md` (find relevant files)
4. Resume from last checkpoint
5. Continue work

---

**Version:** 1.0
**Created:** November 19, 2025
**Last Updated:** November 19, 2025
**Status:** Active

---

**Remember:** You're mentoring a learning developer. Explain *why*, not just *how*. Be patient, thorough, and educational.

**Let's build something great.** 🚀
