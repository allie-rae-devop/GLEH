# GLEH - Quick Deployment Guide

## One-Command Deployment

```bash
# Clone the repository
git clone <your-repo-url> GLEH
cd GLEH/docker

# Run deployment script
./deploy.sh    # Linux/Mac
deploy.bat     # Windows
```

That's it! The script handles everything automatically.

## What the Deployment Script Does

1. ✅ Checks Docker is installed and running
2. ✅ Validates configuration files
3. ✅ Stops any existing containers
4. ✅ Starts all services (PostgreSQL, Flask, Nginx, Calibre)
5. ✅ Waits for services to be healthy
6. ✅ Initializes database schema and admin user

## Quick Status Check

After deployment, verify everything is working:

```bash
cd docker
./status.sh    # Linux/Mac
status.bat     # Windows
```

This shows:
- Container health status
- Database connection and initialization
- Web application status
- Volume status
- Access URLs

## After Deployment

Access your instance:
- **GLEH App**: http://localhost:3080
- **Login**: `admin` / `admin123` ⚠️ **CHANGE THIS!**
- **Calibre**: http://localhost:8080
- **Calibre-Web**: http://localhost:8083

## Fresh Deployment (Wipe Data)

To completely reset and start fresh:

```bash
cd docker
./deploy.sh --fresh    # Linux/Mac
deploy.bat --fresh     # Windows
```

**WARNING**: This will delete all data including the database!

## Manual Deployment (Without Scripts)

If you prefer manual control:

```bash
# 1. Configure environment (optional - has sensible defaults)
cd docker
cp .env.template .env
# Edit .env with your settings

# 2. Start services
docker-compose up -d

# 3. Wait for PostgreSQL to be ready
docker exec gleh-postgres pg_isready -U gleh_user -d gleh_db

# 4. Initialize database
docker exec gleh-web python scripts/init_database.py

# 5. Verify deployment
docker ps --filter "name=gleh-"
curl http://localhost:3080/health
```

## Environment Configuration

### File Structure

- `docker/.env.template` - Template with defaults (in git)
- `docker/.env` - Your personal overrides (gitignored, optional)
- Root `.env` - Local Flask development only (gitignored)

### Key Variables

Edit `docker/.env` to customize:

```bash
# Ports (change if you have conflicts)
NGINX_PORT=3080
NGINX_HTTPS_PORT=3443
CALIBRE_PORT=8080
CALIBRE_WEB_PORT=8083

# Database
DB_NAME=gleh_db
DB_USER=gleh_user
DB_PASSWORD=change_me_in_production

# Security
SECRET_KEY=change_me_in_production

# Flask
FLASK_ENV=production
LOG_LEVEL=INFO
```

See `docker/.env.template` for all available options.

## Production Deployment Checklist

Before deploying to production:

### Security
- [ ] Generate strong `SECRET_KEY`: `python -c "import secrets; print(secrets.token_hex(32))"`
- [ ] Change `DB_PASSWORD` to strong random password
- [ ] Change default admin password after first login
- [ ] Change `CALIBRE_PASSWORD`
- [ ] Set `FLASK_ENV=production`

### Configuration
- [ ] Update `NGINX_PORT` if behind reverse proxy
- [ ] Configure SSL certificates (uncomment nginx SSL volume)
- [ ] Update `CALIBRE_WEB_EXTERNAL_URL` to your domain
- [ ] Review `LOG_LEVEL` (INFO or WARNING for production)

### Infrastructure
- [ ] Set up automated backups for Docker volumes:
  - `gleh-postgres-data` (database)
  - `gleh-calibre-library` (ebooks)
  - `gleh-courses` (course content)
- [ ] Configure firewall rules
- [ ] Set up monitoring/alerting
- [ ] Configure log rotation
- [ ] Test disaster recovery process

## Common Issues

### Issue: Database not initialized

**Symptoms**: "relation 'user' does not exist" error

**Solution**:
```bash
docker exec gleh-web python scripts/init_database.py
```

### Issue: Port conflicts

**Symptoms**: "address already in use" error

**Solution**: Edit `docker/.env` and change port numbers:
```bash
NGINX_PORT=8080
NGINX_HTTPS_PORT=8443
```

### Issue: Containers won't start

**Solution**:
```bash
# Check logs
docker-compose logs -f

# Full reset
docker-compose down
docker volume rm gleh-postgres-data  # WARNING: Deletes data!
docker-compose up -d
docker exec gleh-web python scripts/init_database.py
```

### Issue: Can't access app at localhost

**Symptoms**: Connection refused or timeout

**Check**:
1. Are containers running? `docker ps --filter "name=gleh-"`
2. Is Docker Desktop running? (Windows/Mac)
3. Firewall blocking ports? Test with `curl http://localhost:3080/health`
4. Check nginx logs: `docker logs gleh-nginx`

## Troubleshooting Tools

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker logs gleh-web -f
docker logs gleh-postgres -f
docker logs gleh-nginx -f
```

### Restart Services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart web
docker-compose restart nginx
```

### Access Container Shell
```bash
docker exec -it gleh-web bash
docker exec -it gleh-postgres psql -U gleh_user -d gleh_db
```

### Check Database
```bash
# List tables
docker exec gleh-postgres psql -U gleh_user -d gleh_db -c "\dt"

# Count users
docker exec gleh-postgres psql -U gleh_user -d gleh_db -c "SELECT COUNT(*) FROM \"user\""
```

## Docker Volumes

All data is stored in Docker-managed volumes (portable and efficient):

| Volume | Purpose | Backup Priority |
|--------|---------|-----------------|
| `gleh-postgres-data` | PostgreSQL database | **CRITICAL** |
| `gleh-calibre-library` | Ebook library & metadata | High |
| `gleh-courses` | MIT OCW course content | Medium |
| `gleh-app-logs` | Application logs | Low |

### Backup Volumes
```bash
# Backup database
docker run --rm -v gleh-postgres-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/postgres-backup.tar.gz /data

# Restore database
docker run --rm -v gleh-postgres-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/postgres-backup.tar.gz -C /
```

## Updating GLEH

```bash
# Pull latest code
git pull

# Rebuild and restart
cd docker
docker-compose up -d --build

# Database migration (if needed)
docker exec gleh-web python scripts/migrate_database.py
```

## Architecture Overview

- **gleh-postgres**: PostgreSQL 15 database
- **gleh-web**: Flask app (Python 3.11, Waitress WSGI server)
- **gleh-nginx**: Reverse proxy (serves static files, handles SSL)
- **gleh-calibre**: Calibre ebook management (optional)
- **gleh-calibre-web**: OPDS feed & web reader (optional)

## Additional Documentation

- **Architecture & Status**: [PROJECT_STATE.md](PROJECT_STATE.md) - Current system state & troubleshooting
- **Full Docker Guide**: [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md) - Detailed deployment documentation
- **Main README**: [README.md](README.md) - Project overview and features

## Getting Help

1. Check status: `./status.sh` or `status.bat`
2. Review logs: `docker-compose logs -f`
3. Read [PROJECT_STATE.md](PROJECT_STATE.md) for common issues
4. Create an issue on GitHub with:
   - Output of `./status.sh`
   - Relevant log excerpts
   - Steps to reproduce
