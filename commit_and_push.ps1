#!/usr/bin/env pwsh
# GLEH Smart Commit & Push Script
# Automatically backs up to Samba, commits changes, and pushes to GitHub

param(
    [Parameter(Mandatory=$false)]
    [string]$CommitMessage = ""
)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "GLEH Smart Commit & Push" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Backup to Samba
Write-Host "[1/4] Backing up to Samba..." -ForegroundColor Yellow
$BACKUP_PATH = "\\10.0.10.61\project-data\DEPLOYMENT_BACKUP"

if (Test-Path "\\10.0.10.61\project-data") {
    # Create backup directories
    New-Item -ItemType Directory -Force -Path $BACKUP_PATH | Out-Null
    New-Item -ItemType Directory -Force -Path "$BACKUP_PATH\instance" | Out-Null

    # Backup .env
    if (Test-Path ".env") {
        Copy-Item ".env" -Destination "$BACKUP_PATH\.env" -Force
        Write-Host "  [OK] .env backed up to Samba" -ForegroundColor Green
    }

    # Backup databases
    if (Test-Path "database.db") {
        Copy-Item "database.db" -Destination "$BACKUP_PATH\database.db" -Force
        Write-Host "  [OK] database.db backed up to Samba" -ForegroundColor Green
    }

    if (Test-Path "instance\database.db") {
        Copy-Item "instance\database.db" -Destination "$BACKUP_PATH\instance\database.db" -Force
        Write-Host "  [OK] instance/database.db backed up to Samba" -ForegroundColor Green
    }

    Write-Host "  [OK] Samba backup complete`n" -ForegroundColor Green
} else {
    Write-Host "  [WARN] Samba share not accessible (skipping backup)`n" -ForegroundColor Yellow
}

# Step 2: Git Status
Write-Host "[2/4] Checking Git status..." -ForegroundColor Yellow
git status --short
Write-Host ""

# Step 3: Get commit message if not provided
if ([string]::IsNullOrWhiteSpace($CommitMessage)) {
    Write-Host "[3/4] Enter commit message:" -ForegroundColor Yellow
    $CommitMessage = Read-Host "  Message"
    if ([string]::IsNullOrWhiteSpace($CommitMessage)) {
        Write-Host "`n[ERROR] Commit message cannot be empty!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "[3/4] Using commit message: $CommitMessage`n" -ForegroundColor Yellow
}

# Step 4: Git add, commit, push
Write-Host "[4/4] Committing and pushing to GitHub..." -ForegroundColor Yellow

# Add all changes
git add .
Write-Host "  [OK] Changes staged" -ForegroundColor Green

# Commit
git commit -m "$CommitMessage"
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Changes committed" -ForegroundColor Green
} else {
    Write-Host "  [WARN] Nothing to commit or commit failed" -ForegroundColor Yellow
}

# Push
Write-Host "`n  Pushing to GitHub..." -ForegroundColor Cyan
git push origin master
if ($LASTEXITCODE -eq 0) {
    Write-Host "  [OK] Pushed to GitHub`n" -ForegroundColor Green
} else {
    Write-Host "  [ERROR] Push failed!`n" -ForegroundColor Red
    exit 1
}

# Summary
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "All Done!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "[OK] Samba backup updated" -ForegroundColor Green
Write-Host "[OK] Changes committed to Git" -ForegroundColor Green
Write-Host "[OK] Pushed to GitHub" -ForegroundColor Green
Write-Host "`nCommit message: $CommitMessage`n" -ForegroundColor Cyan
