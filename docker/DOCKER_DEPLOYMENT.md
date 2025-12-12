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

### 3. Generate SSL Certificates

**Required for Calibre Desktop HTTPS access:**

```bash
cd docker/nginx
bash generate_ssl.sh
```

This creates:
- `ssl/calibre.crt` - SSL certificate
- `ssl/calibre.key` - Private key

**Note:** These are self-signed certificates. Your browser will show a security warning. Click "Advanced" and "Accept the Risk" to proceed.

### 4. Start the Stack

```bash
cd docker
docker-compose up -d
```

### 5. Initialize Database

```bash
# Wait for services to be healthy
docker-compose ps

# Initialize database and create admin user
docker-compose exec web python scripts/init_database.py
```

### 6. Access the Application

- **GLEH Web App**: http://localhost:3080 (or your server IP)
- **Admin Login**: admin / admin123 (⚠️ CHANGE THIS!)
- **Calibre Desktop**: https://localhost:3443 (Username: `abc`, Password: from `CALIBRE_PASSWORD` in .env)
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

### 1. Database User Configuration

**Issue:** Flask app can't connect to PostgreSQL, or manual `psql` commands fail with "role does not exist"

**Root Cause:** The database user in `.env` doesn't match what you're using in commands.

**Solution:**

1. Check what user PostgreSQL actually created:
```bash
docker exec edu-postgres psql -U postgres -c "\du"
```

2. Verify your `.env` matches:
```bash
cat docker/.env | grep DB_USER
```

3. **IMPORTANT:** All manual database commands must use the SAME user as `.env`:
```bash
# If DB_USER=edu_user in .env:
docker exec edu-postgres psql -U edu_user -d edu_db -c "SELECT * FROM \"user\";"

# If DB_USER=admin in .env:
docker exec edu-postgres psql -U admin -d edu_db -c "SELECT * FROM \"user\";"
```

4. Flask app automatically uses the correct user from `.env` - verify it works:
```bash
docker exec edu-web python -c "from src.models import db, User; from src.app import app; app.app_context().push(); print(f'Users: {User.query.count()}')"
```

**Recommended:** Use `DB_USER=edu_user` in `.env` to match documentation.

### 2. Calibre Desktop Authentication

**Issue:** Browser keeps asking for username/password for Calibre Desktop, credentials won't work

**Root Cause:** LinuxServer Calibre container uses HTTP Basic Authentication with a fixed username.

**Solution:**

**Username:** `abc` (LinuxServer default - NOT configurable)
**Password:** Value of `CALIBRE_PASSWORD` from your `.env` file

```bash
# Check your Calibre password:
grep CALIBRE_PASSWORD docker/.env

# Or check inside the container:
docker exec edu-calibre printenv PASSWORD
```

**Access URLs:**
- **HTTP (port 8080):** http://localhost:8080 - Works but redirects to HTTPS
- **HTTPS (port 3443):** https://localhost:3443 - Use this for Calibre Desktop VNC interface

### 3. Calibre Desktop SSL/HTTPS Access

**Issue:** Browser shows `SSL_ERROR_RX_RECORD_TOO_LONG` or "Secure Connection Failed" when accessing Calibre

**Root Cause:** Calibre's VNC interface (Selkies) requires HTTPS, but you're accessing HTTP or SSL certificates aren't configured.

**Solution:**

1. **Generate SSL certificates** (if not done):
```bash
cd docker/nginx
bash generate_ssl.sh
```

2. **Access via HTTPS on port 3443:**
```
https://localhost:3443
```

3. **Accept the self-signed certificate warning:**
   - Click "Advanced"
   - Click "Accept the Risk and Continue"

4. **Login with:**
   - Username: `abc`
   - Password: (from `CALIBRE_PASSWORD` in `.env`)

**Why HTTPS is required:** Calibre Desktop uses Selkies for WebRTC-based VNC access, which requires secure connections.

### 4. Stack Won't Start

```bash
# Check service status
docker-compose ps

# View logs
docker-compose logs -f

# Rebuild if needed
docker-compose build --no-cache
docker-compose up -d
```

### 5. Database Connection Errors

```bash
# Verify PostgreSQL is healthy
docker-compose ps db

# Check database logs
docker-compose logs db

# Verify database user (use YOUR DB_USER from .env):
docker exec edu-postgres psql -U edu_user -d edu_db -c "SELECT version();"

# Reinitialize database
docker-compose exec web python scripts/init_database.py
```

### 6. Static Files Not Loading

```bash
# Verify static files were copied
docker exec edu-web ls -la /app/static

# Rebuild with static files
docker-compose build web
docker-compose up -d web
```

### 7. Services Running But Flask Not Responding

**Check Flask is actually running:**
```bash
# Check Flask logs
docker logs edu-web --tail 50

# Verify health endpoint
curl http://localhost:3080/health

# Check internal Flask port
curl http://localhost:5000/health
```

**If Flask is down:**
```bash
# Restart Flask container
docker restart edu-web

# Check for Python errors
docker logs edu-web --tail 100
```

### 8. Port Already In Use

**Error:** "Bind for 0.0.0.0:3080 failed: port is already allocated"

**Solution:**
```bash
# Option 1: Change port in .env
nano docker/.env
# Change NGINX_PORT=3080 to another port

# Option 2: Kill process using the port
sudo lsof -ti:3080 | xargs kill -9
```

### 9. Permission Denied Errors

**For course uploads or log files:**
```bash
# Fix volume permissions
docker exec edu-web chown -R edu:edu /app/data/courses /app/logs

# Or recreate volumes with correct permissions
docker-compose down
docker volume rm edu-courses edu-app-logs
docker-compose up -d
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