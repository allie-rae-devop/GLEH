# Session Security Hardening - AEGIS Phase 1 Implementation

**Status**: Production-Ready
**Implementation Date**: November 13, 2025
**OWASP Alignment**: A02:2021 (Authentication), A07:2021 (Cross-Site Request Forgery)
**Risk Mitigation**: Session hijacking, MitM attacks, unauthorized session access via JavaScript

---

## Executive Summary

This document details the production hardening of Flask-Login session security. The changes enforce HTTPS-only transmission, prevent JavaScript access to session cookies, and reduce the attack surface through shorter session timeouts. These measures comply with OWASP best practices and are critical for institutional data protection.

---

## Changes Made

### 1. SESSION_COOKIE_SECURE = True (ProductionConfig)

**What it does**: Instructs Flask to only send the session cookie over HTTPS connections. The cookie is stripped from HTTP requests.

**Why it matters**:
- **Man-in-the-Middle (MitM) Prevention**: If a user is on an insecure network (unencrypted WiFi), an attacker cannot intercept the session cookie because it's only transmitted over HTTPS.
- **Institutional Trust**: A learning institution's reputation depends on protecting student and instructor data. HTTPS-only enforcement is non-negotiable.
- **Browser Compliance**: Modern browsers (Chrome, Firefox, Safari) require HTTPS for sensitive cookies in many scenarios.

**OWASP A02:2021 Connection**:
- A02:2021 focuses on authentication mechanisms. SESSION_COOKIE_SECURE ensures the session identifier itself cannot be stolen in transit.

**Code Change**:
```python
# Before (ProductionConfig - NOT set, inherits base class insecure default)
# SESSION_COOKIE_SECURE = False (from base Config)

# After (ProductionConfig - Explicitly hardened)
SESSION_COOKIE_SECURE = True
```

**Verification**:
1. Inspect browser DevTools: Network → Cookies → session cookie should show "Secure" flag.
2. Confirm `Set-Cookie` response header includes `Secure; HttpOnly; SameSite=Lax`.

---

### 2. SESSION_COOKIE_HTTPONLY = True (Reinforced in ProductionConfig)

**What it does**: Prevents JavaScript from accessing the session cookie via `document.cookie`. The cookie is only sent with HTTP requests.

**Why it matters**:
- **XSS Mitigation**: Even if an attacker injects malicious JavaScript (e.g., via a comment field), they cannot steal the session token.
- **Defense in Depth**: Complements input validation and output escaping (already implemented via Jinja2's auto-escaping).

**OWASP A07:2021 Connection**:
- A07:2021 is CSRF, but HttpOnly cookies also prevent token exfiltration via XSS.

**Code Change**:
```python
# Already set in base Config, reinforced in ProductionConfig for clarity
SESSION_COOKIE_HTTPONLY = True
```

**Status**: Already implemented in base Config. ProductionConfig reinforces it explicitly for operational clarity.

---

### 3. SESSION_COOKIE_SAMESITE = 'Lax' (Reinforced in ProductionConfig)

**What it does**: The SameSite attribute restricts when the browser sends the cookie in cross-site requests. 'Lax' mode sends the cookie for top-level navigation (safe) but not for cross-site form submissions or embedded resources (protected).

**Why it matters**:
- **CSRF Protection (A07:2021)**: Without SameSite, an attacker can trick a logged-in user into making unauthorized requests (e.g., changing password, deleting courses).
- **Example Attack Blocked**: User is logged in to the learning platform. Attacker tricks them into visiting `evil.com` which contains `<form action="https://platform.edu/api/profile" method="POST">`. With SameSite=Lax, the session cookie is NOT sent with this cross-site POST, so the attack fails.

**Code Change**:
```python
# Already set in base Config, reinforced in ProductionConfig
SESSION_COOKIE_SAMESITE = 'Lax'
```

**Note**: 'Strict' would be more secure but breaks legitimate cross-site navigation (e.g., user clicks a link from an email or social media). 'Lax' balances security and usability.

---

### 4. PERMANENT_SESSION_LIFETIME = 3600 (1-hour timeout, ProductionConfig)

**What it does**: After 1 hour of inactivity, the session expires. The user must re-authenticate.

**Why it matters**:
- **Least Privilege Principle**: A stolen or forgotten session token is only useful for 1 hour, not 24 hours (the old default).
- **Reduced Attack Window**: Reduces the time an attacker has to exploit a compromised session.
- **Institutional Risk Mitigation**: In a multi-user institutional setting, a student leaving their computer unattended puts their account at risk for 24 hours. 1-hour timeout enforces better security hygiene.
- **Compliance**: Many institutional security policies mandate session timeouts of 15-60 minutes for sensitive systems.

**Code Change**:
```python
# Before (base Config)
PERMANENT_SESSION_LIFETIME = 86400  # 24 hours

# After (ProductionConfig)
PERMANENT_SESSION_LIFETIME = 3600   # 1 hour
```

**User Impact**:
- Users will be prompted to re-login after 1 hour of inactivity.
- The `/api/check_session` endpoint will return `is_authenticated: false` and HTTP 401 after timeout.
- Frontend should handle this gracefully (redirect to login, preserve form data).

---

## Before and After Comparison

| Aspect | Before (Development Default) | After (Production Hardened) |
|--------|-----|-----|
| **SESSION_COOKIE_SECURE** | False (insecure, development-only) | True (HTTPS-only) |
| **SESSION_COOKIE_HTTPONLY** | True | True (reinforced) |
| **SESSION_COOKIE_SAMESITE** | Lax | Lax (reinforced) |
| **PERMANENT_SESSION_LIFETIME** | 86400 (24 hours) | 3600 (1 hour) |
| **Flask Dev Server in Prod** | Allowed (security risk) | Rejected (enforces waitress/gunicorn) |

---

## Configuration Files

### config.py (Updated ProductionConfig)

```python
class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False

    # Session Security - Production Hardening (OWASP A02:2021, A07:2021)
    SESSION_COOKIE_SECURE = True        # Enforce HTTPS-only transmission
    SESSION_COOKIE_HTTPONLY = True      # Prevent JavaScript access
    SESSION_COOKIE_SAMESITE = 'Lax'     # CSRF protection
    PERMANENT_SESSION_LIFETIME = 3600   # 1-hour timeout

    # Production database
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        os.environ.get('PROD_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'database.db')
```

### app.py (Updated Main Execution)

```python
# --- Main Execution ---
if __name__ == '__main__':
    env = os.environ.get('FLASK_ENV', 'development')
    if env == 'development':
        app.run(debug=True)
    else:
        print('ERROR: Flask development server must not run in production.')
        print('Use waitress or gunicorn in production. Example:')
        print('  waitress-serve --port=8000 app:app')
        print('Or with gunicorn:')
        print('  gunicorn -w 4 -b 0.0.0.0:8000 app:app')
        exit(1)
```

---

## Environment Variables & Setup

### Required Environment Variables

**Development**:
```bash
FLASK_ENV=development
SECRET_KEY=dev-secret-key-do-not-use-in-production  # Or use dev default
```

**Production**:
```bash
FLASK_ENV=production
SECRET_KEY=<generate-strong-random-key>  # MUST be set, see below
DATABASE_URL=<production-database-connection-string>
```

### Generating a Strong SECRET_KEY

**Python (Recommended)**:
```python
import os
secret = os.urandom(32).hex()
print(secret)
# Output: a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1
```

**OpenSSL**:
```bash
openssl rand -hex 32
```

**Store in environment** (never commit SECRET_KEY to version control):
```bash
# .env file (NOT committed to git)
FLASK_ENV=production
SECRET_KEY=a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1
DATABASE_URL=postgresql://user:pass@db.example.com/gammons
```

---

## Testing Instructions

### 1. Verify Session Cookie Attributes (Development vs Production)

**Development Test**:
```bash
export FLASK_ENV=development
python app.py
# Visit http://localhost:5000/api/login (test login)
# Inspect DevTools: Network → Response Headers
# Set-Cookie: session=...; HttpOnly; Path=/; SameSite=Lax
# Note: NO "Secure" flag (OK for HTTP development)
```

**Production Test** (requires HTTPS setup):
```bash
export FLASK_ENV=production
export SECRET_KEY=<strong-key>
# Start with waitress
waitress-serve --port=8443 --ssl-cert=cert.pem --ssl-key=key.pem app:app
# Visit https://localhost:8443/api/login (test login)
# Inspect DevTools: Network → Response Headers
# Set-Cookie: session=...; Secure; HttpOnly; Path=/; SameSite=Lax
# Verify "Secure" flag IS present
```

### 2. Test Session Timeout (1-hour)

**Manual Test**:
```python
# In app.py, temporarily set for testing:
PERMANENT_SESSION_LIFETIME = 60  # 1 minute for testing

# 1. Login successfully
curl -X POST http://localhost:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "test", "password": "test123"}'
# Response: {"message": "Login successful.", "user": {...}}

# 2. Immediately check session (should work)
curl -X GET http://localhost:5000/api/check_session \
  -H "Cookie: session=<session-cookie-value>"
# Response: {"is_authenticated": true, ...}

# 3. Wait 61 seconds
sleep 61

# 4. Check session again (should fail)
curl -X GET http://localhost:5000/api/check_session \
  -H "Cookie: session=<session-cookie-value>"
# Response: {"is_authenticated": false}, HTTP 401
```

### 3. Test Flask Dev Server Rejection in Production

**Test**:
```bash
export FLASK_ENV=production
python app.py
# Expected output:
# ERROR: Flask development server must not run in production.
# Use waitress or gunicorn in production. Example:
#   waitress-serve --port=8000 app:app
# Process exits with code 1
```

### 4. Test CSRF Protection (A07:2021)

**Existing CSRF tests in test_routes.py**:
The application already uses Flask-WTF CSRF protection. The `/csrf-token` endpoint provides tokens for client-side requests.

Verify with a manual request:
```bash
# Get CSRF token
curl -X GET http://localhost:5000/csrf-token
# Response: {"csrf_token": "IjExMDg0MDQwODg4N..."}

# Use token in state-changing request (e.g., update profile)
curl -X POST http://localhost:5000/api/profile \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: IjExMDg0MDQwODg4N..." \
  -H "Cookie: session=<session-cookie-value>" \
  -d '{"about_me": "Updated bio"}'
# Should succeed with valid token
# Should fail with invalid/missing token
```

---

## OWASP Compliance References

### A02:2021 - Broken Authentication

**Vulnerability**: Weak session management allows attackers to hijack sessions.

**Mitigation**:
- SESSION_COOKIE_SECURE=True prevents MitM interception.
- SESSION_COOKIE_HTTPONLY=True prevents XSS-based token theft.
- PERMANENT_SESSION_LIFETIME=3600 limits the attack window.

**OWASP Guidance**: [A02:2021](https://owasp.org/Top10/A02_2021-Broken_Authentication/)

### A07:2021 - Cross-Site Request Forgery (CSRF)

**Vulnerability**: Attackers trick authenticated users into making unauthorized requests.

**Mitigation**:
- SESSION_COOKIE_SAMESITE='Lax' prevents the browser from sending cookies in cross-site POST requests.
- Flask-WTF CSRF tokens (already implemented) provide additional protection.

**OWASP Guidance**: [A07:2021](https://owasp.org/Top10/A07_2021-Cross_Site_Request_Forgery)

---

## Deployment Checklist (See deployment_checklist.md)

Before deploying to production:
1. Generate and store SECRET_KEY securely
2. Set FLASK_ENV=production
3. Install HTTPS certificate
4. Configure waitress or gunicorn
5. Test session cookies (Secure flag)
6. Test session timeout
7. Monitor authentication logs

---

## Rollback Instructions

If issues arise, rollback is simple (configuration-only change):

**Revert config.py**:
```python
# Remove ProductionConfig session overrides, app will use base Config defaults
# (SESSION_COOKIE_SECURE=False, PERMANENT_SESSION_LIFETIME=86400)
```

**Revert app.py**:
```python
# Replace environment-aware check with dev-only server
if __name__ == '__main__':
    app.run(debug=True)
```

---

## Support & Troubleshooting

See `deployment_checklist.md` for operational runbook and troubleshooting common issues.

---

## Sign-Off

**Reviewer**: AEGIS SRE
**Date**: November 13, 2025
**Status**: Ready for Production Deployment
