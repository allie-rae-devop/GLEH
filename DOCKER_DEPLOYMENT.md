# GLEH Docker Deployment Guide

## Quick Start (Production)

### 1. Clone the Repository

```bash
git clone <your-repo-url> /opt/gleh
cd /opt/gleh
```

### 2. Configure Environment

```bash
# Copy template and edit with your settings
cp .env.template .env
nano .env
```

**Important variables to change:**
- `SECRET_KEY` - Generate a random secret key
- `POSTGRES_PASSWORD` - Set a strong database password
- `CALIBRE_PASSWORD` - Set Calibre admin password
- `MINIO_SECRET_KEY` - Set MinIO secret key
- `MINIO_ROOT_PASSWORD` - Set MinIO root password

### 3. Start the Stack

```bash
cd docker
docker-compose up -d
```

### 4. Initialize Database

```bash
# Wait for services to be healthy
docker-compose ps

# Initialize database and create admin user
docker-compose exec web python scripts/init_database.py
```

### 5. Initialize MinIO Storage

```bash
# Create storage buckets and folder structure
python scripts/init_minio.py
```

### 6. Access the Application

- **GLEH**: http://localhost (or your server IP)
- **Admin Login**: admin / admin123 (CHANGE THIS!)
- **MinIO Console**: http://localhost:9001
- **Calibre-Web**: http://localhost:8083

---

## Local Development

### 1. Setup Environment

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure for local development
cp .env.template .env
```

Edit `.env` for local development:
```env
DATABASE_URL=sqlite:///
CALIBRE_WEB_URL=http://localhost:8083
MINIO_ENDPOINT=localhost:9000
```

### 2. Start External Services

```bash
# Start MinIO and Calibre-Web via Docker
cd docker
docker-compose up -d minio calibre calibre-web
```

### 3. Initialize Database

```bash
python scripts/init_database.py
```

### 4. Run Development Server

```bash
python -m flask run
```

Access at http://localhost:5000

---

## Service URLs

| Service | Development | Docker Stack | Production |
|---------|-------------|--------------|------------|
| GLEH Web App | localhost:5000 | localhost | your-domain.com |
| PostgreSQL | - | localhost:5432 | (internal) |
| MinIO API | localhost:9000 | localhost:9000 | (internal) |
| MinIO Console | localhost:9001 | localhost:9001 | your-domain.com/minio |
| Calibre GUI | localhost:8080 | localhost:8080 | (internal) |
| Calibre-Web | localhost:8083 | localhost:8083 | (internal) |

---

## Troubleshooting

### Stack won't start
```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Rebuild if needed
docker-compose build --no-cache
docker-compose up -d
```

### Database connection errors
```bash
# Verify PostgreSQL is healthy
docker-compose ps db

# Check database logs
docker-compose logs db

# Reinitialize database
docker-compose exec web python scripts/init_database.py
```

### Static files not loading
```bash
# Verify static files were copied
docker-compose exec web ls -la /app/static

# Rebuild with static files
docker-compose build web
docker-compose up -d web
```

### MinIO bucket not found
```bash
# Reinitialize MinIO
python scripts/init_minio.py

# Or create manually in console: http://localhost:9001
```

---

## Production Checklist

Before deploying to production:

- [ ] Change all default passwords in .env
- [ ] Set `FLASK_ENV=production`
- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY`
- [ ] Enable HTTPS (`MINIO_SECURE=true`)
- [ ] Configure Nginx SSL certificates
- [ ] Set up automated backups (PostgreSQL, MinIO)
- [ ] Configure firewall rules
- [ ] Set up monitoring/logging
- [ ] Document disaster recovery procedures

---

## Backup & Restore

### Backup

```bash
# Backup PostgreSQL
docker-compose exec db pg_dump -U gleh_user gleh_db > backup-$(date +%Y%m%d).sql

# Backup MinIO data
docker run --rm -v gleh-minio-data:/source -v ./backups:/backup \
  busybox tar czf /backup/minio-$(date +%Y%m%d).tar.gz -C /source .

# Backup Calibre library
docker run --rm -v gleh-calibre-library:/source -v ./backups:/backup \
  busybox tar czf /backup/calibre-$(date +%Y%m%d).tar.gz -C /source .
```

### Restore

```bash
# Restore PostgreSQL
docker-compose exec -T db psql -U gleh_user gleh_db < backup.sql

# Restore MinIO
docker run --rm -v gleh-minio-data:/dest -v ./backups:/backup \
  busybox tar xzf /backup/minio-backup.tar.gz -C /dest

# Restore Calibre
docker run --rm -v gleh-calibre-library:/dest -v ./backups:/backup \
  busybox tar xzf /backup/calibre-backup.tar.gz -C /dest
```

---

## Updating GLEH

```bash
# Pull latest code
git pull

# Rebuild containers
cd docker
docker-compose build

# Restart services
docker-compose up -d

# Run any new migrations
docker-compose exec web python scripts/init_database.py
```
