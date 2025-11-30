#!/usr/bin/env pwsh
# GLEH Restore Script
# Restores non-git files FROM Samba TO local machine
# Use this when switching devices or pulling latest backup

# Load configuration from .env file
function Get-EnvValue {
    param([string]$Key)

    $envPath = Join-Path (Get-Location).Path.Replace("\scripts", "") ".env"
    if (Test-Path $envPath) {
        $content = Get-Content $envPath
        foreach ($line in $content) {
            if ($line -match "^\s*$Key\s*=\s*(.+)$") {
                return $matches[1].Trim()
            }
        }
    }
    return $null
}

# Read CONTENT_DIR from .env (which points to Samba share)
$CONTENT_DIR = Get-EnvValue "CONTENT_DIR"

if (-not $CONTENT_DIR) {
    Write-Host "[ERROR] CONTENT_DIR must be set in .env file" -ForegroundColor Red
    exit 1
}

# Extract the root of the Samba mount (J:\ or UNC path)
if ($CONTENT_DIR -match "^([A-Z]:\\)") {
    $SAMBA_ROOT = $matches[1]
} elseif ($CONTENT_DIR -match "^(\\\\[^\\]+\\[^\\]+)") {
    $SAMBA_ROOT = $matches[1]
} else {
    $SAMBA_ROOT = $CONTENT_DIR
}

$BACKUP_PATH = Join-Path $SAMBA_ROOT "DEPLOYMENT_BACKUP"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "GLEH Restore from Samba" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test Samba connection
Write-Host "Testing Samba connection to $SAMBA_ROOT..." -ForegroundColor Yellow
if (-not (Test-Path $SAMBA_ROOT)) {
    Write-Host "[ERROR] Cannot access $SAMBA_ROOT" -ForegroundColor Red
    Write-Host "Check CONTENT_DIR in .env file: $CONTENT_DIR`n" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Samba accessible`n" -ForegroundColor Green

# Check backup exists
if (-not (Test-Path $BACKUP_PATH)) {
    Write-Host "[ERROR] Backup folder not found at $BACKUP_PATH" -ForegroundColor Red
    Write-Host "Run backup_to_samba.ps1 from another device first.`n" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Backup folder found`n" -ForegroundColor Green

# Restore .env
Write-Host "Restoring configuration..." -ForegroundColor Yellow
if (Test-Path "$BACKUP_PATH\.env") {
    Copy-Item "$BACKUP_PATH\.env" -Destination ".env" -Force
    Write-Host "[OK] .env restored" -ForegroundColor Green
} else {
    Write-Host "[WARN] .env not found in backup (skipping)" -ForegroundColor Yellow
}

# Restore database.db (root)
if (Test-Path "$BACKUP_PATH\database.db") {
    Copy-Item "$BACKUP_PATH\database.db" -Destination "database.db" -Force
    $dbSize = (Get-Item "database.db").Length / 1KB
    Write-Host "[OK] database.db restored ($([math]::Round($dbSize, 2)) KB)" -ForegroundColor Green
} else {
    Write-Host "[WARN] database.db not found in backup (skipping)" -ForegroundColor Yellow
}

# Restore instance/database.db
Write-Host "`nRestoring instance database..." -ForegroundColor Yellow
if (Test-Path "$BACKUP_PATH\instance\database.db") {
    New-Item -ItemType Directory -Force -Path "instance" | Out-Null
    Copy-Item "$BACKUP_PATH\instance\database.db" -Destination "instance\database.db" -Force
    $instanceSize = (Get-Item "instance\database.db").Length / 1KB
    Write-Host "[OK] instance/database.db restored ($([math]::Round($instanceSize, 2)) KB)" -ForegroundColor Green
} else {
    Write-Host "[WARN] instance/database.db not found in backup (skipping)" -ForegroundColor Yellow
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Restore Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Restored from: $BACKUP_PATH" -ForegroundColor Cyan
Write-Host "Date:          $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" -ForegroundColor Cyan

Write-Host "IMPORTANT: Update .env DATABASE_URL path for this machine!" -ForegroundColor Yellow
Write-Host "Current user: $env:USERNAME" -ForegroundColor Cyan
Write-Host "Expected path: c:/Users/$env:USERNAME/Desktop/AI Projects/GLEH/instance/database.db`n" -ForegroundColor Cyan
