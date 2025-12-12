# GLEH Docker Deployment Guide

### 1. Clone the Repository

```bash
git clone <your-repo-url> /opt/gleh
cd /opt/gleh
```

### 2. Configure Environment

```bash
# Copy template and edit with your settings
cp docker/.env.template docker/.env
nano .env
```

**Important variables to change:**
- `SECRET_KEY` - Generate a random secret key
- `POSTGRES_PASSWORD` - Set a strong database password
- `CALIBRE_PASSWORD` - Set Calibre admin password

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

### 5. Access the Application

- **GLEH**: http://localhost:3080 (or your server IP)
- **Admin Login**: admin / admin123 (CHANGE THIS!)
- **Calibre-Web**: http://localhost:8083

---

## Service URLs

| Service | Development | Docker Stack | Production |
|---------|-------------|--------------|------------|
| GLEH Web App | localhost:5000 | localhost | your-domain.com |
| PostgreSQL  | - | localhost:5432 | (internal) |
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
---

## Production Checklist

Before deploying to production:

- [ ] Change all default passwords in .env
- [ ] Set `FLASK_ENV=production`
- [ ] Set `DEBUG=False`
- [ ] Generate strong `SECRET_KEY`
- [ ] Configure Nginx SSL certificates
- [ ] Set up automated backups (PostgreSQL)
- [ ] Configure firewall rules
- [ ] Set up monitoring/logging
- [ ] Document disaster recovery procedures

---

## Backup & Restore

### Backup

```bash
# Backup PostgreSQL
docker-compose exec db pg_dump -U edu_user edu_db > backup-$(date +%Y%m%d).sql

# Backup Calibre library
docker run --rm -v edu-calibre-library:/source -v ./backups:/backup \
  busybox tar czf /backup/calibre-$(date +%Y%m%d).tar.gz -C /source .

# Backup Courses
docker run --rm -v edu-courses:/source -v ./backups:/backup \
  busybox tar czf /backup/courses-$(date +%Y%m%d).tar.gz -C /source .
```

### Restore

```bash
# Restore PostgreSQL
docker-compose exec -T db psql -U edu_user edu_db < backup.sql

# Restore Calibre
docker run --rm -v edu-calibre-library:/dest -v ./backups:/backup \
  busybox tar xzf /backup/calibre-backup.tar.gz -C /dest

# Restore Courses
docker run --rm -v edu-courses:/dest -v ./backups:/backup \
  busybox tar xzf /backup/courses-backup.tar.gz -C /dest
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