# GLEH Admin Panel - User Guide

**Version**: 2.0 (Refactored for Calibre-Web Integration)
**Last Updated**: 2025-12-03
**Access URL**: http://localhost:3080/admin

---

## Table of Contents

1. [Overview](#overview)
2. [Access Requirements](#access-requirements)
3. [Dashboard Tab](#dashboard-tab)
4. [Courses Tab](#courses-tab)
5. [Diagnostics Tab](#diagnostics-tab)
6. [Users Tab](#users-tab)
7. [About Tab](#about-tab)
8. [Common Tasks](#common-tasks)
9. [Troubleshooting](#troubleshooting)

---

## Overview

The GLEH Admin Panel is a web-based control center for managing your educational platform. It provides comprehensive tools for:

- Managing environment configuration
- Uploading and organizing courses
- Running system diagnostics and maintenance scripts
- Managing user accounts and permissions
- Customizing the About page content

### What's New in Version 2.0

- **Removed**: Textbooks tab (now managed via Calibre-Web at port 8083)
- **Removed**: Layout Editor tab (deprecated)
- **Added**: Environment configuration editor in Dashboard
- **Added**: Course file upload with drag-and-drop
- **Added**: Self-healing diagnostics
- **Added**: Password reset functionality for users
- **Added**: About content editor
- **Enhanced**: Quick access links to Calibre services
- **Renamed**: "Server & Diagnostics" → "Diagnostics"

---

## Access Requirements

### Prerequisites

1. **Admin Account**: You must be logged in with an admin account
   - Default admin credentials (change after first login):
     - Username: `admin`
     - Password: `admin123`

2. **Running Services**: Ensure Docker containers are running:
   ```bash
   docker ps --filter "name=gleh-"
   ```

3. **Browser**: Modern web browser (Chrome, Firefox, Edge, Safari)

### Accessing the Admin Panel

1. Navigate to: http://localhost:3080
2. Log in with admin credentials
3. Click on your username → "Admin Panel" (or navigate to `/admin`)

---

## Dashboard Tab

The Dashboard provides an overview and quick access to key functionality.

### Statistics Cards

- **Courses**: Total number of courses in the database
- **Textbooks (Calibre-Web)**: Number of ebooks in Calibre-Web library
- **Users**: Total registered users

### Quick Access Links

Direct links to integrated services (open in new tabs):

- **Calibre Desktop (Port 8080)**: Desktop Calibre application web interface
  - Default password: `Camel100`
  - Use for: Adding ebooks, editing metadata, managing library

- **Calibre-Web (Port 8083)**: Web-based ebook reader and OPDS server
  - Use for: Reading ebooks, browsing library, OPDS feeds

### Environment Configuration

Manage your `.env` file variables directly from the admin panel.

#### How to Use

1. Click **"Load Configuration"** to view current environment variables
2. Edit variable values directly in the table
3. Click **"Save Changes"** to update the `.env` file
4. **Important**: Restart the server for changes to take effect

#### Adding/Removing Variables

- **Add New Variable**: Click "Add New Variable" button
- **Delete Variable**: Click the "Delete" button next to the variable
- **Rename Variable**: Edit the variable name in the first column

#### Important Variables

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Flask application secret key
- `CALIBRE_WEB_URL`: Internal URL for Calibre-Web API
- `CALIBRE_WEB_EXTERNAL_URL`: External URL for browser access to Calibre-Web

**Warning**: Incorrect configuration can break the application. Make backups before editing critical variables.

---

## Courses Tab

Manage MIT OpenCourseWare and custom course content.

### Course Upload

#### Drag & Drop Method

1. Prepare your course files as a `.zip` archive
2. Drag the file onto the upload area
3. Wait for upload to complete
4. Course will be extracted to the courses volume automatically

#### Browse Method

1. Click the upload area
2. Select a `.zip` file from your computer
3. Upload progress will be displayed
4. Auto-thumbnail generation triggered on success

#### Course File Structure

Your course ZIP should follow this structure:
```
course-name.zip
├── index.html          (main course page)
├── static/
│   ├── images/
│   ├── css/
│   └── js/
└── content/
    └── lecture files
```

### Bulk Operations

#### Scan Course Directory

- **Purpose**: Scan the courses volume for new course folders
- **When to Use**: After manually adding courses to the Docker volume
- **Result**: Shows total courses found, new vs. already imported

#### Generate Thumbnails

- **Purpose**: Generate thumbnail images for courses missing them
- **When to Use**: After bulk course import
- **Note**: Currently a placeholder - implement thumbnail extraction logic

#### Auto-Categorize

- **Purpose**: Automatically assign categories based on course titles
- **How It Works**: Scans titles for keywords (e.g., "Physics", "Computer Science")
- **Result**: Updates course categories in database

### Course Library Table

View and manage all courses in the system.

**Columns**:
- **Title**: Course name
- **Thumbnail**: Indicates if thumbnail exists (Yes/No badge)
- **Categories**: Assigned categories
- **Actions**: Delete button

#### Deleting Courses

1. Click "Delete" next to the course
2. Confirm deletion in the popup
3. Course removed from database (files remain in volume)

**Note**: To fully remove a course, also delete its folder from the Docker volume.

---

## Diagnostics Tab

System health monitoring, maintenance, and troubleshooting tools.

### System Status

Real-time status of critical components:

- **Server**: Always shows "Running" when panel is accessible
- **Database**: Connection status (OK/ERROR)
- **Courses Volume**: Accessibility status (OK/ERROR)
- **Courses Directory**: Path to the courses storage location

### Server Control

#### Restart Server

- **Button**: "Restart Server"
- **Action**: Displays restart instructions
- **Manual Command Required**:
  ```bash
  cd docker
  docker-compose restart web
  ```

**Why Manual?**: In Docker, the Flask app cannot restart its own container. Use this reminder to execute the restart command via CLI.

### Maintenance Scripts

Run critical maintenance scripts with one click.

#### Initialize Database

- **Script**: `init_database.py`
- **Purpose**: Create database tables and default admin user
- **When to Use**:
  - First-time setup
  - After database reset
  - When "relation does not exist" errors occur

#### Import Courses from Volume

- **Script**: `import_courses_from_volume.py`
- **Purpose**: Scan and import all courses from the gleh-courses volume
- **When to Use**:
  - After manually copying courses to the volume
  - When courses exist in volume but not in database

**Output**: Scripts display stdout/stderr in real-time. Green=success, Red=errors.

### Self-Healing Diagnostics

Automated health checks and repair suggestions.

**Checks Performed**:
1. **Database Connectivity**: Verifies PostgreSQL connection
2. **Courses Volume**: Checks if courses directory exists and is accessible
3. **Admin User**: Verifies admin account exists

**Click "Run Auto-Repair"** to execute all checks. Results show:
- ✅ **OK**: Component healthy
- ⚠️ **WARNING**: Component needs attention
- ❌ **ERROR**: Component failed with suggested fix

### System Diagnostics

Comprehensive system report:

- Database status (OK/ERROR)
- Course count in database
- User count in database
- Volume status and directory path

**Use Case**: Generate a health report before making major changes.

### Application Logs

View recent application logs for debugging.

**Log Location**:
- Docker: `/app/logs/app.log` (if volume mounted)
- Alternative: Use `docker logs gleh-web` command

**Features**:
- Displays last 50 log lines
- Auto-detects if log file not available
- Provides Docker command fallback

---

## Users Tab

Comprehensive user account management.

### Create New User

**Form Fields**:
- **Username**: 3-64 characters, alphanumeric with underscores/hyphens
- **Password**: Minimum 8 characters, must contain letters and numbers
- **Admin Checkbox**: Grant admin privileges

**Steps**:
1. Fill in username and password
2. Check "Admin" if user should have admin access
3. Click "Create User"
4. Page refreshes with new user added

### Seed Test Users

Quickly create 3 test accounts for development/testing.

**Click "Seed 3 Test Users"** to create:
- `testuser1` / password: `test123`
- `testuser2` / password: `test123`
- `testuser3` / password: `test123`

**Note**: Skips users that already exist.

### Users Table

View all registered users with management options.

**Columns**:
- **User ID**: Database primary key
- **Username**: Login username
- **Admin**: Yes/No indicator
- **Created**: Registration timestamp
- **Actions**: Reset Password / Delete buttons

**Protected Account**: The `admin` user cannot be deleted (shows "Admin (Protected)").

### Reset Password

Admin function to change any user's password.

**Steps**:
1. Click "Reset Password" next to the user
2. Enter new password in the modal
3. Click "Reset Password" to confirm
4. User can immediately log in with new password

**Use Cases**:
- User forgot their password
- Security incident requiring password change
- Testing password validation

### Delete User

Permanently remove a user account.

**Steps**:
1. Click "Delete" next to the user
2. Confirm deletion in the popup
3. User and all associated data removed from database

**What Gets Deleted**:
- User account
- Course progress records
- Course notes
- Reading progress
- Ebook notes

**Cannot Be Undone**: Ensure you have backups before deleting users.

---

## About Tab

Manage the content displayed on your public "About" page.

### Content Editor

Large text area supporting Markdown formatting.

**Markdown Examples**:
```markdown
# GLEH - Gammons Landing Educational Hub

## Mission Statement

Our platform provides **free access** to MIT OpenCourseWare and thousands of ebooks.

## Features

- Browse 2,000+ MIT OCW courses
- Read ebooks in your browser
- Track your progress
- Take notes on courses and books

[Contact Us](mailto:admin@example.com)
```

### How to Use

1. Click **"Load Content"** to fetch current About text
2. Edit the content in the text area
3. Click **"Save Content"** to persist changes
4. Content saved to `data/about_content.md`

**Note**: You'll need to create a public route to display this content on the frontend. The admin panel only manages the content storage.

---

## Common Tasks

### Initial Setup Checklist

After first deployment:

1. **Access Admin Panel**: http://localhost:3080/admin
2. **Change Admin Password**:
   - Go to Users tab
   - Reset password for `admin` user
   - Use a strong, unique password

3. **Configure Environment**:
   - Dashboard → Load Configuration
   - Verify `DATABASE_URL`, `SECRET_KEY`, etc.
   - Save changes if needed

4. **Import Courses**:
   - Diagnostics → Run "Import Courses from Volume"
   - Or Courses → Scan Course Directory

5. **Add Ebooks**:
   - Navigate to Calibre-Web (port 8083)
   - Upload and manage ebooks there

6. **Create Test Users**:
   - Users → Seed 3 Test Users
   - Test user registration and login

### Adding a New Course

**Method 1: Upload via Admin Panel**
1. Prepare course as `.zip` file
2. Courses tab → Drag & drop onto upload area
3. Wait for upload and extraction
4. Click "Scan Course Directory" to import

**Method 2: Docker Volume**
1. Copy course folder to gleh-courses volume:
   ```bash
   docker cp /path/to/course gleh-web:/app/data/courses/
   ```
2. Admin Panel → Courses → Scan Course Directory
3. Course appears in table

### Troubleshooting Database Issues

If you see "relation 'user' does not exist" or similar errors:

1. **Diagnostics** → Run "Initialize Database" script
2. Verify output shows table creation
3. Refresh admin panel
4. If still failing, run self-healing diagnostics

### Backing Up Configuration

Before making major changes:

1. **Export .env file**:
   ```bash
   docker cp gleh-web:/app/.env ./env-backup-$(date +%Y%m%d).txt
   ```

2. **Backup Database**:
   ```bash
   docker exec gleh-postgres pg_dump -U gleh_user gleh_db > backup.sql
   ```

3. **Backup Courses**:
   ```bash
   docker run --rm -v gleh-courses:/data -v $(pwd):/backup alpine tar czf /backup/courses-backup.tar.gz /data
   ```

---

## Troubleshooting

### Admin Panel Won't Load

**Symptoms**: 403 Forbidden or blank page

**Checks**:
1. Verify you're logged in as admin:
   ```sql
   docker exec gleh-postgres psql -U gleh_user -d gleh_db -c "SELECT username, is_admin FROM user;"
   ```
2. If admin user missing, run init_database.py
3. Clear browser cache and cookies
4. Check Flask logs: `docker logs gleh-web --tail 50`

### Environment Config Not Saving

**Symptoms**: Changes revert after clicking Save

**Fixes**:
1. Check file permissions on `.env`
2. Verify container has write access to `/app/.env`
3. Check Flask logs for permission errors
4. Restart container after saving

### Course Upload Fails

**Symptoms**: Upload progress bar shows error

**Checks**:
1. Verify `.zip` file is not corrupted
2. Check disk space: `docker exec gleh-web df -h`
3. Ensure courses volume is mounted:
   ```bash
   docker inspect gleh-web | grep -A 5 "Mounts"
   ```
4. Check max upload size in nginx config

### Scripts Won't Run

**Symptoms**: "Script not found" or timeout errors

**Fixes**:
1. Verify scripts exist:
   ```bash
   docker exec gleh-web ls -la /app/scripts/
   ```
2. Check script permissions (should be executable)
3. Increase timeout if script takes >5 minutes
4. Run script manually to see full output:
   ```bash
   docker exec gleh-web python scripts/init_database.py
   ```

### Self-Healing Shows Errors

**Database Connectivity Error**:
- Check if PostgreSQL container is running
- Verify DATABASE_URL in environment config
- Test connection: `docker exec gleh-postgres pg_isready`

**Courses Volume Error**:
- Verify volume exists: `docker volume ls | grep gleh-courses`
- Check volume mount in docker-compose.yml
- Recreate volume if needed (data loss warning)

**Admin User Warning**:
- Run Diagnostics → Initialize Database script
- Manually create admin in SQL if needed

### Users Can't Log In After Password Reset

**Symptoms**: "Invalid credentials" after reset

**Fixes**:
1. Verify password meets requirements (8+ chars, letter + number)
2. Check if user account exists in database
3. Try resetting password again
4. If persistent, delete and recreate user account

---

## Security Best Practices

### Admin Account

- Change default `admin` password immediately after deployment
- Use a password manager to generate strong passwords
- Don't share admin credentials with non-admin users

### Environment Variables

- Never commit `.env` files to Git
- Rotate `SECRET_KEY` periodically
- Use strong, unique passwords for database connections
- Store backups of `.env` securely (encrypted)

### User Management

- Only grant admin privileges to trusted users
- Regularly audit user list for inactive accounts
- Implement password policies (enforce via validation)
- Monitor admin panel access logs

### Server Access

- Restrict admin panel access via firewall rules (production)
- Use HTTPS in production (configure nginx with SSL)
- Keep Docker images and dependencies updated
- Regular security audits of exposed ports

---

## API Endpoints Reference

For developers integrating with the admin panel:

### Dashboard
- `GET /api/admin/status` - Dashboard statistics
- `GET /api/admin/env-config` - Load environment config
- `POST /api/admin/env-config` - Save environment config

### Courses
- `POST /api/admin/scan-courses` - Scan courses directory
- `GET /api/admin/get-courses` - List all courses
- `POST /api/admin/generate-thumbnails` - Generate thumbnails
- `POST /api/admin/autocategorize` - Auto-categorize courses
- `DELETE /api/admin/delete-course/<id>` - Delete a course
- `POST /api/admin/upload-course` - Upload course file

### Diagnostics
- `POST /api/admin/server/restart` - Restart server (returns instructions)
- `POST /api/admin/run-script` - Execute maintenance script
- `POST /api/admin/self-heal` - Run self-healing diagnostics
- `GET /api/admin/diagnostics` - System diagnostics report
- `GET /api/admin/logs` - Fetch application logs

### Users
- `GET /api/admin/users` - List all users
- `POST /api/admin/create-user` - Create new user
- `POST /api/admin/delete-user` - Delete user
- `POST /api/admin/reset-password` - Reset user password
- `POST /api/admin/seed-test-users` - Create test users

### About
- `GET /api/admin/about-content` - Load About content
- `POST /api/admin/about-content` - Save About content

**Authentication**: All endpoints require admin authentication and CSRF token.

---

## Support & Feedback

- **Documentation**: See `PROJECT_STATE.md` for system architecture
- **Issues**: https://github.com/anthropics/claude-code/issues
- **Updates**: Check release notes for new features and bug fixes

---

**End of Admin Panel User Guide**
