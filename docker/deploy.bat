@echo off
REM ############################################################################
REM GLEH Automated Deployment Script (Windows)
REM ############################################################################
REM Handles complete deployment from fresh clone or restart
REM Usage: deploy.bat [--fresh]  (--fresh will recreate volumes)
REM ############################################################################

setlocal enabledelayedexpansion

echo ========================================================================
echo                   GLEH Deployment Script v1.0
echo ========================================================================
echo.

REM Check if running in docker directory
if not exist "docker-compose.yml" (
    echo [ERROR] Must run from docker\ directory
    echo Run: cd docker ^&^& deploy.bat
    exit /b 1
)

REM Parse arguments
set FRESH_DEPLOY=false
if "%1"=="--fresh" (
    set FRESH_DEPLOY=true
    echo [WARNING] Fresh deployment mode - will recreate all volumes
    echo [WARNING] All data will be lost!
    set /p confirm="Continue? (yes/no): "
    if not "!confirm!"=="yes" (
        echo Aborted
        exit /b 0
    )
)

REM Step 1: Check for .env file
echo.
echo [1/6] Checking configuration...
if not exist ".env" (
    if not exist ".env.template" (
        echo [ERROR] No .env or .env.template found
        exit /b 1
    )
    echo [WARNING] No .env file found
    echo Using .env.template defaults
)
echo [OK] Configuration OK
echo.

REM Step 2: Stop existing containers
echo [2/6] Stopping existing containers...
docker-compose down >nul 2>&1
echo [OK] Containers stopped
echo.

REM Step 3: Handle fresh deployment
if "%FRESH_DEPLOY%"=="true" (
    echo [3/6] Removing existing volumes...
    docker volume rm gleh-postgres-data >nul 2>&1
    docker volume rm gleh-app-logs >nul 2>&1
    echo [OK] Volumes removed
    echo.
) else (
    echo [3/6] Preserving existing volumes
    echo.
)

REM Step 4: Start services
echo [4/6] Starting services...
docker-compose up -d
if errorlevel 1 (
    echo [ERROR] Failed to start services
    exit /b 1
)
echo [OK] Services started
echo.

REM Step 5: Wait for services to be healthy
echo [5/6] Waiting for services to be ready...
echo Waiting for PostgreSQL...
set /a count=0
:wait_postgres
docker exec gleh-postgres pg_isready -U gleh_user -d gleh_db >nul 2>&1
if errorlevel 1 (
    set /a count+=1
    if !count! gtr 30 (
        echo [ERROR] PostgreSQL failed to start after 30 seconds
        docker logs gleh-postgres --tail 20
        exit /b 1
    )
    timeout /t 1 /nobreak >nul
    goto wait_postgres
)
echo [OK] PostgreSQL ready
echo.

echo Waiting for Flask app...
set /a count=0
:wait_flask
docker exec gleh-web curl -f http://localhost:5000/health >nul 2>&1
if errorlevel 1 (
    set /a count+=1
    if !count! gtr 60 (
        echo [ERROR] Flask app failed to start after 60 seconds
        docker logs gleh-web --tail 20
        exit /b 1
    )
    timeout /t 1 /nobreak >nul
    goto wait_flask
)
echo [OK] Flask app ready
echo.

REM Step 6: Initialize database if needed
echo [6/6] Checking database initialization...
docker exec gleh-postgres psql -U gleh_user -d gleh_db -c "SELECT 1 FROM \"user\" LIMIT 1" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Database not initialized, initializing now...
    docker exec gleh-web python scripts/init_database.py
    if errorlevel 1 (
        echo [ERROR] Database initialization failed
        exit /b 1
    )
    echo [OK] Database initialized
) else (
    echo [OK] Database already initialized
)
echo.

REM Success summary
echo ========================================================================
echo                    GLEH Deployment Successful!
echo ========================================================================
echo.
echo Services:
echo   * Main Application: http://localhost:3080
echo   * Calibre:          http://localhost:8080
echo   * Calibre-Web:      http://localhost:8083
echo.
echo Default Credentials:
echo   * Username: admin
echo   * Password: admin123
echo   [WARNING] Change password after first login!
echo.
echo Useful Commands:
echo   * View logs:    docker-compose logs -f
echo   * Stop all:     docker-compose down
echo   * Restart app:  docker-compose restart web
echo   * Shell access: docker exec -it gleh-web bash
echo.
echo Container Status:
docker ps --filter "name=gleh-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.

endlocal
