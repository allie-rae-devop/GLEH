#!/usr/bin/env pwsh
# Kill all Flask/Python processes
# Use this to clean up multiple Flask instances

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Killing all Python/Flask processes" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Find all Python processes
$pythonProcesses = Get-Process -Name python* -ErrorAction SilentlyContinue

if ($pythonProcesses) {
    Write-Host "Found $($pythonProcesses.Count) Python process(es):" -ForegroundColor Yellow
    foreach ($proc in $pythonProcesses) {
        Write-Host "  PID $($proc.Id): $($proc.ProcessName)" -ForegroundColor Yellow
    }

    Write-Host "`nKilling all Python processes..." -ForegroundColor Yellow
    $pythonProcesses | Stop-Process -Force
    Write-Host "[OK] All Python processes killed`n" -ForegroundColor Green
} else {
    Write-Host "[INFO] No Python processes found running`n" -ForegroundColor Cyan
}

Write-Host "You can now start a fresh Flask instance:" -ForegroundColor Cyan
Write-Host "  python -m flask --app src/app run`n" -ForegroundColor Cyan
