# GLEH - Quick Deployment Guide

## One-Command Installation

```bash
# Clone the repository
git clone <your-repo-url> /opt/gleh
cd /opt/gleh

# Run deployment script
./deploy.sh    # Linux/Mac
deploy.bat     # Windows
```

That's it! The script handles everything automatically.

## What the Deployment Script Does

1. ✅ Checks Docker is installed
2. ✅ Creates `.env` from template
3. ✅ Prompts you to set passwords
4. ✅ Builds all Docker images
5. ✅ Starts all 6 services
6. ✅ Initializes MinIO storage
7. ✅ Creates database and admin user

## After Deployment

Access your instance:
- **GLEH App**: http://localhost
- **Login**: admin / admin123 ⚠️ **CHANGE THIS!**
- **MinIO Console**: http://localhost:9001
- **Calibre-Web**: http://localhost:8083

## Testing Fresh Deployments

```bash
# Complete cleanup (removes everything!)
./cleanup.sh    # Linux/Mac
cleanup.bat     # Windows

# Redeploy from scratch
./deploy.sh
```

## Manual Steps (If Not Using Script)

1. **Configure**: `cp .env.template .env` and edit
2. **Deploy**: `cd docker && docker compose up -d`
3. **Init Storage**: `python scripts/init_minio.py`
4. **Init Database**: `docker compose exec web python scripts/init_database.py`

## Environment Variables to Change

Edit `.env` before deployment:
- `SECRET_KEY` - Random string for Flask
- `POSTGRES_PASSWORD` - Database password
- `CALIBRE_PASSWORD` - Calibre admin password
- `MINIO_SECRET_KEY` - MinIO API secret
- `MINIO_ROOT_PASSWORD` - MinIO console password

See `.env.template` for all options.

## Production Checklist

- [ ] Strong passwords in `.env`
- [ ] `FLASK_ENV=production`
- [ ] `DEBUG=False`
- [ ] HTTPS enabled
- [ ] Backups configured
- [ ] Firewall rules set

For detailed documentation, see [DOCKER_DEPLOYMENT.md](DOCKER_DEPLOYMENT.md)
