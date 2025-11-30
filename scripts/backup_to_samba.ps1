#!/usr/bin/env pwsh
# GLEH Deployment Backup Script
# Backs up non-git files to Samba for easy deployment on other machines

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

# Read Samba configuration from .env
$SAMBA_HOST = Get-EnvValue "SAMBA_HOST"
$SAMBA_SHARE = Get-EnvValue "SAMBA_SHARE"

if (-not $SAMBA_HOST -or -not $SAMBA_SHARE) {
    Write-Host "[ERROR] SAMBA_HOST and SAMBA_SHARE must be set in .env file" -ForegroundColor Red
    exit 1
}

$BACKUP_PATH = "\\$SAMBA_HOST\$SAMBA_SHARE\DEPLOYMENT_BACKUP"
$SAMBA_PATH = "\\$SAMBA_HOST\$SAMBA_SHARE"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "GLEH Deployment Backup to Samba" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test Samba connection
Write-Host "Testing Samba connection to $SAMBA_PATH..." -ForegroundColor Yellow
if (-not (Test-Path $SAMBA_PATH)) {
    Write-Host "[ERROR] Cannot access Samba share at $SAMBA_PATH" -ForegroundColor Red
    Write-Host "Make sure you're on the network and server is running.`n" -ForegroundColor Red
    Write-Host "Check SAMBA_HOST=$SAMBA_HOST and SAMBA_SHARE=$SAMBA_SHARE in .env file`n" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] Samba share accessible`n" -ForegroundColor Green

# Create backup directories
Write-Host "Creating backup directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path $BACKUP_PATH | Out-Null
New-Item -ItemType Directory -Force -Path "$BACKUP_PATH\instance" | Out-Null
Write-Host "[OK] Backup directories ready`n" -ForegroundColor Green

# Backup .env
Write-Host "Backing up configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Copy-Item ".env" -Destination "$BACKUP_PATH\.env" -Force
    Write-Host "[OK] .env backed up" -ForegroundColor Green
} else {
    Write-Host "[WARN] .env not found (skipping)" -ForegroundColor Yellow
}

# Backup database.db (root)
if (Test-Path "database.db") {
    Copy-Item "database.db" -Destination "$BACKUP_PATH\database.db" -Force
    $dbSize = (Get-Item "database.db").Length / 1KB
    Write-Host "[OK] database.db backed up ($([math]::Round($dbSize, 2)) KB)" -ForegroundColor Green
} else {
    Write-Host "[WARN] database.db not found (skipping)" -ForegroundColor Yellow
}

# Backup instance/database.db
if (Test-Path "instance\database.db") {
    Copy-Item "instance\database.db" -Destination "$BACKUP_PATH\instance\database.db" -Force
    $instanceSize = (Get-Item "instance\database.db").Length / 1KB
    Write-Host "[OK] instance/database.db backed up ($([math]::Round($instanceSize, 2)) KB)" -ForegroundColor Green
} else {
    Write-Host "[WARN] instance/database.db not found (skipping)" -ForegroundColor Yellow
}

# Backup static/avatars (legacy location - for migration)
if (Test-Path "static\avatars") {
    New-Item -ItemType Directory -Force -Path "$BACKUP_PATH\static\avatars" | Out-Null
    Copy-Item "static\avatars\*" -Destination "$BACKUP_PATH\static\avatars\" -Force -Recurse -ErrorAction SilentlyContinue
    $avatarCount = (Get-ChildItem "static\avatars").Count
    Write-Host "[OK] static/avatars/ backed up ($avatarCount files)" -ForegroundColor Green
} else {
    Write-Host "[INFO] static/avatars/ not found (avatars now stored on Samba)" -ForegroundColor Cyan
}

# Create README in backup location
$readmeContent = @"
GLEH Deployment Backup
======================

This folder contains files NOT committed to Git for security/privacy reasons.

Files:
- .env                     Your personal configuration (passwords, paths)
- database.db              Your SQLite database (root location)
- instance/database.db     Flask instance database
- static/avatars/          User avatars (legacy location - now on Samba J:\uploads\avatars)

To deploy on a new machine:
1. Clone the repo from GitHub
2. Copy these files to the project root
3. Run: pip install -r requirements.txt
4. Run: python verify_setup.py
5. Run: python -m flask --app src/app run

Note: Avatar uploads are now stored on Samba (J:\uploads\avatars) for multi-device sync.
The static/avatars backup is only for migration purposes.

Last backup: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
"@

$readmeContent | Out-File -FilePath "$BACKUP_PATH\README.txt" -Encoding UTF8
Write-Host "[OK] README.txt created`n" -ForegroundColor Green

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Backup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Location: $BACKUP_PATH" -ForegroundColor Cyan
Write-Host "Date:     $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')`n" -ForegroundColor Cyan
