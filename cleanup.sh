#!/bin/bash
################################################################################
# GLEH Cleanup Script
# Completely removes all GLEH Docker containers, images, and volumes
# USE WITH CAUTION: This will delete all data!
################################################################################

set -e

# Colors
RED='\033[0;31m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${YELLOW}"
echo "============================================================"
echo "  GLEH - Complete Cleanup Script"
echo "  WARNING: This will delete ALL GLEH data!"
echo "============================================================"
echo -e "${NC}"

echo -e "${RED}What to remove:${NC}"
echo "  - All GLEH containers"
echo "  - All GLEH Docker images"
echo "  - Network configuration"
echo ""
echo -e "${YELLOW}Volume Options:${NC}"
echo "  1) Keep volumes (RECOMMENDED for testing)"
echo "     - Preserves books, courses, and database"
echo "     - Fast re-deployment for testing"
echo ""
echo "  2) Delete volumes (complete wipe)"
echo "     - Removes ALL data including books/courses"
echo "     - Need to re-upload everything"
echo ""

read -p "Keep volumes? (yes/no) [yes]: " keep_volumes
keep_volumes=${keep_volumes:-yes}

if [ "$keep_volumes" != "yes" ] && [ "$keep_volumes" != "no" ]; then
    echo -e "${RED}Invalid choice. Please enter 'yes' or 'no'${NC}"
    exit 1
fi

echo ""
if [ "$keep_volumes" = "yes" ]; then
    echo -e "${GREEN}✓ Volumes will be PRESERVED${NC}"
    echo "  - MinIO data (books, courses)"
    echo "  - Calibre library"
    echo "  - PostgreSQL database"
else
    echo -e "${RED}⚠ Volumes will be DELETED${NC}"
    echo "  - All books and courses will be removed"
    echo "  - You'll need to re-upload everything"
    read -p "Are you absolutely sure? Type 'DELETE' to confirm: " confirm_delete
    if [ "$confirm_delete" != "DELETE" ]; then
        echo "Cleanup cancelled."
        exit 0
    fi
fi

echo ""
echo -e "${YELLOW}Starting cleanup...${NC}"

cd docker

# Stop all containers
echo -e "\n[1/4] Stopping containers..."
docker compose down || echo "No containers to stop"
echo -e "${GREEN}✓ Containers stopped${NC}"

# Remove volumes (conditional)
if [ "$keep_volumes" = "no" ]; then
    echo -e "\n[2/4] Removing volumes..."
    docker compose down -v || echo "No volumes to remove"
    echo -e "${GREEN}✓ Volumes removed${NC}"
else
    echo -e "\n[2/4] Preserving volumes..."
    echo -e "${GREEN}✓ Volumes kept (data preserved)${NC}"
fi

# Remove images
echo -e "\n[3/4] Removing images..."
docker rmi docker-web 2>/dev/null || echo "Image docker-web not found"
docker rmi docker-nginx 2>/dev/null || echo "Image docker-nginx not found"
echo -e "${GREEN}✓ Images removed${NC}"

# Clean up any orphaned containers
echo -e "\n[4/4] Cleaning up orphaned resources..."
docker system prune -f
echo -e "${GREEN}✓ Cleanup complete${NC}"

cd ..

echo -e "\n${GREEN}"
echo "============================================================"
echo "  ✓ GLEH Cleanup Complete!"
echo "============================================================"
echo -e "${NC}"
echo ""
echo "To redeploy GLEH, run:"
echo "  ./deploy.sh"
echo ""
echo "Note: You may want to delete .env and recreate from template:"
echo "  rm .env"
echo "  cp .env.template .env"
echo "  # Edit .env with your settings"
echo ""
