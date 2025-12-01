@echo off
REM ############################################################################
REM GLEH Project Cleanup Script (Windows)
REM Removes deprecated files and directories identified in PROJECT_AUDIT_REPORT.md
REM Safe to run - only deletes unused/old development artifacts
REM ############################################################################

setlocal enabledelayedexpansion

echo ============================================================
echo   GLEH Project Cleanup
echo   Removing deprecated files and directories
echo ============================================================
echo.

echo This script will delete:
echo   - Documentation\ directory (wrong project)
echo   - Old .env files (.env.docker, .env.example)
echo   - Deprecated Python scripts (5 files)
echo   - Old documentation files (9 .md files)
echo   - Test artifacts (coverage.json, etc.)
echo   - Runtime data (instance\, logs\, data\)
echo   - Old nginx\ directory
echo.
echo Git history preserves all deleted files
echo.

set /p confirm="Continue with cleanup? (yes/no) [no]: "
if not "%confirm%"=="yes" (
    echo Cleanup cancelled.
    exit /b 0
)

echo.
echo Starting cleanup...
echo.

set deleted_files=0
set deleted_dirs=0

echo [1/5] Removing wrong-project directories...
if exist Documentation\ (
    echo [DELETE DIR] Documentation\
    rd /s /q Documentation
    set /a deleted_dirs+=1
) else (
    echo [SKIP] Documentation\ (already gone)
)

if exist nginx\ (
    echo [DELETE DIR] nginx\
    rd /s /q nginx
    set /a deleted_dirs+=1
) else (
    echo [SKIP] nginx\ (already gone)
)

echo.
echo [2/5] Removing runtime data directories...
if exist instance\ (
    echo [DELETE DIR] instance\
    rd /s /q instance
    set /a deleted_dirs+=1
) else (
    echo [SKIP] instance\ (already gone)
)

if exist logs\ (
    echo [DELETE DIR] logs\
    rd /s /q logs
    set /a deleted_dirs+=1
) else (
    echo [SKIP] logs\ (already gone)
)

if exist data\ (
    echo [DELETE DIR] data\
    rd /s /q data
    set /a deleted_dirs+=1
) else (
    echo [SKIP] data\ (already gone)
)

if exist htmlcov\ (
    echo [DELETE DIR] htmlcov\
    rd /s /q htmlcov
    set /a deleted_dirs+=1
) else (
    echo [SKIP] htmlcov\ (already gone)
)

echo.
echo [3/5] Removing deprecated .env files...
if exist .env.docker (
    echo [DELETE FILE] .env.docker
    del /f .env.docker
    set /a deleted_files+=1
) else (
    echo [SKIP] .env.docker (already gone)
)

if exist .env.example (
    echo [DELETE FILE] .env.example
    del /f .env.example
    set /a deleted_files+=1
) else (
    echo [SKIP] .env.example (already gone)
)

if exist docker\.env.example (
    echo [DELETE FILE] docker\.env.example
    del /f docker\.env.example
    set /a deleted_files+=1
) else (
    echo [SKIP] docker\.env.example (already gone)
)

echo.
echo [4/5] Removing old Python scripts...
for %%f in (startup_manager.py populate_db.py clear_testuser.py verify_setup.py test_content_dir.py) do (
    if exist %%f (
        echo [DELETE FILE] %%f
        del /f %%f
        set /a deleted_files+=1
    ) else (
        echo [SKIP] %%f (already gone)
    )
)

echo.
echo [5/5] Removing old documentation and artifacts...
if exist ADMIN_PANEL_QUICK_REFERENCE.txt (
    echo [DELETE FILE] ADMIN_PANEL_QUICK_REFERENCE.txt
    del /f ADMIN_PANEL_QUICK_REFERENCE.txt
    set /a deleted_files+=1
) else (
    echo [SKIP] ADMIN_PANEL_QUICK_REFERENCE.txt (already gone)
)

for %%f in (COMPLETE_STACK_GUIDE.md DEPLOYMENT_PLAN.md FILES_CREATED_SUMMARY.md FUNCTION_ARCHITECTURE.txt MINIO_SETUP.md RESTRUCTURING_COMPLETE.md STORAGE_QUICK_REFERENCE.md START_HERE.txt) do (
    if exist %%f (
        echo [DELETE FILE] %%f
        del /f %%f
        set /a deleted_files+=1
    ) else (
        echo [SKIP] %%f (already gone)
    )
)

for %%f in (coverage.json ebook_metadata.json nul) do (
    if exist %%f (
        echo [DELETE FILE] %%f
        del /f %%f
        set /a deleted_files+=1
    ) else (
        echo [SKIP] %%f (already gone)
    )
)

echo.
echo ============================================================
echo   Cleanup Complete!
echo ============================================================
echo Deleted: !deleted_dirs! directories, !deleted_files! files
echo.
echo Next steps:
echo   1. Review changes: git status
echo   2. Test deployment: cleanup.bat ^&^& deploy.bat
echo   3. Commit cleanup: git add -A ^&^& git commit -m "Project cleanup: remove deprecated files"
echo.
echo Note: Runtime directories (data\, logs\, instance\) will be recreated on next deployment
echo.

pause
