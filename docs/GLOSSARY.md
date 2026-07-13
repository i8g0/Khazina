# Khazina Glossary

Common terminology used across Khazina project documentation, sprints, and reviews.

---

## Sprint

A single unit of implementation work with one clearly defined objective. Sprints are numbered within phases (e.g., Sprint 2.1). Each sprint receives review, validation, and one logical commit before it is marked complete.

## Phase

A major development stage grouping related sprints toward a shared goal. Khazina is organized into ten phases from Foundation (Phase 1) through Production Deployment (Phase 10). Phases must complete in order unless Tech Lead approves otherwise.

## ADR

Architecture Decision Record. A concise document in `docs/ADR/` capturing a significant technology or design decision, its context, alternatives, and consequences. ADRs are numbered sequentially (e.g., `001-fastapi.md`).

## Repository

The Khazina monorepo containing frontend, backend, AI, database, Docker, documentation, and scripts directories. All application code lives in designated subdirectories, not the repository root.

## Monorepo

A single Git repository containing multiple related projects or services. Khazina's monorepo includes the Next.js frontend, FastAPI backend, Docker configuration, and reserved directories for AI and database assets.

## Tech Lead

The role responsible for architectural approval, sprint review, merge authorization, and escalation decisions. Tech Lead sign-off is required before sprints are marked complete and before changes merge to `main`.

## Developer

The contributor who implements sprint scope, runs local validation, updates documentation, and prepares commits for review.

## Reviewer

Any person who evaluates sprint deliverables. The developer performs self-review; the Tech Lead performs authoritative review before merge.

## Validation

The process of verifying that sprint deliverables work as expected. Includes starting services, running builds, testing endpoints, and confirming no regressions. Results are recorded in `docs/progress.md`.

## Definition of Done

The checklist of conditions that must all be satisfied before a sprint is marked complete. Covers implementation, validation, documentation, review, and Git requirements. See [CONTRIBUTING.md](CONTRIBUTING.md) and [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md).

## ApiResponse

The standardized JSON response envelope used by every Khazina API endpoint. Contains `success`, `message`, `data`, and `errors` fields. Defined in `backend/app/schemas/response.py`.

## Pydantic

Python library used by FastAPI for data validation and serialization. Request and response models are defined as Pydantic classes in `backend/app/schemas/`.

## Alembic

Database migration tool for SQLAlchemy. Manages schema versioning through migration scripts in `backend/alembic/`. Initialized in Phase 1; first business migrations expected in Phase 3.

## Docker Compose

Tool for defining and running multi-container Docker applications. Khazina uses Compose to orchestrate postgres, backend, frontend, and ollama services locally via `docker/docker-compose.yml`.

## Ollama

Local AI inference server included as a Docker Compose service. Provides on-device model execution without external API dependencies. Backend integration is established in Phase 5 (Sprint 5.1); the application is **model-agnostic** and does not define a default or recommended model.

## OLLAMA_MODEL

Environment variable naming the Ollama model identifier for a deployment. **Required operator input** — not hardcoded in application code. Set in `backend/.env` or `docker/.env`. Changing this value switches the configured model without code changes or architectural impact. Current Development Baseline: `Qwen3:8B` (see [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md) §16).

## REST API

Representational State Transfer application programming interface. Khazina's backend exposes a versioned REST API under `/api/v1/` consumed by the Next.js frontend.

## FastAPI

Python web framework used for the Khazina backend. Provides routing, validation, dependency injection, and automatic OpenAPI documentation.

## Next.js

React framework used for the Khazina frontend. Uses the App Router, TypeScript, and Tailwind CSS with RTL support.

## PostgreSQL

Relational database used as Khazina's primary datastore. Version 16, accessed through SQLAlchemy and managed with Alembic migrations.

## SQLAlchemy

Python ORM (Object-Relational Mapper) used by the backend to interact with PostgreSQL. Database session management lives in `backend/app/db/`.

## Foundation First

Khazina's development philosophy: establish stable infrastructure and standards in early phases before implementing business features. Phase 1 completed this foundation.

## Progress Tracker

The live document `docs/progress.md` recording current phase status, sprint history, validation results, review outcomes, and commit hashes.

## Development Journal

Historical record of architectural decisions, implementation history, lessons learned, and obstacles. Maintained in [DEVELOPMENT_JOURNAL.md](DEVELOPMENT_JOURNAL.md).

---

## Related Documents

- [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) — Phase plan and methodology
- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
- [CONTRIBUTING.md](CONTRIBUTING.md) — Workflow and conventions
- [API_CONTRACTS.md](API_CONTRACTS.md) — API standards
