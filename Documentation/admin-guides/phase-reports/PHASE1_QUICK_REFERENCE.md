================================================================================
AEGIS PHASE 1 QUICK REFERENCE GUIDE
================================================================================

PHASE 0 AUDIT COMPLETE: 1 CRITICAL BLOCKER, 6 ACTIONABLE FINDINGS

BLOCKER (FIX IMMEDIATELY):
  [ ] Add "flask-wtf>=1.2.0" to requirements.txt (Line 1-11)
      Verify: pip install -r requirements.txt && pytest tests/test_app.py

PHASE 1 ROADMAP (7.5 HOURS TOTAL):
================================================================================

  PRIORITY 0 - BLOCKER (5 min)
  ============================
  [ ] Fix requirements.txt (add flask-wtf)
      File: requirements.txt
      Change: Add line: flask-wtf>=1.2.0
      Verify: pip install && pytest

  PRIORITY 1 - SESSION SECURITY (30 min)
  ======================================
  [ ] Enable HTTPS-only session cookies
      File: config.py, ProductionConfig class
      Add: SESSION_COOKIE_SECURE = True
      Add: PERMANENT_SESSION_LIFETIME = 3600 (1 hour)
      Document: X-Forwarded-Proto: https required from load balancer

  PRIORITY 2 - HEALTH CHECKS (45 min)
  ===================================
  [ ] Implement /health endpoint (lightweight)
      GET /health → {"status": "ok", "timestamp": "..."}
      Latency: <1ms
      Used by: load balancers, K8s liveness probes

  [ ] Implement /health/deep endpoint (with DB check)
      GET /health/deep → {"status": "ok", "database": "connected"}
      Latency: <50ms
      Used by: monitoring systems, K8s readiness probes

  [ ] Configure pool_pre_ping=True in SQLAlchemy
      Prevents: stale connection false-positive failures
      Impact: +1ms per connection checkout, prevents cascading restarts

  PRIORITY 3 - CSRF TESTS (2 hours)
  =================================
  [ ] Create tests/test_csrf.py with:
      - test_csrf_token_endpoint() - verify /csrf-token returns token
      - test_post_without_csrf_token_rejected() - verify 400 on missing token
      - test_post_with_csrf_token_accepted() - verify 200 with token
      - test_register_without_csrf_token_rejected() - same for register
      - test_register_with_csrf_token_succeeds() - same for register

      Pattern:
      1. token_response = client.get('/csrf-token')
      2. csrf_token = token_response.json['csrf_token']
      3. headers={'X-CSRFToken': csrf_token}
      4. client.post(..., headers=headers)

      Key: WTF_CSRF_ENABLED=True in test config (NOT False!)

  PRIORITY 4 - RATE LIMIT TESTS (1 hour)
  ======================================
  [ ] Create tests/test_rate_limits.py with:
      - test_rate_limit_login_enforcement() - loop 6 times, expect 429 on 6th
      - test_rate_limit_register_enforcement() - same for register

      Pattern:
      1. Fetch CSRF token
      2. Loop 6 times:
         - Attempts 1-5: expect 401/201 (auth response)
         - Attempt 6: expect 429 (Too Many Requests)

  PRIORITY 5 - STRUCTURED LOGGING (1.5 hours)
  ===========================================
  [ ] Create logging_config.py with structlog setup
      - JSON output format
      - TimedRotatingFileHandler (daily rotation)
      - Fields: timestamp, event, method, path, status, duration_ms

  [ ] Update app.py with before/after request hooks
      - Log request received
      - Log request complete with duration and status

  [ ] Create log_analyzer.py script
      - Parse JSON logs
      - Calculate error rate and latency percentiles (P50, P95, P99)
      - Alert if error rate > 1%

      Usage: python log_analyzer.py (analyzes last 10 minutes)

  PRIORITY 6 - IMAGE DIMENSION VALIDATION (30 min)
  ================================================
  [ ] Update upload_avatar() in app.py
      Add after Image.open(file.stream):

      MAX_IMAGE_WIDTH = 4096
      MAX_IMAGE_HEIGHT = 4096
      if img.size[0] > MAX_IMAGE_WIDTH or img.size[1] > MAX_IMAGE_HEIGHT:
          return jsonify({'error': 'Image dimensions too large'}), 400

      Prevents: image bomb DoS attacks

  PRIORITY 7 - QUERY PERFORMANCE TESTING (2 hours, OPTIONAL)
  ===========================================================
  [ ] Create tests/conftest.py with query counter
      - Auto-count queries per test
      - Assert /api/profile uses <= 10 queries (was 300+)
      - Catch N+1 regressions automatically

      Pattern:
      @pytest.fixture(autouse=True)
      def count_database_queries(app):
          global query_count
          # Listen for SQLAlchemy before_cursor_execute
          # Assert <= threshold after test

================================================================================

VERIFICATION CHECKLIST:
========================
  [ ] All requirements.txt dependencies installed
  [ ] pytest runs successfully (4/4 tests passing)
  [ ] Health endpoints return <100ms
  [ ] CSRF tests verify protection is enforced
  [ ] Rate limit tests verify 429 response
  [ ] Structured logs output valid JSON
  [ ] Image dimension validation rejects oversized files
  [ ] No regressions in query count

DEPLOYMENT READINESS:
=====================
  [ ] FLASK_ENV=production configured
  [ ] SECRET_KEY set via environment variable
  [ ] PostgreSQL database (not SQLite) for production
  [ ] HTTPS enabled and X-Forwarded-Proto header verified
  [ ] SESSION_COOKIE_SECURE=True in production config
  [ ] Health check endpoints responding
  [ ] Structured logging to app.log file
  [ ] Log rotation configured (daily)
  [ ] Monitoring reads /health/deep endpoint

RISK ASSESSMENT:
================
  CRITICAL: Missing flask-wtf in requirements.txt (Phase 0 won't work)
  HIGH:     Session cookies not secure for production HTTPS
  MEDIUM:   No health check endpoints (false-positive failures)
  MEDIUM:   No CSRF/rate limit tests (regression risk)
  MEDIUM:   No image dimension validation (DoS risk)
  LOW:      Stale DB connections (fixed by pool_pre_ping)

TIMELINE:
=========
  Phase 1 Complete: ~8-9 hours of work
  By Priority:
    P0:        5 min  (BLOCKER - do immediately)
    P1:       30 min  (foundational)
    P2:       45 min  (required for orchestration)
    P3:      2.00h   (critical test coverage)
    P4:      1.00h   (auth test coverage)
    P5:      1.50h   (SRE metrics)
    P6:       30 min  (DoS prevention)
    P7:      2.00h   (optional, high value)

NEXT STEPS:
===========
  1. Supervisor reviews AEGIS_PHASE1_STRATEGIC_AUDIT.md
  2. Supervisor approves Phase 1 execution
  3. Aegis generates implementation code for each task
  4. Supervisor integrates code and runs tests
  5. Manual verification before production deployment

DOCUMENTS FOR REVIEW:
=====================
  [ ] AEGIS_PHASE0_CODE_REVIEW.md          - Detailed findings
  [ ] AEGIS_PHASE1_STRATEGIC_AUDIT.md      - Implementation guide
  [ ] AEGIS_EXEC_SUMMARY.md                - Decision document
  [ ] AEGIS_NOTES.md                       - Strategic context

STATUS: READY FOR PHASE 1 EXECUTION
BLOCKER: Fix requirements.txt immediately

================================================================================
