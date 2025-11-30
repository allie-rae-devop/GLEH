# Calibre-Web Migration Guide

This guide walks through migrating from the custom ePubLib reader to Calibre-Web with Nginx reverse proxy authentication.

## Architecture Overview

```
User Request → Nginx → auth_request to Flask →
    ├─ Authenticated: Forward to Calibre-Web with X-Remote-User header
    └─ Not Authenticated: Redirect to Flask login page
```

## Step 1: Add Nginx Auth Endpoint to Flask

Add this route to `src/app.py` (place it near your other authentication routes):

```python
@app.route('/auth/check')
def nginx_auth_check():
    """
    Nginx auth_request endpoint.
    Returns 200 if user is authenticated, 401 if not.
    Adds X-Remote-User header for Calibre-Web SSO.
    """
    if current_user.is_authenticated:
        # Return 200 with username header for Calibre-Web
        response = make_response('', 200)
        response.headers['X-Remote-User'] = current_user.username
        return response
    else:
        # Return 401 - Nginx will redirect to login
        return make_response('Unauthorized', 401)
```

## Step 2: Nginx Configuration

Create or update your Nginx configuration file (e.g., `/etc/nginx/sites-available/gleh`):

```nginx
# Flask app upstream
upstream flask_app {
    server 127.0.0.1:5000;
}

# Calibre-Web upstream (update with your Docker container IP:port)
upstream calibre_web {
    server 127.0.0.1:8083;  # Change to your Calibre-Web address
}

server {
    listen 80;
    server_name localhost;  # Change to your domain

    # Increase buffer sizes for large ebook files
    client_max_body_size 100M;
    proxy_buffer_size 128k;
    proxy_buffers 4 256k;
    proxy_busy_buffers_size 256k;

    # Flask app - main application
    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Calibre-Web - protected by Flask authentication
    location /calibre/ {
        # Check authentication with Flask
        auth_request /auth/check;
        auth_request_set $remote_user $upstream_http_x_remote_user;

        # If not authenticated, redirect to Flask login
        error_page 401 = @error401;

        # Pass to Calibre-Web with authentication header
        proxy_pass http://calibre_web/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Critical: Pass username to Calibre-Web for SSO
        proxy_set_header X-Remote-User $remote_user;

        # WebSocket support for Calibre-Web live updates
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # Timeouts for large file downloads
        proxy_read_timeout 300;
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
    }

    # Internal auth_request location
    location = /auth/check {
        internal;
        proxy_pass http://flask_app/auth/check;
        proxy_pass_request_body off;
        proxy_set_header Content-Length "";
        proxy_set_header X-Original-URI $request_uri;
    }

    # Redirect to login on auth failure
    location @error401 {
        return 302 /login?next=$request_uri;
    }
}
```

## Step 3: Configure Calibre-Web for SSO

In your Calibre-Web Docker container or configuration:

1. **Enable Reverse Proxy Authentication**:
   - Admin → Settings → Basic Configuration → Enable "Reverse Proxy Login"
   - Set "Reverse Proxy Header Name" to `X-Remote-User`

2. **Docker Environment Variables** (if using Docker):
   ```yaml
   environment:
     - CALIBRE_ENABLE_PROXY_AUTH=true
     - CALIBRE_PROXY_HEADER=X-Remote-User
   ```

## Step 4: Remove Old Ebook Code from Flask

### A. Update `requirements.txt`

Remove these lines:
```
ebooklib
beautifulsoup4
```

### B. Remove Routes from `src/app.py`

Delete or comment out these routes (lines 857-1052):
- `@app.route('/reader/<uid>')` (line 857)
- `@app.route('/api/reading-progress/<uid>', methods=['GET'])` (line 873)
- `@app.route('/api/reading-progress/<uid>', methods=['POST'])` (line 893)
- `@app.route('/api/ebook/<uid>')` and related (lines 917-1052)

### C. Keep Database Models (Optional)

You can **keep** the `Ebook` and `ReadingProgress` models if:
- You want to maintain your existing ebook catalog in Flask
- You plan to sync or link ebook metadata between Flask and Calibre

Or **remove** them if Calibre-Web will be your sole ebook manager.

### D. Update Templates

In `templates/textbook.html` and `templates/index.html`, update ebook links:

**Old:**
```html
<a href="/reader/{{ ebook.uid }}">
```

**New:**
```html
<a href="/calibre/book/{{ ebook.id }}">
```

Or better yet, create a redirect route in Flask that maps your ebook UIDs to Calibre book IDs.

### E. Delete Template File

Remove `templates/reader.html` - it's no longer needed.

## Step 5: Create Flask → Calibre Book ID Mapping

If you want to maintain your existing ebook catalog in Flask and just use Calibre-Web as the reader:

```python
@app.route('/read/<uid>')
def read_ebook(uid):
    """Redirect to Calibre-Web for this ebook"""
    ebook = Ebook.query.filter_by(uid=uid).first_or_404()

    # Map your ebook to Calibre book ID
    # This assumes you've stored the Calibre book ID in your database
    # OR you can search Calibre's database for matching title/path

    if ebook.calibre_book_id:
        return redirect(f'/calibre/book/{ebook.calibre_book_id}')
    else:
        flash('This book is not available in Calibre-Web yet', 'warning')
        return redirect(url_for('textbook'))
```

Add `calibre_book_id` column to Ebook model:
```python
class Ebook(db.Model):
    # ... existing fields ...
    calibre_book_id = db.Column(db.Integer, nullable=True)  # Calibre book ID
```

## Step 6: Testing Checklist

- [ ] Flask `/auth/check` endpoint returns 200 with username when logged in
- [ ] Flask `/auth/check` endpoint returns 401 when not logged in
- [ ] Nginx redirects unauthenticated users to Flask login page
- [ ] Nginx passes `X-Remote-User` header to Calibre-Web
- [ ] Calibre-Web auto-logs in users via SSO
- [ ] Users can read ebooks in Calibre-Web
- [ ] Ebook links on Flask pages redirect correctly to Calibre-Web
- [ ] Progress tracking works (if using Calibre's built-in tracking)

## Benefits of This Architecture

1. **Centralized Auth**: Flask handles all authentication
2. **Better Reader**: Calibre-Web is a mature, feature-rich ebook reader
3. **No Maintenance**: No custom ebook parsing code to maintain
4. **Automatic Updates**: Calibre library management tools
5. **Format Support**: Calibre handles EPUB, MOBI, AZW3, PDF, CBZ, etc.
6. **Reading Features**: Annotations, highlights, bookmarks, dictionary lookups

## Rollback Plan

If you need to rollback:
1. Re-add `ebooklib` and `beautifulsoup4` to requirements.txt
2. Restore the deleted routes in app.py
3. Restore reader.html template
4. Remove Nginx configuration
5. Run `pip install -r requirements.txt`

## Notes

- Keep database models if you want dual catalog support
- Reading progress tracking can be handled by Calibre-Web natively
- Consider migrating your ebook metadata to Calibre's database for full integration
- You can run both systems in parallel during migration for testing
