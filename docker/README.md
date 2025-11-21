# GLEH Docker Compose Setup

Production-ready Docker Compose configuration for GLEH (Gammons Landing Educational Hub).

## Quick Start

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env with your configuration
# Set your data paths:
# CONTENT_DIR=../data/gleh
# Or individual paths:
# LOCAL_COURSES_DIR=../data/gleh/courses
# LOCAL_EBOOKS_DIR=../data/gleh/ebooks
# LOCAL_UPLOADS_DIR=../data/gleh/uploads

# 3. Create data directories
mkdir -p ../data/gleh/{courses,ebooks,uploads}
mkdir -p ../data/postgres

# 4. Start services
docker-compose up

# Visit: http://localhost
```

## Services

### Flask Application (`web`)
- **Port:** 5000 (internal), accessed via Nginx
- **Image:** Custom built from `Dockerfile`
- **Environment:** Configured via `.env`
- **Volumes:** `/data/gleh` (courses, ebooks, uploads)
- **Health Check:** `GET /health` endpoint

### PostgreSQL Database (`db`)
- **Port:** 5432
- **Image:** `postgres:15-alpine`
- **Credentials:** From `.env` (`DB_USER`, `DB_PASSWORD`)
- **Volumes:** `postgres_data` (persistent database)
- **Health Check:** pg_isready

### Nginx Reverse Proxy (`nginx`)
- **Ports:** 80 (HTTP), 443 (HTTPS - configure for production)
- **Image:** `nginx:alpine`
- **Config:** `nginx/nginx.conf`
- **Static Files:** Serves `/app/static` directly
- **Health Check:** `GET /health`

## Configuration

### Environment Variables (.env)

#### Flask Application
```env
FLASK_ENV=development              # development, production
FLASK_HOST=0.0.0.0                # Listen on all interfaces
FLASK_PORT=5000                   # Internal port (not exposed)
SECRET_KEY=your-secret-key        # Change in production!
DEBUG=False                        # Never true in production
```

#### Database
```env
DB_NAME=gleh_db
DB_USER=gleh_user
DB_PASSWORD=your_password          # Change in production!
DB_PORT=5432
DB_CONTAINER=gleh-postgres
```

#### Storage (choose one approach)

**Option 1: Simple CONTENT_DIR**
```env
STORAGE_TYPE=local
CONTENT_DIR=../data/gleh
```

**Option 2: Individual paths**
```env
STORAGE_TYPE=local
LOCAL_COURSES_DIR=../data/gleh/courses
LOCAL_EBOOKS_DIR=../data/gleh/ebooks
LOCAL_UPLOADS_DIR=../data/gleh/uploads
```

**Option 3: Samba (future)**
```env
STORAGE_TYPE=samba
SAMBA_HOST=192.168.1.100
SAMBA_USERNAME=your_user
SAMBA_PASSWORD=your_password
SAMBA_SHARE_COURSES=courses
SAMBA_SHARE_EBOOKS=ebooks
SAMBA_SHARE_UPLOADS=uploads
SAMBA_MOUNT_BASE=/mnt/samba
```

#### Nginx
```env
NGINX_PORT=80                     # HTTP port
NGINX_HTTPS_PORT=443              # HTTPS port (configure for production)
```

#### Logging
```env
LOG_LEVEL=INFO                    # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_JSON_FORMAT=true              # Structured logging
```

## Usage

### Start Services

```bash
# Development (attached logs)
docker-compose up

# Production (detached)
docker-compose up -d

# With specific environment
FLASK_ENV=production docker-compose up -d
```

### Stop Services

```bash
# Stop and remove containers (keep volumes)
docker-compose down

# Stop and remove everything (including data!)
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web       # Flask app
docker-compose logs -f db        # Database
docker-compose logs -f nginx     # Web server

# Last 100 lines
docker-compose logs --tail=100 web

# From specific time
docker-compose logs --since 2024-11-17T10:00:00 web
```

### Monitor Status

```bash
# Container status
docker-compose ps

# Resource usage
docker stats

# Service health
curl http://localhost/health
curl http://localhost/health/deep
```

### Database Operations

```bash
# Access database shell
docker exec -it gleh-postgres psql -U gleh_user -d gleh_db

# Run migrations
docker-compose exec web flask db upgrade

# Create tables
docker-compose exec web flask shell
# >>> from app.src.database import db
# >>> db.create_all()
# >>> exit()

# Backup database
docker exec gleh-postgres pg_dump -U gleh_user gleh_db > backup.sql

# Restore database
docker exec -i gleh-postgres psql -U gleh_user gleh_db < backup.sql
```

### Application Operations

```bash
# Run build script (scan & populate database)
docker-compose exec web python app/src/build.py

# Access Flask shell
docker-compose exec web flask shell

# View environment variables
docker-compose exec web env | sort

# Check storage configuration
docker-compose exec web python -c "
from app.src.storage import get_storage
import json
s = get_storage()
print(json.dumps(s.get_storage_info(), indent=2))
"
```

## Deployment

### Local Development

1. Copy `.env.example` to `.env`
2. Set `CONTENT_DIR` to your local data directory
3. Run `docker-compose up`
4. Visit http://localhost

### Production

#### Prerequisites
- SSL/TLS certificates for HTTPS
- Strong `SECRET_KEY` (generate with: `python -c "import os; print(os.urandom(24).hex())"`)
- Configured PostgreSQL database
- Secure password for DB user

#### Setup

1. **Configure Nginx for HTTPS:**
   ```bash
   # Copy SSL certificates to nginx/ssl/
   mkdir -p nginx/ssl/
   cp /path/to/cert.pem nginx/ssl/
   cp /path/to/key.pem nginx/ssl/

   # Uncomment HTTPS section in nginx/nginx.conf
   ```

2. **Set environment variables:**
   ```bash
   export FLASK_ENV=production
   export SECRET_KEY=your-random-secret-key
   export DB_PASSWORD=strong-password
   export DATABASE_URL=postgresql://user:password@db:5432/gleh_db
   ```

3. **Start services:**
   ```bash
   docker-compose up -d
   ```

4. **Verify health:**
   ```bash
   curl https://your-domain.com/health
   ```

### Scaling

For multiple instances (requires load balancer):

```yaml
# docker-compose.override.yml
services:
  web:
    deploy:
      replicas: 3
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs web

# Common issues:
# 1. Port already in use
docker-compose down
netstat -ano | findstr :80  # Windows
sudo lsof -i :80            # Mac/Linux

# 2. Database not ready
docker-compose logs db
# Wait for "database system is ready to accept connections"

# 3. Permission denied
chmod -R 755 ../data/
```

### Database connection failed

```bash
# Check database health
docker-compose ps db

# Check database logs
docker-compose logs db

# Test connection
docker-compose exec db pg_isready -U gleh_user

# Restart database
docker-compose restart db
```

### Static files not serving

```bash
# Check if volume is mounted
docker-compose exec nginx ls -la /app/static/

# Verify path in nginx.conf
cat nginx/nginx.conf | grep alias

# Rebuild Nginx
docker-compose build nginx
docker-compose up nginx
```

### Storage path issues

```bash
# Check mounted volumes
docker inspect gleh-web | grep Mounts

# Verify path exists on host
ls -la ../data/gleh/

# Check app's view of storage
docker-compose exec web python -c "
from app.src.storage import get_storage
print(get_storage().ensure_storage_ready())
"
```

## Maintenance

### Updates

```bash
# Update images
docker-compose pull

# Rebuild application
docker-compose build web

# Apply changes
docker-compose up -d
```

### Backup

```bash
# Backup database
docker-compose exec db pg_dump -U gleh_user gleh_db | gzip > backup-$(date +%Y%m%d).sql.gz

# Backup all data
tar -czf backup-$(date +%Y%m%d).tar.gz ../data/

# Backup Docker volumes
docker run --rm -v gleh_postgres_data:/data -v $(pwd):/backup alpine tar czf /backup/postgres-backup.tar.gz /data
```

### Cleanup

```bash
# Remove unused images
docker image prune -a

# Remove unused volumes
docker volume prune

# Clean build cache
docker builder prune
```

## Performance Tuning

### Database
```yaml
# docker-compose.yml
db:
  environment:
    POSTGRES_INITDB_ARGS: "-c shared_buffers=256MB -c effective_cache_size=1GB"
  deploy:
    resources:
      limits:
        memory: 2G
```

### Flask
```yaml
web:
  environment:
    FLASK_WORKERS: 4  # Gunicorn workers
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G
```

### Nginx
```conf
# nginx/nginx.conf
worker_processes auto;
worker_connections 2048;
```

## Security

- [ ] Change `DB_PASSWORD` from default
- [ ] Generate strong `SECRET_KEY`
- [ ] Enable `SESSION_COOKIE_SECURE=true` with HTTPS
- [ ] Configure SSL certificates
- [ ] Set `FLASK_ENV=production`
- [ ] Use environment variables for secrets (not `.env` file)
- [ ] Configure firewall rules
- [ ] Set resource limits (memory, CPU)
- [ ] Regular security updates: `docker-compose pull`

## Health Checks

Endpoints for monitoring:

- **Lightweight:** `GET /health` - Basic connectivity
- **Deep Check:** `GET /health/deep` - All components

```bash
# Quick check
curl http://localhost/health

# Full diagnostics
curl http://localhost/health/deep
```

## Documentation

- **Main Guide:** See `../MIGRATION_GUIDE.md`
- **Configuration:** See `.env.example`
- **Nginx Config:** See `nginx/nginx.conf`
- **Docker Docs:** https://docs.docker.com/
- **Docker Compose:** https://docs.docker.com/compose/

## Support

For issues or questions, refer to:
1. This README
2. `MIGRATION_GUIDE.md` in the project root
3. Docker logs: `docker-compose logs -f`
4. Health endpoints: `curl http://localhost/health/deep`

---

**Version:** 1.0
**Last Updated:** 2024-11-17
**Maintainer:** GLEH Development Team
