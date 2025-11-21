# AEGIS Phase 0: Critical Security Hardening - IN PROGRESS

**Status:** Phase 0 Implementation In Progress
**Started:** 2025-11-14
**Priority:** CRITICAL - Blocking Production Deployment

---

## Phase 0 Overview

Phase 0 addresses three CRITICAL findings that must be fixed before production deployment:
1. CSRF Protection - State-changing endpoints vulnerable
2. Image Upload Security - DoS and validation gaps
3. N+1 Query Problem - Performance bottleneck in profile endpoint

---

## Item 1: CSRF Protection Implementation ✅ 60% COMPLETE

### Changes Made:
1. **Installed Flask-SeaSurf** (`pip install flask-seasurf`)
2. **app.py**:
   - Added `from flask_seasurf import SeaSurf` import
   - Initialized CSRF: `csrf = SeaSurf(app)` after database init
   - Created `/csrf-token` GET endpoint that returns CSRF token for JavaScript

3. **static/js/main.js**:
   - Added `CSRF_TOKEN` global variable
   - Added `getCsrfToken()` async function to fetch token from server
   - Added `fetchWithCsrf()` wrapper that automatically includes `X-CSRFToken` header on state-changing requests
   - Updated `init()` to call `getCsrfToken()` on page load
   - Updated `login()` to use `fetchWithCsrf()` instead of `fetch()`
   - Updated `register()` to use `fetchWithCsrf()`
   - Updated `logout()` to use `fetchWithCsrf()`

### Still Need To Do:
- Update ALL other POST/PUT/DELETE requests in:
  - profile.js (profile edit, avatar upload, note saving)
  - course_detail.js (progress updates, note saving)
  - Any other state-changing API calls
- Remove `WTF_CSRF_ENABLED = False` from TestingConfig in config.py
- Add CSRF token validation tests

### How It Works:
1. Page loads → `init()` calls `getCsrfToken()` → fetches from `/csrf-token` endpoint
2. CSRF token cached in `CSRF_TOKEN` global variable
3. Any POST/PUT/DELETE call uses `fetchWithCsrf()` instead of `fetch()`
4. `fetchWithCsrf()` automatically adds `X-CSRFToken: [token]` header
5. Flask-SeaSurf validates token on server side, rejects requests without valid token

---

## Item 2: Image Upload Security - NOT STARTED

### Key Vulnerabilities to Fix:
1. No image format validation before saving to disk
2. No file size limit (disk exhaustion DoS)
3. No exception handling for malformed images
4. Extension check bypassable (checks extension only, not magic bytes)

### Implementation Plan:
1. Add `MAX_UPLOAD_SIZE = 5MB` to config.py
2. Update `/api/profile/avatar` endpoint to:
   - Use `Image.open(file.stream)` BEFORE saving
   - Validate image format (JPEG, PNG only)
   - Check file size against limit
   - Wrap in try/except for PIL.UnidentifiedImageError
3. Reject malformed files with 400 Bad Request

---

## Item 3: N+1 Query Problem - NOT STARTED

### Issue Location:
- `/api/profile` GET endpoint (lines 293-354)
- Makes 1 initial query + N additional queries per course/note/ebook
- With 100 courses: 300+ queries per profile load
- Causes timeouts and cascading failures

### Implementation Plan:
1. Add relationships to models.py:
   - CourseProgress → Course
   - CourseNote → Course
   - ReadingProgress → Ebook
2. Update `/api/profile` endpoint to use eager-loading:
   - Use `.options(joinedload(CourseProgress.course))`
   - Reduces 1+N queries to 1 query with JOIN

---

## Testing Requirements (To Be Added):
- CSRF token is generated and returned by `/csrf-token`
- CSRF token is included in POST request headers
- POST requests without valid CSRF token are rejected with 403
- Login/register/logout work with CSRF protection enabled
- Image uploads reject invalid formats
- Image uploads reject oversized files
- Profile endpoint completes in <100ms with 100+ courses

---

## Next Steps:
1. **Complete CSRF**: Update remaining POST requests in all JS files
2. **Implement Image Upload Security**: Add validation before save
3. **Implement N+1 Fix**: Add eager-loading to profile queries
4. **Testing**: Remove WTF_CSRF_ENABLED=False, add comprehensive tests
5. **Documentation**: Create PHASE0_COMPLETE.md after testing passes

---

## Dependencies:
- flask-seasurf==2.0.0 ✅ (installed)
- No new dependencies needed for image upload or N+1 fixes

---

**Last Updated:** 2025-11-14 02:XX UTC
**Next Review:** After completing all three items
