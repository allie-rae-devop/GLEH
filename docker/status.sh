#!/bin/bash
################################################################################
# GLEH Status Check Script
################################################################################
# Quick health check for all services
# Usage: ./status.sh
################################################################################

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                  GLEH Status Check                            ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════════╝${NC}"
echo

# Check Docker is running
if ! docker info &>/dev/null; then
    echo -e "${RED}✗ Docker is not running${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"

# Check if in docker directory
if [ ! -f "docker-compose.yml" ]; then
    cd docker 2>/dev/null || {
        echo -e "${RED}✗ Not in GLEH directory${NC}"
        exit 1
    }
fi

# Check containers
echo
echo -e "${BLUE}Container Status:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

declare -a containers=("gleh-postgres" "gleh-web" "gleh-nginx" "gleh-calibre" "gleh-calibre-web")
declare -a required=("yes" "yes" "yes" "no" "no")
all_ok=true

for i in "${!containers[@]}"; do
    container="${containers[$i]}"
    is_required="${required[$i]}"

    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        status=$(docker ps --format '{{.Status}}' --filter "name=^${container}$")
        if [[ $status == *"healthy"* ]]; then
            echo -e "  ${GREEN}✓${NC} ${container}: ${GREEN}healthy${NC}"
        elif [[ $status == *"unhealthy"* ]]; then
            echo -e "  ${RED}✗${NC} ${container}: ${RED}unhealthy${NC}"
            all_ok=false
        else
            echo -e "  ${YELLOW}◐${NC} ${container}: ${YELLOW}starting${NC}"
        fi
    else
        if [ "$is_required" == "yes" ]; then
            echo -e "  ${RED}✗${NC} ${container}: ${RED}not running${NC}"
            all_ok=false
        else
            echo -e "  ${YELLOW}◐${NC} ${container}: ${YELLOW}not running (optional)${NC}"
        fi
    fi
done

# Check database initialization
echo
echo -e "${BLUE}Database Status:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if docker exec gleh-postgres pg_isready -U gleh_user -d gleh_db &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} PostgreSQL connection: ${GREEN}OK${NC}"

    if docker exec gleh-postgres psql -U gleh_user -d gleh_db -c "SELECT 1 FROM \"user\" LIMIT 1" &>/dev/null; then
        user_count=$(docker exec gleh-postgres psql -U gleh_user -d gleh_db -t -c "SELECT COUNT(*) FROM \"user\"" 2>/dev/null | tr -d ' ')
        echo -e "  ${GREEN}✓${NC} Database initialized: ${GREEN}${user_count} users${NC}"
    else
        echo -e "  ${RED}✗${NC} Database not initialized"
        echo -e "    ${YELLOW}Run:${NC} docker exec gleh-web python scripts/init_database.py"
        all_ok=false
    fi
else
    echo -e "  ${RED}✗${NC} Cannot connect to PostgreSQL"
    all_ok=false
fi

# Check web app
echo
echo -e "${BLUE}Web Application Status:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

if docker exec gleh-web curl -sf http://localhost:5000/health &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} Flask health check: ${GREEN}OK${NC}"
else
    echo -e "  ${RED}✗${NC} Flask health check failed"
    all_ok=false
fi

if curl -sf http://localhost:3080/health &>/dev/null; then
    echo -e "  ${GREEN}✓${NC} Nginx proxy: ${GREEN}OK${NC}"
else
    echo -e "  ${RED}✗${NC} Nginx proxy not responding"
    all_ok=false
fi

# Check volumes
echo
echo -e "${BLUE}Volume Status:${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

declare -a volumes=("gleh-postgres-data" "gleh-app-logs" "gleh-calibre-library" "gleh-courses")
for volume in "${volumes[@]}"; do
    if docker volume ls --format '{{.Name}}' | grep -q "^${volume}$"; then
        echo -e "  ${GREEN}✓${NC} ${volume}"
    else
        echo -e "  ${YELLOW}◐${NC} ${volume}: ${YELLOW}not created${NC}"
    fi
done

# Summary
echo
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ "$all_ok" = true ]; then
    echo -e "${GREEN}✓ All critical services operational${NC}"
    echo
    echo -e "${BLUE}Access URLs:${NC}"
    echo -e "  • Main App:    ${GREEN}http://localhost:3080${NC}"
    echo -e "  • Calibre:     ${GREEN}http://localhost:8080${NC}"
    echo -e "  • Calibre-Web: ${GREEN}http://localhost:8083${NC}"
else
    echo -e "${RED}✗ Some services have issues${NC}"
    echo -e "${YELLOW}Troubleshooting:${NC}"
    echo -e "  1. View logs: ${BLUE}docker-compose logs -f${NC}"
    echo -e "  2. Restart: ${BLUE}docker-compose restart${NC}"
    echo -e "  3. Full reset: ${BLUE}./deploy.sh --fresh${NC}"
fi
echo
