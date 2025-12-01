#!/bin/bash
################################################################################
# GLEH Project Cleanup Script
# Removes deprecated files and directories identified in PROJECT_AUDIT_REPORT.md
# Safe to run - only deletes unused/old development artifacts
################################################################################

set -e

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}"
echo "============================================================"
echo "  GLEH Project Cleanup"
echo "  Removing deprecated files and directories"
echo "============================================================"
echo -e "${NC}"

echo -e "${YELLOW}This script will delete:${NC}"
echo "  - Documentation/ directory (wrong project)"
echo "  - Old .env files (.env.docker, .env.example)"
echo "  - Deprecated Python scripts (5 files)"
echo "  - Old documentation files (9 .md files)"
echo "  - Test artifacts (coverage.json, etc.)"
echo "  - Runtime data (instance/, logs/, data/)"
echo "  - Old nginx/ directory"
echo ""
echo -e "${GREEN}Git history preserves all deleted files${NC}"
echo ""

read -p "Continue with cleanup? (yes/no) [no]: " confirm
if [ "$confirm" != "yes" ]; then
    echo "Cleanup cancelled."
    exit 0
fi

echo ""
echo -e "${CYAN}Starting cleanup...${NC}"
echo ""

# Track what we delete
deleted_files=0
deleted_dirs=0

# Function to safely delete directory
delete_dir() {
    if [ -d "$1" ]; then
        echo -e "${YELLOW}[DELETE DIR]${NC} $1"
        rm -rf "$1"
        ((deleted_dirs++))
    else
        echo -e "${GREEN}[SKIP]${NC} $1 (already gone)"
    fi
}

# Function to safely delete file
delete_file() {
    if [ -f "$1" ]; then
        echo -e "${YELLOW}[DELETE FILE]${NC} $1"
        rm -f "$1"
        ((deleted_files++))
    else
        echo -e "${GREEN}[SKIP]${NC} $1 (already gone)"
    fi
}

echo "[1/5] Removing wrong-project directories..."
delete_dir "Documentation"
delete_dir "nginx"

echo ""
echo "[2/5] Removing runtime data directories..."
delete_dir "instance"
delete_dir "logs"
delete_dir "data"
delete_dir "htmlcov"

echo ""
echo "[3/5] Removing deprecated .env files..."
delete_file ".env.docker"
delete_file ".env.example"
delete_file "docker/.env.example"

echo ""
echo "[4/5] Removing old Python scripts..."
delete_file "startup_manager.py"
delete_file "populate_db.py"
delete_file "clear_testuser.py"
delete_file "verify_setup.py"
delete_file "test_content_dir.py"

echo ""
echo "[5/5] Removing old documentation and artifacts..."
delete_file "ADMIN_PANEL_QUICK_REFERENCE.txt"
delete_file "COMPLETE_STACK_GUIDE.md"
delete_file "DEPLOYMENT_PLAN.md"
delete_file "FILES_CREATED_SUMMARY.md"
delete_file "FUNCTION_ARCHITECTURE.txt"
delete_file "MINIO_SETUP.md"
delete_file "RESTRUCTURING_COMPLETE.md"
delete_file "STORAGE_QUICK_REFERENCE.md"
delete_file "START_HERE.txt"
delete_file "coverage.json"
delete_file "ebook_metadata.json"
delete_file "nul"

echo ""
echo -e "${GREEN}"
echo "============================================================"
echo "  Cleanup Complete!"
echo "============================================================"
echo -e "${NC}"
echo "Deleted: $deleted_dirs directories, $deleted_files files"
echo ""
echo -e "${CYAN}Next steps:${NC}"
echo "  1. Review changes: git status"
echo "  2. Test deployment: ./cleanup.sh && ./deploy.sh"
echo "  3. Commit cleanup: git add -A && git commit -m 'Project cleanup: remove deprecated files'"
echo ""
echo -e "${YELLOW}Note: Runtime directories (data/, logs/, instance/) will be recreated on next deployment${NC}"
echo ""
