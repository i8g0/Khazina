# Khazina Business Features Freeze

**Sprint:** 6.10 — Business Features Freeze  
**Date:** 2026-07-15  
**Status:** **APPROVED — FROZEN**

This document formally freezes the Khazina Phase 6 business features layer as implemented at the end of Sprints 6.1–6.9 (plus approved stabilization fixes). No architectural changes, new business capabilities, optimizations, or schema/API expansions are permitted without a new ADR (where applicable) and Tech Lead approval.

**Related documents:**

- [AI_FREEZE.md](AI_FREEZE.md) — Phase 5 AI layer freeze (Sprint 5.6)
- [ADR 010: Financial Snapshot Architecture](ADR/010-financial-snapshot-architecture.md)
- [BUSINESS_ENGINE_ARCHITECTURE.md](BUSINESS_ENGINE_ARCHITECTURE.md)
- [BUSINESS_DOMAIN_DISCOVERY.md](BUSINESS_DOMAIN_DISCOVERY.md)
- [HACKATHON_READINESS_SPECIFICATION.md](HACKATHON_READINESS_SPECIFICATION.md)
- [SPRINT_6.10_SPECIFICATION.md](SPRINT_6.10_SPECIFICATION.md)
- [progress.md](progress.md) — authoritative sprint completion record
- [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) — Phase 9+ planning

> **Documentation sync (2026-07-16):** Phases 7–8 and Product Polish are complete. Deferred targets below reflect the reconciled roadmap; see [progress.md](progress.md).

---

## Executive Summary

Phase 6 delivers the end-to-end **business backend pipeline** for Khazina:

```
Upload → Bronze → Silver (Financial Snapshot)
       → Waste Decision (Gold)
       → AI Recommendations (Facts-only insights)
       → Scenario Simulation (Gold)
       → Executive Reports → PDF Export
       → Notifications (Platform Events)
       → Organization Settings (six-section config)
```

Sprints **6.1–6.9** are **implementation-complete**. Full demo critical path has been verified on real APIs (Login → Upload → Waste → AI → Scenario → Report → PDF → Notifications). Sprint **6.10** certifies freeze and closes Phase 6 for Phase 7.

---

## Phase Objectives

| Objective | Status |
|-----------|--------|
| Financial Snapshot architecture (ADR-010) | ✅ Delivered |
| Ingest Excel/CSV into Bronze/Silver | ✅ Delivered |
| Waste Decision Engine (Silver → Gold) | ✅ Delivered |
| AI Recommendations from Facts only | ✅ Delivered |
| Scenario Analysis (what-if → Gold) | ✅ Delivered |
| Executive Reports from persisted artifacts | ✅ Delivered |
| Notifications + read state | ✅ Delivered |
| Organization Settings + consumer gates | ✅ Delivered |
| PDF export + user notification prefs + failure notifications | ✅ Delivered |
| Official freeze / phase closure | ✅ This document |

---

## Scope Delivered

| Domain | Pipeline stage | Backend entry | Persistence |
|--------|----------------|---------------|-------------|
| Financial Ingestion | Bronze → Silver | `POST .../financial-files/upload` | `financial_files`, `financial_snapshots` |
| Waste Decision | Silver → Gold | `POST .../decisions/waste/execute` | `analysis_runs`, `waste_analysis_results` |
| AI Recommendations | Facts → AI insights | `POST .../ai-recommendations/waste/generate` | `runtime_metadata.ai_insights`, `recommendations` |
| Scenario Analysis | Silver → Gold (simulation) | `POST .../simulation/scenarios/{id}/execute` | `analysis_runs`, simulation Gold tables |
| Executive Reports | Gold/AI → Report Content | `POST .../reports/generate` | `reports.content_representation` |
| Report Export | Content → PDF | `GET .../reports/{id}/export?format=pdf` | `report_exports` + filesystem storage |
| Notifications | Platform Events → notifications | `GET/POST .../notifications` | `notifications`, `notification_read_receipts` |
| User Notification Prefs | User overrides | `GET/PATCH .../users/me/notification-preferences` | `user_notification_preferences` |
| Organization Settings | Six-section config | `GET/PATCH .../settings` | `organization_settings` |

**Registered Business Engines (Phase 6):** Waste (`app/business/engines/waste/`), Scenario (`app/business/engines/scenario/`).

**Platform Event kinds (Phase 6):** `analysis_completed`, `scenario_completed`, `ai_recommendations_completed`, `report_generated`, `report_published`, `analysis_failed`, `scenario_failed`.

---

## Scope Explicitly Deferred

| Category | Deferred item | Target |
|----------|---------------|--------|
| Frontend | Full live API depth for all Phase 2 shells | Phase 7 |
| Frontend | Org Management, Settings UI, Notifications Center | Phase 7 |
| Analytics | Executive Dashboard API | Phase 7 |
| Analytics | Repository Summary API | Phase 7 |
| Export | Excel / PowerPoint binary export | Phase 10 |
| Notifications | Email, SMS, push, webhooks | Phase 7+ ops |
| Notifications | Role / department / watcher recipients | Future sprint |
| Notifications | Ingestion failure notifications | Future sprint |
| Notifications | AI recommendation failure notifications | Future sprint |
| AI | Number Guard / response regeneration | Future hardening |
| AI | Simulation-domain AI (`SCENARIO_ANALYSIS` production pipeline) | Future sprint |
| Engines | Financial Engine (ratios, liquidity, profitability) | Future engine sprint |
| Engines | Risk, Revenue, Budget, Cost, Supplier, Liquidity engines | Phase 9+ (Risk UI — Phase 9) |
| Settings | Audit log for preference/export changes | Future sprint |
| Reports | Background export jobs / scheduling | Future sprint |
| Ingestion | Cloud blob storage; snapshot re-parse UX | ADR-010 deferred |
| Quality | CI pipelines, coverage gates | Phase 10 |
| Ops | Production deployment, monitoring | Phase 10 |

---

## Sprint-by-Sprint Certification

| Sprint | Deliverable | Status | Evidence |
|--------|-------------|--------|----------|
| 6.1 | Financial Snapshot Architecture (ADR-010) | ✅ Complete | ADR-010; Sprint 6.2 §11 contract |
| 6.2 | Bronze → Silver ingestion | ✅ Complete | `app/ingestion/`, `tests/ingestion/` |
| 6.3 | Decision Engine (Waste) | ✅ Complete | `app/decision/`, `tests/decision/` |
| 6.4 | AI Recommendations (waste) | ✅ Complete | `app/ai_recommendations/`, `tests/ai_recommendations/` |
| 6.5 | Scenario Analysis | ✅ Complete | `app/scenario/`, `app/business/engines/scenario/`, `tests/scenario/` |
| 6.6 | Executive Reports | ✅ Complete | `app/reports/`, `tests/reports/` |
| 6.7 | Notifications | ✅ Complete | `app/notifications/`, `tests/notifications/` |
| 6.8 | Organization Settings | ✅ Complete | `app/settings/`, `tests/settings/` |
| 6.9 | PDF, user prefs, failure notifications | ✅ Complete | `app/reports/export_*.py`, `tests/advanced_features/` |
| 6.10 | Business Features Freeze (this document) | ✅ Complete | Documentation / governance only |

---

## Business Features Certified

### Implemented business pipeline

```
Upload → Bronze → Silver (Financial Snapshot)
       → Waste Decision (Gold)
       → AI Recommendations (Facts-only)
       → Scenario Simulation (Gold)
       → Executive Reports → PDF Export
       → Notifications (Platform Events)
       → Organization Settings (six-section config)
```

### Approved components (frozen)

The following packages are **frozen** as of Sprint 6.10. Modifications require Tech Lead approval and, for architectural change, a new ADR.

| Component | Status | Package / Path |
|-----------|--------|----------------|
| ✓ Ingestion pipeline | Frozen | `app/ingestion/` |
| ✓ Financial Snapshot model/repo | Frozen | `app/db/models/snapshot.py`, `app/repositories/snapshot.py` |
| ✓ Decision (Waste) path | Frozen | `app/decision/` |
| ✓ AI Recommendations service | Frozen | `app/ai_recommendations/` |
| ✓ Scenario path + Scenario Engine | Frozen | `app/scenario/`, `app/business/engines/scenario/` |
| ✓ Report Builder | Frozen | `app/reports/` (builder/content/loaders/service) |
| ✓ Report PDF Export | Frozen | `app/reports/export_service.py`, `pdf_renderer.py`, `export_storage.py` |
| ✓ Notifications | Frozen | `app/notifications/` |
| ✓ Organization Settings | Frozen | `app/settings/` |
| ✓ Facts Contract (Phase 5) | Still frozen | `app/business/facts/contract.py` |
| ✓ Waste Engine (Phase 5) | Still frozen | `app/business/engines/waste/` |
| ✓ AI Prompt Engine / Client (Phase 5) | Still frozen | `app/ai/` — change control via `AI_FREEZE.md` |

**Stabilization fixes retained as Phase 6 baseline (not temporary):**

| Fix | Nature |
|-----|--------|
| Scenario assumptions ORM-safe field access | Correctness aligned with Sprint 6.5 contract |
| `organization_settings.id` server default (`c1a8f3e92b04`) | Schema aligned with `UUIDPrimaryKeyMixin` |
| `notifications` / `report_exports` / related `id` defaults (`d2f6b8a14e37`) | Schema aligned with `UUIDPrimaryKeyMixin` |
| RECOMMENDATIONS Arabic output-format instructions | Prompt formatting only; parser/validation contract unchanged |
| Recommendation Markdown numbered-item wrappers | Parser Markdown compatibility only |
| E2E AI pipeline timeout (`TOTAL_AI_PIPELINE_TIMEOUT`) | Demo verification harness only |

---

## Demo Readiness

| Check | Status |
|-------|--------|
| Login → Upload → Waste → AI → Scenario → Report → PDF → Notifications | ✅ Verified on real APIs (2026-07-15) |
| Demo org / workbook / bootstrap | ✅ Present (`scripts/demo/`) |
| Ollama model for demo | `qwen3.5:2b`, thinking disabled (`AI_FREEZE.md`) |
| PDF export | ✅ Operational after `id` default migration |
| Notifications list / unread / mark read | ✅ Operational after `id` default migration |

---

## Validation Summary

| Check | Result |
|-------|--------|
| Sprints 6.1–6.9 marked Completed in `progress.md` | ✅ |
| Sprint deliverables match specifications (implementation scope) | ✅ |
| Phase 6 business deferrals G-01–G-04 closed in Sprint 6.9 | ✅ |
| Demo critical path verified end-to-end | ✅ |
| No Phase 7 analytics APIs in Phase 6 | ✅ |
| No unfinished Phase 6 feature TODOs in business modules | ✅ |
| No temporary debug instrumentation in Phase 6 packages | ✅ |
| Schema id defaults aligned with ORM mixin | ✅ (corrective migrations; permanent) |
| Formal freeze document produced | ✅ (this document) |

---

## Known Operational Risks

Documented at freeze time. **Not Phase 6 incomplete acceptance criteria.** Not to be “silently” solved by reopening Phase 6 without TL assignment.

| Risk | Description |
|------|-------------|
| LLM output variability | Occasional AI recommendations still fail `invalid_recommendation_count` despite formatting prompts (~10% in 10-run sample) |
| Exception cleanup masking | `AiRecommendationError` can surface as HTTP 500 due to `contextlib` `TypeError` during DB session cleanup |
| Local Ollama dependency | Demo path requires running Ollama + configured model |
| AI latency | Full three-task pipeline often ~90–160s on demo hardware |
| Exact LLM bytes not persisted on failure | Failed runs do not store raw recommendations text in metadata |

---

## Non-blocking Technical Debt

| Item | Classification |
|------|----------------|
| `AiRecommendationError` → HTTP 500 via `contextlib` | Exception-handler / ASGI cleanup — maintenance if assigned |
| Stale “Next step” prose in older sprint detail sections | Documentation hygiene — addressed in Sprint 6.10 progress update |
| Frontend content max-width inconsistency (1440 vs 1760) | Open Item — Phase 7 / design decision |
| Phase 3 migration validation checklist unchecked in `progress.md` | Historical Phase 3 ops note — not Phase 6 feature gap |
| Number Guard absent | Explicitly deferred in Sprint 6.4 |
| Corrective id-default migrations | **Permanent** schema alignment — not disposable workarounds |

---

## Lessons Learned

1. **ORM vs mixin defaults must match migrations** — `UUIDPrimaryKeyMixin.server_default` is ineffective if Alembic omits `gen_random_uuid()`; causes production `NotNullViolation` on insert.
2. **LLM formatting is a first-class reliability surface** — Markdown wrappers (`###`, `**`) and introductory prose break numbered-item parsers; constrain prompts for small models.
3. **Terminal consumers need defensive adapters** — Assumption rows may be ORM instances or dicts; eager `.get()` on objects fails.
4. **Freeze sprints are mandatory governance** — Implementation complete ≠ phase closed without freeze document and tracker update (precedent: 3.7 / 4.5 / 5.6).
5. **Persist failure evidence** — Without raw LLM capture on failed AI runs, diagnosis requires expensive replay and remains non-deterministic.

---

## Technical Lead Certification

| Item | Status |
|------|--------|
| Sprints 6.1–6.9 objectives complete | ✅ |
| Phase 6 business acceptance criteria satisfied (delivered scope) | ✅ |
| Demo critical path verified on real APIs | ✅ |
| Deferred backlog documented | ✅ |
| No unfinished Phase 6 implementation TODOs in business modules | ✅ |
| No temporary debug code in Phase 6 packages | ✅ |
| Corrective id-default migrations retained as permanent schema | ✅ |
| Sprint 6.10 documentation-only constraint respected | ✅ |
| Ready for Phase 7 against frozen backend baseline | ✅ |

**Sign-off field:** Technical Lead approval of this freeze document marks Phase 6 **officially closed**.

---

## Phase 6 Freeze Declaration

### Business Features Status: **APPROVED — FROZEN**

| Field | Value |
|-------|-------|
| **Frozen after** | Sprint 6.10 |
| **Phase 6 status** | **Completed and frozen** |
| **Ready for** | Phase 7 — Frontend Features |
| **Change control** | Modifications to frozen Phase 6 business packages require Tech Lead approval; architectural changes require ADR + Tech Lead approval |
| **AI Freeze** | Remains in force (`AI_FREEZE.md`) |
| **Business Engine Freeze** | Waste + Scenario only; additional engines require ADR-009 process |

Phase 6 business backend is complete for its approved scope, demo-critical path verified, and formally frozen. Phase 7 may consume this baseline without modifying Phase 6 modules unless explicitly approved.

---

*End of Business Features Freeze document.*
