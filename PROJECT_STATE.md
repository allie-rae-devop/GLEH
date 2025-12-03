# GLEH Project State Documentation

**Last Updated**: 2025-12-03
**Purpose**: Quick reference for Claude to prevent debugging waste

## CRITICAL: Start-of-Session Checklist

Before making ANY changes, verify:

1. **Containers running?** `docker ps --filter "name=gleh-"`
2. **Database initialized?** `docker exec gleh-web python scripts/init_database.py`
3. **All volumes are Docker volumes** (NO bind mounts for data)
4. **Current directory** is `D:\GLEH` (project moved from `D:\AI Projects\GLEH`)

## Architecture Overview

### Services (docker-compose.yml)
- **gleh-postgres** - PostgreSQL 15 database
- **gleh-web** - Flask application (Python 3.11, Waitress server)
- **gleh-nginx** - Reverse proxy (serves static files)
- **gleh-calibre** - Calibre ebook management
- **gleh-calibre-web** - OPDS/web interface for ebooks

### Volumes (ALL must be Docker volumes, NOT bind mounts)

| Volume Name | Purpose | Type | Status |
|------------|---------|------|--------|
| `gleh-postgres-data` | PostgreSQL database | Docker volume | ✅ CORRECT |
| `gleh-app-logs` | Flask application logs | Docker volume | ✅ CORRECT |
| `gleh-calibre-library` | Calibre library & metadata | Docker volume | ✅ CORRECT |
| `gleh-courses` | MIT OCW course content | Docker volume | ✅ CORRECT |

**IMPORTANT**: The postgres_data volume was previously a bind mount to `data/postgres` which broke when project moved. Now fixed as proper Docker volume.

### Bind Mounts (Configuration files ONLY - acceptable)

| Mount | Purpose | Why bind mount is OK |
|-------|---------|---------------------|
| `./nginx/nginx.conf` | Nginx configuration | Version-controlled config, relative path from docker/ |
| `./nginx/conf.d/` | Nginx additional configs | Version-controlled, relative path |
| `../static` | Static assets | Version-controlled, mounted for development convenience |

**Key**: Bind mounts are acceptable for **configuration/source files** (in git), NOT for **runtime data**.

## Environment Configuration

### Structure (DO NOT CONFUSE THESE)

```
Root .env (gitignored)          → Local Flask development (SQLite)
  ├─ DATABASE_URL=sqlite:///
  ├─ CALIBRE_WEB_URL=http://10.0.10.75:8083
  └─ Used when running Flask directly (python src/app.py)

docker/.env.template (in git)    → Template for deployment
  ├─ DB_NAME=gleh_db
  ├─ CALIBRE_WEB_URL=http://calibre-web:8083
  └─ Generic values for fresh deployments

docker/.env (gitignored)         → Personal Docker overrides (optional)
  └─ If exists, overrides template values

docker-compose.yml environment   → Runtime values (highest priority)
  └─ These override everything when containers run
```

### How It Works

1. **Local Development** (not Docker):
   - Run: `python src/app.py`
   - Uses: Root `.env`
   - Database: SQLite at `instance/database.db`

2. **Docker Development** (current):
   - Run: `cd docker && docker-compose up`
   - Uses: `docker-compose.yml` environment variables
   - Database: PostgreSQL in `gleh-postgres-data` volume
   - Flask loads root `.env` but docker-compose environment variables override it

3. **Fresh Deployment**:
   ```bash
   git clone <repo>
   cd GLEH/docker
   cp .env.template .env      # Optional: customize settings
   docker-compose up -d
   docker exec gleh-web python scripts/init_database.py
   ```

## Common Issues & Solutions

### Issue 1: Database Not Initialized

**Symptoms**: "relation 'user' does not exist" error

**Solution**:
```bash
docker exec gleh-web python scripts/init_database.py
```

### Issue 2: Postgres Container Won't Start

**Symptoms**: Container exits immediately or shows "database does not exist" in healthcheck

**Root Causes**:
- Healthcheck using wrong database name
- Volume has stale bind mount configuration
- Old volume from moved project directory

**Solution**:
```bash
# Check if volume has old path
docker volume inspect gleh-postgres-data

# If needed, remove and recreate
docker-compose down
docker volume rm gleh-postgres-data
docker-compose up -d
docker exec gleh-web python scripts/init_database.py
```

### Issue 3: "No such file or directory" on Volume Mount

**Symptoms**: Error about `/run/desktop/mnt/host/d/AI Projects/GLEH/...`

**Root Cause**: Volume has old path from before project was moved

**Solution**: Remove the stale volume (see Issue 2)

### Issue 4: Changes to .env Not Taking Effect in Docker

**Root Cause**: Docker Compose uses `docker-compose.yml` environment section, NOT root `.env`

**Solution**: Edit `docker-compose.yml` or create `docker/.env` (not root `.env`)

## Database Initialization

The database must be initialized after first deployment:

```bash
docker exec gleh-web python scripts/init_database.py
```

This creates:
- All database tables (User, Course, Ebook, Progress, Notes, etc.)
- Default admin user (username: `admin`, password: `admin123`)

**IMPORTANT**: Change admin password after first login!

## Access URLs

| Service | URL | Credentials |
|---------|-----|-------------|
| GLEH Main App | http://localhost:3080 | admin / admin123 |
| Calibre Desktop | http://localhost:8080 | Password: Camel100 |
| Calibre-Web | http://localhost:8083 | (Configure on first run) |
| PostgreSQL | localhost:5432 | gleh_user / change_me_in_production |

## Project Structure

```
GLEH/
├── src/               # Flask application source
│   ├── app.py        # Main Flask app
│   ├── config.py     # Configuration classes
│   ├── models.py     # SQLAlchemy models
│   └── ...
├── templates/         # Jinja2 templates
├── static/           # CSS, JS, images (mounted to nginx)
├── scripts/          # Utility scripts
│   └── init_database.py  # Database initialization
├── docker/           # Docker configuration
│   ├── Dockerfile    # Flask app image
│   ├── docker-compose.yml
│   ├── .env.template # Template for deployment
│   └── nginx/        # Nginx configurations
├── .env              # Local development (gitignored)
├── .gitignore        # Ignores .env, data/, *.db, etc.
└── requirements.txt  # Python dependencies
```

## Deprecated/Removed Features

- ❌ MinIO object storage (replaced with Docker volumes)
- ❌ Samba network shares (public release uses local volumes only)
- ❌ Flask-Migrate (removed in cleanup, manual migrations)
- ❌ Bind mount for postgres data (now proper Docker volume)

## Development Workflow

### Making Changes to Code

1. Edit files locally in `src/`, `templates/`, `static/`
2. Rebuild Flask container: `cd docker && docker-compose up -d --build web`
3. Changes to templates/static are immediate (bind-mounted)

### Making Changes to Database Schema

1. Edit `src/models.py`
2. Rebuild container
3. Manual migration needed (no Flask-Migrate)

### Making Changes to Nginx Config

1. Edit `docker/nginx/nginx.conf` or `docker/nginx/conf.d/*.conf`
2. Reload nginx: `docker exec gleh-nginx nginx -s reload`
3. Or restart: `docker-compose restart nginx`

## Git Workflow

### What's in Git?
- ✅ Source code (`src/`, `templates/`, `static/`)
- ✅ Docker configs (`docker/Dockerfile`, `docker-compose.yml`)
- ✅ Environment templates (`.env.template`, `docker/.env.template`)
- ✅ Documentation (`.md` files)
- ✅ Requirements (`requirements.txt`)

### What's NOT in Git?
- ❌ Personal `.env` files
- ❌ Database files (`*.db`, `instance/`)
- ❌ Runtime data (`data/` directory)
- ❌ Docker volumes
- ❌ Virtual environments (`.venv/`)
- ❌ Large media files (course content, ebooks)
- ❌ IDE settings (`.idea/`, `.vscode/`)

## Troubleshooting Checklist

If app is not working:

1. ✅ Check all containers are running: `docker ps --filter "name=gleh-"`
2. ✅ Check container logs: `docker logs gleh-web --tail 50`
3. ✅ Verify database initialized: `docker exec gleh-postgres psql -U gleh_user -d gleh_db -c "\dt"`
4. ✅ Check healthchecks: `docker ps --format "table {{.Names}}\t{{.Status}}"`
5. ✅ Verify volumes are Docker volumes (not bind mounts): `docker volume ls | grep gleh`
6. ✅ Test database connection: `docker exec gleh-web python -c "from src.database import db; from src.app import app; app.app_context().push(); print('DB OK')"`

## Known Working State (2025-12-03)

- PostgreSQL: Running, healthy, initialized
- Flask: Running, healthy, serving on port 5000
- Nginx: Running, healthy, serving on ports 3080/3443
- Calibre/Calibre-Web: Running
- Database: Initialized with admin user
- All volumes: Proper Docker volumes (no bind mounts for data)

## Critical Reminders for Claude

1. **NEVER** create bind mounts for runtime data (database, logs, user uploads)
2. **ALWAYS** check if database is initialized before debugging "table doesn't exist" errors
3. **DON'T** confuse root `.env` (local dev) with docker environment (container runtime)
4. **DO** check `git ls-files | grep env` to verify what's tracked before editing .env files
5. **REMEMBER**: Project is at `D:\GLEH` (not `D:\AI Projects\GLEH`)
6. **VERIFY**: When user says "app was working before", check if database just needs init script
