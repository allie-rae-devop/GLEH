# Next Session Checklist - Phase 0 Continuation

## Priority Order (Do These First)

### 1. CSRF Protection Completion
**Status:** 60% done - Only login/register/logout updated

**MUST DO:**
- [ ] Update `static/js/profile.js` - Add `fetchWithCsrf()` to:
  - Profile update endpoint
  - Avatar upload endpoint
  - Note saving endpoint

- [ ] Update `static/js/course_detail.js` - Add `fetchWithCsrf()` to:
  - Progress update endpoint (3 progress buttons)
  - Note saving endpoint
  - Login/register in modal

- [ ] Update `config.py` - Remove CSRF test bypass:
  - Change `WTF_CSRF_ENABLED = False` to `True` in TestingConfig

- [ ] Test CSRF is working:
  - Try login/register - should work
  - Try saving profile - should work
  - Try updating progress - should work
  - Try saving notes - should work

**Expected Outcome:** All POST requests protected by CSRF tokens

---

### 2. Image Upload Security
**Status:** 0% - Not started

**MUST DO:**
- [ ] Add to `config.py`:
  ```python
  MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
  ```

- [ ] Update `app.py` - `/api/profile/avatar` endpoint:
  - Add pre-save validation using `Image.open(file.stream)`
  - Check image format (JPEG, PNG only)
  - Check file size against MAX_UPLOAD_SIZE
  - Add try/except for PIL.UnidentifiedImageError
  - Reject invalid files with 400 Bad Request

- [ ] Test image upload:
  - Upload valid PNG - should work
  - Upload valid JPEG - should work
  - Upload invalid format (e.g., .txt as image) - should reject
  - Upload oversized file (>5MB) - should reject
  - Upload malformed image - should reject

**Expected Outcome:** Only valid, small images can be uploaded

---

### 3. N+1 Query Fix
**Status:** 0% - Not started

**MUST DO:**
- [ ] Update `models.py` - Add relationships:
  - `CourseProgress.course = db.relationship('Course')`
  - `CourseNote.course = db.relationship('Course')`
  - `ReadingProgress.ebook = db.relationship('Ebook')`

- [ ] Update `app.py` - `/api/profile` endpoint:
  - Change progress query to use `.options(joinedload(CourseProgress.course))`
  - Change notes query to use `.options(joinedload(CourseNote.course))`
  - Change reading query to use `.options(joinedload(ReadingProgress.ebook))`

- [ ] Test profile loads fast:
  - Load profile page - should load in <100ms
  - Check no N+1 queries occurring

**Expected Outcome:** Profile loads from 300+ queries down to 1-2 queries

---

### 4. Testing Updates
**Status:** Not started

**MUST DO:**
- [ ] Remove CSRF test bypass from `config.py` TestingConfig
- [ ] Add CSRF token tests
- [ ] Add image upload validation tests
- [ ] Add rate limit tests
- [ ] Run all tests - should pass

---

## Quick Reference Files

- **AEGIS_PHASE0_IN_PROGRESS.md** - Detailed Phase 0 status
- **SESSION_SUMMARY_2025-11-14.md** - What was accomplished
- **IMPLEMENTATION_SUMMARY.md** - Overall project features
- **app.py** - Main Flask application (line 106-112: CSRF endpoint)
- **static/js/main.js** - CSRF token handling (lines 13-42)

---

## Testing Endpoints

```bash
# Get CSRF token
curl http://127.0.0.1:5000/csrf-token

# Login with CSRF (need to extract token first)
curl -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: [YOUR_TOKEN_HERE]" \
  -d '{"username":"admin","password":"Admin123"}'
```

---

## Files Ready for Update

✅ app.py - CSRF endpoint added, ready for image/N+1 updates
✅ static/js/main.js - CSRF token handling done
⏳ static/js/profile.js - Needs CSRF updates
⏳ static/js/course_detail.js - Needs CSRF updates
⏳ models.py - Needs relationships added
⏳ config.py - Needs MAX_UPLOAD_SIZE, CSRF test config update

---

## Known Working Features

✅ User authentication (login/register/logout)
✅ User profiles with avatar uploads
✅ Course progress tracking (buttons)
✅ Course notes
✅ Ebook reader (EPUB/PDF)
✅ Rate limiting
✅ Profile dashboard
✅ Course detail pages
✅ CSRF tokens (for login/register/logout)

---

## Server Status

**Running:** ✅ Yes
**URL:** http://127.0.0.1:5000
**Database:** ✅ Active
**Test Account:** admin / Admin123

---

## Estimated Time to Complete Phase 0

- CSRF Completion: 30-45 minutes
- Image Upload Security: 30-45 minutes
- N+1 Query Fix: 20-30 minutes
- Testing & Validation: 30-45 minutes
- Documentation: 15-20 minutes

**Total Phase 0:** ~2.5-3 hours

---

## Phase 1 Preview (After Phase 0 Complete)

1. Session Security (HTTPS cookies)
2. Health Check Endpoint
3. Test Coverage Updates
4. Documentation

---

**Last Updated:** 2025-11-14
**Ready to Continue:** YES ✅
