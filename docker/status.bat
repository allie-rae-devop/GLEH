@echo off
REM ############################################################################
REM GLEH Status Check Script (Windows)
REM ############################################################################
REM Quick health check for all services
REM Usage: status.bat
REM ############################################################################

setlocal enabledelayedexpansion

echo ========================================================================
echo                       GLEH Status Check
echo ========================================================================
echo.

REM Check Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running
    exit /b 1
)
echo [OK] Docker is running

REM Check if in docker directory
if not exist "docker-compose.yml" (
    cd docker 2>nul
    if errorlevel 1 (
        echo [ERROR] Not in GLEH directory
        exit /b 1
    )
)

REM Check containers
echo.
echo Container Status:
echo ------------------------------------------------------------------------

set all_ok=true

REM Check gleh-postgres
docker ps --format "{{.Names}}" | findstr "gleh-postgres" >nul 2>&1
if errorlevel 1 (
    echo   [ERROR] gleh-postgres: not running
    set all_ok=false
) else (
    for /f "tokens=*" %%i in ('docker ps --format "{{.Status}}" --filter "name=^gleh-postgres$"') do set status=%%i
    echo !status! | findstr /i "healthy" >nul 2>&1
    if errorlevel 1 (
        echo   [WARNING] gleh-postgres: !status!
    ) else (
        echo   [OK] gleh-postgres: healthy
    )
)

REM Check gleh-web
docker ps --format "{{.Names}}" | findstr "gleh-web" >nul 2>&1
if errorlevel 1 (
    echo   [ERROR] gleh-web: not running
    set all_ok=false
) else (
    for /f "tokens=*" %%i in ('docker ps --format "{{.Status}}" --filter "name=^gleh-web$"') do set status=%%i
    echo !status! | findstr /i "healthy" >nul 2>&1
    if errorlevel 1 (
        echo   [WARNING] gleh-web: !status!
    ) else (
        echo   [OK] gleh-web: healthy
    )
)

REM Check gleh-nginx
docker ps --format "{{.Names}}" | findstr "gleh-nginx" >nul 2>&1
if errorlevel 1 (
    echo   [ERROR] gleh-nginx: not running
    set all_ok=false
) else (
    for /f "tokens=*" %%i in ('docker ps --format "{{.Status}}" --filter "name=^gleh-nginx$"') do set status=%%i
    echo !status! | findstr /i "healthy" >nul 2>&1
    if errorlevel 1 (
        echo   [WARNING] gleh-nginx: !status!
    ) else (
        echo   [OK] gleh-nginx: healthy
    )
)

REM Check gleh-calibre (optional)
docker ps --format "{{.Names}}" | findstr "gleh-calibre$" >nul 2>&1
if errorlevel 1 (
    echo   [WARNING] gleh-calibre: not running ^(optional^)
) else (
    echo   [OK] gleh-calibre: running
)

REM Check gleh-calibre-web (optional)
docker ps --format "{{.Names}}" | findstr "gleh-calibre-web" >nul 2>&1
if errorlevel 1 (
    echo   [WARNING] gleh-calibre-web: not running ^(optional^)
) else (
    echo   [OK] gleh-calibre-web: running
)

REM Check database initialization
echo.
echo Database Status:
echo ------------------------------------------------------------------------

docker exec gleh-postgres pg_isready -U gleh_user -d gleh_db >nul 2>&1
if errorlevel 1 (
    echo   [ERROR] Cannot connect to PostgreSQL
    set all_ok=false
) else (
    echo   [OK] PostgreSQL connection: OK
    docker exec gleh-postgres psql -U gleh_user -d gleh_db -c "SELECT 1 FROM \"user\" LIMIT 1" >nul 2>&1
    if errorlevel 1 (
        echo   [ERROR] Database not initialized
        echo   Run: docker exec gleh-web python scripts/init_database.py
        set all_ok=false
    ) else (
        for /f %%i in ('docker exec gleh-postgres psql -U gleh_user -d gleh_db -t -c "SELECT COUNT(*) FROM \"user\""') do set user_count=%%i
        echo   [OK] Database initialized: !user_count! users
    )
)

REM Check web app
echo.
echo Web Application Status:
echo ------------------------------------------------------------------------

docker exec gleh-web curl -sf http://localhost:5000/health >nul 2>&1
if errorlevel 1 (
    echo   [ERROR] Flask health check failed
    set all_ok=false
) else (
    echo   [OK] Flask health check: OK
)

curl -sf http://localhost:3080/health >nul 2>&1
if errorlevel 1 (
    echo   [ERROR] Nginx proxy not responding
    set all_ok=false
) else (
    echo   [OK] Nginx proxy: OK
)

REM Check volumes
echo.
echo Volume Status:
echo ------------------------------------------------------------------------

docker volume ls --format "{{.Name}}" | findstr "gleh-postgres-data" >nul 2>&1
if errorlevel 1 (
    echo   [WARNING] gleh-postgres-data: not created
) else (
    echo   [OK] gleh-postgres-data
)

docker volume ls --format "{{.Name}}" | findstr "gleh-app-logs" >nul 2>&1
if errorlevel 1 (
    echo   [WARNING] gleh-app-logs: not created
) else (
    echo   [OK] gleh-app-logs
)

docker volume ls --format "{{.Name}}" | findstr "gleh-calibre-library" >nul 2>&1
if errorlevel 1 (
    echo   [WARNING] gleh-calibre-library: not created
) else (
    echo   [OK] gleh-calibre-library
)

docker volume ls --format "{{.Name}}" | findstr "gleh-courses" >nul 2>&1
if errorlevel 1 (
    echo   [WARNING] gleh-courses: not created
) else (
    echo   [OK] gleh-courses
)

REM Summary
echo.
echo ------------------------------------------------------------------------
if "%all_ok%"=="true" (
    echo [OK] All critical services operational
    echo.
    echo Access URLs:
    echo   * Main App:    http://localhost:3080
    echo   * Calibre:     http://localhost:8080
    echo   * Calibre-Web: http://localhost:8083
) else (
    echo [ERROR] Some services have issues
    echo.
    echo Troubleshooting:
    echo   1. View logs:   docker-compose logs -f
    echo   2. Restart:     docker-compose restart
    echo   3. Full reset:  deploy.bat --fresh
)
echo.

endlocal
