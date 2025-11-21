# PHASE 1 P3-P6 WORKPLAN
# TaskOrchestrator Execution Strategy

**Created:** 2025-11-14 08:45 UTC
**Owner:** TaskOrchestrator
**Scope:** Phase 1 P3-P6 (CSRF Tests, Rate Limit Tests, Structured Logging, Image Validation)
**Estimated Duration:** 3.5 hours (with parallelization)
**Token Budget:** 90,000 tokens projected (of 183,000 available)

---

## Executive Summary

This document coordinates the parallel execution of Phase 1 P3-P6 deliverables across three specialized agent teams:

- **TestEngineer**: Implements P3 (CSRF), P4 (Rate Limiting), P6 (Image Validation) test suites
- **InfrastructureEngineer**: Designs and implements P5 (Structured Logging) architecture
- **solutions-architect**: Validates P5 design and plans Phase 2 strategy

**Critical Path:** P3 (2 hrs) → P4+P6 parallel (1.5 hrs) = 3.5 hours total

**Key Insight:** P5 (Logging) can run 100% parallel with P3, reducing overall timeline from 5 hours sequential to 3.5 hours parallel.

---

## 1. Dependency Analysis

### 1.1 Dependency Graph (Text-Based)

```
START (T=0)
│
├─→ [P3: CSRF Tests] ────────────────────→ (2 hours) ─────┐
│   Owner: TestEngineer                                     │
│   Blocking: P4, P6                                        │
│   Blocked by: None                                        │
│                                                           │
├─→ [P5: Logging Design] ─────────→ (1.5 hours) ───────┐   │
│   Owner: InfrastructureEngineer                       │   │
│   Blocking: P5 Tests (part of TestEngineer work)      │   │
│   Blocked by: None (PARALLEL with P3)                 │   │
│                                                        │   │
├─→ [P5: Architecture Review] ───→ (1 hour) ────────┐   │   │
│   Owner: solutions-architect                       │   │   │
│   Blocking: P5 Implementation approval             │   │   │
│   Blocked by: None (PARALLEL with P3)              │   │   │
│   └─→ Approval Gate ───────────────────────────────┴───┘   │
│                                                             │
└─→ P3 COMPLETE (T=2.0 hrs) ←────────────────────────────────┘
    │
    ├─→ [P4: Rate Limit Tests] ────→ (1 hour) ──────┐
    │   Owner: TestEngineer                          │
    │   Blocking: Integration                        │
    │   Blocked by: P3 complete                      │
    │                                                 │
    └─→ [P6: Image Validation] ────→ (0.5 hours) ───┤
        Owner: TestEngineer                          │
        Blocking: Integration                        │
        Blocked by: P3 complete                      │
        (CAN RUN PARALLEL with P4)                   │
                                                     │
    └─→ P4+P6 COMPLETE (T=3.5 hrs) ←─────────────────┘
        │
        └─→ [INTEGRATION: Full Test Suite] → (0.5 hours)
            All agents consolidate
            Create pytest.ini
            Run full test suite
            Generate completion report

    └─→ PHASE 1 P3-P6 COMPLETE (T=4.0 hrs) ←─────────┘
        │
        └─→ [AEGIS Validation] → (0.5 hours)
            Security audit
            Production readiness
            Approval for deployment
```

### 1.2 Critical Path Identification

**CRITICAL PATH (longest sequence):**
```
START → P3 (2.0 hrs) → P4 (1.0 hrs) → Integration (0.5 hrs) → COMPLETE
Total: 3.5 hours
```

**Non-Critical Paths (can run parallel):**
```
Path 2: P5 Logging (1.5 hrs) || P3 (2.0 hrs)
Path 3: P5 Architecture Review (1.0 hrs) || P3 (2.0 hrs)
Path 4: P6 (0.5 hrs) || P4 (1.0 hrs) [both after P3]
```

**Key Observation:** P5 completes before P3, enabling TestEngineer to test logging immediately after P3.

### 1.3 Blocking Relationships

| Task | Blocks | Blocked By | Can Parallelize With |
|------|--------|------------|---------------------|
| P3 (CSRF Tests) | P4, P6 | None | P5 Logging, P5 Architecture Review |
| P4 (Rate Limits) | Integration | P3 complete | P6, P5 (already done) |
| P5 (Logging Design) | P5 Tests | None | P3, P4, P6 |
| P5 (Arch Review) | P5 Approval | None | P3, P4, P6 |
| P6 (Image Valid) | Integration | P3 complete | P4, P5 (already done) |
| Integration | AEGIS | P3, P4, P6 | None |

---

## 2. Timeline Visualization

### 2.1 Gantt-Style ASCII Chart

```
Time →   0h    0.5h   1.0h   1.5h   2.0h   2.5h   3.0h   3.5h   4.0h
         │      │      │      │      │      │      │      │      │
Track A  ├──────────P3: CSRF Tests───────────┤P4:Rate┤P6:Img├Int─┤
(Test)   │ TestEngineer                      │Limits │Valid │egr │
         │                                   │       │(para)│ate │
         │      │      │      │      │      │      │      │      │
Track B  ├─────P5: Logging Design────┤       │      │      │      │
(Infra)  │ InfrastructureEngineer    │       │      │      │      │
         │                            │       │      │      │      │
         │      │      │      │      │      │      │      │      │
Track C  ├──P5: Arch Review───┤       │      │      │      │      │
(Arch)   │ solutions-architect│       │      │      │      │      │
         │                    │       │      │      │      │      │
         └─────────────────────────────────────────────────────────┘

Legend:
────  Active work
│     Time marker
├─┤   Task boundary
(para) Parallel execution

CRITICAL PATH HIGHLIGHTED:
═══════P3══════════════════════════P4═══════Integration═══
0h                               2.0h    3.0h          3.5h
```

### 2.2 Timeline Breakdown by Hour

**Hour 0.0 - 1.0 (Parallel Startup)**
- **Track A (TestEngineer)**: Start P3 CSRF Tests (design test strategy, create test file structure)
- **Track B (InfrastructureEngineer)**: Start P5 Logging Design (evaluate structlog, design JSON schema)
- **Track C (solutions-architect)**: Start P5 Architecture Review (review logging approach)

**Hour 1.0 - 2.0 (P3 Heavy Lifting, P5 Completion)**
- **Track A (TestEngineer)**: Continue P3 (implement 20+ test cases, run coverage analysis)
- **Track B (InfrastructureEngineer)**: Complete P5 design (80% → 100%, hand off to TestEngineer)
- **Track C (solutions-architect)**: Complete architecture approval (approve or iterate)

**Hour 2.0 - 3.0 (P3→P4 Transition, P4 Start)**
- **Track A (TestEngineer)**: P3 COMPLETE → Start P4 Rate Limit Tests (design + implement)
- **Track B (InfrastructureEngineer)**: IDLE (P5 complete, available for support)
- **Track C (solutions-architect)**: IDLE (P5 approved, available for Phase 2 planning)

**Hour 3.0 - 3.5 (P4+P6 Parallel, Integration)**
- **Track A (TestEngineer)**: P4 COMPLETE → Start P6 Image Validation (parallel with P4 wrap-up if needed)
- **Track A (TestEngineer)**: P6 COMPLETE → Integration (create pytest.ini, run full suite)
- **Track B/C**: Available for integration support

**Hour 3.5 - 4.0 (Final Consolidation)**
- **All Tracks**: Generate Phase 1 P3-P6 completion report
- **All Tracks**: Prepare handoff to AEGIS for validation

---

## 3. Agent Task Assignments

### 3.1 Agent 1: TestEngineer

**Task:** Implement Phase 1 P3, P4, P6 test suites
**Authority:** Full code modification, spawn sub-agents if needed
**Entry Point:** `docs/phases/PHASE1_QUICK_REFERENCE.md`
**References:**
- `docs/living-memory.md` (project context)
- `docs/security/AEGIS_PHASE1_STRATEGIC_AUDIT.md` (security requirements)
- `app.py` (lines 25-27 for CSRF, lines 82-114 for rate limiting)

**Timeline:** 3.5 hours (sequential P3→P4→P6, integration at end)

---

#### Task P3: CSRF Test Suite (2 hours)

**Objective:** Create comprehensive CSRF protection test suite with 20+ test cases

**Deliverables:**
1. `tests/test_csrf.py` - Comprehensive CSRF test file
2. `tests/conftest.py` - Pytest fixtures for CSRF token handling
3. Coverage report showing CSRF protection validation
4. Test execution report (all tests passing)

**Test Categories:**
1. **Token Generation Tests** (3 tests)
   - `test_csrf_token_endpoint_returns_valid_token()`
   - `test_csrf_token_format_validation()`
   - `test_csrf_token_uniqueness()`

2. **Token Validation Tests** (5 tests)
   - `test_post_without_csrf_token_rejected()`
   - `test_post_with_valid_csrf_token_accepted()`
   - `test_post_with_invalid_csrf_token_rejected()`
   - `test_post_with_expired_csrf_token_rejected()`
   - `test_csrf_token_reuse_prevention()`

3. **Endpoint Coverage Tests** (8 tests)
   - `test_register_without_csrf_token_rejected()`
   - `test_register_with_csrf_token_succeeds()`
   - `test_login_without_csrf_token_rejected()`
   - `test_login_with_csrf_token_succeeds()`
   - `test_upload_avatar_without_csrf_token_rejected()`
   - `test_upload_avatar_with_csrf_token_succeeds()`
   - `test_update_profile_csrf_protection()`
   - `test_admin_actions_csrf_protection()`

4. **Edge Cases & Security Tests** (5+ tests)
   - `test_csrf_token_cross_session_invalid()`
   - `test_csrf_token_persists_across_requests_in_same_session()`
   - `test_get_requests_do_not_require_csrf()`
   - `test_csrf_exempt_endpoints_if_any()`
   - `test_double_submit_cookie_pattern_if_used()`

**Success Criteria:**
- All 20+ tests pass
- WTF_CSRF_ENABLED=True in test config (NOT False)
- Coverage analysis shows CSRF protection validation
- No false positives (valid tokens accepted)
- No false negatives (invalid tokens rejected)

**Implementation Pattern:**
```python
def test_post_with_csrf_token_accepted(client):
    # 1. Fetch CSRF token
    token_response = client.get('/csrf-token')
    csrf_token = token_response.json['csrf_token']

    # 2. Make POST request with token
    headers = {'X-CSRFToken': csrf_token}
    response = client.post('/api/endpoint',
                          json={'data': 'value'},
                          headers=headers)

    # 3. Assert success
    assert response.status_code == 200
```

**Key Configuration:**
```python
# tests/conftest.py
@pytest.fixture
def app():
    app = create_app('testing')
    app.config['WTF_CSRF_ENABLED'] = True  # CRITICAL: Must be True
    app.config['TESTING'] = True
    return app
```

---

#### Task P4: Rate Limit Test Suite (1 hour)

**Objective:** Validate rate limiting enforcement across authentication endpoints

**Deliverables:**
1. `tests/test_rate_limiting.py` - Rate limit test file
2. Test report showing rate limits enforced correctly
3. Edge case documentation (in-memory vs Redis)

**Test Categories:**
1. **Login Rate Limiting** (3 tests)
   - `test_rate_limit_login_enforcement()` - 5 attempts OK, 6th rejected with 429
   - `test_rate_limit_login_reset_after_window()` - Limits reset after time window
   - `test_rate_limit_login_per_ip_isolation()` - Different IPs have separate limits

2. **Register Rate Limiting** (3 tests)
   - `test_rate_limit_register_enforcement()` - 5 attempts OK, 6th rejected with 429
   - `test_rate_limit_register_reset_after_window()`
   - `test_rate_limit_register_per_ip_isolation()`

3. **Other Endpoints** (2 tests)
   - `test_rate_limit_avatar_upload_enforcement()`
   - `test_no_rate_limit_on_get_endpoints()` - GET requests not rate limited

4. **In-Memory Tracking Validation** (3 tests)
   - `test_rate_limit_counter_accuracy()` - Verify counter tracks attempts correctly
   - `test_rate_limit_cleanup_old_attempts()` - Old attempts cleaned from memory
   - `test_rate_limit_memory_usage_bounded()` - Memory doesn't grow unbounded

**Success Criteria:**
- Rate limits enforced correctly (429 on 6th attempt)
- Rate limits reset after time window
- Per-IP isolation works correctly
- In-memory tracking accurate (not off-by-one errors)
- No memory leaks (old attempts cleaned up)

**Implementation Pattern:**
```python
def test_rate_limit_login_enforcement(client):
    # Fetch CSRF token
    token_response = client.get('/csrf-token')
    csrf_token = token_response.json['csrf_token']

    headers = {'X-CSRFToken': csrf_token}

    # Attempt 1-5: Should return 401 (invalid credentials) or 201 (success)
    for i in range(5):
        response = client.post('/api/login',
                              json={'username': 'test', 'password': 'wrong'},
                              headers=headers)
        assert response.status_code in [401, 201]

    # Attempt 6: Should return 429 (Too Many Requests)
    response = client.post('/api/login',
                          json={'username': 'test', 'password': 'wrong'},
                          headers=headers)
    assert response.status_code == 429
    assert 'rate limit' in response.json['error'].lower()
```

**Edge Cases to Document:**
- In-memory rate limiting is single-instance (not distributed)
- For production with multiple servers, use Redis backend
- Time window calculation (UTC vs local time)
- IP address extraction (X-Forwarded-For handling)

---

#### Task P6: Image Dimension Validation Tests (30 minutes)

**Objective:** Test image dimension checks to prevent DoS attacks

**Deliverables:**
1. `tests/test_image_validation.py` - Image validation test file
2. Performance impact analysis
3. Test report showing DoS prevention works

**Test Categories:**
1. **Dimension Validation** (4 tests)
   - `test_valid_image_dimensions_accepted()` - 1024x768 image accepted
   - `test_oversized_width_rejected()` - 5000x1000 image rejected (400 error)
   - `test_oversized_height_rejected()` - 1000x5000 image rejected (400 error)
   - `test_max_dimensions_boundary()` - 4096x4096 accepted (at limit)

2. **Format Detection** (3 tests)
   - `test_valid_image_formats_accepted()` - JPEG, PNG, GIF accepted
   - `test_invalid_image_format_rejected()` - BMP, TIFF rejected
   - `test_malformed_image_rejected()` - Corrupted file rejected

3. **DoS Prevention** (3 tests)
   - `test_image_bomb_detection()` - Decompression bomb rejected
   - `test_large_file_size_rejected()` - 50MB file rejected
   - `test_processing_time_bounded()` - Image processing < 500ms

4. **Performance Impact** (2 tests)
   - `test_validation_overhead_acceptable()` - < 50ms overhead
   - `test_concurrent_uploads_no_resource_exhaustion()` - 10 concurrent uploads OK

**Success Criteria:**
- Oversized images (>4096x4096) rejected with 400 error
- Valid images accepted
- Decompression bombs detected
- Processing time < 500ms per image
- Validation overhead < 50ms

**Implementation Pattern:**
```python
from PIL import Image
import io

def test_oversized_width_rejected(client, auth_headers):
    # Create oversized image (5000x1000)
    img = Image.new('RGB', (5000, 1000), color='red')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # Upload oversized image
    response = client.post('/api/upload-avatar',
                          data={'avatar': (img_bytes, 'test.png')},
                          headers=auth_headers,
                          content_type='multipart/form-data')

    # Should be rejected
    assert response.status_code == 400
    assert 'dimensions too large' in response.json['error'].lower()
```

**Code Validation:**
Verify app.py contains:
```python
MAX_IMAGE_WIDTH = 4096
MAX_IMAGE_HEIGHT = 4096
if img.size[0] > MAX_IMAGE_WIDTH or img.size[1] > MAX_IMAGE_HEIGHT:
    return jsonify({'error': 'Image dimensions too large'}), 400
```

---

### 3.2 Agent 2: InfrastructureEngineer

**Task:** Design and implement structured logging architecture (P5)
**Authority:** Full code modification, database schema changes if needed
**Entry Point:** `docs/architecture/STRUCTURE_AUDIT.md`
**References:**
- `docs/living-memory.md` (project context)
- `docs/security/AEGIS_PHASE1_STRATEGIC_AUDIT.md` (logging requirements)
- `app.py` (current application structure)

**Timeline:** 1.5 hours (parallel with P3)

---

#### Task P5: Structured Logging Architecture (1.5 hours)

**Objective:** Design JSON-structured logging framework with request ID tracking

**Deliverables:**
1. **Logging Architecture Design Document** (20 minutes)
   - JSON output schema specification
   - Log levels strategy (DEBUG, INFO, WARNING, ERROR, CRITICAL)
   - Request ID tracking mechanism
   - Security event logging strategy
   - Production deployment considerations

2. **Technology Evaluation Report** (15 minutes)
   - structlog vs alternatives (python-json-logger, pythonjsonlogger)
   - Rationale for chosen approach
   - Pros/cons analysis

3. **Flask Integration Design** (15 minutes)
   - before_request hook design
   - after_request hook design
   - Error handler logging strategy
   - Performance impact analysis (<5ms overhead target)

4. **Log Analyzer Tool Design** (20 minutes)
   - Script specification: `scripts/log_analyzer.py`
   - Features: error rate calculation, latency percentiles (P50, P95, P99)
   - Alert thresholds: error rate > 1%
   - Usage: `python scripts/log_analyzer.py [--last-minutes 10]`

5. **Implementation Plan** (20 minutes)
   - Step-by-step implementation guide
   - Code snippets for each component
   - Testing strategy for logging
   - Handoff to TestEngineer at 80% complete

**JSON Output Schema:**
```json
{
  "timestamp": "2025-11-14T08:45:23.123Z",
  "level": "INFO",
  "event": "request_received",
  "request_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "method": "POST",
  "path": "/api/login",
  "remote_addr": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "user_id": 42,
  "duration_ms": 123.45,
  "status_code": 200,
  "error": null,
  "extra": {
    "custom_field": "value"
  }
}
```

**Flask Integration Pattern:**
```python
import structlog
import uuid
from flask import g, request

logger = structlog.get_logger()

@app.before_request
def before_request_logging():
    g.request_id = str(uuid.uuid4())
    g.start_time = time.time()

    logger.info("request_received",
                request_id=g.request_id,
                method=request.method,
                path=request.path,
                remote_addr=request.remote_addr)

@app.after_request
def after_request_logging(response):
    duration_ms = (time.time() - g.start_time) * 1000

    logger.info("request_complete",
                request_id=g.request_id,
                method=request.method,
                path=request.path,
                status_code=response.status_code,
                duration_ms=duration_ms)

    return response
```

**Log Analyzer Tool Features:**
1. **Error Rate Calculation**
   - Parse JSON logs from last N minutes
   - Calculate: (status_code >= 400) / total_requests
   - Alert if > 1%

2. **Latency Percentiles**
   - Parse duration_ms from logs
   - Calculate P50, P95, P99
   - Alert if P95 > 1000ms

3. **Top Errors Report**
   - Group errors by path + error message
   - Show top 10 most frequent errors

**Success Criteria:**
- JSON output schema defined and approved by solutions-architect
- structlog vs alternatives evaluated with clear rationale
- Flask integration design complete (before/after hooks)
- Log analyzer tool specification complete
- Implementation plan ready for handoff to TestEngineer
- Performance overhead < 5ms per request

---

### 3.3 Agent 3: solutions-architect

**Task:** Validate InfrastructureEngineer's P5 design, plan Phase 2 strategy
**Authority:** Approve or recommend changes to InfrastructureEngineer
**Entry Point:** `docs/living-memory.md`
**References:**
- `docs/security/AEGIS_PHASE1_STRATEGIC_AUDIT.md` (strategic requirements)
- InfrastructureEngineer's P5 design deliverables (as they become available)

**Timeline:** 1 hour (parallel with P3, quick turnaround on P5 review)

---

#### Task P5: Architecture Validation & Phase 2 Planning (1 hour)

**Objective:** Validate P5 logging architecture and plan Phase 2 migration strategy

**Deliverables:**
1. **P5 Design Review Report** (15 minutes)
   - Validation of JSON schema (aligns with AHDM requirements?)
   - Validation of Flask integration approach (performance acceptable?)
   - Validation of log analyzer tool design (meets observability needs?)
   - APPROVE or REQUEST CHANGES with specific recommendations

2. **AHDM Integration Validation** (15 minutes)
   - Confirm JSON schema supports AHDM log analysis
   - Confirm request_id tracking enables distributed tracing
   - Confirm error event logging supports predictive analysis
   - Confirm security event logging supports audit trail

3. **Phase 2 Structured Logging Migration Plan** (15 minutes)
   - Strategy for migrating existing log statements to structured logging
   - Identifying critical log points (auth, errors, security events)
   - Performance monitoring strategy during migration
   - Rollback plan if logging causes issues

4. **Architecture Decision Record** (10 minutes)
   - Document key decisions (why structlog? why JSON?)
   - Document rationale for JSON schema fields
   - Document performance trade-offs
   - Document production deployment considerations

5. **Approval Gate** (5 minutes)
   - **APPROVE:** P5 design meets requirements → proceed to implementation
   - **ITERATE:** Specific changes needed → feedback to InfrastructureEngineer

**Review Checklist:**

**JSON Schema Validation:**
- [ ] Includes timestamp (ISO 8601 format)
- [ ] Includes request_id (UUID format)
- [ ] Includes standard HTTP fields (method, path, status_code)
- [ ] Includes performance metrics (duration_ms)
- [ ] Includes error details (error field for exceptions)
- [ ] Includes user_id for audit trail
- [ ] Extensible (extra field for custom data)

**Flask Integration Validation:**
- [ ] before_request hook lightweight (<2ms overhead)
- [ ] after_request hook captures response metadata
- [ ] Error handlers log exceptions with stack traces
- [ ] Logging does not block request processing
- [ ] Log output goes to file (not just console)
- [ ] Log rotation configured (daily rotation)

**Log Analyzer Validation:**
- [ ] Parses JSON logs correctly
- [ ] Calculates error rate accurately
- [ ] Calculates latency percentiles correctly
- [ ] Provides actionable alerts
- [ ] Can analyze last N minutes of logs
- [ ] Performance acceptable (analyze 10k log lines in <5s)

**AHDM Integration Validation:**
- [ ] JSON schema compatible with AHDM log parser
- [ ] request_id enables distributed tracing across services
- [ ] Error events provide sufficient context for root cause analysis
- [ ] Security events (auth failures, CSRF violations) logged
- [ ] Performance metrics (duration_ms) enable SLO monitoring

**Approval Decision Matrix:**

| Criteria | Weight | Pass? | Notes |
|----------|--------|-------|-------|
| JSON schema complete | HIGH | [ ] | All required fields present? |
| Flask integration sound | HIGH | [ ] | Performance acceptable? |
| AHDM compatible | HIGH | [ ] | JSON parseable by AHDM? |
| Log analyzer functional | MEDIUM | [ ] | Meets observability needs? |
| Performance overhead | MEDIUM | [ ] | <5ms per request? |
| Security events logged | HIGH | [ ] | Audit trail complete? |

**Approval Outcome:**
- **If all HIGH criteria pass:** APPROVE
- **If any HIGH criteria fail:** REQUEST CHANGES with specific feedback
- **If only MEDIUM criteria fail:** APPROVE with recommendations for future improvement

**Phase 2 Migration Strategy:**

**Phase 2 Structured Logging Scope:**
1. **Week 1:** Migrate authentication logging (login, logout, register)
2. **Week 2:** Migrate error handling logging (exceptions, validation errors)
3. **Week 3:** Migrate security event logging (CSRF, rate limits, authorization)
4. **Week 4:** Migrate business logic logging (course progress, ebook reading)

**Success Metrics for Phase 2:**
- All critical paths have structured logging
- Error rate visible in real-time via log analyzer
- P95 latency tracked and alerted on
- Security events auditable via JSON logs
- AHDM can analyze logs for predictive insights

---

## 4. Handoff Points & Coordination

### 4.1 Explicit Handoff Points

| Time | From | To | Artifact | Purpose |
|------|------|----|----|---------|
| **T=0.75 hrs** | InfrastructureEngineer | solutions-architect | P5 Design Draft | Early review, course correction |
| **T=1.0 hrs** | solutions-architect | InfrastructureEngineer | Approval or Feedback | Approve or iterate on design |
| **T=1.5 hrs** | InfrastructureEngineer | TestEngineer | P5 Implementation Plan | TestEngineer ready to test logging (after P3) |
| **T=2.0 hrs** | TestEngineer | ALL | P3 Complete Report | P3 done, moving to P4 |
| **T=3.0 hrs** | TestEngineer | ALL | P4 Complete Report | P4 done, moving to P6 |
| **T=3.5 hrs** | TestEngineer | ALL | P6 Complete Report | P6 done, integration starts |
| **T=4.0 hrs** | ALL | TaskOrchestrator | Phase 1 P3-P6 Report | Consolidation, handoff to AEGIS |

### 4.2 Coordination Mechanisms

**Shared Workspace:**
- All agents update `docs/living-memory.md` → "Current Agent Assignments" table
- Status updates: PENDING → IN_PROGRESS → COMPLETE
- Blockers logged in `docs/operations/ERROR_RECOVERY.md` (if needed)

**Communication Protocol:**
1. **Status Updates:** Update living-memory.md every 30 minutes
2. **Completion Reports:** Append to `docs/operations/IMPLEMENTATION_LOGS.md`
3. **Issues/Blockers:** Create entry in ERROR_RECOVERY.md with:
   - Issue description
   - Impact on timeline
   - Proposed resolution
   - Escalation trigger (if 3 attempts fail)

**Approval Gates:**
- **P5 Architecture Approval:** solutions-architect MUST approve before InfrastructureEngineer finalizes
- **Integration Gate:** ALL P3-P6 tests must pass before AEGIS validation

---

## 5. Risk Assessment

### 5.1 Risks by Task

| Task | Risk | Likelihood | Impact | Mitigation |
|------|------|------------|--------|------------|
| **P3: CSRF Tests** | Tests fail due to config issues | MEDIUM | HIGH | Verify WTF_CSRF_ENABLED=True, not False |
| **P3: CSRF Tests** | Flask-WTF version incompatibility | LOW | MEDIUM | Verify flask-wtf>=1.2.0 in requirements.txt |
| **P4: Rate Limits** | In-memory rate limiting test flakiness | MEDIUM | MEDIUM | Use time mocking, isolate tests |
| **P4: Rate Limits** | Rate limit counter off-by-one errors | MEDIUM | HIGH | Thorough boundary testing (5th vs 6th attempt) |
| **P5: Logging** | Performance overhead too high (>5ms) | LOW | HIGH | Profile logging hooks, optimize JSON serialization |
| **P5: Logging** | JSON schema not AHDM-compatible | MEDIUM | HIGH | Early review by solutions-architect (T=0.75 hrs) |
| **P5: Logging** | structlog dependency conflicts | LOW | MEDIUM | Test in isolated virtualenv first |
| **P6: Image Valid** | PIL/Pillow decompression bomb false positives | MEDIUM | MEDIUM | Test with variety of valid large images |
| **P6: Image Valid** | Performance degradation on large images | LOW | MEDIUM | Set timeout for image processing (500ms) |
| **Integration** | Pytest configuration issues | LOW | HIGH | Create pytest.ini with clear settings |
| **Integration** | Test interdependencies cause failures | MEDIUM | HIGH | Isolate tests (use fixtures, not shared state) |

### 5.2 Critical Path Risks

**Risk 1: P3 takes longer than 2 hours**
- **Impact:** Delays P4, P6, and integration → entire timeline slips
- **Likelihood:** MEDIUM (CSRF tests can be complex)
- **Mitigation:**
  - TestEngineer can parallelize test writing (use sub-agents if available)
  - Prioritize critical tests first (token validation, endpoint coverage)
  - Defer edge case tests if behind schedule (can add later)

**Risk 2: P5 design rejected by solutions-architect**
- **Impact:** InfrastructureEngineer must iterate → delays P5 completion
- **Likelihood:** LOW (early review at T=0.75 hrs catches issues)
- **Mitigation:**
  - solutions-architect provides early feedback at 50% completion
  - Clear approval criteria defined upfront (JSON schema, performance)
  - InfrastructureEngineer can implement while awaiting approval (revert if rejected)

**Risk 3: Test failures during integration**
- **Impact:** Debugging adds time → delays AEGIS validation
- **Likelihood:** MEDIUM (new tests often have issues)
- **Mitigation:**
  - Run tests incrementally during development (not just at end)
  - Use pytest markers to run test suites independently
  - Allocate 0.5 hours buffer for integration debugging

### 5.3 Escalation Criteria

**ESCALATE TO CLAUDE CODE IF:**
1. **Architectural Flaw Found:** Fundamental issue with Flask-WTF, structlog, or rate limiting approach
2. **3 Failures on Same Task:** Agent attempts same task 3 times without success
3. **Security Issue Discovered:** New security vulnerability found during testing
4. **Token Budget Exceeded:** Agents consume >90,000 tokens (projected budget)
5. **Timeline Slip >1 Hour:** Critical path slips more than 1 hour beyond estimate

**DO NOT ESCALATE FOR:**
- Individual test failures (debug and fix autonomously)
- Minor design disagreements between agents (resolve via approval gate)
- Documentation formatting issues (fix autonomously)
- Non-critical path delays (P5 taking 2 hours instead of 1.5 hours is OK)

---

## 6. Success Criteria

### 6.1 Completion Criteria by Task

**P3: CSRF Test Suite**
- [ ] `tests/test_csrf.py` created with 20+ test cases
- [ ] `tests/conftest.py` created with CSRF token fixtures
- [ ] All CSRF tests pass (pytest tests/test_csrf.py)
- [ ] Coverage report shows CSRF protection validated
- [ ] Test report documents test strategy and results

**P4: Rate Limit Test Suite**
- [ ] `tests/test_rate_limiting.py` created with 10+ test cases
- [ ] All rate limit tests pass
- [ ] 429 status code returned on 6th attempt
- [ ] In-memory tracking accuracy validated
- [ ] Edge cases documented (single-instance limitation)

**P5: Structured Logging**
- [ ] Logging architecture design document complete
- [ ] JSON output schema defined and approved
- [ ] structlog vs alternatives evaluation complete
- [ ] Flask integration design complete (before/after hooks)
- [ ] Log analyzer tool specification complete
- [ ] Implementation plan ready for TestEngineer
- [ ] Approved by solutions-architect

**P6: Image Dimension Validation**
- [ ] `tests/test_image_validation.py` created with 10+ test cases
- [ ] All image validation tests pass
- [ ] Oversized images (>4096x4096) rejected with 400 error
- [ ] DoS prevention validated (decompression bomb detection)
- [ ] Performance impact < 500ms per image

**Integration**
- [ ] `pytest.ini` created with test configuration
- [ ] Full test suite runs successfully (pytest tests/)
- [ ] All P3, P4, P6 tests pass
- [ ] No test interdependencies or flakiness
- [ ] Phase 1 P3-P6 completion report generated

### 6.2 Overall Phase 1 P3-P6 Success Criteria

**Functional Requirements:**
- [ ] CSRF protection validated across all POST endpoints
- [ ] Rate limiting enforced on authentication endpoints
- [ ] Structured logging architecture designed and approved
- [ ] Image dimension validation prevents DoS attacks
- [ ] All tests pass in single test suite run

**Quality Requirements:**
- [ ] Test coverage >80% for security features
- [ ] No false positives or false negatives in tests
- [ ] Tests are isolated (no shared state)
- [ ] Tests are fast (<5 seconds for full suite)
- [ ] Documentation clear and comprehensive

**Integration Requirements:**
- [ ] All agents complete work on time (3.5 hours target)
- [ ] No architectural flaws discovered
- [ ] No security vulnerabilities introduced
- [ ] Token budget <90,000 tokens
- [ ] Ready for AEGIS validation

**Handoff Requirements:**
- [ ] Phase 1 P3-P6 completion report submitted
- [ ] living-memory.md updated with status
- [ ] IMPLEMENTATION_LOGS.md updated with summaries
- [ ] All code committed to git (no uncommitted changes)
- [ ] Ready for AEGIS security audit

---

## 7. Token Budget Projection

### 7.1 Token Budget by Agent

| Agent | Task | Estimated Tokens | Justification |
|-------|------|------------------|---------------|
| **TestEngineer** | P3 CSRF Tests | 20,000 | 20+ test cases, complex CSRF token handling |
| **TestEngineer** | P4 Rate Limit Tests | 10,000 | 10+ test cases, rate limit logic testing |
| **TestEngineer** | P6 Image Validation | 5,000 | 10+ test cases, image creation/upload |
| **TestEngineer** | Integration | 5,000 | pytest.ini, full suite run, debugging |
| **InfrastructureEngineer** | P5 Logging Design | 15,000 | Architecture design, evaluation, documentation |
| **solutions-architect** | P5 Review & Phase 2 | 10,000 | Design review, approval, Phase 2 planning |
| **TaskOrchestrator** | Coordination | 5,000 | Status updates, handoffs, consolidation |
| **Buffer** | Debugging & Iteration | 20,000 | Unexpected issues, retries, escalations |

**Total Projected:** 90,000 tokens
**Available Budget:** 183,000 tokens (from living-memory.md)
**Remaining After P3-P6:** 93,000 tokens (46.5% of original budget)

### 7.2 Token Budget Safeguards

**Budget Monitoring:**
- Track token usage after each task completion
- Update living-memory.md with running total
- Alert if any agent exceeds individual budget by >20%

**Budget Overrun Scenarios:**
- **If TestEngineer exceeds 40,000 tokens:** Prioritize critical tests, defer edge cases
- **If InfrastructureEngineer exceeds 15,000 tokens:** Simplify design documentation
- **If total exceeds 110,000 tokens:** Escalate to Claude Code (risky for Phase 2)

**Budget Optimization:**
- Reuse test fixtures across test files (reduce duplication)
- Use concise but clear documentation (avoid verbosity)
- Consolidate status updates (batch updates every 30 min, not per test)

---

## 8. Post-Completion Checklist

### 8.1 Agent Consolidation Tasks

**TaskOrchestrator Post-Completion:**
1. [ ] Collect completion reports from all agents
2. [ ] Verify all deliverables submitted
3. [ ] Update living-memory.md with final status
4. [ ] Generate Phase 1 P3-P6 completion report
5. [ ] Create handoff document for AEGIS
6. [ ] Update PHASE1_QUICK_REFERENCE.md (mark P3-P6 complete)

**TestEngineer Post-Completion:**
1. [ ] Commit all test files to git
2. [ ] Generate test coverage report (pytest --cov)
3. [ ] Document any test failures or edge cases
4. [ ] Submit completion summary to IMPLEMENTATION_LOGS.md
5. [ ] Update living-memory.md with P3, P4, P6 status

**InfrastructureEngineer Post-Completion:**
1. [ ] Finalize P5 design document
2. [ ] Submit implementation plan to TestEngineer
3. [ ] Document architectural decisions (ADR format)
4. [ ] Submit completion summary to IMPLEMENTATION_LOGS.md
5. [ ] Update living-memory.md with P5 status

**solutions-architect Post-Completion:**
1. [ ] Finalize P5 approval decision
2. [ ] Submit Phase 2 migration strategy
3. [ ] Document approval rationale (ADR format)
4. [ ] Submit completion summary to IMPLEMENTATION_LOGS.md
5. [ ] Update living-memory.md with approval status

### 8.2 Handoff to AEGIS

**Handoff Document Contents:**
1. **Phase 1 P3-P6 Summary**
   - Tasks completed (P3, P4, P5, P6)
   - Test results (all passing?)
   - Deliverables submitted (test files, design docs)

2. **Test Coverage Report**
   - CSRF protection: 20+ tests, coverage %
   - Rate limiting: 10+ tests, coverage %
   - Image validation: 10+ tests, coverage %

3. **Structured Logging Architecture**
   - Design approved by solutions-architect
   - JSON schema defined
   - Implementation plan ready

4. **Outstanding Issues**
   - Any edge cases deferred
   - Any known limitations (in-memory rate limiting)
   - Any recommendations for AEGIS review

5. **Next Steps for AEGIS**
   - Security audit of test coverage
   - Validation of CSRF protection implementation
   - Validation of rate limiting enforcement
   - Validation of image validation DoS prevention
   - Approval for production deployment

---

## 9. Lessons Learned & Continuous Improvement

### 9.1 Post-Mortem Questions

**After Phase 1 P3-P6 completion, answer:**

1. **Timeline Accuracy:** Did we meet the 3.5 hour estimate? If not, why?
2. **Parallelization Effectiveness:** Did P5 running parallel with P3 save time?
3. **Agent Coordination:** Were handoffs smooth? Any communication gaps?
4. **Test Quality:** Did any tests fail? Were they flaky or robust?
5. **Token Budget:** Did we stay under 90,000 tokens? If not, where did we overspend?
6. **Risk Mitigation:** Did any identified risks materialize? How did we handle them?

### 9.2 Improvement Opportunities

**For Future Phases:**
- [ ] Template test files to speed up TestEngineer work
- [ ] Pre-approve design patterns to reduce review cycles
- [ ] Automate status updates (reduce manual living-memory.md updates)
- [ ] Create test data fixtures upfront (reduce test writing time)
- [ ] Use pytest markers for better test organization

---

## 10. Appendix: Quick Reference

### 10.1 Key File Locations

| File | Path | Purpose |
|------|------|---------|
| Living Memory | `docs/living-memory.md` | Central project context |
| Phase 1 Reference | `docs/phases/PHASE1_QUICK_REFERENCE.md` | Phase 1 task list |
| Structure Audit | `docs/architecture/STRUCTURE_AUDIT.md` | Codebase structure |
| Implementation Logs | `docs/operations/IMPLEMENTATION_LOGS.md` | Agent work summaries |
| Test Directory | `tests/` | All test files |
| CSRF Tests | `tests/test_csrf.py` | P3 deliverable |
| Rate Limit Tests | `tests/test_rate_limiting.py` | P4 deliverable |
| Image Tests | `tests/test_image_validation.py` | P6 deliverable |
| Pytest Config | `pytest.ini` | Test suite configuration |
| App Entry Point | `app.py` | Main Flask application |

### 10.2 Key Commands

**Run Full Test Suite:**
```bash
cd "C:\Users\nissa\Desktop\HTML5 Project for courses"
pytest tests/ -v --tb=short
```

**Run Individual Test Suites:**
```bash
pytest tests/test_csrf.py -v
pytest tests/test_rate_limiting.py -v
pytest tests/test_image_validation.py -v
```

**Generate Coverage Report:**
```bash
pytest tests/ --cov=app --cov-report=html
```

**Update Living Memory:**
```bash
# Edit docs/living-memory.md
# Update "Current Agent Assignments" table
# Update "Token Budget Tracking" section
```

### 10.3 Agent Contact Protocol

**Status Update Format:**
```markdown
## Agent Status Update - [Agent Name] - [Time]

**Task:** [P3/P4/P5/P6]
**Status:** [IN_PROGRESS/COMPLETE]
**Progress:** [X% complete]
**Blockers:** [None / Issue description]
**Next Steps:** [What's next]
**ETA:** [Estimated completion time]
```

**Completion Report Format:**
```markdown
## Task Completion Report - [Agent Name] - [Task]

**Completed:** [Timestamp]
**Deliverables:**
- [File 1]
- [File 2]

**Results:**
- [Outcome 1]
- [Outcome 2]

**Issues Encountered:**
- [Issue 1 + resolution]

**Handoff Notes:**
- [Next agent + artifact]
```

---

## 11. Execution Authorization

**TaskOrchestrator Authorization:**
- Full authority to spawn TestEngineer, InfrastructureEngineer, solutions-architect
- Full authority to coordinate handoffs and dependencies
- Full authority to update living-memory.md and project documentation
- Authority to escalate if escalation criteria met
- Authority to terminate agents if needed (token budget exhaustion, blocking issues)

**Agent Autonomy:**
- Agents have full code modification authority within their scope
- Agents can spawn sub-agents if needed (e.g., TestEngineer spawns test-writer, test-runner)
- Agents debug and iterate autonomously (do not escalate for routine failures)
- Agents update living-memory.md with status every 30 minutes

**Escalation Authority:**
- TaskOrchestrator escalates to Claude Code only if escalation criteria met
- solutions-architect has veto authority on P5 design (can request changes)
- AEGIS has final authority on security validation (after P3-P6 complete)

---

## 12. Final Notes

**Critical Success Factors:**
1. **P3 must complete on time (2 hours)** - It blocks P4 and P6
2. **P5 design must be approved by solutions-architect** - Early review critical
3. **Tests must be isolated and robust** - No flakiness or interdependencies
4. **Token budget must stay under 90,000** - Else Phase 2 at risk
5. **All agents coordinate via living-memory.md** - Single source of truth

**Key Risks:**
1. **P3 taking >2 hours** - Delays entire timeline
2. **Test flakiness** - Wastes time debugging
3. **P5 design rejection** - Requires iteration, delays completion

**Mitigation:**
- TestEngineer prioritizes critical tests first
- Use time mocking and fixtures to prevent flakiness
- solutions-architect provides early P5 feedback at T=0.75 hrs

**Expected Outcome:**
- Phase 1 P3-P6 complete in 3.5 hours
- All tests passing, logging designed, ready for AEGIS validation
- Token budget <90,000, leaving 93,000 for Phase 2
- Clean handoff to AEGIS with comprehensive test coverage

---

**STATUS:** READY FOR EXECUTION
**NEXT STEP:** Spawn 3 agents (TestEngineer, InfrastructureEngineer, solutions-architect) and begin parallel execution

**END OF WORKPLAN**
