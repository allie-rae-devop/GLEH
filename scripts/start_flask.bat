@echo off
cd /d "d:\AI Projects\GLEH"
echo Starting Flask server...
echo.
echo Server will be available at: http://127.0.0.1:5000
echo Press Ctrl+C to stop the server
echo.
.venv\Scripts\python.exe -m flask --app src/app run
