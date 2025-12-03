#!/bin/bash
################################################################################
# GLEH Automated Deployment Script
################################################################################
# Handles complete deployment from fresh clone or restart
# Usage: ./deploy.sh [--fresh]  (--fresh will recreate volumes)
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║              GLEH Deployment Script v1.0                      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo

# Check if running in docker directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}Error: Must run from docker/ directory${NC}"
    echo "Run: cd docker && ./deploy.sh"
    exit 1
fi

# Parse arguments
FRESH_DEPLOY=false
if [ "$1" == "--fresh" ]; then
    FRESH_DEPLOY=true
    echo -e "${YELLOW}⚠ Fresh deployment mode - will recreate all volumes${NC}"
    echo -e "${YELLOW}⚠ All data will be lost!${NC}"
    read -p "Continue? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        echo "Aborted"
        exit 0
    fi
fi

# Step 1: Check for .env file
echo -e "\n${BLUE}[1/6] Checking configuration...${NC}"
if [ ! -f ".env" ] && [ ! -f ".env.template" ]; then
    echo -e "${RED}✗ No .env or .env.template found${NC}"
    exit 1
fi

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ No .env file found${NC}"
    echo -e "${GREEN}Using .env.template defaults${NC}"
fi
echo -e "${GREEN}✓ Configuration OK${NC}"

# Step 2: Stop existing containers
echo -e "\n${BLUE}[2/6] Stopping existing containers...${NC}"
docker-compose down 2>/dev/null || true
echo -e "${GREEN}✓ Containers stopped${NC}"

# Step 3: Handle fresh deployment
if [ "$FRESH_DEPLOY" = true ]; then
    echo -e "\n${BLUE}[3/6] Removing existing volumes...${NC}"
    docker volume rm gleh-postgres-data 2>/dev/null || true
    docker volume rm gleh-app-logs 2>/dev/null || true
    echo -e "${GREEN}✓ Volumes removed${NC}"
else
    echo -e "\n${BLUE}[3/6] Preserving existing volumes${NC}"
fi

# Step 4: Start services
echo -e "\n${BLUE}[4/6] Starting services...${NC}"
docker-compose up -d
echo -e "${GREEN}✓ Services started${NC}"

# Step 5: Wait for services to be healthy
echo -e "\n${BLUE}[5/6] Waiting for services to be ready...${NC}"
echo -n "Waiting for PostgreSQL"
for i in {1..30}; do
    if docker exec gleh-postgres pg_isready -U gleh_user -d gleh_db &>/dev/null; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e " ${RED}✗ Timeout${NC}"
        echo -e "${RED}PostgreSQL failed to start${NC}"
        docker logs gleh-postgres --tail 20
        exit 1
    fi
done

echo -n "Waiting for Flask app"
for i in {1..60}; do
    if docker exec gleh-web curl -f http://localhost:5000/health &>/dev/null; then
        echo -e " ${GREEN}✓${NC}"
        break
    fi
    echo -n "."
    sleep 1
    if [ $i -eq 60 ]; then
        echo -e " ${RED}✗ Timeout${NC}"
        echo -e "${RED}Flask app failed to start${NC}"
        docker logs gleh-web --tail 20
        exit 1
    fi
done

# Step 6: Initialize database if needed
echo -e "\n${BLUE}[6/6] Checking database initialization...${NC}"
if docker exec gleh-postgres psql -U gleh_user -d gleh_db -c "SELECT 1 FROM \"user\" LIMIT 1" &>/dev/null; then
    echo -e "${GREEN}✓ Database already initialized${NC}"
else
    echo -e "${YELLOW}⚠ Database not initialized, initializing now...${NC}"
    docker exec gleh-web python scripts/init_database.py
    echo -e "${GREEN}✓ Database initialized${NC}"
fi

# Success summary
echo
echo -e "${GREEN}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║               GLEH Deployment Successful!                     ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════════╝${NC}"
echo
echo -e "${BLUE}Services:${NC}"
echo -e "  • Main Application: ${GREEN}http://localhost:3080${NC}"
echo -e "  • Calibre:          ${GREEN}http://localhost:8080${NC}"
echo -e "  • Calibre-Web:      ${GREEN}http://localhost:8083${NC}"
echo
echo -e "${BLUE}Default Credentials:${NC}"
echo -e "  • Username: ${YELLOW}admin${NC}"
echo -e "  • Password: ${YELLOW}admin123${NC}"
echo -e "  ${RED}⚠ Change password after first login!${NC}"
echo
echo -e "${BLUE}Useful Commands:${NC}"
echo -e "  • View logs:   ${YELLOW}docker-compose logs -f${NC}"
echo -e "  • Stop all:    ${YELLOW}docker-compose down${NC}"
echo -e "  • Restart app: ${YELLOW}docker-compose restart web${NC}"
echo -e "  • Shell access: ${YELLOW}docker exec -it gleh-web bash${NC}"
echo

# Show container status
echo -e "${BLUE}Container Status:${NC}"
docker ps --filter "name=gleh-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo
