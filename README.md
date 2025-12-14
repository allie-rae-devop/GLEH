# GLEH - Gammons Landing Educational Hub

[![Release](https://img.shields.io/badge/release-v1.0-blue.svg)](https://github.com/allie-rae-devop/GLEH/releases)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)

**🎉 Public Demo Now Available:** [LINK TO PUBLIC DEMO]

---

## 🤖 AI Acknowledgment & Origin Story

This project began as an "AI vibe coding" experiment—a personal challenge to see what could be built through conversational prompting with an AI assistant.

**The Original Intent:** I needed a simple internal tool to organize and manage my paid and copyrighted educational content, particularly courses from MIT OpenCourseWare and various technical textbooks. What started as a basic script to ingest and catalog these materials quickly evolved into something much larger.

**The Evolution:** As the project grew, it transformed from a quick utility into a passion project and a technical proving ground. The question became: *Could a full-stack web application—complete with database design, API architecture, frontend UI, Docker orchestration, and production deployment—be built, debugged, and refined almost entirely through AI-assisted development?*

**The Answer:** You're looking at it.

**Credit Where Credit is Due:** This application was built in partnership with **Claude AI** (Anthropic), which served as the primary coding partner throughout the entire development lifecycle—from initial architecture decisions to debugging production deployment issues on a Raspberry Pi.

This README marks the official 1.0 release. The experiment worked.

---

![Main Dashboard](assets/main.png)

---

## About GLEH

**GLEH** (Gammons Landing Educational Hub) is a self-hosted learning management system designed for individuals and small institutions who want complete control over their educational content. Built with a Docker-first architecture, GLEH combines course management, e-book library integration, and user progress tracking into a single, cohesive platform.

### Key Features

**📚 Course Management**

- Host unlimited video-based courses with organized module structure
- Automatic course scanning and thumbnail generation
- Progress tracking with completion percentages
- Student note-taking during video playback
- Admin panel for course upload, organization, and deletion

**📖 Integrated E-Book Library**

- Full Calibre and Calibre-Web integration via OPDS feed
- Support for EPUB, PDF, MOBI, and other ebook formats
- Built-in EPUB reader with persistent reading progress
- Cover image display with automatic thumbnail generation
- Guest access support for public book browsing

**👤 User Management**

- Role-based access control (Admin/Student)
- Individual user profiles with learning history
- Bookmark management and course enrollment tracking
- Single sign-on (SSO) integration with Calibre-Web
- Batch user creation for classrooms

**🔧 Administration Panel**

- Five-tab admin interface (Dashboard, Courses, Users, Diagnostics, About)
- Real-time system health monitoring
- Log viewer with filtering capabilities
- Environment variable editor
- Self-healing diagnostics for common issues
- WYSIWYG editor for About page content

**🐳 Production-Ready Infrastructure**

- Docker Compose orchestration with five containerized services
- Nginx reverse proxy with intelligent rate limiting
- PostgreSQL database with automated backups
- Health checks and automatic container restart policies
- Resource limits and network isolation

---

## Credits

**MIT OpenCourseWare:** This project was inspired by and designed around organizing content from [MIT OpenCourseWare](https://ocw.mit.edu/), a web-based publication of virtually all MIT course content. MIT OCW is open and available to the world and is a permanent MIT activity. We are grateful for their commitment to open education and the free sharing of knowledge.

**Calibre & Calibre-Web:** E-book management powered by [Calibre](https://calibre-ebook.com/) and [Calibre-Web](https://github.com/janw/calibre-web).

---

## Installation & Usage

### Prerequisites

- **Docker & Docker Compose** - [Install Docker](https://docs.docker.com/get-docker/)
- **Minimum System Requirements:**
  - 2 CPU cores
  - 4GB RAM
  - 20GB disk space
- **Operating System:** Linux, macOS, Windows (with WSL2), or Raspberry Pi OS

---

### 1. Clone the Repository

```bash
git clone https://github.com/allie-rae-devop/GLEH
cd GLEH/
```

### 2. Configure Environment

```bash
# Copy template and edit with your settings
cp docker/.env.template docker/.env
nano docker/.env
```

**Important variables to change:**

- `SECRET_KEY` - Generate a random secret key for Flask sessions
- `POSTGRES_PASSWORD` - Set a strong database password
- `CALIBRE_PASSWORD` - Set password for Calibre Desktop access

### 3. Generate SSL Certificates

**Required for Calibre Desktop HTTPS access:**

```bash
cd docker/nginx
bash generate_ssl.sh
cd ..  # Back to docker/ directory
```

This creates self-signed SSL certificates for Calibre Desktop. Your browser will show a security warning—click "Advanced" and "Accept the Risk" to proceed.

### 4. Start the Stack

```bash
# Make sure you're in the docker/ directory
docker compose up -d
```

This will start five services:

- `edu-web` - Flask application server
- `edu-postgres` - PostgreSQL database
- `edu-nginx` - Nginx reverse proxy
- `edu-calibre` - Calibre Desktop (ebook management)
- `edu-calibre-web` - Calibre-Web (web interface for ebooks)

### 5. Initialize Database

```bash
# Wait for services to be healthy
docker compose ps

# Initialize database and create admin user
docker exec edu-web python scripts/init_database.py
```

### 6. Upload Content (Courses and Ebooks)

#### 6.1. Upload Content via FTP/SFTP

Use your preferred FTP/SFTP client (FileZilla, WinSCP, etc.) to upload content to your server:

```bash
# Create upload directories on your server
cd ~
mkdir -p upload/courses/
mkdir -p upload/books/
cd upload/
```

Upload your files:

- **Course materials** (MIT OCW, etc.) → `~/upload/courses/`
- **Ebooks (EPUB, PDF, MOBI)** → `~/upload/books/`

#### 6.2. Copy Courses into Docker Volume

```bash
docker cp courses/. edu-web:/app/data/courses/
```

Log into the admin panel at `http://YOUR_IP:3080/admin`, go to the Courses tab, and click "Scan Courses" and "Generate Thumbnails."

#### 6.3. Import Ebooks into Calibre

Calibre manages its own database, so books must be imported through Calibre Desktop:

```bash
# Create ingress folder for Calibre imports
docker exec edu-calibre mkdir -p /config/ingress

# Copy books to ingress folder
docker cp books/. edu-calibre:/config/ingress/

# Access Calibre Desktop to import books:
# 1. Open: https://YOUR_IP:3443
# 2. Login (Username: abc, Password: from .env CALIBRE_PASSWORD)
# 3. Click "Add books"
# 4. Navigate up two directories and choose /config/ingress
# 5. Select all books and import
# 6. Calibre will organize them and update the database automatically
```

### 7. Access the Application

- **Main App:** `http://YOUR_IP:3080`
- **Admin Panel:** `http://YOUR_IP:3080/admin`
- **Calibre Desktop:** `https://YOUR_IP:3443` (Username: `abc`, Password: from `.env`)
- **Calibre-Web:** `http://YOUR_IP:8083`

**Default Admin Login:**

- Username: `admin`
- Password: `admin123`

⚠️ **IMPORTANT:** Change the default password immediately after first login!

**⚠️ CRITICAL - Calibre Desktop Access:**

- ✅ **CORRECT:** `https://YOUR_IP:3443` (Nginx SSL proxy)
- ❌ **WRONG:** Port 8080 (will show "HTTPS required" error)
- Port 8080 is for internal Docker networking only

### 8. Configure Calibre-Web Settings

**IMPORTANT:** After first deployment, configure Calibre-Web to enable SSO and guest access.

1. **Access Calibre-Web:** `http://YOUR_IP:8083`

2. **Login with default credentials:**
   - Username: `admin`
   - Password: `admin123`
   - ⚠️ Change this password immediately!

3. **Navigate to Admin Panel:**
   - Click your username (top right) → "Admin"

4. **Enable Reverse Proxy Authentication:**
   - Go to: "Admin" → "Basic Configuration" → "Feature Configuration"
   - Find "Reverse Proxy Authentication"
   - Set **Reverse Proxy Header Name:** `X-Remote-User`
   - Click "Save"

5. **Enable Guest Access:**
   - Go to: "Admin" → "Basic Configuration" → "Feature Configuration"
   - Enable "Anonymous Browsing"
   - Click "Save"

6. **Configure Guest User Permissions:**
   - Go to: "Admin" → "Edit Users" → Select "Guest" user
   - Enable:
     - ✅ Allow Browse
     - ✅ Allow Read Books
     - ✅ Allow Download
     - ✅ Show Detail Random
   - Click "Save"

7. **Enable E-Reader Features:**
   - Go to: "Admin" → "Basic Configuration" → "Feature Configuration"
   - Enable "E-Book Viewer"
   - Enable "E-Book Conversion"
   - Click "Save"

8. **Point to Calibre Library:**
   - Go to: "Admin" → "Basic Configuration" → "Database Configuration"
   - Set "Database Path:" `/books/metadata.db`
   - Click "Save" and restart when prompted

9. **Verify Integration:**
   - Go to GLEH homepage: `http://YOUR_IP:3080`
   - You should see featured textbooks with cover images
   - Click "Launch Book" - should open in reader (no login required for guests)

---

### Troubleshooting

For comprehensive troubleshooting, deployment guides, and advanced configuration, see the full documentation:

**📖 [Full Deployment Guide & Troubleshooting](docker/DOCKER_DEPLOYMENT.md)**

Common quick fixes:

**Check service status:**
```bash
docker compose ps
```

**View logs:**
```bash
docker logs edu-web -f
docker logs edu-nginx -f
```

**Database not initialized:**
```bash
docker exec edu-web python scripts/init_database.py
```

**Containers won't start:**
```bash
docker compose down
docker compose up -d
```

---

## Gallery

![Course Launch Page](assets/course-launch.png)

![User Profile](assets/user-profile.png)

![Textbook Reader](assets/textbook.png)

![Courses Page](assets/courses.png)

![Admin Panel](assets/admin-panel.png)

---

## Support & Documentation

- **Issues & Bug Reports:** [GitHub Issues](https://github.com/allie-rae-devop/GLEH/issues)
- **Full Deployment Guide:** [docker/DOCKER_DEPLOYMENT.md](docker/DOCKER_DEPLOYMENT.md)
- **Admin Panel Documentation:** [docs/admin-panel-readme.md](docs/admin-panel-readme.md)

---

## License

See [LICENSE](LICENSE) file for details.

---

**Built with Flask, Docker, PostgreSQL, and Calibre**
**Developed in partnership with Claude AI**
