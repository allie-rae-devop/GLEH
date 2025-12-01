#!/bin/bash
################################################################################
# GLEH Deployment Script
# One-command deployment for production and testing
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "============================================================"
echo "  GLEH - Gammons Landing Educational Hub"
echo "  Automated Deployment Script"
echo "============================================================"
echo -e "${NC}"

# ============================================================================
# STEP 1: Environment Check
# ============================================================================
echo -e "${BLUE}[1/6] Checking prerequisites...${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}✗ Docker is not installed${NC}"
    echo "Please install Docker first: https://docs.docker.com/get-docker/"
    exit 1
fi
echo -e "${GREEN}✓ Docker installed${NC}"

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo -e "${RED}✗ Docker Compose is not available${NC}"
    echo "Please install Docker Compose or upgrade Docker"
    exit 1
fi
echo -e "${GREEN}✓ Docker Compose available${NC}"

# ============================================================================
# STEP 2: Environment Configuration
# ============================================================================
echo -e "\n${BLUE}[2/6] Configuring environment...${NC}"

if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env file found. Creating from template...${NC}"

    if [ ! -f .env.template ]; then
        echo -e "${RED}✗ .env.template not found!${NC}"
        exit 1
    fi

    cp .env.template .env
    echo -e "${GREEN}✓ Created .env from template${NC}"

    echo -e "\n${YELLOW}================================================${NC}"
    echo -e "${YELLOW}IMPORTANT: Edit .env and set your credentials!${NC}"
    echo -e "${YELLOW}================================================${NC}"
    echo -e "Required changes:"
    echo -e "  - SECRET_KEY (generate random string)"
    echo -e "  - POSTGRES_PASSWORD (strong password)"
    echo -e "  - CALIBRE_PASSWORD (Calibre admin password)"
    echo -e "  - MINIO_SECRET_KEY (MinIO secret)"
    echo -e "  - MINIO_ROOT_PASSWORD (MinIO root password)"
    echo ""
    read -p "Press ENTER after editing .env, or Ctrl+C to exit..."
else
    echo -e "${GREEN}✓ .env file exists${NC}"
fi

# Validate required variables
source .env
REQUIRED_VARS=("POSTGRES_PASSWORD" "SECRET_KEY")
MISSING_VARS=()

for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo -e "${RED}✗ Missing required variables in .env:${NC}"
    for var in "${MISSING_VARS[@]}"; do
        echo -e "  - $var"
    done
    exit 1
fi

echo -e "${GREEN}✓ Environment configured${NC}"

# ============================================================================
# STEP 3: Build Docker Images
# ============================================================================
echo -e "\n${BLUE}[3/6] Building Docker images...${NC}"

cd docker
docker compose build --no-cache
echo -e "${GREEN}✓ Images built successfully${NC}"

# ============================================================================
# STEP 4: Start Services
# ============================================================================
echo -e "\n${BLUE}[4/6] Starting services...${NC}"

docker compose up -d

echo "Waiting for services to be healthy..."
sleep 15

# Check service health
docker compose ps

echo -e "${GREEN}✓ Services started${NC}"

# ============================================================================
# STEP 5: Initialize MinIO Storage
# ============================================================================
echo -e "\n${BLUE}[5/6] Initializing MinIO storage...${NC}"

cd ..
if [ -f scripts/init_minio.py ]; then
    python3 scripts/init_minio.py || echo -e "${YELLOW}⚠ MinIO initialization failed (may already be initialized)${NC}"
    echo -e "${GREEN}✓ MinIO storage initialized${NC}"
else
    echo -e "${YELLOW}⚠ scripts/init_minio.py not found, skipping...${NC}"
fi

# ============================================================================
# STEP 6: Initialize Database
# ============================================================================
echo -e "\n${BLUE}[6/6] Initializing database...${NC}"

cd docker
docker compose exec -T web python scripts/init_database.py

echo -e "${GREEN}✓ Database initialized${NC}"

# ============================================================================
# DEPLOYMENT COMPLETE
# ============================================================================
echo -e "\n${GREEN}"
echo "============================================================"
echo "  ✓ DEPLOYMENT COMPLETE!"
echo "============================================================"
echo -e "${NC}"

echo -e "Access your GLEH instance:"
echo -e "  ${GREEN}Main Application:${NC}  http://localhost"
echo -e "  ${GREEN}Login:${NC}             admin / admin123"
echo -e "  ${GREEN}MinIO Console:${NC}     http://localhost:9001"
echo -e "  ${GREEN}Calibre GUI:${NC}       http://localhost:8080"
echo -e "  ${GREEN}Calibre-Web:${NC}       http://localhost:8083"
echo ""
echo -e "${YELLOW}IMPORTANT:${NC} Change the default admin password after first login!"
echo ""
echo -e "To stop the stack:"
echo -e "  cd docker && docker compose down"
echo ""
echo -e "To view logs:"
echo -e "  cd docker && docker compose logs -f"
echo ""
