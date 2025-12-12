@echo off
REM Import courses from Docker volume to database
REM This script runs the Python import inside the edu-web container

echo ================================================================================
echo Course Importer - Docker Volume
echo ================================================================================
echo.

REM Copy the Python script into the container
echo Copying import script to container...
docker cp scripts\import_courses_from_volume.py edu-web:/tmp/import_courses_from_volume.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to copy script to container
    exit /b 1
)

echo Running import inside Docker container...
echo.
docker exec edu-web python /tmp/import_courses_from_volume.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Import failed
    exit /b 1
)

echo.
echo Cleaning up...
docker exec edu-web rm /tmp/import_courses_from_volume.py

echo.
echo ================================================================================
echo Import complete!
echo ================================================================================
echo.
pause
