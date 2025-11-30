@echo off
cd /d "d:\AI Projects\GLEH"
echo Running Samba restore script...
echo.
pwsh -ExecutionPolicy Bypass -File "%~dp0restore_from_samba.ps1"
pause
