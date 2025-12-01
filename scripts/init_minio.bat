@echo off
REM Initialize MinIO bucket and folder structure for GLEH
REM This script creates the required bucket and folders in MinIO

echo ========================================
echo GLEH - MinIO Storage Initialization
echo ========================================
echo.

REM Change to project root directory
cd /d "%~dp0\.."

REM Run the Python initialization script
python scripts\init_minio.py

echo.
pause
