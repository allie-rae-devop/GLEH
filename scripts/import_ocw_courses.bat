@echo off
REM Import courses from Docker volume to database
REM This script runs the Python import inside the gleh-web container

echo ================================================================================
echo Course Importer - Docker Volume
echo ================================================================================
echo.

REM Copy the Python script into the container
echo Copying import script to container...
docker cp scripts\import_courses_from_volume.py gleh-web:/tmp/import_courses_from_volume.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to copy script to container
    exit /b 1
)

echo Running import inside Docker container...
echo.
docker exec gleh-web python /tmp/import_courses_from_volume.py
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Import failed
    exit /b 1
)

echo.
echo Cleaning up...
docker exec gleh-web rm /tmp/import_courses_from_volume.py

echo.
echo ================================================================================
echo Import complete!
echo ================================================================================
echo.
pause
