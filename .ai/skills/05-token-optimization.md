# Skill 05 — Token Optimization

Reduce context size by reading only what the task requires.

Start with [.ai/AI_PROJECT_PROFILE.md](../AI_PROJECT_PROFILE.md). Use it to decide which docs to load.

**Do not read every document on every task.**

---

## Step 1 — Classify the Task

Assign one primary category (and optional secondary):

| Category | Examples |
|----------|----------|
| Documentation | Create or update docs, ADRs, glossary |
| Frontend | Components, pages, layout, styling, RTL |
| Backend | Routes, schemas, services, config, exception handlers |
| Database | Models, migrations, Alembic, queries |
| Infrastructure | Docker, Compose, env files, scripts |
| Architecture | Folder structure, framework, API standards |
| Testing | Unit tests, integration tests, validation |
| Bug Fix | Correcting broken behavior within existing scope |
| Refactor | Restructuring code without behavior change |

---

## Step 2 — Read Minimum Required Docs

Always read:

| Document | Why |
|----------|-----|
| [.ai/AI_PROJECT_PROFILE.md](../AI_PROJECT_PROFILE.md) | Orientation |
| [docs/progress.md](../../docs/progress.md) | Current phase and sprint |

Then add by category:

### Documentation

| Read | Skip unless needed |
|------|-------------------|
| [02-documentation-rules.md](02-documentation-rules.md) | — |
| The specific target doc being updated | Other unrelated docs |
| [docs/AI_GUIDELINES.md](../../docs/AI_GUIDELINES.md) | ARCHITECTURE.md |

### Frontend

| Read | Skip unless needed |
|------|-------------------|
| [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) — frontend sections only | Full backend sections |
| [docs/progress.md](../../docs/progress.md) | DEVELOPMENT_JOURNAL.md |
| Relevant files in `frontend/` | Entire codebase |

### Backend

| Read | Skip unless needed |
|------|-------------------|
| [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) — backend sections only | Full frontend sections |
| [docs/API_CONTRACTS.md](../../docs/API_CONTRACTS.md) | PROJECT_ROADMAP.md |
| Relevant files in `backend/` | Entire codebase |

### Database

| Read | Skip unless needed |
|------|-------------------|
| [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) — database sections | Frontend docs |
| [docs/ADR/003-postgresql.md](../../docs/ADR/003-postgresql.md) | Other ADRs |
| `backend/alembic/` and relevant `backend/app/db/` files | — |

### Infrastructure

| Read | Skip unless needed |
|------|-------------------|
| [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) — Docker sections | API_CONTRACTS.md |
| [docs/ADR/004-docker.md](../../docs/ADR/004-docker.md) | Frontend/backend app code |
| `docker/` files | — |

### Architecture

| Read | Skip unless needed |
|------|-------------------|
| [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) | progress.md details beyond current sprint |
| All relevant [docs/ADR/](../../docs/ADR/) | Application source code |
| [03-architecture-rules.md](03-architecture-rules.md) | — |

### Testing

| Read | Skip unless needed |
|------|-------------------|
| [docs/progress.md](../../docs/progress.md) | PROJECT_ROADMAP.md full history |
| Files under test | Unrelated modules |
| [docs/CONTRIBUTING.md](../../docs/CONTRIBUTING.md) — validation checklist | — |

### Bug Fix

| Read | Skip unless needed |
|------|-------------------|
| [docs/progress.md](../../docs/progress.md) | Full roadmap |
| Files directly involved in the bug | Unrelated modules |
| Relevant architecture section only if bug touches conventions | Full ARCHITECTURE.md |

### Refactor

| Read | Skip unless needed |
|------|-------------------|
| [04-minimal-changes.md](04-minimal-changes.md) | — |
| [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) — conventions only | ADRs unless framework-related |
| Files being refactored | Unrelated modules |

---

## Step 3 — Load Skills by Category

| Always | Category-specific |
|--------|-------------------|
| [01-development-workflow.md](01-development-workflow.md) | [03-architecture-rules.md](03-architecture-rules.md) for code/infra |
| [04-minimal-changes.md](04-minimal-changes.md) for file edits | [02-documentation-rules.md](02-documentation-rules.md) for doc tasks |
| [06-output-format.md](06-output-format.md) | — |

---

## Step 4 — Avoid Context Waste

- Do not paste entire documentation files into responses
- Do not re-read docs already confirmed in the current session unless they may have changed
- Do not explore the full codebase when a targeted file search suffices
- Do not load DEVELOPMENT_JOURNAL.md unless historical context is relevant
- Do not load GLOSSARY.md unless terminology is ambiguous
- Reference doc paths instead of reproducing their content

---

## References

- Pre-implementation checklist: [docs/AI_GUIDELINES.md](../../docs/AI_GUIDELINES.md)
- Profile: [.ai/AI_PROJECT_PROFILE.md](../AI_PROJECT_PROFILE.md)
