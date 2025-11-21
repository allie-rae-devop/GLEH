# Production Deployment Checklist - AEGIS Phase 1

**Application**: Gammons Landing Educational Hub
**Implementation**: Session Security Hardening
**Environment**: Production
**Last Updated**: November 13, 2025

---

## Overview

This checklist ensures safe, verified deployment of session security hardening to production. It covers pre-deployment validation, deployment steps, post-deployment verification, and monitoring. Follow each step in order.

**Timeline**: 30-45 minutes
**Required Personnel**: 1 DevOps Engineer + 1 SRE (or combined role)
**Rollback Window**: 15 minutes

---

## Pre-Deployment Phase (Do This 24 Hours Before)

### 1. Code Review & Testing

- [ ] **Code review**: Verify config.py ProductionConfig has SESSION_COOKIE_SECURE=True, PERMANENT_SESSION_LIFETIME=3600
- [ ] **Code review**: Verify app.py main execution block has FLASK_ENV check and rejects production Flask dev server
- [ ] **Unit tests pass**: Run `pytest test_routes.py test_features.py -v`
- [ ] **Integration test**: Test session creation and timeout locally with FLASK_ENV=production

### 2. HTTPS Certificate Verification

- [ ] **Certificate issued**: Obtain SSL/TLS certificate for production domain (e.g., from Let's Encrypt, DigiCert)
- [ ] **Certificate location**: Store cert.pem and key.pem in `/etc/ssl/certs/` (or deployment-specific path)
- [ ] **Certificate validity**: Verify expiration date is > 30 days in the future
- [ ] **Certificate chain**: If intermediate CAs exist, download and verify the chain
- [ ] **Private key permissions**: Ensure key.pem is readable only by the app user: `chmod 400 /path/to/key.pem`

### 3. Environment Variable Setup

- [ ] **SECRET_KEY generated**: Use Python to generate: `python -c "import os; print(os.urandom(32).hex())"`
- [ ] **SECRET_KEY stored securely**: Add to production .env file or secrets manager (NOT git)
- [ ] **FLASK_ENV set**: Confirm FLASK_ENV=production in production environment
- [ ] **DATABASE_URL set**: Verify DATABASE_URL points to production database
- [ ] **No sensitive data in git**: Run `git log --all -S "SECRET_KEY" --source --remotes` to verify no secrets in history

**Example /home/appuser/.env (production)**:
```bash
FLASK_ENV=production
SECRET_KEY=a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1
DATABASE_URL=postgresql://gammons_user:STRONG_PASSWORD@prod-db.internal/gammons_prod
```

### 4. Server & Dependencies

- [ ] **Python 3.8+**: Confirm Python version: `python --version`
- [ ] **waitress installed**: `pip install waitress` (or verify in requirements.txt)
- [ ] **All dependencies installed**: `pip install -r requirements.txt`
- [ ] **Database migrated**: Run `flask db upgrade` to apply all migrations
- [ ] **Disk space**: Confirm sufficient disk space for logs (at least 10GB)

### 5. Network & Infrastructure

- [ ] **HTTPS port open**: Verify firewall allows 443/tcp inbound
- [ ] **Load balancer configured**: If behind load balancer, enable HTTPS passthrough or terminate
- [ ] **HSTS header optional**: Confirm web server or reverse proxy can add `Strict-Transport-Security: max-age=31536000` header (recommended)
- [ ] **DNS verified**: Confirm A/AAAA records point to production IP

### 6. Rollback Plan

- [ ] **Backup database**: Run `pg_dump gammons_prod > /backups/gammons_$(date +%Y%m%d_%H%M%S).sql`
- [ ] **Current config backed up**: Copy config.py and app.py to /backups/
- [ ] **Rollback script created**: Create a script to quickly revert config/app if needed
- [ ] **Team notified**: Inform on-call team of deployment window and rollback contact

---

## Deployment Phase (Execute During Maintenance Window)

### 7. Pre-Deployment Validation

```bash
# On production server

# 1. Verify environment
export FLASK_ENV=production
export SECRET_KEY=$(cat /path/to/secret_key.env)
export DATABASE_URL=$(cat /path/to/db_url.env)

# 2. Test app startup with waitress (dry run, don't bind yet)
waitress-serve --help | grep -q "waitress" && echo "OK: waitress installed"

# 3. Verify config is correct
python -c "
from app import app
print('SESSION_COOKIE_SECURE:', app.config['SESSION_COOKIE_SECURE'])
print('SESSION_COOKIE_HTTPONLY:', app.config['SESSION_COOKIE_HTTPONLY'])
print('SESSION_COOKIE_SAMESITE:', app.config['SESSION_COOKIE_SAMESITE'])
print('PERMANENT_SESSION_LIFETIME:', app.config['PERMANENT_SESSION_LIFETIME'])
"
# Expected output:
# SESSION_COOKIE_SECURE: True
# SESSION_COOKIE_HTTPONLY: True
# SESSION_COOKIE_SAMESITE: Lax
# PERMANENT_SESSION_LIFETIME: 3600
```

### 8. Start Production Server

```bash
# Stop current app (if running)
systemctl stop gammons || pkill -f "flask run"

# Start with waitress
cd /app/gammons-landing
export FLASK_ENV=production
export SECRET_KEY=<from-env>
export DATABASE_URL=<from-env>

# Option A: Using systemd (recommended)
systemctl start gammons

# Option B: Using waitress directly (for manual testing)
waitress-serve \
  --port=8000 \
  --host=127.0.0.1 \
  --threads=4 \
  --max-request-body-size=5242880 \
  app:app

# Option C: Using gunicorn (if preferred)
gunicorn \
  --workers=4 \
  --worker-class=sync \
  --bind=127.0.0.1:8000 \
  --access-logfile=- \
  --error-logfile=- \
  app:app
```

### 9. Reverse Proxy Configuration (nginx example)

```nginx
# /etc/nginx/sites-available/gammons-landing

upstream gammons_app {
    server 127.0.0.1:8000;
    # Add more if load balancing across multiple app instances
}

server {
    listen 443 ssl http2;
    server_name platform.edu;

    ssl_certificate /etc/ssl/certs/platform.edu.crt;
    ssl_certificate_key /etc/ssl/private/platform.edu.key;

    # TLS 1.2+ only (not 1.0 or 1.1)
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # HSTS: Enforce HTTPS for all future requests
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location / {
        proxy_pass http://gammons_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Redirect HTTP to HTTPS
    error_page 497 =301 https://$host$request_uri;
}

# HTTP redirect
server {
    listen 80;
    server_name platform.edu;
    return 301 https://$host$request_uri;
}
```

**Apply and test**:
```bash
nginx -t  # Syntax check
systemctl reload nginx
```

---

## Post-Deployment Verification Phase (Execute Immediately After Startup)

### 10. Connectivity & Basic Health

```bash
# Test HTTPS endpoint
curl -I https://platform.edu/
# Expected: HTTP/1.1 200 OK

# Test API health
curl https://platform.edu/api/content
# Expected: HTTP 200 with course JSON (no auth required)
```

### 11. Session Cookie Verification (Critical)

**Test 1: Verify Secure Flag**
```bash
# Login and inspect Set-Cookie response
curl -X POST https://platform.edu/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "password": "test_password"}' \
  -v 2>&1 | grep -i "set-cookie"

# Expected output includes:
# Set-Cookie: session=...; Path=/; Secure; HttpOnly; SameSite=Lax
#             ^^^^^^^^^
# CRITICAL: Verify "Secure" flag is present (not optional)
```

**Test 2: Verify HTTPS-Only Enforcement**
```bash
# Attempt to access over HTTP (should redirect or fail)
curl -X POST http://platform.edu/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "password": "test_password"}'

# Expected: 301/302 redirect to HTTPS (not login success)
```

**Test 3: Verify HttpOnly Flag**
```bash
# In browser DevTools console:
# Open https://platform.edu and login
# Run: document.cookie
# Expected: Session cookie NOT visible (empty string or excluded)
# This verifies HttpOnly flag is working
```

### 12. Session Timeout Verification (Non-Critical but Important)

```bash
# 1. Login and capture session cookie
SESSION_COOKIE=$(curl -s -X POST https://platform.edu/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test_user", "password": "test_password"}' \
  -c /tmp/cookies.txt | jq -r '.user.id')

# 2. Immediately check session (should work)
curl -b /tmp/cookies.txt https://platform.edu/api/check_session
# Expected: {"is_authenticated": true, ...}

# 3. Simulate 1-hour wait (for testing, set PERMANENT_SESSION_LIFETIME=60)
# In production, manually test by updating config temporarily to 60-second timeout
# Then wait 61 seconds and recheck

# 4. Re-check session (should fail after timeout)
curl -b /tmp/cookies.txt https://platform.edu/api/check_session
# Expected: {"is_authenticated": false}, HTTP 401
```

### 13. CSRF Protection Verification

```bash
# Get CSRF token
TOKEN=$(curl -s https://platform.edu/csrf-token | jq -r '.csrf_token')

# Attempt state-changing request (update profile)
curl -X POST https://platform.edu/api/profile \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: $TOKEN" \
  -b /tmp/cookies.txt \
  -d '{"about_me": "Test bio"}'

# Expected: 200 OK with success message

# Attempt WITHOUT valid CSRF token (should fail)
curl -X POST https://platform.edu/api/profile \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: invalid-token" \
  -b /tmp/cookies.txt \
  -d '{"about_me": "Test bio"}'

# Expected: 400 Bad Request, CSRF validation failure message
```

### 14. Authentication Flow Testing

```bash
# 1. Register new test user
curl -X POST https://platform.edu/api/register \
  -H "Content-Type: application/json" \
  -d '{"username": "aegis_test_user", "password": "TestPassword123"}'
# Expected: 201 User registered successfully

# 2. Login
curl -X POST https://platform.edu/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "aegis_test_user", "password": "TestPassword123"}' \
  -c /tmp/cookies.txt
# Expected: 200 Login successful, session cookie in response

# 3. Access protected endpoint (/profile requires login)
curl -b /tmp/cookies.txt https://platform.edu/profile
# Expected: 200 OK, user profile page

# 4. Logout
curl -X POST -b /tmp/cookies.txt https://platform.edu/api/logout
# Expected: 200 Logout successful

# 5. Verify logout (access protected endpoint after logout)
curl -b /tmp/cookies.txt https://platform.edu/profile
# Expected: 401 Unauthorized or redirect to login
```

### 15. Load & Performance Check

```bash
# Light load test (simulate 10 concurrent users for 60 seconds)
ab -n 100 -c 10 -H "Connection: close" https://platform.edu/api/content

# Expected output should include:
# Requests per second: > 10 (adjust based on hardware)
# Failed requests: 0
# Time per request: < 500ms (adjust based on requirements)
```

### 16. Log Inspection

```bash
# Check application logs for errors
tail -100 /var/log/gammons/app.log | grep -i error

# Expected: No CSRF errors, no session errors, no authentication errors

# Check access logs
tail -100 /var/log/gammons/access.log | grep -v "GET /api/content"

# Expected: Mix of GET, POST requests, status 200/302/401 as appropriate
# Should NOT see any 500 errors in critical paths
```

---

## Issue Detection & Remediation

### Issue: "Secure flag missing from session cookie"

**Symptom**: Browser DevTools shows "Set-Cookie: session=... HttpOnly; SameSite=Lax" (no Secure)

**Root Cause**: FLASK_ENV not set to 'production' or HTTP used instead of HTTPS

**Fix**:
```bash
# 1. Verify FLASK_ENV
echo $FLASK_ENV  # Should print "production"

# 2. If not set:
export FLASK_ENV=production

# 3. Restart app
systemctl restart gammons

# 4. Re-test with HTTPS (not HTTP)
curl -I https://platform.edu/api/check_session
```

### Issue: "Session expires immediately (within seconds)"

**Symptom**: User logged in, but after 30 seconds, requests return 401

**Root Cause**: PERMANENT_SESSION_LIFETIME accidentally set to very short value (e.g., 30), or session.permanent not set to True at login

**Fix**:
```bash
# 1. Check config
python -c "from app import app; print(app.config['PERMANENT_SESSION_LIFETIME'])"
# Should print 3600 (1 hour)

# 2. If not 3600, update config.py ProductionConfig and restart

# 3. Verify login sets session.permanent=True (already in code, line 276)
```

### Issue: "CSRF token validation failing (400 Bad Request)"

**Symptom**: User can login but form submission returns 400 "The CSRF token is missing"

**Root Cause**: Frontend not including X-CSRFToken header or csrf_token in form data

**Fix**:
```bash
# 1. Verify /csrf-token endpoint works
curl https://platform.edu/csrf-token
# Should return: {"csrf_token": "..."}

# 2. Frontend must:
#    - Call GET /csrf-token to retrieve token
#    - Include token in subsequent POST/PUT/DELETE requests
#    - Via X-CSRFToken header (for API calls) or form field (for HTML forms)

# 3. If frontend code is unclear, check:
# - GET /csrf-token is called on page load
# - Token is stored in JavaScript variable or HTML hidden field
# - All form submissions include token
```

### Issue: "Cannot connect to production database"

**Symptom**: App starts but returns 500 error on API endpoints that require DB access

**Root Cause**: DATABASE_URL not set or points to wrong database

**Fix**:
```bash
# 1. Verify DATABASE_URL is set
echo $DATABASE_URL

# 2. Test database connection manually
psql $DATABASE_URL -c "SELECT 1;"
# Should return: 1

# 3. If not set:
export DATABASE_URL=postgresql://user:pass@host/dbname

# 4. Restart app
systemctl restart gammons

# 5. Run migrations (if first-time)
flask db upgrade
```

### Issue: "Load balancer health check failing"

**Symptom**: Load balancer marks instance unhealthy, removes from rotation

**Root Cause**: Health check endpoint not implemented or returns non-200 status

**Fix**:
```bash
# Create a simple health check endpoint in app.py
@app.route('/health', methods=['GET'])
def health_check():
    try:
        # Lightweight check (not a full DB query)
        return jsonify({'status': 'ok'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Configure load balancer to check https://platform.edu/health
# Expected: HTTP 200 with {"status": "ok"}
```

---

## Monitoring & Alerts (Post-Deployment)

### 1. Set Up Authentication Failure Logging

```python
# In app.py, add logging to login endpoint
import logging
logger = logging.getLogger(__name__)

@app.route('/api/login', methods=['POST'])
def login():
    # ... existing code ...
    if user and user.check_password(data['password']):
        logger.info(f'User login successful: {user.username}')
        # ... existing success code ...
    else:
        logger.warning(f'Failed login attempt: username={data["username"]}, ip={request.remote_addr}')
        # ... existing error code ...
```

### 2. Monitor Session Timeout Events

```bash
# In logs, watch for session-related errors
grep -i "session\|401\|unauthorized" /var/log/gammons/app.log

# Alert if error rate > 5% during normal hours
# (Higher rate may indicate attack or misconfiguration)
```

### 3. Monitor CSRF Validation Failures

```bash
# In logs, watch for CSRF failures
grep -i "csrf" /var/log/gammons/app.log

# Alert if CSRF failures > 1% of requests
# (May indicate frontend bug or attack)
```

### 4. Certificate Expiration Monitoring

```bash
# Add cron job to check certificate expiration
0 9 * * 0 openssl x509 -noout -dates -in /etc/ssl/certs/platform.edu.crt | mail -s "Cert Check" ops@example.com

# Alert if certificate expires in < 30 days
```

---

## Rollback Instructions (If Critical Issue Occurs)

### Rollback Scenario: Session Secure Flag Breaking User Access

```bash
# 1. Stop the app
systemctl stop gammons

# 2. Revert config.py to pre-deployment version (from /backups/)
cp /backups/config.py.pre-deployment /app/gammons-landing/config.py

# 3. Update SESSION_COOKIE_SECURE back to False (or remove ProductionConfig override)
# 4. Update PERMANENT_SESSION_LIFETIME back to 86400 (or remove ProductionConfig override)

# 5. Restart app
systemctl start gammons

# 6. Verify app is accessible
curl https://platform.edu/api/content
# Expected: 200 OK

# 7. Notify team of rollback and open incident
```

### Rollback Scenario: Environment Variable Missing

```bash
# 1. If SECRET_KEY missing:
export SECRET_KEY=$(python -c "import os; print(os.urandom(32).hex())")
echo "SECRET_KEY=$SECRET_KEY" > /path/to/secret.env

# 2. If DATABASE_URL missing:
export DATABASE_URL=postgresql://user:pass@backup-db/gammons_backup

# 3. Restart app
systemctl restart gammons
```

---

## Sign-Off & Closure

- [ ] **All checks passed**: Run through entire checklist, mark items complete
- [ ] **Team sign-off**: Get approval from ops lead before marking "complete"
- [ ] **Monitoring enabled**: Alerts for CSRF, auth failures, cert expiration configured
- [ ] **Backup verified**: Database backup exists and can be restored
- [ ] **Documentation updated**: This checklist updated with any issues/findings
- [ ] **Incident contact notified**: On-call team aware of deployment and has rollback plan

**Deployment completed by**: _________________ (Name)
**Date/Time**: _________________ (2025-11-13 HH:MM UTC)
**Approval by**: _________________ (Ops Lead)

---

## Quick Reference

**Critical Settings** (Must be verified):
```
SESSION_COOKIE_SECURE = True      (HTTPS-only)
SESSION_COOKIE_HTTPONLY = True    (No JavaScript access)
SESSION_COOKIE_SAMESITE = 'Lax'   (CSRF protection)
PERMANENT_SESSION_LIFETIME = 3600 (1-hour timeout)
FLASK_ENV = production            (No Flask dev server)
```

**Commands**:
```bash
# Start production app
waitress-serve --port=8000 app:app

# Check session config
python -c "from app import app; print(app.config['SESSION_COOKIE_SECURE'])"

# Test HTTPS
curl -I https://platform.edu/

# View logs
tail -f /var/log/gammons/app.log
```

---

## Support

For questions or issues, contact:
- **On-Call SRE**: ops@example.com
- **Session Security Lead**: aegis@example.com (AEGIS SRE)
- **Incident Response**: Follow incident.example.com runbook
