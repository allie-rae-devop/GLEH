@echo off
cd /d "d:\AI Projects\GLEH"
echo Running Samba backup script...
echo.
pwsh -ExecutionPolicy Bypass -File "%~dp0backup_to_samba.ps1"
pause
