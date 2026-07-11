# Khazina — AI Project Profile

One-page orientation for AI assistants. Read this first, then load only the documentation required for the current task.

Documentation in `docs/` is the single source of truth. This file does not replace it.

---

## Current Development Mode

**Current Mode:** Hackathon MVP

**Current Goal:** Deliver a stable MVP within four days while preserving production-quality architecture.

Execution plan: [docs/HACKATHON_PLAN.md](../docs/HACKATHON_PLAN.md)

---

## Quick Task Routing

Use this table to load only the skills and documentation required for the task. Minimize token usage — do not read every document every time.

| Task | Required Skills | Required Documentation |
|------|-----------------|------------------------|
| Documentation | Skill 02 | Relevant docs |
| Frontend | Skill 01 + Skill 04 | [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) + [docs/PROJECT_ROADMAP.md](../docs/PROJECT_ROADMAP.md) |
| Backend | Skill 01 + Skill 04 | [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) + relevant [docs/ADR/](../docs/ADR/) |
| Database | Skill 03 | [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) + relevant [docs/ADR/](../docs/ADR/) |
| Infrastructure | Skill 03 | [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) + relevant [docs/ADR/](../docs/ADR/) |
| AI | Skill 01 + Skill 05 | [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) + [docs/AI_GUIDELINES.md](../docs/AI_GUIDELINES.md) |
| Bug Fix | Skill 04 | Relevant documentation |
| Refactor | Skill 04 | Relevant documentation |
| Architecture | Skill 03 | [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) + relevant [docs/ADR/](../docs/ADR/) |
| Testing | Skill 01 | Relevant documentation |

Always load Skill 05 (token optimization) and Skill 06 (output format) when unsure which docs to read.

Prompt templates: [.ai/prompts/](prompts/)

---

## Project Name

**Khazina** — Enterprise Financial Decision Intelligence Platform

## Project Vision

A scalable platform for financial decision support: structured backend services, a modern web interface, and AI-assisted analysis. Full vision and goals: [docs/PROJECT_ROADMAP.md](../docs/PROJECT_ROADMAP.md)

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, App Router, RTL |
| Backend | FastAPI, Pydantic, SQLAlchemy, Alembic |
| Database | PostgreSQL 16 |
| AI (future) | Ollama (Compose service; no business logic until Phase 5) |
| Containers | Docker, Docker Compose |

Details: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) · ADRs: [docs/ADR/](../docs/ADR/)

## Current Phase

**Phase 2 — Frontend Foundation** (Phase 1 completed)

Authoritative status: [docs/progress.md](../docs/progress.md)

## Current Sprint

**Sprint 2.1** — check [docs/progress.md](../docs/progress.md) for objective and scope before implementing.

## Repository Philosophy

Monorepo. Application code lives only in designated directories (`frontend/`, `backend/`, `ai/`, `database/`, `docker/`, `docs/`, `scripts/`). No application code in the repository root.

## Development Philosophy

**Foundation first, features second.** One logical sprint at a time. Stop after delivery and wait for Tech Lead review. One logical commit per sprint.

Methodology: [docs/PROJECT_ROADMAP.md](../docs/PROJECT_ROADMAP.md) · Workflow: [docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md)

## Current Architecture Summary

```
Browser → Next.js → REST API (/api/v1) → FastAPI → SQLAlchemy → PostgreSQL → Ollama
```

- All API responses use the `ApiResponse` envelope
- API versioned under `/api/v1/`
- Layered backend: `api/` → `schemas/`, `core/`, `db/`
- Phase-gated: no DB models (Phase 3), no auth (Phase 4), no AI business logic (Phase 5)

Full architecture: [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md)

## Documentation Structure

| Document | Owns |
|----------|------|
| [docs/progress.md](../docs/progress.md) | Current phase, sprint status, validation, commits |
| [docs/PROJECT_ROADMAP.md](../docs/PROJECT_ROADMAP.md) | Phases, sprint rules, Definition of Done |
| [docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) | System architecture, stack, conventions |
| [docs/AI_GUIDELINES.md](../docs/AI_GUIDELINES.md) | AI behavior, pre-implementation checklist |
| [docs/CONTRIBUTING.md](../docs/CONTRIBUTING.md) | Developer workflow, branches, PRs |
| [docs/API_CONTRACTS.md](../docs/API_CONTRACTS.md) | API standards, response format, naming |
| [docs/GLOSSARY.md](../docs/GLOSSARY.md) | Project terminology |
| [docs/DEVELOPMENT_JOURNAL.md](../docs/DEVELOPMENT_JOURNAL.md) | Historical decisions, lessons learned |
| [docs/ADR/](../docs/ADR/) | Architecture Decision Records |

## Important Project Rules

1. Implement only current sprint scope — never ahead of phase gates
2. Never change architecture, folder structure, or API standards without Tech Lead approval
3. Never add dependencies without Tech Lead approval
4. Prefer minimal diffs; never regenerate entire files unless requested
5. All text files: UTF-8 without BOM
6. Do not commit unless explicitly requested
7. Update only the document that owns the information being changed
8. Skills in `.ai/skills/` define AI behavior; `docs/` defines project knowledge

## Skills Library

Load skills from `.ai/skills/` based on task type:

| Skill | When to Load |
|-------|--------------|
| [01-development-workflow.md](skills/01-development-workflow.md) | Every task |
| [02-documentation-rules.md](skills/02-documentation-rules.md) | Any doc update |
| [03-architecture-rules.md](skills/03-architecture-rules.md) | Code or infrastructure changes |
| [04-minimal-changes.md](skills/04-minimal-changes.md) | Any file modification |
| [05-token-optimization.md](skills/05-token-optimization.md) | Before reading docs |
| [06-output-format.md](skills/06-output-format.md) | Every response |
