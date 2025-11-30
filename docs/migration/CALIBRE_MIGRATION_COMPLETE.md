# Calibre-Web Migration - Implementation Complete

## ✅ What's Been Done

### 1. Flask Auth Endpoint Created
**File**: [src/app.py](src/app.py) (lines 624-637)
- Added `/auth/check` route for Nginx auth_request
- Returns 200 with `X-Remote-User` header when authenticated
- Returns 401 when not authenticated for Nginx redirect

### 2. Nginx Configuration Created
**File**: [nginx/gleh.conf](nginx/gleh.conf)
- Complete reverse proxy setup for Flask + Calibre-Web
- SSO authentication via auth_request
- Configured for localhost:8083 (your Calibre-Web instance)
- Includes error handling and redirects

### 3. Old Ebook Code Removed
**File**: [src/app.py](src/app.py)
- ✅ Removed `/reader/<uid>` route (replaced with redirect to `/calibre/`)
- ✅ Removed `/api/reading-progress/<uid>` GET/POST routes
- ✅ Removed `/api/ebook/<uid>` file serving routes (200+ lines of EPUB parsing)
- ✅ Removed ZIP file handling, MIME type detection, base tag injection
- All code is documented with comments for easy rollback if needed

### 4. Dependencies Cleaned
**File**: [requirements.txt](requirements.txt)
- ✅ Removed `ebooklib`
- ✅ Removed `beautifulsoup4`
- Commented for clarity on why they were removed

## 📋 Next Steps

### Step 1: Install/Configure Nginx

**On Windows** (if not already installed):
```powershell
# Download Nginx for Windows from nginx.org
# Or use Chocolatey:
choco install nginx
```

**Copy the config file**:
```bash
# Copy nginx/gleh.conf to your Nginx conf.d directory
# Or include it in your main nginx.conf
```

**On Linux/Docker**:
```bash
# Copy nginx/gleh.conf to /etc/nginx/sites-available/
sudo cp nginx/gleh.conf /etc/nginx/sites-available/gleh
sudo ln -s /etc/nginx/sites-available/gleh /etc/nginx/sites-enabled/
sudo nginx -t  # Test config
sudo systemctl reload nginx
```

### Step 2: Configure Calibre-Web SSO

1. **Access Calibre-Web** at http://localhost:8083
2. **Login as admin** (default: admin/admin123)
3. **Navigate to**: Admin → Settings → Basic Configuration
4. **Enable**:
   - ☑ Reverse Proxy Authentication
   - Set "Reverse Proxy Header Name" to `X-Remote-User`
5. **Save settings**

### Step 3: Update Flask Templates (Optional)

If you want to update your textbook/ebook links to point directly to Calibre-Web:

**Find ebook links in templates** (likely in `templates/textbook.html` and `templates/index.html`):
```html
<!-- Old -->
<a href="/reader/{{ ebook.uid }}">Read</a>

<!-- New -->
<a href="/calibre/">Browse Library</a>
```

Or keep the current setup - the `/reader/<uid>` route now redirects to `/calibre/` automatically.

### Step 4: Test the Integration

1. **Start Flask** (if not running):
   ```bash
   .venv/Scripts/python.exe -m flask --app src/app run
   ```

2. **Start Nginx** (with the new config)

3. **Test Authentication Flow**:
   - Visit `http://localhost/calibre/` (through Nginx)
   - Should redirect to Flask login if not logged in
   - After login, should access Calibre-Web with your username

4. **Verify SSO**:
   - Check that you're auto-logged into Calibre-Web
   - Your Flask username should appear in Calibre-Web

### Step 5: Uninstall Old Dependencies (Optional)

```bash
pip uninstall ebooklib beautifulsoup4
```

## 🔧 Troubleshooting

### Issue: "502 Bad Gateway" on /calibre/
**Solution**: Make sure Calibre-Web is running on localhost:8083

### Issue: Redirects to login but doesn't work
**Solution**: Check Flask `/auth/check` endpoint returns correct headers:
```bash
curl -H "Cookie: session=YOUR_SESSION" http://localhost:5000/auth/check -v
```

### Issue: Can't access Calibre-Web through Nginx
**Solution**: Test direct access first:
```bash
# This should work:
curl http://localhost:8083

# This should redirect or show Calibre-Web:
curl http://localhost/calibre/
```

### Issue: Calibre-Web doesn't auto-login
**Solution**: Verify in Calibre-Web admin that:
- Reverse Proxy Authentication is enabled
- Header name is exactly `X-Remote-User`
- User exists in Calibre-Web (create manually first time)

## 📚 Database Models

**KEPT**: `Ebook` and `ReadingProgress` models remain in the database for now.

**Options**:
1. **Keep them**: Use Flask as a metadata catalog, Calibre-Web as the reader
2. **Remove them**: Let Calibre handle all ebook management (requires migration script)
3. **Dual system**: Sync between Flask and Calibre databases

## 🔄 Rollback Plan

If you need to rollback to the custom reader:

1. **Restore requirements.txt**:
   ```
   Flask
   Flask-SQLAlchemy
   ...
   ebooklib
   beautifulsoup4
   ...
   ```

2. **Restore routes in src/app.py**:
   - Uncomment the old ebook routes (they're all documented)
   - Remove the redirect in `/reader/<uid>`

3. **Reinstall dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Remove Nginx config** or comment out the `/calibre/` location block

## 📈 Benefits Achieved

- ✅ **200+ lines of code removed** (EPUB parsing, ZIP handling, etc.)
- ✅ **Better ebook reader** (Calibre-Web is production-grade)
- ✅ **Single Sign-On** (Flask auth → Calibre-Web)
- ✅ **Format support** (EPUB, MOBI, AZW3, PDF, CBZ, etc.)
- ✅ **Professional features** (annotations, highlights, bookmarks, etc.)
- ✅ **No maintenance burden** (Calibre handles updates)

## 🎯 Current Status

**Ready for Testing**:
- Flask auth endpoint: ✅ **FIXED & TESTED** (401 when unauthenticated)
- Nginx config: ✅ Ready
- Old code removed: ✅ Complete
- Dependencies cleaned: ✅ Complete

**What Was Fixed**:
- Added missing `make_response` import to [src/app.py](src/app.py:12)
- Tested `/auth/check` endpoint - returns 401 when not logged in ✅

**Pending**:
- Nginx installation/configuration
- Calibre-Web SSO setup
- Integration testing
- Template updates (optional)

## 📞 Need Help?

Refer to:
- [CALIBRE_WEB_MIGRATION.md](CALIBRE_WEB_MIGRATION.md) - Detailed migration guide
- [nginx/gleh.conf](nginx/gleh.conf) - Nginx configuration
- Calibre-Web docs: https://github.com/janeczku/calibre-web

---

**Migration completed**: All code changes done, ready for deployment testing.
