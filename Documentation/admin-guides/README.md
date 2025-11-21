# GLEH Documentation Hub

Welcome to the central documentation system for **Gammons Landing Educational Hub (GLEH)**.

This directory contains all project documentation organized for easy navigation and agent autonomy.

---

## Start Here

**New to the project?** Read these in order:

1. **[living-memory.md](./living-memory.md)** - Central project context, current status, and quick navigation
2. **[Phase Status Dashboard](./phases/)** - What's completed, in progress, and pending
3. **[Agent Assignments](./operations/IMPLEMENTATION_LOGS.md)** - Who's doing what and current progress

---

## Documentation by Topic

### Architecture & Structure
- **[Stack Design & Tech Choices](./architecture/)** - Flask, SQLAlchemy, security frameworks
- **[Code Structure Audit](./architecture/STRUCTURE_AUDIT.md)** - Current state analysis and recommendations
- **[Multi-Agent Team Structure](./architecture/MULTI_AGENT_TEAM_STRUCTURE.md)** - Agent roles and coordination

### Security
- **[AEGIS Executive Summary](./security/AEGIS_EXEC_SUMMARY.md)** - High-level security status
- **[Security Audits](./security/)** - Phase 0 and Phase 1 security reviews
- **[Session Security](./security/SESSION_SECURITY.md)** - Session management implementation
- **[Security Checklist](./security/SECURITY_CHECKLIST.md)** - Pre-deployment validation (to be created)

### Operations & Deployment
- **[Deployment Checklist](./operations/DEPLOYMENT_CHECKLIST.md)** - Step-by-step deployment guide
- **[Implementation Logs](./operations/IMPLEMENTATION_LOGS.md)** - Agent work summaries and progress
- **[Error Recovery](./operations/ERROR_RECOVERY.md)** - Issue tracking and resolution (created as needed)

### Development & Phases
- **[Phase 0: Complete](./phases/PHASE0_COMPLETE.md)** - CSRF, image security, N+1 fixes
- **[Phase 1: Quick Reference](./phases/PHASE1_QUICK_REFERENCE.md)** - Requirements, sessions, health checks
- **[Phase 2: Completed](./phases/PHASE2_COMPLETED.md)** - Hardened config, input validation, rate limiting
- **[Phase 3: In Progress](./phases/PHASE3_IN_PROGRESS.md)** - Test suites and logging (to be created)

### Session History
- **[Session 2025-11-14](./sessions/SESSION_2025-11-14.md)** - Today's session summary
- **[Resumption Checkpoints](./sessions/RESUMPTION_CHECKPOINTS.md)** - Session handoff points

---

## For Agents

### Quick Start Protocol
1. **READ** [living-memory.md](./living-memory.md) first to get current context
2. **CHECK** your assignment in the "Current Agent Assignments" table
3. **VERIFY** dependencies in the "Critical Dependencies" section
4. **START** your work based on agent-specific entry points
5. **UPDATE** your status when starting work
6. **SUBMIT** completion summary to [IMPLEMENTATION_LOGS.md](./operations/IMPLEMENTATION_LOGS.md)

### Agent-Specific Entry Points

| Agent | Primary Entry Point | Secondary References |
|-------|-------------------|---------------------|
| **AEGIS** | [AEGIS_EXEC_SUMMARY.md](./security/AEGIS_EXEC_SUMMARY.md) | [living-memory.md](./living-memory.md) |
| **TestEngineer** | [PHASE1_QUICK_REFERENCE.md](./phases/PHASE1_QUICK_REFERENCE.md) | [living-memory.md](./living-memory.md) |
| **InfrastructureEngineer** | [STRUCTURE_AUDIT.md](./architecture/STRUCTURE_AUDIT.md) | [living-memory.md](./living-memory.md) |
| **AHDM** | [DEPLOYMENT_CHECKLIST.md](./operations/DEPLOYMENT_CHECKLIST.md) | [living-memory.md](./living-memory.md) |
| **DocumentationCoordinator** | [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) | [living-memory.md](./living-memory.md) |
| **solutions-architect** | [living-memory.md](./living-memory.md) | All architecture docs |

### Communication Standards

**Status Updates:**
- Update "Current Agent Assignments" table in living-memory.md
- Mark status as: PENDING → IN_PROGRESS → COMPLETE

**Completion Reports:**
- Append to [IMPLEMENTATION_LOGS.md](./operations/IMPLEMENTATION_LOGS.md)
- Use the provided template
- Include: what was done, decisions, issues, next steps, time/tokens

**Issues/Blockers:**
- Create entry in ERROR_RECOVERY.md if needed
- Update living-memory.md "Blockers" section
- Notify Claude Code if blocking other agents

**Key Decisions:**
- Add to living-memory.md "Key Decisions Log"
- Include: date, decision, rationale, impact, owner, status

---

## Directory Structure

```
docs/
├── living-memory.md              # Central context hub (START HERE)
├── README.md                     # This file - navigation guide
├── DOCUMENTATION_INDEX.md        # Searchable file index
│
├── phases/                       # Phase documentation
│   ├── PHASE0_COMPLETE.md
│   ├── PHASE1_QUICK_REFERENCE.md
│   ├── PHASE2_COMPLETED.md
│   ├── PHASE3_IN_PROGRESS.md    # To be created
│   └── future-phases.md          # Phase 2+ planning (to be created)
│
├── sessions/                     # Session logs
│   ├── SESSION_2025-11-14.md
│   └── RESUMPTION_CHECKPOINTS.md
│
├── architecture/                 # Architecture docs
│   ├── MULTI_AGENT_TEAM_STRUCTURE.md
│   ├── STRUCTURE_AUDIT.md
│   └── stack-design.md           # To be created
│
├── operations/                   # Operational docs
│   ├── DEPLOYMENT_CHECKLIST.md
│   ├── IMPLEMENTATION_LOGS.md   # Agent work summaries
│   └── ERROR_RECOVERY.md         # Created as needed
│
└── security/                     # Security docs
    ├── AEGIS_EXEC_SUMMARY.md
    ├── AEGIS_PHASE0_CODE_REVIEW.md
    ├── AEGIS_PHASE1_STRATEGIC_AUDIT.md
    ├── SESSION_SECURITY.md
    └── SECURITY_CHECKLIST.md     # To be created
```

---

## Documentation Principles

### 1. Searchability
- Use clear, descriptive filenames
- Include keyword-rich headers
- Cross-reference related docs with relative links

### 2. Maintainability
- Keep living-memory.md as the single source of truth
- Update timestamps and "Last Updated By" fields
- Archive outdated docs to sessions/ directory

### 3. Autonomy
- Each agent should find what they need without human intervention
- Entry points are clearly marked
- Dependencies and blockers are explicit

### 4. Discoverability
- Related docs are linked in context
- DOCUMENTATION_INDEX.md provides searchable catalog
- README.md (this file) provides navigation paths

---

## Quick Reference Commands

### Find a file
Check [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md)

### Understand current status
Read [living-memory.md](./living-memory.md) sections:
- Phase Status Dashboard
- Current Agent Assignments

### See what's been done
Check [IMPLEMENTATION_LOGS.md](./operations/IMPLEMENTATION_LOGS.md)

### Check security status
Start at [AEGIS_EXEC_SUMMARY.md](./security/AEGIS_EXEC_SUMMARY.md)

### Deploy to production
Follow [DEPLOYMENT_CHECKLIST.md](./operations/DEPLOYMENT_CHECKLIST.md)

---

## Maintenance Schedule

**Daily:**
- Update living-memory.md after each agent completion
- Append to IMPLEMENTATION_LOGS.md after each task

**Per Phase:**
- Create new PHASE*_IN_PROGRESS.md when phase starts
- Archive to PHASE*_COMPLETE.md when phase finishes

**Per Session:**
- Create SESSION_YYYY-MM-DD.md at session start
- Update RESUMPTION_CHECKPOINTS.md at session end

---

## Questions?

- **For project context:** Read [living-memory.md](./living-memory.md)
- **For agent coordination:** Check [MULTI_AGENT_TEAM_STRUCTURE.md](./architecture/MULTI_AGENT_TEAM_STRUCTURE.md)
- **For deployment:** Follow [DEPLOYMENT_CHECKLIST.md](./operations/DEPLOYMENT_CHECKLIST.md)
- **For security:** Review [AEGIS_EXEC_SUMMARY.md](./security/AEGIS_EXEC_SUMMARY.md)

---

**Last Updated:** 2025-11-14 08:23 UTC
**Maintained By:** DocumentationCoordinator
**Version:** 1.0
