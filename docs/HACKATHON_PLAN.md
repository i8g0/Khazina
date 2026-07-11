# Khazina Hackathon Plan

This document supplements [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) with execution strategy for time-constrained development. It does **not** replace the roadmap.

The roadmap defines the complete long-term product. This plan defines how the team delivers an MVP within a four-day hackathon while preserving production-quality architecture.

For current sprint status, see [progress.md](progress.md).

---

## Overview

Hackathons change **implementation scope**, not project direction. Phases, architecture, documentation standards, and review requirements remain in force. Features not completed during the hackathon stay on the roadmap for post-hackathon delivery.

---

## Objectives

1. **Deliver a stable MVP** — working frontend, backend, database, and AI integration demonstrable end-to-end.
2. **Maintain production-ready architecture** — no shortcuts that compromise structure, standards, or the `ApiResponse` contract.
3. **Preserve documentation quality** — update owning documents; do not skip validation or progress tracking.

---

## Team Structure

Five-person team with defined responsibilities. No individual names assigned.

| Role | Responsibility |
|------|----------------|
| Frontend | UI components, pages, layout, RTL, API consumption |
| Backend | REST API routes, schemas, services, exception handling |
| Database | Models, migrations, seed data, query optimization |
| AI | Ollama integration, prompts, inference pipeline, performance validation |
| Integration / Tech Lead | Cross-team coordination, architecture compliance, reviews, demo readiness |

---

## Four-Day Plan

### Day 1 — Foundation

- Frontend foundation (layout, routing, shared components)
- Database foundation (core models, initial migrations)
- Backend skeleton (API structure, health, core config)

### Day 2 — Core Services

- Backend APIs (business endpoints, `ApiResponse` compliance)
- Authentication (core only — if required for demo)
- Core integration (frontend ↔ backend ↔ database)

### Day 3 — AI and Features

- AI integration (Ollama connection, inference endpoints)
- Business features (MVP-scope only per [roadmap hackathon table](PROJECT_ROADMAP.md#hackathon-execution-strategy))
- AI performance validation (timing, resource usage, demo readiness)

### Day 4 — Demo Readiness

- Dashboard (basic MVP dashboard)
- Smoke testing (critical paths only)
- Bug fixes (blocking issues only)
- Demo preparation (stable, reproducible demo flow)

---

## MVP Definition

The MVP must demonstrate:

| Component | MVP Requirement |
|-----------|-----------------|
| Frontend | Loads, navigates, displays data from backend |
| Backend | Serves versioned API under `/api/v1/` with `ApiResponse` envelope |
| Database | Connected, migrated, stores core data |
| AI | Responds to at least one inference request via Ollama |
| Integration | End-to-end flow works without manual intervention |

Features marked **Core Only**, **MVP Features**, or **Basic Dashboard** in the roadmap hackathon scope table are in scope. Everything else remains on the roadmap for post-hackathon completion.

---

## AI Performance Validation

Before demo, validate AI service readiness:

| Metric | What to Measure |
|--------|-----------------|
| Cold start timing | Time from first request to first response after service start |
| Warm response timing | Time for subsequent requests after model is loaded |
| RAM usage | Peak and steady-state memory consumption |
| CPU/GPU usage | Utilization during inference |
| Model comparison | Response quality and speed across candidate models (if multiple evaluated) |
| Demo readiness | Consistent responses within acceptable latency for live demo |

Record results in [progress.md](progress.md). Detailed analysis can follow post-hackathon.

---

## Testing Strategy

| Period | Approach |
|--------|----------|
| During hackathon | Smoke testing — verify critical paths work end-to-end |
| After hackathon | Full QA — comprehensive test coverage per Phase 8 roadmap |

Smoke tests cover: frontend load, API health, database connectivity, AI response, and the primary demo flow.

---

## Risks

| Risk | Mitigation |
|------|------------|
| AI latency | Pre-load models; validate timing before demo; have fallback demo script |
| Integration issues | Integration / Tech Lead validates cross-service flows daily |
| Time constraints | Reduce feature scope per roadmap hackathon table; never cut architecture |
| Unexpected bugs | Fix blocking bugs only on Day 4; defer non-blocking issues post-hackathon |

---

## Demo Checklist

- [ ] Working frontend
- [ ] Working backend
- [ ] Database connected
- [ ] AI responding
- [ ] No blocking bugs
- [ ] Stable demo (reproducible without manual fixes)

---

## After Hackathon

Remaining roadmap phases continue normally. Hackathon scope reductions (Core Only, MVP Features, Basic Dashboard, Smoke Tests, Demo Deployment) are completed to full roadmap standard in subsequent sprints.

Update [progress.md](progress.md) with hackathon outcomes, validation results, and deferred items. Record significant lessons in [DEVELOPMENT_JOURNAL.md](DEVELOPMENT_JOURNAL.md) if warranted.

---

## Related Documents

- [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) — Long-term phase plan and hackathon scope table
- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture (unchanged during hackathon)
- [AI_GUIDELINES.md](AI_GUIDELINES.md) — Time-constrained development rules
- [CONTRIBUTING.md](CONTRIBUTING.md) — Hackathon workflow
- [progress.md](progress.md) — Current sprint and phase status
