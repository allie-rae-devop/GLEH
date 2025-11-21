# PHASE 2 ARCHITECTURE STRATEGY

**Strategist:** solutions-architect
**Date:** 2025-11-14
**Status:** STRATEGIC PLAN - AWAITING APPROVAL
**Prerequisites:** Phase 1 Complete + AHDM Deployment Validated

---

## EXECUTIVE SUMMARY

Phase 2 will enhance GLEH with user management features, production security, and content management capabilities. This document provides strategic guidance on feature prioritization, technology selection, and implementation roadmap.

**Total Estimated Effort:** 22 hours across 5 features
**Timeline:** 3-4 weeks (assuming 1-2 agents, 6-8 hours/week)
**Risk Level:** MEDIUM (requires careful planning for email/2FA integration)

**Strategic Recommendation:**
1. Prioritize email verification and password reset (user retention)
2. Implement HTTPS enforcement early (security mandate)
3. Defer 2FA to later phase (complexity vs urgency)
4. Allocate significant research time for page builder (strategic decision)

---

## PHASE 2 FEATURES OVERVIEW

Based on PHASE2_COMPLETED.md analysis and strategic assessment:

### Confirmed Phase 2 Features

1. **Email Verification** (post-registration confirmation)
2. **Two-Factor Authentication (2FA)** (TOTP or SMS)
3. **Password Reset Flow** (forgot password)
4. **HTTPS Enforcement** (production security)
5. **Page Builder Integration** (visual content editor)

---

## FEATURE PRIORITIZATION MATRIX

| Feature | Effort | Risk | User Impact | Technical Debt | Business Value | Priority | Recommendation |
|---------|--------|------|-------------|----------------|----------------|----------|-----------------|
| Email Verification | MEDIUM | LOW | HIGH | LOW | HIGH | P2.1 | DO FIRST |
| Password Reset | MEDIUM | LOW | HIGH | LOW | HIGH | P2.2 | DO SECOND |
| HTTPS Enforcement | LOW | LOW | CRITICAL | NONE | CRITICAL | P2.3 | DO THIRD |
| 2FA (TOTP) | HIGH | MEDIUM | MEDIUM | MEDIUM | MEDIUM | P2.4 | DEFER |
| Page Builder | VERY HIGH | HIGH | HIGH | UNKNOWN | HIGH | P2.5 | RESEARCH FIRST |

### Priority Rationale

**P2.1 - Email Verification (DO FIRST):**
- Prevents fake account spam
- Enables password reset (prerequisite)
- User retention (verify real users)
- Moderate effort (4 hours)
- Low risk (well-established pattern)

**P2.2 - Password Reset (DO SECOND):**
- Critical user experience feature
- Reduces support burden (locked accounts)
- Depends on email verification
- Moderate effort (3 hours)
- Low risk (standard implementation)

**P2.3 - HTTPS Enforcement (DO THIRD):**
- Security mandate for production
- Protects session cookies (secure flag)
- Prevents MITM attacks
- Low effort (1 hour)
- Zero risk (configuration only)

**P2.4 - 2FA (DEFER):**
- Advanced security feature
- Complex implementation (6 hours)
- Moderate user impact (friction)
- Should follow email verification
- Can be added incrementally

**P2.5 - Page Builder (RESEARCH FIRST):**
- Strategic decision required
- Very high effort (8-20 hours depending on approach)
- High risk (scope creep potential)
- Requires product team input
- Needs technology evaluation phase

---

## DETAILED FEATURE ANALYSIS

### P2.1: EMAIL VERIFICATION

**Objective:** Verify user email addresses post-registration to prevent spam and enable account recovery.

**User Flow:**
1. User registers with email address
2. System sends verification email with unique token
3. User clicks link in email
4. System verifies token and activates account
5. User can now log in

**Technical Design:**

**Database Schema Changes:**
```sql
ALTER TABLE user ADD COLUMN email VARCHAR(255) UNIQUE;
ALTER TABLE user ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE user ADD COLUMN verification_token VARCHAR(255);
ALTER TABLE user ADD COLUMN verification_token_expires DATETIME;
```

**New Endpoints:**
- `POST /api/register` (modified: send verification email)
- `GET /api/verify-email/<token>` (verify email, activate account)
- `POST /api/resend-verification` (resend verification email)

**Email Provider Options:**

| Provider | Pros | Cons | Cost | Recommendation |
|----------|------|------|------|-----------------|
| **SendGrid** | Easy API, 100 free/day | Requires signup | Free tier OK | RECOMMENDED |
| **AWS SES** | Cheap, scalable | AWS account needed | $0.10/1000 emails | IF AWS deployment |
| **Mailgun** | Developer-friendly | 5000 free/month limit | Free tier OK | ALTERNATIVE |
| **Local SMTP** | No external dependency | Complex setup, deliverability issues | Free | NOT RECOMMENDED |

**Recommendation:** SendGrid (free tier: 100 emails/day)

**Implementation Checklist:**
- [ ] Add email field to User model (migration)
- [ ] Generate verification token (UUID4 + expiry)
- [ ] Configure SendGrid API key (environment variable)
- [ ] Create email template (HTML + plain text)
- [ ] Implement `/api/verify-email/<token>` endpoint
- [ ] Add email verification check to login
- [ ] Create resend verification endpoint
- [ ] Add email verification status to user profile
- [ ] Write tests (email sending, token validation, expiry)

**Estimated Effort:** 4 hours
**Risk Level:** LOW
**Dependencies:** Email provider account (SendGrid)

**Security Considerations:**
- Token must be cryptographically secure (secrets.token_urlsafe)
- Token expiry (24 hours recommended)
- Rate limit verification email sends (prevent spam)
- Log email verification events (security audit)

---

### P2.2: PASSWORD RESET FLOW

**Objective:** Allow users to reset forgotten passwords via email link.

**User Flow:**
1. User clicks "Forgot Password" on login page
2. User enters email address
3. System sends password reset email with unique token
4. User clicks link in email
5. User enters new password
6. System validates token and updates password
7. User can now log in with new password

**Technical Design:**

**Database Schema Changes:**
```sql
ALTER TABLE user ADD COLUMN reset_token VARCHAR(255);
ALTER TABLE user ADD COLUMN reset_token_expires DATETIME;
```

**New Endpoints:**
- `POST /api/forgot-password` (send reset email)
- `GET /api/reset-password/<token>` (validate token, show reset form)
- `POST /api/reset-password/<token>` (update password)

**Implementation Checklist:**
- [ ] Add reset token fields to User model (migration)
- [ ] Create `/api/forgot-password` endpoint (send email)
- [ ] Generate reset token (UUID4 + 1 hour expiry)
- [ ] Create password reset email template
- [ ] Create reset password form page
- [ ] Implement `/api/reset-password/<token>` endpoint
- [ ] Validate new password (strength requirements)
- [ ] Invalidate old sessions on password reset
- [ ] Log password reset events (security audit)
- [ ] Write tests (token generation, expiry, password update)

**Estimated Effort:** 3 hours
**Risk Level:** LOW
**Dependencies:** Email verification (P2.1 must be complete)

**Security Considerations:**
- Token must be single-use (invalidate after use)
- Token expiry (1 hour recommended, shorter than verification)
- Rate limit password reset requests (5 per hour per IP)
- Log all password reset attempts (detect attacks)
- Invalidate all user sessions after password change
- Send notification email after successful reset

---

### P2.3: HTTPS ENFORCEMENT

**Objective:** Enforce HTTPS in production to protect session cookies and prevent MITM attacks.

**Technical Design:**

**Configuration Changes:**

**Option A: Reverse Proxy (Nginx) - RECOMMENDED**
```nginx
server {
    listen 80;
    server_name gleh.example.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name gleh.example.com;

    ssl_certificate /etc/letsencrypt/live/gleh.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/gleh.example.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
    }
}
```

**Option B: Flask-Talisman (Application-Level)**
```python
from flask_talisman import Talisman

if app.config['ENV'] == 'production':
    Talisman(app, force_https=True)
```

**Recommendation:** Option A (Nginx reverse proxy) for production deployments

**Session Cookie Configuration:**
```python
# In config.py (already implemented in Phase 1)
SESSION_COOKIE_SECURE = True      # HTTPS only
SESSION_COOKIE_HTTPONLY = True    # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Lax'   # CSRF protection
```

**Implementation Checklist:**
- [ ] Set up reverse proxy (Nginx or Apache)
- [ ] Obtain SSL certificate (Let's Encrypt recommended)
- [ ] Configure HTTPS redirect (HTTP -> HTTPS)
- [ ] Update session cookie settings (secure flag)
- [ ] Test HTTPS deployment (SSL Labs scan)
- [ ] Update documentation (deployment guide)

**Estimated Effort:** 1 hour (configuration only)
**Risk Level:** LOW
**Dependencies:** SSL certificate, reverse proxy setup

**Security Considerations:**
- Use strong SSL/TLS configuration (TLS 1.2+)
- Enable HSTS (HTTP Strict Transport Security)
- Disable weak ciphers
- Regular certificate renewal (Let's Encrypt auto-renewal)

---

### P2.4: TWO-FACTOR AUTHENTICATION (2FA)

**Objective:** Add optional 2FA for enhanced account security.

**User Flow:**
1. User enables 2FA in account settings
2. System generates QR code (TOTP secret)
3. User scans QR code with authenticator app (Google Authenticator, Authy)
4. User enters verification code to confirm setup
5. On future logins: User enters password + 6-digit TOTP code

**Technical Design:**

**Database Schema Changes:**
```sql
ALTER TABLE user ADD COLUMN totp_secret VARCHAR(32);
ALTER TABLE user ADD COLUMN totp_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE user ADD COLUMN backup_codes TEXT;  -- JSON array of backup codes
```

**New Endpoints:**
- `GET /api/2fa/setup` (generate TOTP secret, return QR code)
- `POST /api/2fa/verify-setup` (confirm TOTP setup with code)
- `POST /api/2fa/disable` (disable 2FA, requires password)
- `POST /api/login` (modified: check TOTP code if enabled)
- `POST /api/2fa/backup-codes` (generate new backup codes)

**Technology Stack:**

| Option | Pros | Cons | Recommendation |
|--------|------|------|-----------------|
| **TOTP (pyotp)** | Standard, secure, offline | Requires authenticator app | RECOMMENDED |
| **SMS (Twilio)** | User-friendly | Costs money, SIM swapping risk | NOT RECOMMENDED |
| **WebAuthn (FIDO2)** | Most secure | Complex, hardware needed | FUTURE (Phase 3) |

**Recommendation:** TOTP via pyotp library

**Implementation Checklist:**
- [ ] Add TOTP fields to User model (migration)
- [ ] Install pyotp library (`pip install pyotp`)
- [ ] Create `/api/2fa/setup` endpoint (generate secret, QR code)
- [ ] Generate QR code (qrcode library)
- [ ] Create 2FA setup page (display QR code)
- [ ] Implement TOTP verification in login flow
- [ ] Generate backup codes (10 codes, single-use)
- [ ] Create 2FA disable endpoint (password required)
- [ ] Add "Remember this device" option (30 days)
- [ ] Write tests (TOTP generation, verification, backup codes)

**Estimated Effort:** 6 hours
**Risk Level:** MEDIUM
**Dependencies:** None (can be standalone)

**Security Considerations:**
- TOTP secret must be encrypted at rest
- Backup codes must be hashed (like passwords)
- Rate limit TOTP verification attempts (5 per minute)
- Log 2FA events (enable, disable, failed attempts)
- Allow account recovery via backup codes
- Warn users to save backup codes securely

**User Experience Considerations:**
- Make 2FA optional (not mandatory)
- Provide clear setup instructions
- Offer backup codes for device loss
- "Remember this device" reduces friction
- Support multiple authenticator apps

---

### P2.5: PAGE BUILDER INTEGRATION

**Objective:** Enable visual content editing for course pages without coding.

**Strategic Assessment:**

This is the most complex Phase 2 feature requiring significant research and decision-making.

**Approach Options:**

#### Option A: Headless CMS (e.g., Strapi, Sanity)

**Pros:**
- Rich content management
- User-friendly admin interface
- API-first architecture
- Mature ecosystem

**Cons:**
- External service dependency
- Additional infrastructure
- Learning curve
- Integration complexity

**Effort:** 12-15 hours
**Cost:** Free tier available (Sanity: 100k API requests/month)

#### Option B: Custom Drag-and-Drop Editor (e.g., GrapesJS, Editor.js)

**Pros:**
- Full control over features
- No external dependencies
- Integrated with existing app
- Customizable

**Cons:**
- High development effort
- Maintenance burden
- Security considerations (XSS risks)
- Complex state management

**Effort:** 15-20 hours
**Cost:** Free (open-source libraries)

#### Option C: Markdown + Preview Editor

**Pros:**
- Simple implementation
- Low maintenance
- Developer-friendly
- Fast rendering

**Cons:**
- Limited visual editing
- Not user-friendly for non-technical users
- Requires markdown knowledge

**Effort:** 4-6 hours
**Cost:** Free

#### Option D: Third-Party Embed (e.g., Notion, Google Docs)

**Pros:**
- Zero development effort
- Rich editing features
- Familiar interface

**Cons:**
- No control over functionality
- Vendor lock-in
- Limited customization
- Potential privacy concerns

**Effort:** 2-3 hours (integration only)
**Cost:** Varies by service

**Decision Matrix:**

| Option | Effort | Control | User-Friendly | Maintenance | Recommendation |
|--------|--------|---------|---------------|-------------|-----------------|
| Headless CMS | HIGH | MEDIUM | HIGH | LOW | FOR CONTENT TEAMS |
| Custom Editor | VERY HIGH | HIGH | MEDIUM | HIGH | FOR FULL CONTROL |
| Markdown | LOW | HIGH | LOW | LOW | FOR MVP |
| Third-Party | LOW | LOW | HIGH | NONE | FOR QUICK START |

**Strategic Recommendation:**

**Phase 2A: Research & Prototype (8 hours)**
1. Define requirements with product team
2. Evaluate user needs (technical vs non-technical editors)
3. Build prototypes for top 2 options
4. User testing with stakeholders
5. Make final technology decision

**Phase 2B: Implementation (Depends on choice)**
- Markdown approach: 4-6 hours
- Headless CMS: 12-15 hours
- Custom editor: 15-20 hours

**Questions to Answer Before Implementation:**
1. Who will edit content? (Technical vs non-technical users)
2. What types of content? (Courses, ebooks, landing pages)
3. Is version control needed? (Content history, rollback)
4. Is collaboration needed? (Multiple editors, review workflow)
5. What's the budget? (Self-hosted vs SaaS)
6. What's the timeline? (MVP vs full-featured)

**Recommendation:** Allocate 1 week for research phase before committing to implementation approach.

---

## ARCHITECTURE DECISIONS SUMMARY

### Email Provider: SendGrid
- **Rationale:** Free tier (100 emails/day), easy API, reliable deliverability
- **Alternative:** AWS SES (if AWS deployment), Mailgun
- **Cost:** Free (Phase 2 volume <100/day)

### 2FA Method: TOTP (Time-based One-Time Password)
- **Rationale:** Industry standard, secure, no recurring costs
- **Alternative:** SMS (Twilio) - not recommended due to SIM swapping risk
- **Library:** pyotp + qrcode
- **Cost:** Free

### HTTPS Deployment: Nginx Reverse Proxy
- **Rationale:** Production-grade, SSL termination, static file serving
- **Alternative:** Flask-Talisman (application-level, less flexible)
- **Certificate:** Let's Encrypt (free, auto-renewal)
- **Cost:** Free

### Page Builder: RESEARCH PHASE REQUIRED
- **Rationale:** High complexity, strategic decision, stakeholder input needed
- **Timeline:** 1 week research + prototype phase
- **Decision Criteria:** User needs, technical requirements, budget, timeline

---

## DATABASE SCHEMA CHANGES

### Required Migrations

**P2.1 - Email Verification:**
```sql
ALTER TABLE user ADD COLUMN email VARCHAR(255) UNIQUE;
ALTER TABLE user ADD COLUMN email_verified BOOLEAN DEFAULT FALSE;
ALTER TABLE user ADD COLUMN verification_token VARCHAR(255);
ALTER TABLE user ADD COLUMN verification_token_expires DATETIME;

CREATE INDEX idx_user_email ON user(email);
CREATE INDEX idx_user_verification_token ON user(verification_token);
```

**P2.2 - Password Reset:**
```sql
ALTER TABLE user ADD COLUMN reset_token VARCHAR(255);
ALTER TABLE user ADD COLUMN reset_token_expires DATETIME;

CREATE INDEX idx_user_reset_token ON user(reset_token);
```

**P2.4 - Two-Factor Authentication:**
```sql
ALTER TABLE user ADD COLUMN totp_secret VARCHAR(32);
ALTER TABLE user ADD COLUMN totp_enabled BOOLEAN DEFAULT FALSE;
ALTER TABLE user ADD COLUMN backup_codes TEXT;  -- JSON array

CREATE INDEX idx_user_totp_enabled ON user(totp_enabled);
```

**P2.5 - Page Builder (Content Management):**
```sql
CREATE TABLE page_content (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_identifier VARCHAR(255) UNIQUE NOT NULL,
    content_type VARCHAR(50) NOT NULL,  -- 'markdown', 'html', 'json'
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES user(id),
    version INTEGER DEFAULT 1
);

CREATE TABLE page_content_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    page_content_id INTEGER REFERENCES page_content(id),
    content TEXT NOT NULL,
    version INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    created_by INTEGER REFERENCES user(id)
);

CREATE INDEX idx_page_identifier ON page_content(page_identifier);
CREATE INDEX idx_page_content_history ON page_content_history(page_content_id, version);
```

**Migration Strategy:**
1. Use Flask-Migrate (already in requirements.txt)
2. Generate migrations: `flask db migrate -m "Add email verification"`
3. Review generated migration
4. Apply migration: `flask db upgrade`
5. Test rollback: `flask db downgrade`

---

## SECURITY IMPLICATIONS

### Email Verification (P2.1)
- **Tokens:** Must be cryptographically secure (secrets.token_urlsafe)
- **Expiry:** 24 hours (balance security vs user convenience)
- **Rate Limiting:** Max 5 verification emails per hour per user
- **Logging:** Log all verification attempts (detect abuse)

### Password Reset (P2.2)
- **Tokens:** Single-use, 1-hour expiry
- **Rate Limiting:** Max 5 reset requests per hour per IP
- **Session Invalidation:** Invalidate all sessions on password change
- **Notification:** Send email notification after successful reset
- **Logging:** Log all reset attempts (security audit)

### HTTPS Enforcement (P2.3)
- **TLS Version:** Minimum TLS 1.2
- **Ciphers:** Disable weak ciphers (3DES, RC4)
- **HSTS:** Enable HTTP Strict Transport Security
- **Certificate Validation:** Monitor expiry, auto-renewal

### Two-Factor Authentication (P2.4)
- **Secret Storage:** Encrypt TOTP secrets at rest
- **Backup Codes:** Hash like passwords (bcrypt)
- **Rate Limiting:** Max 5 TOTP attempts per minute
- **Logging:** Log all 2FA events (enable, disable, failures)
- **Recovery:** Backup codes for device loss

### Page Builder (P2.5)
- **XSS Prevention:** Sanitize user-generated HTML (bleach library)
- **CSRF Protection:** Enforce CSRF tokens on content updates
- **Authorization:** Role-based access (admin only for page builder)
- **Audit Trail:** Version history with user attribution
- **Input Validation:** Validate content structure before saving

---

## PHASE 2 TIMELINE & ROADMAP

### Week 1: Email Verification + Password Reset (7 hours)

**Day 1-2: Email Verification (4 hours)**
- [ ] Database migration (email, verification_token)
- [ ] Configure SendGrid API
- [ ] Create email templates (verification, welcome)
- [ ] Implement `/api/verify-email/<token>` endpoint
- [ ] Update registration flow
- [ ] Write tests

**Day 3: Password Reset (3 hours)**
- [ ] Database migration (reset_token)
- [ ] Implement `/api/forgot-password` endpoint
- [ ] Create reset email template
- [ ] Implement `/api/reset-password/<token>` endpoint
- [ ] Create reset password form
- [ ] Write tests

**Deliverables:**
- Email verification functional
- Password reset functional
- Tests passing
- Documentation updated

---

### Week 2: HTTPS + 2FA Research (7 hours)

**Day 1: HTTPS Enforcement (1 hour)**
- [ ] Configure Nginx reverse proxy
- [ ] Obtain Let's Encrypt certificate
- [ ] Set up HTTPS redirect
- [ ] Test SSL configuration (SSL Labs)
- [ ] Update documentation

**Day 2-3: 2FA Implementation (6 hours)**
- [ ] Database migration (totp_secret, backup_codes)
- [ ] Install pyotp + qrcode libraries
- [ ] Implement 2FA setup flow
- [ ] Generate QR codes
- [ ] Update login flow (check TOTP)
- [ ] Generate backup codes
- [ ] Write tests

**Deliverables:**
- HTTPS enforced in production
- 2FA functional (optional for users)
- Tests passing
- Documentation updated

---

### Week 3-4: Page Builder Research & Implementation (8-15 hours)

**Week 3: Research Phase (8 hours)**
- [ ] Requirements gathering (product team meeting)
- [ ] Technology evaluation (Strapi, GrapesJS, Markdown)
- [ ] Build prototypes (2-3 approaches)
- [ ] User testing with stakeholders
- [ ] Document decision rationale
- [ ] Create implementation plan

**Week 4: Implementation Phase (Depends on choice)**
- Markdown approach: 4-6 hours
- Headless CMS integration: 12-15 hours
- Custom editor: 15-20 hours

**Deliverables:**
- Technology decision documented
- Page builder prototype functional
- Content creation workflow validated
- Tests passing
- User guide created

---

## AGENT ASSIGNMENTS

### Recommended Agent Roster for Phase 2

**P2.1-P2.2 (Email Verification + Password Reset):**
- **Agent:** BackendEngineer
- **Skills:** Flask, SQLAlchemy, email integration
- **Duration:** 7 hours

**P2.3 (HTTPS Enforcement):**
- **Agent:** InfrastructureEngineer
- **Skills:** Nginx, SSL/TLS, deployment
- **Duration:** 1 hour

**P2.4 (Two-Factor Authentication):**
- **Agent:** SecurityEngineer
- **Skills:** Authentication, cryptography, TOTP
- **Duration:** 6 hours

**P2.5 (Page Builder Research):**
- **Agent:** solutions-architect + ProductEngineer
- **Skills:** Architecture, UX design, technology evaluation
- **Duration:** 8 hours (research phase)

**P2.5 (Page Builder Implementation):**
- **Agent:** FullStackEngineer
- **Skills:** Frontend (JS), backend (Flask), CMS integration
- **Duration:** 4-20 hours (depends on approach)

**Testing (All Features):**
- **Agent:** TestEngineer
- **Skills:** Pytest, integration testing, security testing
- **Duration:** 6 hours

**Security Review:**
- **Agent:** AEGIS
- **Skills:** Security audit, penetration testing
- **Duration:** 2 hours

---

## RISK ASSESSMENT

### P2.1 - Email Verification (LOW RISK)
- **Technical Risk:** LOW (well-established pattern)
- **Integration Risk:** LOW (SendGrid API is stable)
- **User Impact:** MEDIUM (users must verify email)
- **Mitigation:** Clear instructions, resend functionality, support documentation

### P2.2 - Password Reset (LOW RISK)
- **Technical Risk:** LOW (standard implementation)
- **Security Risk:** MEDIUM (token management critical)
- **User Impact:** HIGH (locked accounts are frustrating)
- **Mitigation:** Thorough testing, clear error messages, short token expiry

### P2.3 - HTTPS Enforcement (LOW RISK)
- **Technical Risk:** LOW (configuration only)
- **Deployment Risk:** LOW (Let's Encrypt is reliable)
- **User Impact:** NONE (transparent to users)
- **Mitigation:** Test SSL configuration, monitor certificate expiry

### P2.4 - Two-Factor Authentication (MEDIUM RISK)
- **Technical Risk:** MEDIUM (TOTP library integration)
- **User Experience Risk:** MEDIUM (friction in login flow)
- **Security Risk:** LOW (TOTP is battle-tested)
- **Mitigation:** Make 2FA optional, provide backup codes, clear setup guide

### P2.5 - Page Builder (HIGH RISK)
- **Scope Risk:** HIGH (feature complexity unknown)
- **Technology Risk:** MEDIUM (depends on choice)
- **Timeline Risk:** HIGH (could take 2-4 weeks)
- **Security Risk:** MEDIUM (XSS, CSRF concerns)
- **Mitigation:** Research phase first, prototype before committing, phased rollout

---

## SUCCESS CRITERIA

### P2.1 - Email Verification
- [ ] Users receive verification email within 1 minute of registration
- [ ] Verification link works and activates account
- [ ] Expired tokens (>24 hours) are rejected
- [ ] Users can resend verification email
- [ ] Verified users can log in, unverified users cannot
- [ ] Email sending is logged for audit

### P2.2 - Password Reset
- [ ] Users receive reset email within 1 minute of request
- [ ] Reset link works and allows password change
- [ ] Expired tokens (>1 hour) are rejected
- [ ] Old sessions are invalidated after password change
- [ ] Users receive notification email after successful reset
- [ ] Reset attempts are logged for audit

### P2.3 - HTTPS Enforcement
- [ ] All HTTP requests redirect to HTTPS
- [ ] SSL certificate is valid (A+ rating on SSL Labs)
- [ ] Session cookies have secure flag set
- [ ] HSTS header is present
- [ ] Certificate auto-renewal is configured

### P2.4 - Two-Factor Authentication
- [ ] Users can enable 2FA with QR code
- [ ] TOTP codes are validated correctly
- [ ] Backup codes work for account recovery
- [ ] Users can disable 2FA with password confirmation
- [ ] 2FA status is visible in user profile
- [ ] "Remember this device" option works (30 days)

### P2.5 - Page Builder
- [ ] Authorized users can create/edit page content
- [ ] Content is rendered correctly on frontend
- [ ] Version history is maintained
- [ ] XSS protection is in place (content sanitized)
- [ ] CSRF tokens are enforced
- [ ] User guide is available

---

## TECHNOLOGY STACK ADDITIONS

### New Dependencies (requirements.txt)

**P2.1 - Email Verification:**
```
sendgrid>=6.11.0  # Email sending
```

**P2.4 - Two-Factor Authentication:**
```
pyotp>=2.9.0      # TOTP generation/verification
qrcode>=7.4.2     # QR code generation
Pillow>=10.0.0    # Already installed (QR code image generation)
```

**P2.5 - Page Builder (Depends on approach):**
```
# Option A: Headless CMS
# No Python dependencies (external service)

# Option B: Custom Editor
bleach>=6.1.0     # HTML sanitization (XSS prevention)

# Option C: Markdown
markdown>=3.5.0   # Markdown to HTML conversion
```

---

## DEPLOYMENT CONSIDERATIONS

### Environment Variables (Update .env.example)

**P2.1 - Email Verification:**
```env
SENDGRID_API_KEY=your_sendgrid_api_key_here
EMAIL_FROM_ADDRESS=noreply@gleh.example.com
EMAIL_FROM_NAME=Gammons Landing Educational Hub
```

**P2.3 - HTTPS Enforcement:**
```env
FLASK_ENV=production  # Enables secure session cookies
```

**P2.5 - Page Builder (If using headless CMS):**
```env
CMS_API_URL=https://your-cms-instance.com/api
CMS_API_TOKEN=your_cms_api_token_here
```

### Infrastructure Requirements

**P2.1 - Email Verification:**
- SendGrid account (free tier: 100 emails/day)
- DNS configuration (SPF, DKIM for deliverability)

**P2.3 - HTTPS Enforcement:**
- Reverse proxy (Nginx or Apache)
- SSL certificate (Let's Encrypt recommended)
- Domain name with DNS configured

**P2.4 - Two-Factor Authentication:**
- No additional infrastructure required

**P2.5 - Page Builder (If using headless CMS):**
- CMS hosting (Sanity/Strapi/Contentful)
- API access configuration
- Additional database for CMS (if self-hosted)

---

## PHASE 2 COST ANALYSIS

| Component | Service | Cost | Notes |
|-----------|---------|------|-------|
| Email Sending | SendGrid | Free (100/day) | Upgrade to $19.95/mo for 40k/mo |
| SSL Certificate | Let's Encrypt | Free | Auto-renewal recommended |
| 2FA | pyotp (self-hosted) | Free | No recurring costs |
| Page Builder (Headless CMS) | Sanity | Free (100k API requests/mo) | Upgrade to $99/mo for 500k requests |
| Page Builder (Custom) | Self-hosted | Free | Development time cost |
| **Total Monthly Cost** | | **$0-$120/mo** | Depends on page builder choice |

**Budget Recommendation:**
- Phase 2A (Email + Password Reset + HTTPS + 2FA): $0/month (free tier sufficient)
- Phase 2B (Page Builder): $0-$120/month depending on approach

---

## DOCUMENTATION UPDATES REQUIRED

### User Documentation
- [ ] Email verification guide (how to verify account)
- [ ] Password reset guide (how to reset forgotten password)
- [ ] 2FA setup guide (how to enable, use authenticator app)
- [ ] Page builder user guide (how to create/edit content)

### Developer Documentation
- [ ] Email integration architecture
- [ ] TOTP implementation details
- [ ] Page builder API documentation
- [ ] Database migration guide

### Operations Documentation
- [ ] HTTPS deployment checklist
- [ ] SSL certificate renewal process
- [ ] Email deliverability troubleshooting
- [ ] 2FA recovery procedures

---

## OPEN QUESTIONS FOR STAKEHOLDERS

### Product Team Questions
1. **Email Verification:** Should unverified users have limited access or no access?
2. **2FA:** Should 2FA be optional or mandatory for admin accounts?
3. **Page Builder:** Who is the primary audience? (Technical editors vs marketing team)
4. **Page Builder:** What types of content need editing? (Courses, landing pages, blog posts)
5. **Page Builder:** Is version control/history required?

### Infrastructure Team Questions
1. **Email:** What email volume is expected? (impacts SendGrid tier)
2. **HTTPS:** What domain name will be used in production?
3. **Page Builder:** Self-hosted CMS or SaaS?
4. **Budget:** What is the monthly budget for external services?

### Security Team Questions
1. **2FA:** Should 2FA be enforced for admin accounts?
2. **Password Reset:** What is acceptable token expiry time?
3. **Page Builder:** What level of HTML sanitization is required?
4. **Compliance:** Are there GDPR/privacy requirements for email storage?

---

## FINAL RECOMMENDATIONS TO CLAUDE CODE

### Immediate Actions (This Session)
1. **Approve P5 (Structured Logging):** Ready for TestEngineer handoff
2. **Approve Phase 2 Strategy:** Use this document as Phase 2 roadmap
3. **Schedule Phase 2 Kickoff:** After AHDM deployment validates Phase 1

### Phase 2 Execution Order
1. **P2.1:** Email Verification (4 hours) - BackendEngineer
2. **P2.2:** Password Reset (3 hours) - BackendEngineer
3. **P2.3:** HTTPS Enforcement (1 hour) - InfrastructureEngineer
4. **P2.4:** 2FA Implementation (6 hours) - SecurityEngineer
5. **P2.5 Research:** Page Builder Evaluation (8 hours) - solutions-architect + ProductEngineer
6. **P2.5 Implementation:** Page Builder Build (4-20 hours) - FullStackEngineer

### Risk Mitigation
- Start with low-risk features (email verification, HTTPS)
- Allocate research time for page builder (don't commit prematurely)
- Involve product team early for requirements validation
- Budget extra time for testing and documentation

### Success Metrics
- Phase 2A (P2.1-P2.4): Complete in 2-3 weeks
- Phase 2B (P2.5): Complete in 2-4 weeks after research phase
- Zero security vulnerabilities introduced
- User satisfaction with new features
- Email deliverability >95%
- 2FA adoption rate >20% (voluntary)

---

## SIGN-OFF

**Strategist:** solutions-architect
**Date:** 2025-11-14
**Status:** STRATEGIC PLAN COMPLETE

**Recommendations:**
1. APPROVE Phase 2 roadmap
2. PROCEED with P2.1-P2.3 immediately (low risk, high value)
3. DEFER P2.4 (2FA) until P2.1-P2.3 complete
4. ALLOCATE 1 week for P2.5 research before implementation

**Next Steps:**
1. Await Claude Code approval
2. Spawn BackendEngineer for P2.1-P2.2
3. Spawn InfrastructureEngineer for P2.3
4. Begin P2.5 research phase with product team

---

**END OF PHASE 2 ARCHITECTURE STRATEGY**
