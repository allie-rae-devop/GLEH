#!/bin/bash

################################################################################
# GLEH Docker Entrypoint Script
# Handles database migrations, initialization, and application startup
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DB_RETRIES=5
DB_RETRY_INTERVAL=5

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}GLEH - Starting Application${NC}"
echo -e "${GREEN}================================================${NC}"

# ============================================================================
# DATABASE CONNECTIVITY CHECK
# ============================================================================
echo -e "${YELLOW}Checking database connectivity...${NC}"

if [ -z "$DATABASE_URL" ]; then
    echo -e "${YELLOW}WARNING: DATABASE_URL not set, using SQLite${NC}"
else
    # Extract DB host from DATABASE_URL
    DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\).*/\1/p')
    DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\).*/\1/p')

    # Default PostgreSQL port if not specified
    DB_PORT=${DB_PORT:-5432}

    echo "Database: $DB_HOST:$DB_PORT"

    # Retry logic for database connectivity
    RETRY_COUNT=0
    while [ $RETRY_COUNT -lt $DB_RETRIES ]; do
        if nc -z $DB_HOST $DB_PORT 2>/dev/null; then
            echo -e "${GREEN}✓ Database is accessible${NC}"
            break
        else
            RETRY_COUNT=$((RETRY_COUNT + 1))
            if [ $RETRY_COUNT -lt $DB_RETRIES ]; then
                echo -e "${YELLOW}Database not ready, retrying in ${DB_RETRY_INTERVAL}s (${RETRY_COUNT}/${DB_RETRIES})${NC}"
                sleep $DB_RETRY_INTERVAL
            else
                echo -e "${RED}✗ Failed to connect to database after ${DB_RETRIES} attempts${NC}"
                exit 1
            fi
        fi
    done
fi

# ============================================================================
# STORAGE INITIALIZATION
# ============================================================================
echo -e "${YELLOW}Initializing storage...${NC}"

# Create necessary directories if using local storage
if [ "$STORAGE_TYPE" = "local" ] || [ -z "$STORAGE_TYPE" ]; then
    STORAGE_BASE=${LOCAL_COURSES_DIR%/courses}  # Remove /courses suffix
    mkdir -p "$LOCAL_COURSES_DIR" "$LOCAL_EBOOKS_DIR" "$LOCAL_UPLOADS_DIR"
    echo -e "${GREEN}✓ Storage directories initialized${NC}"
fi

# ============================================================================
# DATABASE MIGRATIONS
# ============================================================================
echo -e "${YELLOW}Running database migrations...${NC}"

cd /app

# Check if this is the first run (no migrations directory)
if [ ! -d "app/migrations" ]; then
    echo -e "${YELLOW}First run detected, initializing migrations...${NC}"
    python -m flask db init || echo -e "${YELLOW}Migrations already initialized${NC}"
fi

# Run pending migrations
if python -m flask db upgrade 2>&1 | tee /tmp/migration.log; then
    echo -e "${GREEN}✓ Database migrations completed${NC}"
else
    if grep -q "No such table" /tmp/migration.log 2>/dev/null; then
        echo -e "${YELLOW}Database appears uninitialized, creating schema...${NC}"
        python -m flask shell << 'EOF'
from app.src.database import db
db.create_all()
print("✓ Database schema created")
EOF
    else
        echo -e "${RED}✗ Database migration failed${NC}"
        exit 1
    fi
fi

# ============================================================================
# INITIAL DATA POPULATION (Optional)
# ============================================================================
# Uncomment if you want to auto-populate content on first run
# echo -e "${YELLOW}Scanning for content...${NC}"
# python app/src/build.py || echo "Content scan failed or no content found"

# ============================================================================
# APPLICATION STARTUP
# ============================================================================
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✓ All checks passed, starting application${NC}"
echo -e "${GREEN}================================================${NC}"

# Execute the command passed to the container
exec "$@"
