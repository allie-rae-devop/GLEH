# GLEH - Gammons Landing Educational Hub

A production-ready, self-hosted educational platform for managing courses and e-books with integrated ebook library management.

**Status:** 🟢 Production Ready - v2.0
**Last Updated:** December 12, 2024
**Version:** 2.0

---

## What is GLEH?

GLEH is a self-hosted learning management system that provides:

- **Course Management** - Host and deliver video-based courses with progress tracking
- **E-Book Library** - Integrated Calibre-Web OPDS feed for ebook management
- **User Profiles** - Track learning progress, take notes, and manage bookmarks
- **Admin Panel** - Comprehensive admin interface for content and user management

**Perfect for:** Home labs, educational institutions, personal learning environments, or anyone who wants to self-host their educational content.

---

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- 2GB RAM minimum
- 10GB disk space

### Deployment

```bash
# 1. Clone the repository
git clone https://github.com/your-org/GLEH.git
cd GLEH

# 2. Generate SSL certificates (for Calibre Desktop)
cd docker/nginx && bash generate_ssl.sh && cd ..

# 3. Start all services
docker-compose up -d

# 4. Initialize database
docker exec edu-web python scripts/init_database.py

# 5. Access the application
# Main App: http://localhost:3080
# Calibre Desktop: https://localhost:3443 (user: abc, password: changeme)
# Login: admin / admin123 (⚠️ CHANGE ALL DEFAULT PASSWORDS!)
```

That's it! For detailed deployment instructions, see [docker/DOCKER_DEPLOYMENT.md](docker/DOCKER_DEPLOYMENT.md).

---

## Features

### For Students

- **Course Enrollment** - Browse and enroll in video-based courses
- **Progress Tracking** - Automatic progress tracking with completion status
- **Note Taking** - Take notes while watching courses
- **E-Book Reader** - Read EPUBs and PDFs with persistent reading progress
- **Personal Profile** - Manage your profile, view learning history

### For Administrators

- **Dashboard** - System overview with quick access to all services
- **Course Management** - Upload, scan, delete, and manage course content
- **User Management** - Full CRUD operations, password reset, seed test users
- **Diagnostics** - System health monitoring, logs viewer, self-healing checks
- **About Page Editor** - WYSIWYG editor for managing about content
- **Environment Config** - Edit .env variables directly from web UI

Full admin panel documentation: [docs/admin-panel-readme.md](docs/admin-panel-readme.md)

---

## Architecture

### Technology Stack

**Backend:**
- Flask 3.1.2 (Python web framework)
- PostgreSQL 15 (Database)
- SQLAlchemy (ORM)
- Waitress (WSGI server)

**Frontend:**
- Bootstrap 5 (Dark theme)
- EPUB.js (E-book reader)
- Vanilla JavaScript

**Infrastructure:**
- Docker & Docker Compose
- Nginx (Reverse proxy)
- Calibre & Calibre-Web (Ebook management)

### Service Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Web Browser                        │
│         http://localhost:3080                        │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│         Nginx (edu-nginx) - Port 3080               │
│  • Rate limiting                                    │
│  • Static file serving                              │
│  • Reverse proxy                                    │
└─────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────┐
│       Flask App (edu-web) - Port 5000               │
│  • Authentication & sessions                        │
│  • Course & user management                         │
│  • API endpoints                                    │
│  • Admin panel                                      │
└─────────────────────────────────────────────────────┘
         │                    │
         ▼                    ▼
┌──────────────────┐   ┌──────────────────┐
│   PostgreSQL     │   │   Calibre-Web    │
│  (edu-postgres)  │   │ (edu-calibre-web)│
│   Port 5432      │   │   Port 8083      │
└──────────────────┘   └──────────────────┘
```

### Docker Volumes

All data is stored in Docker-managed volumes:

- **edu-postgres-data** - PostgreSQL database (users, courses, progress)
- **edu-calibre-library** - Calibre ebook library and metadata
- **edu-courses** - Course content (videos, HTML)
- **edu-app-logs** - Application logs

---

## Project Structure

```
GLEH/
├── src/                       # Flask application source
│   ├── app.py                 # Main Flask app
│   ├── admin_api.py           # Admin panel endpoints
│   ├── models.py              # Database models
│   ├── calibre_client.py      # Calibre-Web OPDS integration
│   └── config.py              # Configuration
│
├── templates/                 # Jinja2 HTML templates
│   ├── admin.html             # Admin panel (5 tabs)
│   ├── index.html             # Homepage
│   ├── course.html            # Course player
│   └── reader.html            # E-book reader
│
├── static/                    # CSS, JavaScript, images
│   ├── css/
│   ├── js/
│   └── images/
│
├── scripts/                   # Utility scripts
│   └── init_database.py       # Database initialization
│
├── docker/                    # Docker configuration
│   ├── docker-compose.yml     # Service orchestration
│   ├── Dockerfile             # Flask container
│   ├── .env.template          # Environment template
│   ├── deploy.sh              # Deployment script
│   ├── status.sh              # Health check script
│   ├── nginx/
│   │   └── nginx.conf         # Nginx configuration
│   └── DOCKER_DEPLOYMENT.md   # Deployment guide
│
├── docs/                      # Documentation
│   └── admin-panel-readme.md  # Admin panel guide
│
└── README.md                  # This file
```

---

## Configuration

All configuration is done via environment variables in `docker/.env.template`:

```env
# Ports
NGINX_PORT=3080
CALIBRE_PORT=8080
CALIBRE_WEB_PORT=8083

# Database
DB_NAME=edu_db
DB_USER=edu_user
DB_PASSWORD=change_me_in_production

# Flask
FLASK_ENV=production
SECRET_KEY=change_me_in_production

# Calibre-Web Integration
CALIBRE_WEB_URL=http://calibre-web:8083
CALIBRE_WEB_EXTERNAL_URL=http://localhost:8083
```

Copy `.env.template` to `.env` and customize for your deployment.

---

## Administration

### Access URLs

- **Main App**: http://localhost:3080
- **Calibre Desktop**: https://localhost:3443 (Username: `abc`, Password: `changeme`)
- **Calibre-Web**: http://localhost:8083
- **Admin Panel**: http://localhost:3080/admin

**Note:** Calibre Desktop uses HTTPS on port 3443. Your browser will show a security warning for the self-signed certificate - click "Advanced" and "Accept the Risk" to proceed.

### Default Credentials

- **Username**: admin
- **Password**: admin123

⚠️ **IMPORTANT**: Change the default password immediately after first login!

### Managing Content

**Upload Courses:**
1. Go to Admin Panel → Courses tab
2. Drag and drop course .zip files
3. Click "Scan Course Directory" to detect new content

**Add E-books:**
1. Access Calibre Desktop at port 8080
2. Add books using the Calibre interface
3. Books automatically appear in GLEH via OPDS feed

**Manage Users:**
1. Go to Admin Panel → Users tab
2. Create, edit, or delete user accounts
3. Reset passwords or seed test users

Full guide: [docs/admin-panel-readme.md](docs/admin-panel-readme.md)

---

## Deployment

### Production Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Change `DB_PASSWORD` to a strong password
- [ ] Change default admin password (admin123)
- [ ] Change `CALIBRE_PASSWORD`
- [ ] Update `CALIBRE_WEB_EXTERNAL_URL` to your domain
- [ ] Configure SSL certificates (optional)
- [ ] Set up automated backups for Docker volumes
- [ ] Configure firewall rules

### Backup & Restore

```bash
# Backup PostgreSQL
docker-compose exec db pg_dump -U edu_user edu_db > backup.sql

# Backup Calibre library
docker run --rm -v edu-calibre-library:/source -v ./backups:/backup \
  busybox tar czf /backup/calibre.tar.gz -C /source .

# Backup Courses
docker run --rm -v edu-courses:/source -v ./backups:/backup \
  busybox tar czf /backup/courses.tar.gz -C /source .
```

Full deployment guide: [docker/DOCKER_DEPLOYMENT.md](docker/DOCKER_DEPLOYMENT.md)

---

## Updating

```bash
# Pull latest code
git pull

# Rebuild and restart
cd docker
docker-compose build
docker-compose up -d

# Check status
docker ps --filter "name=edu-"
```

---

## Troubleshooting

### Check Service Status

```bash
cd docker
./status.sh    # Linux/Mac
status.bat     # Windows
```

### View Logs

```bash
docker-compose logs -f        # All services
docker logs edu-web -f        # Flask app
docker logs edu-nginx -f      # Nginx
docker logs edu-postgres -f   # Database
```

### Common Issues

**Database not initialized:**
```bash
docker exec edu-web python scripts/init_database.py
```

**Containers won't start:**
```bash
docker-compose down
docker-compose up -d
```

**Port conflicts:**
Edit `docker/.env` and change `NGINX_PORT=3080` to another port.

---

## Development

### Local Development Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run Flask locally (development only)
cd src
flask run
```

### Testing

```bash
# Run tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

---

## Changelog

### December 12, 2024 - v2.0 Production Release ✅

**Major Updates:**
- Complete Admin Panel v2.0 with 5-tab interface
- Docker-first deployment with edu-* naming convention
- Removed deprecated MinIO storage
- Production-ready with comprehensive documentation
- Self-healing diagnostics and monitoring
- Environment configuration editor

**Documentation:**
- [docker/DOCKER_DEPLOYMENT.md](docker/DOCKER_DEPLOYMENT.md) - Deployment guide
- [docs/admin-panel-readme.md](docs/admin-panel-readme.md) - Admin panel guide

---

## Contributing

```bash
# Fork the repository
git clone https://github.com/your-username/GLEH.git

# Create a feature branch
git checkout -b feature/your-feature

# Make changes and test
docker-compose up -d
pytest tests/ -v

# Commit and push
git commit -m "Description of changes"
git push origin feature/your-feature

# Create a pull request
```

---

## License

See LICENSE file for details.

---

## Support

- **Documentation**: [docker/DOCKER_DEPLOYMENT.md](docker/DOCKER_DEPLOYMENT.md)
- **Admin Guide**: [docs/admin-panel-readme.md](docs/admin-panel-readme.md)
- **Issues**: https://github.com/your-org/GLEH/issues

---

**Built with ❤️ using Flask, Docker, and Calibre**
