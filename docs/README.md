# Khazina Documentation

Official project documentation for the Khazina Enterprise Financial Decision Intelligence Platform.

---

## Core Documents

| Document | Purpose |
|----------|---------|
| [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) | Phase plan, sprint methodology, quality gates |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Platform architecture, layers, infrastructure |
| [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md) | **Official AI subsystem specification (frozen Sprint 5.2)** |
| [BUSINESS_ENGINE_ARCHITECTURE.md](BUSINESS_ENGINE_ARCHITECTURE.md) | **Business Engine layer specification (frozen Sprint 5.3A)** |
| [progress.md](progress.md) | Sprint status and deliverables |
| [AI_GUIDELINES.md](AI_GUIDELINES.md) | Rules for AI-assisted development tools |

## Completion Reports

| Document | Purpose |
|----------|---------|
| [PRODUCT_POLISH_COMPLETION_REPORT.md](PRODUCT_POLISH_COMPLETION_REPORT.md) | Product Polish transition stage closure (D1–D5) |
| [PHASE_8_COMPLETION_REPORT.md](PHASE_8_COMPLETION_REPORT.md) | Phase 8 — Testing & Quality Assurance acceptance |
| [SPRINT_8_1_BACKEND_TESTING_REPORT.md](SPRINT_8_1_BACKEND_TESTING_REPORT.md) | Sprint 8.1 backend QA |
| [SPRINT_8_2_FRONTEND_TESTING_REPORT.md](SPRINT_8_2_FRONTEND_TESTING_REPORT.md) | Sprint 8.2 frontend QA |
| [SPRINT_8_3_INTEGRATION_TESTING_REPORT.md](SPRINT_8_3_INTEGRATION_TESTING_REPORT.md) | Sprint 8.3 integration & E2E |
| [SPRINT_8_4_PERFORMANCE_AI_REPORT.md](SPRINT_8_4_PERFORMANCE_AI_REPORT.md) | Sprint 8.4 performance & AI |
| [SPRINT_8_5_QA_FREEZE_REPORT.md](SPRINT_8_5_QA_FREEZE_REPORT.md) | Sprint 8.5 QA freeze |

> **Sprint numbering note:** Pre-polish work uses `SPRINT_8.1_*` / `SPRINT_8_2_*` filenames (mock removal, verification, demo polish). Phase 8 QA sprints use `SPRINT_8_1_*` through `SPRINT_8_5_*` (underscore form). Both sets are documented; see [progress.md](progress.md) sprint summary.

## Specifications

| Document | Purpose |
|----------|---------|
| [FRONTEND_SPECIFICATION.md](FRONTEND_SPECIFICATION.md) | Frontend pages and integration contracts |
| [COMPONENT_SPECIFICATION.md](COMPONENT_SPECIFICATION.md) | UI component behavior |
| [API_CONTRACTS.md](API_CONTRACTS.md) | REST API standards |
| [DATABASE_SCHEMA_DESIGN.md](DATABASE_SCHEMA_DESIGN.md) | Relational schema design |

## Architecture Decision Records

| ADR | Topic |
|-----|-------|
| [ADR 001](ADR/001-fastapi.md) | FastAPI |
| [ADR 006](ADR/006-ollama.md) | Ollama local inference |
| [ADR 007](ADR/007-authentication-authorization.md) | Authentication & authorization |
| [ADR 008](ADR/008-ai-architecture.md) | AI architecture adoption |
| [ADR 009](ADR/009-business-engine-architecture.md) | Business Engine architecture adoption |

Full ADR index: [docs/ADR/](ADR/)

---

For setup and quick start, see the repository root [README.md](../README.md).
