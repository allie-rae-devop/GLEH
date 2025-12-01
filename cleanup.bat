@echo off
REM ############################################################################
REM GLEH Cleanup Script (Windows)
REM Completely removes all GLEH Docker containers, images, and volumes
REM USE WITH CAUTION: This will delete all data!
REM ############################################################################

echo ============================================================
echo   GLEH - Complete Cleanup Script (Windows)
echo   WARNING: This will delete ALL GLEH data!
echo ============================================================
echo.

echo What to remove:
echo   - All GLEH containers
echo   - All GLEH Docker images
echo   - Network configuration
echo.
echo Volume Options:
echo   1^) Keep volumes (RECOMMENDED for testing^)
echo      - Preserves books, courses, and database
echo      - Fast re-deployment for testing
echo.
echo   2^) Delete volumes (complete wipe^)
echo      - Removes ALL data including books/courses
echo      - Need to re-upload everything
echo.

set /p keep_volumes="Keep volumes? (yes/no) [yes]: "
if "%keep_volumes%"=="" set keep_volumes=yes

if not "%keep_volumes%"=="yes" if not "%keep_volumes%"=="no" (
    echo Invalid choice. Please enter 'yes' or 'no'
    exit /b 1
)

echo.
if "%keep_volumes%"=="yes" (
    echo + Volumes will be PRESERVED
    echo   - MinIO data (books, courses^)
    echo   - Calibre library
    echo   - PostgreSQL database
) else (
    echo ! Volumes will be DELETED
    echo   - All books and courses will be removed
    echo   - You'll need to re-upload everything
    set /p confirm_delete="Are you absolutely sure? Type 'DELETE' to confirm: "
    if not "!confirm_delete!"=="DELETE" (
        echo Cleanup cancelled.
        exit /b 0
    )
)

echo.
echo Starting cleanup...

cd docker

REM Stop all containers
echo.
echo [1/4] Stopping containers...
docker compose down 2>nul
if %errorlevel% neq 0 (
    echo No containers to stop
)
echo + Containers stopped

REM Remove volumes (conditional)
if "%keep_volumes%"=="no" (
    echo.
    echo [2/4] Removing volumes...
    docker compose down -v 2>nul
    if %errorlevel% neq 0 (
        echo No volumes to remove
    )
    echo + Volumes removed
) else (
    echo.
    echo [2/4] Preserving volumes...
    echo + Volumes kept (data preserved^)
)

REM Remove images
echo.
echo [3/4] Removing images...
docker rmi docker-web 2>nul
docker rmi docker-nginx 2>nul
echo + Images removed

REM Clean up orphaned resources
echo.
echo [4/4] Cleaning up orphaned resources...
docker system prune -f
echo + Cleanup complete

cd ..

echo.
echo ============================================================
echo   + GLEH Cleanup Complete!
echo ============================================================
echo.
echo.
echo To redeploy GLEH, run:
echo   deploy.bat
echo.
echo Note: You may want to delete .env and recreate from template:
echo   del .env
echo   copy .env.template .env
echo   REM Edit .env with your settings
echo.

pause
