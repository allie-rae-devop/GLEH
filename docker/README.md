# GLEH Docker Deployment

This directory contains the Docker configuration for GLEH (Gammons Landing Educational Hub).

## Quick Start

**For deployment instructions, see the root directory documentation:**

- **Quick Start:** [README_DEPLOYMENT.md](../README_DEPLOYMENT.md) - One-command deployment
- **Detailed Guide:** [DOCKER_DEPLOYMENT.md](../DOCKER_DEPLOYMENT.md) - Complete deployment documentation
- **Main README:** [README.md](../README.md) - Project overview

## One-Command Deployment

From the project root:

```bash
# Linux/Mac
./deploy.sh

# Windows
deploy.bat
```

The deployment script automatically:

- Checks Docker prerequisites
- Creates `.env` from template
- Builds all Docker images
- Starts all 5 services (PostgreSQL, Calibre, Calibre-Web, Flask, Nginx)
- Creates database and admin user
- Initializes Docker volumes

## Services

This Docker Compose stack includes:

- **web** - Flask application (Waitress WSGI server)
- **nginx** - Nginx reverse proxy and static file server
- **db** - PostgreSQL database
- **calibre** - Calibre ebook server
- **calibre-web** - Calibre-Web ebook management UI

## Configuration

Configuration is managed through `.env` file in the project root.

See [.env.template](../.env.template) for all available options.

## Common Operations

```bash
# Start services
cd docker && docker compose up -d

# Stop services
cd docker && docker compose down

# View logs
cd docker && docker compose logs -f

# Rebuild and restart
cd docker && docker compose build && docker compose up -d
```

## Testing Fresh Deployments

```bash
# Clean up (keeps volumes - fast re-testing)
./cleanup.sh    # Linux/Mac
cleanup.bat     # Windows

# Redeploy
./deploy.sh
```

## Documentation

All documentation is in the project root:

- [README_DEPLOYMENT.md](../README_DEPLOYMENT.md) - Quick deployment guide
- [DOCKER_DEPLOYMENT.md](../DOCKER_DEPLOYMENT.md) - Detailed deployment guide
- [README.md](../README.md) - Project overview and features
- [.env.template](../.env.template) - Environment configuration reference

---

**For complete deployment instructions, return to the project root and read [README_DEPLOYMENT.md](../README_DEPLOYMENT.md)**
