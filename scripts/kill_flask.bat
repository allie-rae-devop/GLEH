@echo off
echo Killing all Flask instances...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *flask*" 2>nul
taskkill /F /FI "IMAGENAME eq python.exe" /FI "MEMUSAGE gt 10000" 2>nul
timeout /t 2 /nobreak >nul
echo Flask instances killed.
