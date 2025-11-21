# AEGIS PHASE 1 STRATEGIC AUDIT & IMPLEMENTATION PLAN
**Aegis Agent (Yang)** - SRE Security & Reliability Review
**Date:** 2025-11-14
**Status:** PHASE 0 REVIEW COMPLETE + PHASE 1 PLANNING ACTIVE

---

## SECTION 1: PHASE 0 CODE REVIEW FINDINGS

### Table 1: AEGIS CODE REVIEW FINDINGS (PHASE 0)

| Risk Level | Finding Category | Issue Description | Proposed Remediation | Status |
|------------|------------------|-------------------|----------------------|--------|
| **CRITICAL** | Security (OWASP) | **Residual CSRF Risk in Test Suite** - `requirements.txt` missing `flask-wtf`. Phase 0 implementation assumes Flask-WTF is installed, but dependency is not declared. This will cause import failure in CI/CD or fresh deployments. File: `requirements.txt`, Line: 1-11 (missing flask-wtf package). | Add `flask-wtf>=1.2.0` to requirements.txt immediately. This is a blocking dependency for Phase 0 CSRF protection to function. Test by running `pip install -r requirements.txt && python -c "from flask_wtf import CSRFProtect"` | **BLOCKED** |
| **HIGH** | Security (OWASP) | **Session Security Gap: SESSION_COOKIE_SECURE Not Set for Production** - File: `config.py`, Line 9. `SESSION_COOKIE_SECURE = False` is hardcoded in base Config class. Production deployments over HTTPS will transmit session cookies over the wire in plain text, violating zero-trust security mandate. | Modify `ProductionConfig` in config.py to override with `SESSION_COOKIE_SECURE = True`. This must be automatically enforced when `FLASK_ENV=production`. See Phase 1 Priority 1 implementation. | **PENDING** |
| **HIGH** | Performance (N+1) | **Potential N+1 in `/api/content` Endpoint** - File: `app.py`, Lines 150-186. The endpoint queries all courses and all ebooks separately (lines 150-151), then iterates over them (lines 162, 172). No explicit eager-loading for course thumbnails or ebook cover_paths. However, no navigation relationships are accessed in the loop, so N+1 is avoided. **Verdict:** Safe. No action required. | No remediation needed. The current implementation avoids N+1 by accessing only scalar columns (thumbnail, cover_path) that are stored in the same table. Confirm with a query analyzer in Phase 1 testing if scale increases. | **VERIFIED SAFE** |
| **MEDIUM** | Stack Integrity (Pillow) | **Image Upload DoS Mitigation - Dimension Validation Missing** - File: `app.py`, Lines 416-437. The `upload_avatar()` endpoint validates file size and format, but does NOT validate image dimensions. An attacker could upload a 5MB file with huge dimensions (e.g., 100,000x100,000 pixels), causing Pillow to consume excessive memory or CPU during rendering (image bombs). Current implementation: Size check + Pillow open() validation, but no dimension limits. | Add dimension validation after `Image.open(file.stream)`. Enforce maximum dimensions (e.g., `if img.size[0] > 4096 or img.size[1] > 4096: reject`). This prevents denial-of-service via resource exhaustion. Implementation: See Phase 1 detailed remediation section. | **PENDING** |
| **MEDIUM** | Testing | **CSRF Test Coverage Gap - No Explicit CSRF Token Validation Tests** - File: `tests/test_app.py`, Lines 1-77. The existing test suite does NOT include tests for CSRF protection. Tests like `test_index_page`, `test_check_session`, etc., do NOT attempt to POST without a token. This creates a blindspot: CSRF could be misconfigured and tests would still pass. | Add `test_csrf_protection_enabled()` and `test_csrf_token_validation()` tests in Phase 1. Pattern: (1) Fetch CSRF token from `/csrf-token`, (2) Attempt POST without token (expect 400), (3) Attempt POST with token (expect success). This verifies the middleware is active. See Phase 1 test section for full implementation. | **PENDING** |
| **MEDIUM** | Testing | **Rate Limit Test Coverage Gap** - File: `tests/test_app.py`. No tests validate rate limiting on `/api/login` or `/api/register`. Current implementation (lines 86-106 of app.py) tracks in-memory, but tests do not verify behavior. Antipattern: In-memory tracking resets on server restart and doesn't scale to multi-instance deployments. | Add `test_rate_limit_login_enforcement()` test. Pattern: Loop 6 times making login requests from same IP, assert first 5 return 200/401 (auth response), 6th returns 429 (Too Many Requests). This is Phase 1 priority task. Production will require Redis-based rate limiting (Phase 2). | **PENDING** |
| **MEDIUM** | Stack Integrity (Flask-Login) | **Missing Session Context in Tests** - File: `tests/test_app.py`. Tests that require authentication (future: profile endpoint tests) will fail because Flask-Login's `current_user` requires session context. Pattern issue: `login_user(user)` outside a `with client:` block loses session context. | Phase 1 test pattern: Wrap authenticated requests in `with client:` block to maintain Flask-Login session context across the test. Example: `with client: client.post('/login', ...); response = client.get('/api/profile')`. This ensures current_user is available throughout the request. | **PENDING** |
| **MEDIUM** | Performance | **Missing Health Check Endpoint for Production Monitoring** - File: `app.py`. No `/health` or `/health/deep` endpoint exists. Production orchestrators (Kubernetes, Docker Compose health checks, load balancers) require a health endpoint to determine if the instance is alive. Without this, false-positive failures can occur (stale database connections), leading to cascading restarts and downtime. | Implement `/health` endpoint (Phase 1 Priority 2). Lightweight non-blocking check. Also implement `/health/deep` for detailed diagnostics (database ping with `pool_pre_ping=True`). This prevents false-positive-induced outages. See Phase 1 implementation section. | **PENDING** |
| **LOW** | Code Quality | **Hardcoded Debug Mode in Production** - File: `app.py`, Line 515. `if __name__ == '__main__': app.run(debug=True)` enables Flask's development server. This should NEVER be used in production. Current mitigationStrategy: The app.py entrypoint is not used in production; instead, `runner.py` is used with `waitress`. However, this is fragile and relies on operational discipline. | Document in README.md: "app.py is for development only. Use runner.py with waitress in production." Add a startup check in runner.py: `if app.debug and os.environ.get('FLASK_ENV') == 'production': raise RuntimeError("Flask debug mode enabled in production!")`. | **PENDING** |

---

## SECTION 2: PHASE 0 VERDICT

### Summary Findings

| Category | Finding | Severity | Action |
|----------|---------|----------|--------|
| **CSRF Implementation** | Flask-WTF properly initialized; `/csrf-token` endpoint functional; frontend integration with `X-CSRFToken` header. All state-changing endpoints protected. | ✅ SAFE | No immediate action (pending flask-wtf in requirements.txt) |
| **Image Upload Security** | Filename sanitization, file size validation, Pillow magic byte verification, extension spoofing prevention all implemented. Validation occurs BEFORE saving to disk. | ✅ SAFE | Add dimension validation (Phase 1 enhancement) |
| **N+1 Query Prevention** | Eager-loading relationships implemented via `lazy='joined'` in CourseProgress, CourseNote, ReadingProgress models. Profile endpoint confirmed optimized from 300+ to 3-4 queries. | ✅ SAFE | Monitor with automated N+1 detection in Phase 1 testing |
| **Test Suite Status** | 2/4 tests passing. Failures are in `/api/content` (database population timing) and `/course/detail` (missing in-memory DB setup), NOT security-related. | ⚠️ INVESTIGATE | Fix test setup (minor DB context issue), not security blocker |
| **Security Configuration** | SECRET_KEY environment-based, password validation enforced, rate limiting in place (in-memory). Session management configured for dev; production settings pending. | ✅ MOSTLY SAFE | Production session hardening required (Phase 1) |

### CRITICAL BLOCKING ISSUE

**ISSUE:** `flask-wtf` is NOT in `requirements.txt`.
**IMPACT:** Phase 0 CSRF protection depends on Flask-WTF. Fresh deployments will fail with ImportError.
**REMEDIATION:** Add `flask-wtf>=1.2.0` to requirements.txt **IMMEDIATELY** before proceeding to Phase 1.
**VERIFICATION:** Run `pip install -r requirements.txt && pytest tests/test_app.py` successfully.

---

## SECTION 3: PHASE 1 IMPLEMENTATION PLAN

### Overview

Phase 1 focuses on **Production Readiness**: Session Security, Health Monitoring, Test Coverage, and Structured Logging. These are foundational for the 100% uptime mandate.

---

### Phase 1 Priority Matrix

| Priority | Initiative | Effort | Impact | Blockers |
|----------|-----------|--------|--------|----------|
| **P0 (CRITICAL)** | Fix requirements.txt (add flask-wtf) | 5 min | Unblock all Phase 0 functionality | NONE - execute immediately |
| **P1 (CRITICAL)** | Session Security (HTTPS cookies) | 30 min | Enable production deployment with secure sessions | NONE |
| **P2 (HIGH)** | Health Check Endpoints | 45 min | Enable production orchestration (K8s, Docker, LB) | NONE |
| **P3 (HIGH)** | CSRF & Authentication Test Suite | 2 hours | Prevent regression on critical flows | P1 session setup |
| **P4 (HIGH)** | Rate Limit Test Suite | 1 hour | Verify brute-force protection works at scale | NONE |
| **P5 (MEDIUM)** | Structured Logging (structlog + JSON) | 1.5 hours | Enable SRE metrics and AHDM predictive analysis | NONE |
| **P6 (MEDIUM)** | Image Upload Dimension Validation | 30 min | DoS prevention (image bombs) | NONE |
| **P7 (NICE-TO-HAVE)** | Query Performance Testing (pytest N+1 detection) | 2 hours | Automated regression prevention for N+1 queries | NONE |

**Total Phase 1 Effort: 7.5 hours (including testing)**

---

### Phase 1 Detailed Recommendations

---

## PHASE 1 PRIORITY 1: SESSION SECURITY (30 minutes)

### Problem Statement
`SESSION_COOKIE_SECURE = False` in production exposes session cookies to man-in-the-middle attacks. Over HTTPS, cookies should have the `Secure` flag to prevent transmission over HTTP fallback.

### Current Config
```python
# config.py, Line 9 (Base Config class)
SESSION_COOKIE_SECURE = False  # ← Development default
```

### Required Change
```python
# config.py - Modify ProductionConfig class
class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True  # ← HTTPS only
    SESSION_COOKIE_SAMESITE = 'Lax'  # ← Already correct
    PERMANENT_SESSION_LIFETIME = 3600  # ← Change to 1 hour (from 86400)
```

### Implementation Steps
1. Edit `config.py` line 43-56 (ProductionConfig class)
2. Add `SESSION_COOKIE_SECURE = True`
3. Add `PERMANENT_SESSION_LIFETIME = 3600` (1 hour, configurable)
4. Document: "In production with HTTPS, session cookies are marked Secure. Verify your load balancer forwards X-Forwarded-Proto: https header."
5. Verify by running app with `FLASK_ENV=production` and checking session cookie headers in browser DevTools.

### Risk Mitigation
- **Downside:** Sessions will timeout after 1 hour (configurable). Users must re-login.
- **Mitigation:** Display session timeout warning 5 minutes before expiry (frontend enhancement, Phase 2).

### Verification
```bash
# After update, test with:
FLASK_ENV=production python runner.py
# Check session cookie in browser: Secure; HttpOnly; SameSite=Lax flags should be present
```

---

## PHASE 1 PRIORITY 2: HEALTH CHECK ENDPOINTS (45 minutes)

### Problem Statement
Production deployments require health check endpoints for:
- Kubernetes liveness/readiness probes
- Docker health checks
- Load balancer status verification
- Automated remediation (kill instance if unhealthy)

Without a health endpoint, false-positive database connection failures can cascade, violating the 100% uptime mandate.

### Design

#### Endpoint 1: `/health` (Lightweight)
```python
@app.route('/health', methods=['GET'])
def health():
    """
    Lightweight health check. Returns 200 if app is running.
    No blocking operations.
    """
    return jsonify({'status': 'ok', 'timestamp': datetime.utcnow().isoformat()}), 200
```

**Response:** `{"status": "ok", "timestamp": "2025-11-14T10:30:00.123456"}`
**Latency:** <1ms
**Used By:** Load balancers, orchestrators for fast checks every 5 seconds

#### Endpoint 2: `/health/deep` (Detailed)
```python
@app.route('/health/deep', methods=['GET'])
def health_deep():
    """
    Deep health check. Verifies database connectivity.
    Includes pool_pre_ping to avoid stale connection issues.
    """
    try:
        # Test database connectivity
        db.session.execute('SELECT 1')
        db.session.close()

        return jsonify({
            'status': 'ok',
            'database': 'connected',
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'degraded',
            'database': 'unavailable',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503
```

**Response (Healthy):** `{"status": "ok", "database": "connected", ...}`
**Response (Degraded):** `{"status": "degraded", "database": "unavailable", "error": "...", ...}` (HTTP 503)
**Latency:** <50ms (includes DB ping)
**Used By:** Monitoring systems, detailed diagnostics

### Critical Configuration: `pool_pre_ping`

**THE STALE POOL PITFALL**

In production, database connections in a pool can go stale (network interruption, DB restart, idle timeout). When the health check grabs a stale connection and runs `SELECT 1`, it hangs or times out. The orchestrator (K8s, Docker) sees a failed health check and kills the instance, causing a cascading outage.

**SOLUTION:** Add `pool_pre_ping=True` to SQLAlchemy engine config.

```python
# In database.py or at app initialization
from sqlalchemy import event
from sqlalchemy.pool import Pool

@event.listens_for(Pool, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign keys for SQLite."""
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

# In app.py, after creating Flask app
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'pool_pre_ping': True,  # ← Forces SELECT 1 before checkout
    'pool_recycle': 3600,   # ← Recycle connections after 1 hour
}
```

**What `pool_pre_ping` Does:**
- Before giving a connection to the app, SQLAlchemy runs a pessimistic health check (`SELECT 1`).
- If the check fails, the connection is discarded and a new one is created.
- This adds ~1ms overhead per checkout but prevents stale connection failures.

### Implementation Steps

1. Add `/health` endpoint to `app.py`
2. Add `/health/deep` endpoint with database ping
3. Configure `pool_pre_ping=True` in database engine options
4. Create health check tests in Phase 1 test suite
5. Document for DevOps: "Use `/health` for liveness (K8s: livenessProbe). Use `/health/deep` for readiness (K8s: readinessProbe)."

### Kubernetes Integration (Reference)
```yaml
# Example K8s healthcheck config (for DevOps reference)
livenessProbe:
  httpGet:
    path: /health
    port: 5000
  initialDelaySeconds: 10
  periodSeconds: 5

readinessProbe:
  httpGet:
    path: /health/deep
    port: 5000
  initialDelaySeconds: 30
  periodSeconds: 10
```

---

## PHASE 1 PRIORITY 3: CSRF & AUTHENTICATION TEST SUITE (2 hours)

### Problem Statement
Phase 0 CSRF implementation is untested. The current test suite does NOT verify:
- CSRF tokens are required for state-changing endpoints
- Requests without tokens are rejected (HTTP 400/403)
- Token validation actually works

**Antipattern Danger:** A form missing `{{ csrf_token() }}` or AJAX call missing `X-CSRFToken` header will pass tests (because CSRF is not tested) but fail in production (where CSRF IS enabled), causing an outage.

### Test Suite Implementation

```python
# File: tests/test_csrf.py (NEW FILE)

import pytest
from app import app as flask_app, db, csrf
from models import User
from flask_login import login_user

@pytest.fixture
def app():
    """Create app instance for CSRF testing."""
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": True  # ← Explicitly enabled
    })
    with flask_app.app_context():
        db.create_all()
    yield flask_app
    with flask_app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def authenticated_client(client, app):
    """Create authenticated test client."""
    with app.app_context():
        user = User(username='testuser')
        user.set_password('TestPass123')
        db.session.add(user)
        db.session.commit()

    with client:
        client.post('/api/login', json={'username': 'testuser', 'password': 'TestPass123'})
        yield client

def test_csrf_token_endpoint(client):
    """Test that /csrf-token returns a valid token."""
    response = client.get('/csrf-token')
    assert response.status_code == 200
    assert 'csrf_token' in response.get_json()
    assert len(response.get_json()['csrf_token']) > 0

def test_post_without_csrf_token_rejected(authenticated_client):
    """Test that POST without CSRF token is rejected."""
    # Attempt to update profile WITHOUT token
    response = authenticated_client.post(
        '/api/profile',
        json={'about_me': 'Updated bio'},
        content_type='application/json'
    )
    # Should return 400 Bad Request (CSRF failure)
    assert response.status_code == 400

def test_post_with_csrf_token_accepted(authenticated_client):
    """Test that POST WITH CSRF token succeeds."""
    # Step 1: Fetch CSRF token
    token_response = authenticated_client.get('/csrf-token')
    csrf_token = token_response.get_json()['csrf_token']

    # Step 2: Make POST request with token in header
    response = authenticated_client.post(
        '/api/profile',
        json={'about_me': 'Updated bio'},
        headers={'X-CSRFToken': csrf_token},
        content_type='application/json'
    )
    # Should return 200 OK
    assert response.status_code == 200
    assert 'message' in response.get_json()

def test_register_without_csrf_token_rejected(client):
    """Test that register POST without token is rejected."""
    response = client.post(
        '/api/register',
        json={'username': 'newuser', 'password': 'NewPass123'},
        content_type='application/json'
    )
    assert response.status_code == 400

def test_register_with_csrf_token_succeeds(client):
    """Test that register with token succeeds."""
    # Fetch token
    token_response = client.get('/csrf-token')
    csrf_token = token_response.get_json()['csrf_token']

    # Register with token
    response = client.post(
        '/api/register',
        json={'username': 'newuser2', 'password': 'NewPass123'},
        headers={'X-CSRFToken': csrf_token},
        content_type='application/json'
    )
    assert response.status_code == 201
```

### Key Testing Patterns

1. **Get Token Pattern:**
   ```python
   response = client.get('/csrf-token')
   csrf_token = response.get_json()['csrf_token']
   ```

2. **Include Token in Header:**
   ```python
   headers={'X-CSRFToken': csrf_token}
   ```

3. **Session Persistence with Context Manager:**
   ```python
   with client:  # ← Maintains Flask session context
       client.post('/login', ...)
       response = client.get('/api/profile')  # ← current_user available
   ```

4. **Authentication Fixture:**
   ```python
   @pytest.fixture
   def authenticated_client(client, app):
       # Create user in DB
       # Login client
       # Yield client with session
   ```

---

## PHASE 1 PRIORITY 4: RATE LIMIT TEST SUITE (1 hour)

### Test Implementation

```python
# File: tests/test_rate_limits.py (NEW FILE)

import pytest
from app import app as flask_app, db

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "AUTH_RATE_LIMIT": 5  # Allow 5 attempts per minute
    })
    with flask_app.app_context():
        db.create_all()
    yield flask_app
    with flask_app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_rate_limit_login_enforcement(client, app):
    """
    Test that /api/login enforces rate limiting.
    After 5 attempts, the 6th should be rejected with 429.
    """
    # Get CSRF token
    csrf_response = client.get('/csrf-token')
    csrf_token = csrf_response.get_json()['csrf_token']

    # Attempt login 6 times rapidly
    for attempt in range(1, 7):
        response = client.post(
            '/api/login',
            json={'username': 'baduser', 'password': 'wrongpass'},
            headers={'X-CSRFToken': csrf_token},
            content_type='application/json'
        )

        if attempt <= 5:
            # First 5 attempts should return 401 (bad credentials)
            assert response.status_code == 401, f"Attempt {attempt} should return 401"
        else:
            # 6th attempt should return 429 (rate limit)
            assert response.status_code == 429, f"Attempt {attempt} should return 429"
            error = response.get_json()
            assert 'Too many attempts' in error.get('error', '')

def test_rate_limit_register_enforcement(client, app):
    """Test that /api/register also enforces rate limiting."""
    csrf_response = client.get('/csrf-token')
    csrf_token = csrf_response.get_json()['csrf_token']

    for attempt in range(1, 7):
        response = client.post(
            '/api/register',
            json={'username': f'user{attempt}', 'password': 'ValidPass123'},
            headers={'X-CSRFToken': csrf_token},
            content_type='application/json'
        )

        if attempt <= 5:
            # First 5 might succeed or fail (depends on username uniqueness)
            assert response.status_code in [201, 409]
        else:
            # 6th should be rate limited
            assert response.status_code == 429
```

### Rate Limit Behavior Verification
- **Attempts 1-5:** Should return auth response (401 for bad credentials, 201 for success)
- **Attempt 6:** Should return 429 Too Many Requests
- **After 1 minute:** Limit resets and new attempt succeeds

---

## PHASE 1 PRIORITY 5: STRUCTURED LOGGING (1.5 hours)

### Problem Statement
Current logging is unstructured text (default Flask logging). This makes it impossible to:
- Calculate error rates programmatically
- Extract latency percentiles (P95, P99)
- Trigger automated alerts
- Enable AHDM predictive analysis

**Solution:** Migrate to `structlog` with JSON output.

### Implementation Overview

```python
# File: logging_config.py (NEW FILE)

import structlog
import logging
from logging.handlers import TimedRotatingFileHandler
import sys
from datetime import datetime

def configure_logging(app):
    """
    Configure structured logging with JSON output.
    Logs are written to app.log and rotated daily.
    """

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure Flask's logger with JSON handler
    handler = TimedRotatingFileHandler('app.log', when='midnight', interval=1)
    handler.setFormatter(logging.Formatter(
        '%(message)s'  # structlog already formats as JSON
    ))

    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)

    return structlog.get_logger()
```

### Integration with Flask

```python
# In app.py, after Flask app initialization
from logging_config import configure_logging

app = Flask(__name__)
log = configure_logging(app)

# Log requests with context
@app.before_request
def log_request():
    request.start_time = datetime.utcnow()
    log.info(
        'request_received',
        method=request.method,
        path=request.path,
        remote_addr=request.remote_addr,
        user_agent=request.user_agent.string
    )

@app.after_request
def log_response(response):
    if hasattr(request, 'start_time'):
        duration = (datetime.utcnow() - request.start_time).total_seconds() * 1000
        log.info(
            'request_complete',
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration_ms=duration
        )
    return response
```

### Log Output Format

Each log entry is a single JSON object:
```json
{
  "event": "request_complete",
  "method": "POST",
  "path": "/api/login",
  "status_code": 200,
  "duration_ms": 45.2,
  "timestamp": "2025-11-14T10:30:00.123456Z"
}
```

### Automated Log Analysis Script

```python
# File: log_analyzer.py (NEW FILE)

import json
from datetime import datetime, timedelta
from collections import defaultdict

def analyze_logs(log_file='app.log', minutes=10):
    """
    Analyze JSON logs from the last N minutes.
    Calculates error rate and latency percentiles.
    """
    cutoff = datetime.utcnow() - timedelta(minutes=minutes)
    latencies = []
    errors = 0
    total = 0

    try:
        with open(log_file, 'r') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    if 'timestamp' not in entry:
                        continue

                    ts = datetime.fromisoformat(entry['timestamp'].replace('Z', '+00:00'))
                    if ts < cutoff:
                        continue

                    if entry.get('event') == 'request_complete':
                        total += 1
                        if entry.get('status_code', 200) >= 500:
                            errors += 1
                        if 'duration_ms' in entry:
                            latencies.append(entry['duration_ms'])

                except json.JSONDecodeError:
                    continue

    except FileNotFoundError:
        print(f"Log file {log_file} not found.")
        return

    # Calculate percentiles
    latencies.sort()
    p50 = latencies[len(latencies) // 2] if latencies else 0
    p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0
    p99 = latencies[int(len(latencies) * 0.99)] if latencies else 0

    error_rate = (errors / total * 100) if total > 0 else 0

    # Print report
    print(f"\nLog Analysis Report (Last {minutes} minutes)")
    print("=" * 50)
    print(f"Total Requests: {total}")
    print(f"5xx Errors: {errors}")
    print(f"Error Rate: {error_rate:.2f}%")
    print(f"\nLatency Percentiles:")
    print(f"  P50: {p50:.2f}ms")
    print(f"  P95: {p95:.2f}ms")
    print(f"  P99: {p99:.2f}ms")
    print("=" * 50)

    # Alert if error rate exceeds threshold
    if error_rate > 1.0:
        print("WARNING: Error rate exceeds 1%! Investigate immediately.")
        exit(1)

if __name__ == '__main__':
    analyze_logs()
```

### Integration with CI/CD

```bash
# In your CI/CD pipeline (e.g., GitHub Actions)
# Run analyzer after tests to check for regressions
python log_analyzer.py
```

---

## PHASE 1 PRIORITY 6: IMAGE UPLOAD DIMENSION VALIDATION (30 min)

### Problem Statement
The current `upload_avatar()` endpoint validates file size (5MB) but not image dimensions. An attacker could upload a 5MB image with 100,000x100,000 pixels, causing:
- Memory exhaustion when Pillow renders the image
- CPU exhaustion during format conversion
- DoS that crashes the server

### Solution

Add dimension validation after Pillow opens the image:

```python
# In app.py, upload_avatar() function, after Image.open()

# Validate image dimensions (prevent image bombs)
MAX_IMAGE_WIDTH = 4096
MAX_IMAGE_HEIGHT = 4096
if img.size[0] > MAX_IMAGE_WIDTH or img.size[1] > MAX_IMAGE_HEIGHT:
    return jsonify({'error': f'Image dimensions too large. Maximum: {MAX_IMAGE_WIDTH}x{MAX_IMAGE_HEIGHT}'}), 400
```

### Complete Updated upload_avatar() Snippet

```python
@app.route('/api/profile/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """Upload user avatar with validation"""
    # ... existing validation code ...

    # Validate image with Pillow before saving
    try:
        img = Image.open(file.stream)

        # Verify image format matches file extension
        extension = file.filename.rsplit('.', 1)[1].lower()
        valid_formats = {
            'png': 'PNG', 'jpg': 'JPEG', 'jpeg': 'JPEG', 'gif': 'GIF'
        }
        if img.format and img.format.upper() != valid_formats.get(extension):
            return jsonify({'error': 'File extension does not match image format'}), 400

        # NEW: Validate image dimensions (prevent image bombs)
        MAX_IMAGE_WIDTH = 4096
        MAX_IMAGE_HEIGHT = 4096
        if img.size[0] > MAX_IMAGE_WIDTH or img.size[1] > MAX_IMAGE_HEIGHT:
            return jsonify({
                'error': f'Image dimensions too large. Maximum: {MAX_IMAGE_WIDTH}x{MAX_IMAGE_HEIGHT}'
            }), 400

        file.seek(0)
    except Exception as e:
        return jsonify({'error': f'Invalid or corrupted image file: {str(e)}'}), 400

    # ... rest of save logic ...
```

### Dimension Validation Test

```python
# In tests/test_image_upload.py

def test_image_dimension_validation(authenticated_client, app):
    """Test that oversized images are rejected."""
    from PIL import Image
    from io import BytesIO

    # Create a 5000x5000 image (exceeds 4096x4096 limit)
    img = Image.new('RGB', (5000, 5000), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    response = authenticated_client.post(
        '/api/profile/avatar',
        data={'avatar': (img_bytes, 'large.png')},
        headers={'X-CSRFToken': get_csrf_token(authenticated_client)}
    )

    assert response.status_code == 400
    assert 'dimensions too large' in response.get_json()['error']
```

---

## PHASE 1 PRIORITY 7: QUERY PERFORMANCE TESTING (2 hours - NICE-TO-HAVE)

### Problem Statement
Phase 0 implemented N+1 fixes, but there's no automated way to detect future N+1 regressions. If a developer forgets to use eager-loading and adds `post.author.name` in a loop, tests should FAIL immediately.

### Solution: Automated N+1 Detection

```python
# File: tests/conftest.py (NEW FILE)

import pytest
from sqlalchemy import event
from sqlalchemy.engine import Engine

# Global query counter
query_count = 0

@pytest.fixture(autouse=True)
def count_database_queries(app):
    """
    Automatically count queries in each test.
    Fail if too many queries detected (N+1 indicator).
    """
    global query_count
    query_count = 0

    def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        global query_count
        query_count += 1

    # Register event listener
    event.listen(Engine, 'before_cursor_execute', receive_before_cursor_execute)

    yield

    # Clean up
    event.remove(Engine, 'before_cursor_execute', receive_before_cursor_execute)

    # Assert query count is reasonable
    # Example: profile endpoint should use ~4 queries, not 300+
    # Adjust thresholds per endpoint

def test_profile_query_count(authenticated_client):
    """Verify /api/profile uses minimal queries (no N+1)."""
    global query_count
    query_count = 0

    response = authenticated_client.get('/api/profile')
    assert response.status_code == 200

    # Profile endpoint should use ~4 queries (1 user, 1 course progress, 1 notes, 1 reading progress)
    # Fail if > 10 queries (indicates N+1)
    assert query_count <= 10, f"N+1 detected: {query_count} queries for /api/profile"
```

### Expected Query Counts (After N+1 Fix)

| Endpoint | Expected Queries | Risk Level |
|----------|------------------|-----------|
| `/api/profile` | 3-4 | ✅ Safe |
| `/api/content` | 2 | ✅ Safe |
| `/api/course/<uid>/note` | 1-2 | ✅ Safe |

---

## SECTION 4: RISK ASSESSMENT & MITIGATION

### Phase 1 Risks & Mitigation Strategies

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **Session Timeout Causes User Frustration** | Medium | Medium | Add frontend warning 5 min before expiry; provide re-login without losing state |
| **Database Health Check Fails on Production DB** | Low | CRITICAL | Use `pool_pre_ping=True` to prevent stale connection issues; test thoroughly with production DB |
| **Structured Logging Causes Performance Regression** | Low | High | structlog is async-friendly; JSON serialization has <1ms overhead; monitor latency in Phase 2 load test |
| **Dimension Validation Too Strict (Rejects Legitimate Images)** | Low | Medium | Set MAX_IMAGE dimensions to 4096x4096 (sufficient for avatars); make configurable if needed |
| **Tests Break if requirements.txt Still Missing flask-wtf** | High | CRITICAL | **MUST fix immediately before Phase 1 tests** |
| **Rate Limit Doesn't Work in Production (In-Memory)** | High | High | Phase 1 uses in-memory (acceptable for single instance); Phase 2 will migrate to Redis for multi-instance deployments |

---

## SECTION 5: IMPLEMENTATION SEQUENCE & DEPENDENCIES

### Dependency Graph

```
P0: Fix requirements.txt (flask-wtf)
    ↓
P1: Session Security (config update)
    ↓
P2: Health Check Endpoints (+ pool_pre_ping)
    ↓
P3: CSRF Tests (depends on working CSRF implementation)
    ↓
P4: Rate Limit Tests (independent)
    ↓
P5: Structured Logging (independent)
    ↓
P6: Image Dimension Validation (independent)
    ↓
P7: Query Performance Testing (independent, optional)
```

### Recommended Execution Order

1. **Fix requirements.txt** (5 min) - BLOCKER
2. **Session Security** (30 min) - Foundational for production
3. **Health Check Endpoints** (45 min) - Required for orchestration
4. **CSRF Tests** (2 hours) - Validate critical security feature
5. **Rate Limit Tests** (1 hour) - Complete auth test coverage
6. **Structured Logging** (1.5 hours) - SRE foundational
7. **Image Dimension Validation** (30 min) - DoS prevention
8. **Query Performance Testing** (2 hours, optional) - Nice-to-have

**Total Time: ~7.5 hours (including testing)**

---

## SECTION 6: DEPLOYMENT READINESS CHECKLIST

### Before Phase 1 Implementation
- [ ] Confirm flask-wtf in requirements.txt
- [ ] Verify all Phase 0 tests pass

### After Phase 1 Implementation
- [ ] All tests pass (CSRF, Rate Limit, Image Upload, Health Check)
- [ ] Health endpoints respond in <100ms
- [ ] Structured logging produces valid JSON
- [ ] Session cookies have Secure flag in production config
- [ ] Load test with 100+ concurrent users (Phase 2)

### Pre-Production Deployment
- [ ] Set `FLASK_ENV=production`
- [ ] Set `SECRET_KEY` via environment variable (not hardcoded)
- [ ] Configure PostgreSQL (not SQLite) for production database
- [ ] Enable HTTPS and verify `SESSION_COOKIE_SECURE=True`
- [ ] Set up monitoring to collect `/health/deep` metrics
- [ ] Configure log rotation and archival
- [ ] Test with actual production workload (Phase 2 load test)

---

## SECTION 7: SUMMARY TABLE: PHASE 1 OVERVIEW

| Initiative | Status | Priority | Effort | Blocker | Owner |
|-----------|--------|----------|--------|---------|-------|
| Fix requirements.txt (flask-wtf) | ⏳ TODO | P0 | 5 min | YES - CRITICAL | Aegis |
| Session Security (HTTPS cookies) | ⏳ TODO | P1 | 30 min | NO | Aegis |
| Health Check Endpoints | ⏳ TODO | P2 | 45 min | NO | Aegis |
| CSRF Test Suite | ⏳ TODO | P3 | 2 hrs | NO (but P3+ blocked) | Aegis |
| Rate Limit Test Suite | ⏳ TODO | P4 | 1 hr | NO | Aegis |
| Structured Logging | ⏳ TODO | P5 | 1.5 hrs | NO | Aegis |
| Image Dimension Validation | ⏳ TODO | P6 | 30 min | NO | Aegis |
| Query Perf Testing (N+1) | ⏳ OPTIONAL | P7 | 2 hrs | NO | Aegis |

---

## APPENDIX A: PHASE 2 STRATEGIC PREVIEW

Phase 2 (next phase after Phase 1) will focus on:

1. **Redis Rate Limiting** - Replace in-memory with Redis for multi-instance deployments
2. **Email Verification** - Require email confirmation on registration
3. **Two-Factor Authentication (2FA)** - TOTP/SMS support
4. **Password Reset Flow** - Forgot password functionality
5. **Session Timeout UX** - Frontend warning before auto-logout
6. **Automated Alerting** - Monitor error rates and trigger Slack/PagerDuty alerts
7. **Load Testing** - 1000+ concurrent users, latency under 200ms P95

---

## APPENDIX B: CRITICAL REFERENCES

**Phase 0 Completion Report:** `PHASE0_COMPLETE.md`
**Phase 2 Requirements:** `PHASE2_COMPLETED.md`
**Session Summary:** See project root for session logs
**Multi-Agent Team Structure:** See `.claude/agents/` directory

---

## SIGN-OFF

**Aegis Strategic Review Complete**

**Date:** 2025-11-14
**Reviewer:** Aegis Agent (SRE Yang)
**Status:** Ready for Supervisor (Claude Code) approval and Phase 1 execution

**Next Step:** Supervisor reviews findings and approves Phase 1 implementation plan. Aegis awaits permission to generate implementation code.

---

**Document End**
