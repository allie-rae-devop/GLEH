@echo off
REM ############################################################################
REM GLEH Deployment Script (Windows)
REM One-command deployment for production and testing
REM ############################################################################

setlocal enabledelayedexpansion

echo ============================================================
echo   GLEH - Gammons Landing Educational Hub
echo   Automated Deployment Script (Windows)
echo ============================================================
echo.

REM ============================================================================
REM STEP 1: Environment Check
REM ============================================================================
echo [1/6] Checking prerequisites...

where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo X Docker is not installed
    echo Please install Docker Desktop: https://docs.docker.com/desktop/install/windows-install/
    exit /b 1
)
echo + Docker installed

docker compose version >nul 2>nul
if %errorlevel% neq 0 (
    echo X Docker Compose is not available
    echo Please install Docker Compose or upgrade Docker Desktop
    exit /b 1
)
echo + Docker Compose available

REM ============================================================================
REM STEP 2: Environment Configuration
REM ============================================================================
echo.
echo [2/6] Configuring environment...

if not exist .env (
    echo No .env file found. Creating from template...

    if not exist .env.template (
        echo X .env.template not found!
        exit /b 1
    )

    copy .env.template .env >nul
    echo + Created .env from template

    echo.
    echo ================================================
    echo IMPORTANT: Edit .env and set your credentials!
    echo ================================================
    echo Required changes:
    echo   - SECRET_KEY (generate random string^)
    echo   - POSTGRES_PASSWORD (strong password^)
    echo   - CALIBRE_PASSWORD (Calibre admin password^)
    echo   - MINIO_SECRET_KEY (MinIO secret^)
    echo   - MINIO_ROOT_PASSWORD (MinIO root password^)
    echo.
    pause
) else (
    echo + .env file exists
)

REM ============================================================================
REM STEP 3: Build Docker Images
REM ============================================================================
echo.
echo [3/6] Building Docker images...

cd docker
docker compose build --no-cache
if %errorlevel% neq 0 (
    echo X Build failed
    exit /b 1
)
echo + Images built successfully

REM ============================================================================
REM STEP 4: Start Services
REM ============================================================================
echo.
echo [4/6] Starting services...

docker compose up -d
if %errorlevel% neq 0 (
    echo X Failed to start services
    exit /b 1
)

echo Waiting for services to be healthy...
timeout /t 15 /nobreak >nul

docker compose ps

echo + Services started

REM ============================================================================
REM STEP 5: Initialize MinIO Storage
REM ============================================================================
echo.
echo [5/6] Initializing MinIO storage...

cd ..
if exist scripts\init_minio.py (
    python scripts\init_minio.py
    if %errorlevel% neq 0 (
        echo ! MinIO initialization failed (may already be initialized^)
    ) else (
        echo + MinIO storage initialized
    )
) else (
    echo ! scripts\init_minio.py not found, skipping...
)

REM ============================================================================
REM STEP 6: Initialize Database
REM ============================================================================
echo.
echo [6/6] Initializing database...

cd docker
docker compose exec -T web python scripts/init_database.py
if %errorlevel% neq 0 (
    echo X Database initialization failed
    exit /b 1
)

echo + Database initialized

REM ============================================================================
REM DEPLOYMENT COMPLETE
REM ============================================================================
echo.
echo ============================================================
echo   + DEPLOYMENT COMPLETE!
echo ============================================================
echo.

echo Access your GLEH instance:
echo   Main Application:  http://localhost
echo   Login:             admin / admin123
echo   MinIO Console:     http://localhost:9001
echo   Calibre GUI:       http://localhost:8080
echo   Calibre-Web:       http://localhost:8083
echo.
echo IMPORTANT: Change the default admin password after first login!
echo.
echo To stop the stack:
echo   cd docker ^&^& docker compose down
echo.
echo To view logs:
echo   cd docker ^&^& docker compose logs -f
echo.

pause
