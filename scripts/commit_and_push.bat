@echo off
cd /d "d:\AI Projects\GLEH"
echo Running commit and push script...
echo.
pwsh -ExecutionPolicy Bypass -File "%~dp0commit_and_push.ps1" %*
pause
