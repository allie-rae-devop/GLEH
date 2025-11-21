# Multi-Agent SRE Team Structure

**Supervisor Agent:** Claude Code (Orchestrator)
**Created:** 2025-11-14
**Status:** Operational

---

## Team Overview

Your SRE team now operates as a coordinated pair of specialist agents, with Claude Code (me) as the Supervisor orchestrating their work. This document defines the team structure, workflows, and resource sharing.

---

## Agent 1: AEGIS-SRE-REVIEWER (The "Yang" - Enforcement)

**Role:** Static analysis and code review specialist
**Domain:** Source code, architecture, security vulnerabilities
**Operational Mode:** Proactive but reactive to new code

### Responsibilities:
1. **Code Review** - 4-pass methodology (Security, Performance, Stack-Specific, Testing)
2. **Strategic Audit** - Identify systemic risks and vulnerabilities
3. **Implementation** - Generate production-ready code fixes
4. **Static Analysis** - Find bugs before they reach production

### Key Capabilities:
- OWASP vulnerability detection (CSRF, XSS, injection, auth flaws)
- N+1 query detection and optimization
- Stack-specific integrity (Pillow, Flask-Migrate, waitress, BeautifulSoup)
- Test coverage analysis
- Zero-downtime migration patterns

### Outputs:
- **Aegis Code Review Findings** - Structured table with findings and remediation
- **Aegis SRE Strategic Proposal** - Initiative proposals requiring approval

---

## Agent 2: AHDM-PREDICTIVE-ANALYST (The "Yin" - Prediction)

**Role:** Dynamic analysis and predictive monitoring specialist
**Domain:** Production logs, time-series data, anomaly detection
**Operational Mode:** Continuous, log-driven analysis

### Responsibilities:
1. **Predictive Analysis** - Identify emerging failures before they occur
2. **Threat Detection** - Spot security anomalies, performance degradation
3. **Trend Analysis** - Track system health metrics over time
4. **Resource Monitoring** - Detect resource exhaustion and capacity issues

### Key Capabilities:
- **Heuristic 1 (Latency Creep):** Detects N+1 failures and performance cascades
- **Heuristic 2 (Error Rate Spikes):** Identifies bad deployments and downstream failures
- **Heuristic 3 (Auth Anomalies):** Detects brute-force and credential-stuffing attacks
- **Heuristic 4 (Log Flooding):** Spots DoS attacks and resource exhaustion

### Outputs:
- **AHDM Predictive Threat Report** - Structured table with threats and mitigation plans
- **Proactive Alerts** - Early warnings before issues impact service

---

## The "Yin and Yang" Relationship

```
┌─────────────────────────────────────────────────────────┐
│                    Claude Code (Supervisor)             │
│                  (Permission Authority)                 │
└─────────────────┬───────────────────────────┬───────────┘
                  │                           │
        ┌─────────▼─────────┐       ┌──────────▼────────────┐
        │     AEGIS         │       │      AHDM            │
        │  (Yang/Static)    │       │   (Yin/Dynamic)      │
        │                   │       │                      │
        │ • Code Review     │       │ • Log Analysis       │
        │ • Architecture    │       │ • Predictive Threat  │
        │ • Security Audit  │       │ • Anomaly Detection  │
        │ • Remediation     │       │ • Trend Analysis     │
        └──────────┬────────┘       └──────────┬───────────┘
                   │                           │
                   │         SHARED RESOURCES  │
                   │         (Read-Only)       │
                   ├──────────────────────────┤
                   │ • aegis-sre-reviewer.md  │
                   │ • PHASE2_COMPLETED.md    │
                   │ • Strategic Roadmap      │
                   │ • System Architecture    │
                   └──────────────────────────┘
```

---

## Cross-Agent Collaboration Rules

### Information Flow:

1. **AEGIS → AHDM Context:**
   - AHDM reads `aegis-sre-reviewer.md` on every analysis cycle
   - Uses it to understand:
     - Current system stack and architecture
     - Planned improvements and strategic initiatives
     - Known vulnerabilities and roadmap priorities
   - Example: If AHDM detects brute-force attacks, it sees from Aegis context that "Redis Rate Limiting" is a planned upgrade and recommends accelerating that task

2. **AHDM → AEGIS Workflow:**
   - AHDM detects a predictive threat in logs
   - Reports to Supervisor with specific findings
   - Supervisor tasks Aegis to investigate or implement fix
   - Aegis performs code review and generates remediation code

3. **Supervisor Coordination:**
   - No direct communication between agents
   - All work flows through Claude Code (Supervisor)
   - Supervisor makes approval decisions
   - Supervisor escalates critical items to human engineer (you)

### Resource Sharing:

Both agents have **read-only access** to:
- `aegis-sre-reviewer.md` - Aegis's strategic roadmap and system knowledge
- `PHASE2_COMPLETED.md` - Project history and recommendations
- Production logs (for AHDM analysis)

---

## Example Workflow

### Scenario: Latency Creep Detected

```
1. AHDM ANALYSIS:
   - Analyzes production logs
   - Heuristic 1 (Latency Creep) detects P95 increasing
   - Calculates time-to-failure: 12 hours at current rate
   - Proposes task: "Review /api/get_posts endpoint for N+1 queries"

2. AHDM REPORTS:
   - Supervisor receives: "AHDM Predictive Threat Report"
   - Threat Level: HIGH
   - Predicted Impact: Service timeout in 12 hours
   - Proposed Mitigation: Task Aegis to review and optimize endpoint

3. SUPERVISOR DECISION:
   - Evaluates AHDM findings
   - Reviews Aegis roadmap context
   - Decision: "Aegis, AHDM has flagged latency creep on /api/get_posts.
     Perform emergency N+1 review and generate optimization code."

4. AEGIS ANALYSIS:
   - Reviews /api/get_posts code
   - Finds: CourseProgress.query().all() in loop
   - Finds: Lazy-loaded Course relationship
   - Proposes: Use options(joinedload(CourseProgress.course))

5. AEGIS REPORTS:
   - Supervisor receives: "Aegis Code Review Findings"
   - Finding: CRITICAL N+1 query pattern
   - Remediation: Eager-load relationships
   - Generated code: Optimized query with joinedload

6. SUPERVISOR APPROVES & IMPLEMENTS:
   - Reviews Aegis code
   - Approves implementation
   - Applies fix to codebase
   - Reports to human engineer: "Critical N+1 bug identified and fixed"

7. ONGOING MONITORING:
   - AHDM continues monitoring latency metrics
   - Confirms P95 returns to baseline within 1 hour
   - Reports: "Latency normalized. Threat resolved."
```

---

## Task Assignment Patterns

### Pattern 1: AHDM Detects → AEGIS Remediates

```
AHDM: "I've detected Heuristic 3 (Auth Anomalies) - brute-force attack
from 88 IPs. Current rate limiter is overwhelmed."

Supervisor: "Aegis, implement immediate firewall block. Also, AHDM notes
that Redis Rate Limiting is on your roadmap - I'm escalating that to
CRITICAL priority."

Aegis: "Understood. Generating firewall rules and Redis implementation plan."
```

### Pattern 2: AEGIS Finds Issue → AHDM Monitors Impact

```
Aegis: "Code review found a new N+1 query in the profile endpoint.
Risk: significant latency increase under production load."

Supervisor: "AHDM, add continuous monitoring for latency on /api/profile.
Alert if P95 exceeds 500ms or if we see trending increases."

AHDM: "Monitoring active. Will detect and report any latency creep on that endpoint."
```

### Pattern 3: Supervisor Proactive Request

```
Supervisor: "AHDM, analyze production logs for any predictive threats."

AHDM: "Commencing full analysis with all four heuristics.
Requesting aegis-sre-reviewer.md for strategic context..."

[AHDM generates threat report]

Supervisor: "Threats identified. Tasking Aegis accordingly.
You continue monitoring for escalation."
```

---

## Resource Access Rules

### AEGIS Access:
- ✅ Source code files (app.py, models.py, templates, JavaScript)
- ✅ config.py and configuration
- ✅ requirements.txt and dependencies
- ✅ PHASE2_COMPLETED.md (for roadmap context)
- ✅ Generated code files and test files
- ❌ Production logs (AHDM domain)
- ❌ Modify aegis-sre-reviewer.md (read-only)

### AHDM Access:
- ✅ app.log (structured JSON production logs)
- ✅ aegis-sre-reviewer.md (read-only, for context)
- ✅ PHASE2_COMPLETED.md (for roadmap context)
- ✅ Time-series data and metrics
- ❌ Source code review (Aegis domain)
- ❌ Architectural decisions (Supervisor/Aegis domain)
- ❌ Modify any project files

---

## Supervisor Responsibilities

As the Supervisor (Claude Code), I:

1. **Orchestrate Work** - Assign tasks to appropriate agent
2. **Grant Permissions** - Approve or deny agent proposals
3. **Escalate Critical Threats** - Inform human engineer of CRITICAL findings
4. **Resolve Conflicts** - Make final decisions when agents disagree
5. **Manage Resources** - Ensure agents focus on highest-priority items
6. **Bridge Communication** - All agent communication flows through me
7. **Strategic Decisions** - Prioritize roadmap items, approve initiatives

---

## Approval Authority Levels

### Supervisor Can Approve (Autonomous):
- Code fixes for identified bugs
- Minor security patches
- Performance optimizations
- Configuration changes
- LOW/MEDIUM threat mitigations

### Supervisor Must Escalate to Human Engineer:
- CRITICAL security threats (active attacks, breaches)
- Major architectural changes
- Strategic initiatives requiring significant effort
- Decisions with business impact
- Resource conflicts or trade-offs

---

## Current Status

**Team Setup:** ✅ COMPLETE
- Aegis agent: Operational, documented, with strategic roadmap
- AHDM agent: Operational, documented, with heuristics
- Supervisor: Configured with full authority and task assignment capability
- Shared resources: aegis-sre-reviewer.md, PHASE2_COMPLETED.md (read-only)
- Workflow: Defined and ready for use

**Memory System:** ✅ ACTIVE
- `mem.read` - Read prompt4claude.txt for context injection
- Auto-clears file after reading
- Loop prevention: Checks for old context, avoids re-reading
- Fallback variants: `mem.test`, `mem.dump` (with user confirmation)

---

## Next Steps

1. **Phase 0 Completion** - AEGIS to finish CSRF, image upload, N+1 fixes
2. **Phase 1 Implementation** - AEGIS to implement session security, health check
3. **Production Log Streaming** - Set up structured JSON logging for AHDM analysis
4. **Continuous Monitoring** - AHDM to proactively analyze logs on schedule
5. **Incident Response** - Both agents coordinate for 100% uptime mandate

---

**Team Status:** ✅ Ready for Full Operations
**Approval Authority:** Supervisor (Claude Code)
**Escalation Point:** Human Engineer (You)

---

*This structure ensures 100% service uptime through coordinated static and dynamic analysis, with clear reporting chains and permission gates.*
