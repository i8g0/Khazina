# Sprint 6.9 — Advanced Features

**Phase:** 6 — Business Features  
**Predecessor:** Sprint 6.8 — Settings — **Complete and approved**  
**Status:** **DRAFT** — Awaiting Technical Lead review (revision 1.1)  
**Date:** 2026-07-15  

**TL adjustments applied (2026-07-15):**

1. **Executive Dashboard API removed** — cross-domain KPI/chart/list aggregation is **Phase 7 analytics** (`PROJECT_ROADMAP.md` Phase 7 / Phase 8 boundary; `DATABASE_SCHEMA_DESIGN.md` §16 query-time dashboard aggregation). Sprint 6.9 must **not** introduce dashboard read-model endpoints.
2. **Repository Summary API removed** — file inventory and quality metric aggregation for Data Management is **Phase 7 analytics**, not Phase 6 business features.
3. **Scope refocused on Phase 6 business completion** — deliver deferred capabilities from Sprints 6.6–6.8: PDF report export, user notification preferences, report export preferences, and analysis failure notifications.

**Normative references (frozen — must not be modified in this sprint):**

- [ADR 008: AI Architecture](ADR/008-ai-architecture.md)
- [ADR 009: Business Engine Architecture](ADR/009-business-engine-architecture.md)
- [ADR 010: Financial Snapshot Architecture](ADR/010-financial-snapshot-architecture.md)
- [AI_FREEZE.md](AI_FREEZE.md)
- [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)
- [BUSINESS_ENGINE_ARCHITECTURE.md](BUSINESS_ENGINE_ARCHITECTURE.md)
- [SPRINT_6.3_SPECIFICATION.md](SPRINT_6.3_SPECIFICATION.md) — Decision Engine; `AnalysisService.complete_run` / `fail_run`
- [SPRINT_6.4_SPECIFICATION.md](SPRINT_6.4_SPECIFICATION.md) — AI Recommendation Service completion/failure paths
- [SPRINT_6.5_SPECIFICATION.md](SPRINT_6.5_SPECIFICATION.md) — Scenario Analysis; shared analysis lifecycle
- [SPRINT_6.6_SPECIFICATION.md](SPRINT_6.6_SPECIFICATION.md) — Report Builder; Report Content Representation; binary export deferred (E-05, A-05)
- [SPRINT_6.7_SPECIFICATION.md](SPRINT_6.7_SPECIFICATION.md) — Notification Builder; user preferences deferred (E-12); failure notifications deferred (E-08)
- [SPRINT_6.8_SPECIFICATION.md](SPRINT_6.8_SPECIFICATION.md) — Settings Service; report export preferences deferred (E-11); user-level prefs deferred (E-02)
- [DATABASE_SCHEMA_DESIGN.md](DATABASE_SCHEMA_DESIGN.md) — §14.3 `report_exports`; ambiguity A-05
- [BUSINESS_DOMAIN_DISCOVERY.md](BUSINESS_DOMAIN_DISCOVERY.md) — §9.6 Executive Reporting export execution gap
- [FRONTEND_SPECIFICATION.md](FRONTEND_SPECIFICATION.md) — Page 5 `export?format=pdf` (Phase 7 consumer — backend contract only in this sprint)
- [API_CONTRACTS.md](API_CONTRACTS.md) — org-scoped route nesting; `ApiResponse` envelope
- [ARCHITECTURE.md](ARCHITECTURE.md) — Phase 4 User System and JWT auth (frozen)
- [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) — Phase 6 business vs Phase 7 frontend / Phase 8 analytics boundary

**Tracker alignment:** `progress.md` (post–Sprint 6.8): *“Next step: Frontend Organization Management and Settings page (Phase 7), user-level notification preferences (Sprint 6.7 E-12), or binary report export — separate sprint approval required.”* Sprint 6.9 closes **documented Phase 6 backend business deferrals** — not Phase 7 analytics.

**TL pattern expectation (consistent with Sprints 6.5–6.8):** Sprint 6.9 reuses established architectural patterns (terminal consumer discipline, deterministic assembly, org-scoped services, composition-only integration, settings/notification gate resolution, fail-closed preconditions) instead of introducing preemptive mapping contract documents. Gap Discovery Protocol applies if implementation finds a genuine architectural gap — including inability to persist `report_exports` or user notification preferences within approved schema constraints.

---

## Terminology Mapping (Repository Authority)

| Sprint 6.9 term | Repository authority | Meaning |
|---|---|---|
| **Binary Report Export** | `DATABASE_SCHEMA_DESIGN.md` §14.3 `report_exports`; Sprint 6.6 E-05 | Deterministic **PDF** artifact generated from persisted Report Content Representation — not live re-assembly |
| **Exportable Report (JSON)** | Sprint 6.6 — `GET .../reports/{id}/export` | Existing deterministic JSON serialization — **unchanged** when `format` omitted |
| **Report Export Record** | *Sprint 6.9 concept* | Persisted metadata for a generated binary export (format, fingerprint, storage reference). Storage form **implementation-defined** (Gap Discovery if schema insufficient) |
| **Report Export Preferences** | Sprint 6.8 E-11; `ReportPreferencesSection` extension | Org-level export behavior consumed by Report Export Service — deferred until `report_exports` exists |
| **User Notification Preferences** | Sprint 6.7 E-12; Sprint 6.8 E-02 | Per-user overrides composing **atop** Platform Default Notification Preferences |
| **Effective Notification Preferences** | *Sprint 6.9 resolution concept* | Deterministic merge: platform defaults → org Platform Default Notification Preferences → user overrides |
| **Analysis failure notification** | Sprint 6.7 E-08 | Platform Event materialized when `AnalysisService.fail_run()` persists `status = failed` |
| **Platform Event (failure kinds)** | Sprint 6.7 registry extension | `analysis_failed` (`financial_waste`); `scenario_failed` (`simulation`) — symmetric to success kinds (R-05 pattern) |
| **Export execution** | `BUSINESS_DOMAIN_DISCOVERY.md` §9.6 | Reporting domain owns actual file download/export execution — not dashboard aggregation |

**Critical constraint:** Sprint 6.9 completes **business-domain delivery paths** (report export execution, notification preference resolution, failure-path notifications). It **does not invoke AI**, **does not dispatch Business Engines**, and **does not introduce analytics aggregation endpoints**.

**Phase boundary (normative):**

| Responsibility | Phase | Sprint 6.9 |
|---|---|---|
| PDF/binary report export from persisted content | Phase 6 — Reports business domain | **In scope** |
| User + org notification preference resolution | Phase 6 — Notifications / Settings | **In scope** |
| Analysis failure notification materialization | Phase 6 — Notifications business domain | **In scope** |
| Executive Dashboard KPI/chart/list APIs | Phase 7 — analytics | **Excluded** |
| Repository summary / Data Management aggregation APIs | Phase 7 — analytics | **Excluded** |
| Cross-domain query-time aggregation tables | Phase 7/8 — `DATABASE_SCHEMA_DESIGN.md` §16 | **Excluded** |

---

## 1. Sprint Goal

Sprint 6.9 delivers the **final Phase 6 business-feature completions** deferred across Sprints 6.6–6.8:

> **Persisted Report Content + Settings + Notification Preferences + Failed Analysis Runs → Report Export Service / Preference Resolver / Notification Builder (failure kinds) → Enhanced business delivery — with deterministic outputs and zero AI or Business Engine execution.**

After this sprint:

- Analysts can generate and retrieve **deterministic PDF exports** from persisted Report Content Representation rows, with export metadata persisted in `report_exports`.
- Organizations can configure **Report Export Preferences** consumed by the export path (Sprint 6.8 E-11 closure).
- Users can persist and retrieve **user-level notification preferences** that refine org-level Platform Default Notification Preferences.
- **Analysis and scenario failures** can materialize notifications for the initiating user when enabled by effective preferences.
- All outputs are **deterministic**: identical persisted inputs produce identical export artifacts and preference resolutions.
- **No AI module is invoked** (`AI_FREEZE.md`).
- **No Business Engine is executed** (ADR-009).
- **No analytics aggregation APIs** are introduced (Phase 7 boundary).

Sprint 6.9 does **not** deliver frontend pages, dashboard APIs, repository summary APIs, email/push delivery, Excel/PowerPoint export, or forecasting.

---

## 2. Business Objective

### Capability unlocked

The platform closes **documented Phase 6 deferrals** in Reporting and Notifications — without pulling Phase 7 analytics forward:

| Before Sprint 6.9 | After Sprint 6.9 |
|---|---|
| Report export is JSON serialization only (Sprint 6.6) | **PDF binary export** with persisted `report_exports` records (Discovery §9.6 export execution) |
| Report export behavior is not configurable per org | **Report Export Preferences** in Settings consumed by export service (Sprint 6.8 E-11) |
| Notifications use org-level Platform Default Notification Preferences only | **User-level notification preferences** compose atop org defaults (Sprint 6.7 E-12) |
| Analysis failure is silent beyond persisted `failed` status | **Failure Platform Events** can materialize initiating-user notifications (Sprint 6.7 E-08) |
| Dashboard/repository aggregation proposed in draft v1.0 | Correctly **deferred to Phase 7** — not implemented in this sprint |

### Executive value

| Stakeholder need | Sprint 6.9 response |
|---|---|
| Board-ready report delivery | Deterministic PDF from frozen report content |
| Org-appropriate export defaults | Report Export Preferences without code deploy |
| Personal notification control | User prefs without changing org-wide defaults |
| Awareness when analyses fail | Failure notifications for initiating user |
| Phase discipline | Business features complete; analytics remain Phase 7 |

### Repository gap analysis (Phase 6 only)

The following deferrals remain open after Sprints 6.6–6.8 and belong to **Phase 6 business domains** (not Phase 7 analytics):

| Gap ID | Deferred item | Source | Domain |
|---|---|---|---|
| G-01 | Binary report export (`report_exports`) | Sprint 6.6 E-05; `progress.md` | Executive Reporting §9.6 |
| G-02 | Report binary export preferences | Sprint 6.8 E-11 | Settings / Reports |
| G-03 | User-level notification preferences | Sprint 6.7 E-12; Sprint 6.8 E-02 | Notifications |
| G-04 | Analysis failure notifications | Sprint 6.7 E-08 | Notifications |

**Explicitly not Phase 6 (deferred to Phase 7+):**

| Item | Source | Reason |
|---|---|---|
| Executive Dashboard API | `FRONTEND_SPECIFICATION.md` Page 1; schema §16 | Analytics aggregation — TL rejected for 6.9 |
| Repository Summary API | `FRONTEND_SPECIFICATION.md` Page 6; Discovery §9.2 metrics | Analytics aggregation — TL rejected for 6.9 |
| Ingestion/file-processing failure notifications | Sprint 6.2 E-16 | Not in repository Phase 6 scope |
| Email/push/SMS delivery | Sprint 6.7 E-05 | Ops channel — out of scope |
| Excel/PowerPoint export | Sprint 6.6 E-05; A-05 | Partial deferral; PDF v1 only |
| Simulation-domain AI | `progress.md` | AI scope — separate approval |
| Financial Engine / new engines | Sprint 6.2 E-14; ADR-009 | Engine freeze |

---

## 3. Scope

### 3.1 INCLUDED (strict)

| ID | Item | Repository basis |
|---|---|---|
| I-01 | **Report Export Service** (suggested: extension of `app/reports/`) | Sprint 6.6 E-05; Discovery §9.6 export execution |
| I-02 | **PDF export generation** from persisted `reports.content_representation` | Deterministic template rendering; org **Report Language** (Sprint 6.8 Localization) |
| I-03 | **`report_exports` persistence** | `DATABASE_SCHEMA_DESIGN.md` §14.3 — Gap Discovery if schema insufficient |
| I-04 | **Export endpoint enhancement** | `GET .../reports/{id}/export?format=pdf` per FRONTEND_SPEC Page 5; preserve JSON when `format` omitted |
| I-05 | **Report Export Preferences** — extension to Sprint 6.8 `ReportPreferencesSection` | Sprint 6.8 E-11; consumed read-only by export service |
| I-06 | **Settings resolver + API patch support** for new export preference fields | Extends existing Settings Service — no new settings section |
| I-07 | **User Notification Preferences persistence** | Sprint 6.7 E-12 |
| I-08 | **User notification preferences API** | `GET/PATCH .../users/me/notification-preferences` (org-scoped) |
| I-09 | **Effective preference resolution** | `NotificationBuilder` reads merged org + user prefs before materialization gate |
| I-10 | **Analysis failure Platform Event kinds** | `analysis_failed`, `scenario_failed` — Sprint 6.7 E-08 |
| I-11 | **Failure notification templates** | Deterministic Arabic title/body from `runtime_metadata.failure` + run fields |
| I-12 | **Composition hook** on `AnalysisService.fail_run()` | Mirror success-path `try_materialize` discipline; `initiating_user_id` required |
| I-13 | **Idempotent materialization** for failure events | Reuse Sprint 6.7 fingerprint pattern |
| I-14 | **Automated tests** — determinism, isolation (no `app.ai`, no engine registry), export fingerprint, preference merge, failure notifications | Phase 6 test patterns |
| I-15 | **`progress.md` update** | Post-implementation only |

### 3.2 EXCLUDED (strict)

| ID | Item | Reason / deferral |
|---|---|---|
| E-01 | **Executive Dashboard API** — summary, charts, recent analyses, timeline slices | **Phase 7 analytics** — TL adjustment 2026-07-15 |
| E-02 | **Repository Summary API** — file counts, import metrics, quality aggregation | **Phase 7 analytics** — TL adjustment 2026-07-15 |
| E-03 | **AI invocation, LLM-composed export or notification text** | AI freeze |
| E-04 | **Business Engine execution** | ADR-009 |
| E-05 | **Modification of frozen modules** — `app/ai/`, `app/business/engines/waste/` | Phase 5/6 freeze |
| E-06 | **Frontend Reports export button, Notifications prefs UI, Settings UI** | Phase 7 consumer |
| E-07 | **Excel and PowerPoint binary export** | A-05 partial; PDF v1 only |
| E-08 | **Email, SMS, push, webhooks** | Sprint 6.7 E-05 |
| E-09 | **Forecasting, Monte Carlo, predictive models** | User constraint |
| E-10 | **ERP or external integrations** | User constraint |
| E-11 | **Ingestion/file-processing failure notifications** | Sprint 6.2 E-16 |
| E-12 | **AI recommendation failure notifications** | Not in Sprint 6.7 E-08 deferral; separate sprint if needed |
| E-13 | **Role-based, department-based, watcher notification recipients** | Sprint 6.7 E-15 |
| E-14 | **Audit log for export/preference changes** | Sprint 6.8 E-14 |
| E-15 | **Report scheduling or background export jobs** | Sprint 6.6 E-06; on-demand only in v1 |
| E-16 | **Cross-org operations** | MVP single-org model |
| E-17 | **Workflow side effects** (export triggers re-generation) | Terminal consumer rule |
| E-18 | **Preemptive mapping contract documents** | TL pattern |
| E-19 | **Analytics query optimization or materialized views** | Phase 8 |

---

## 4. Inputs

All inputs are **read-only persisted artifacts** or **already-committed lifecycle transitions**, except user/org preference documents owned by this sprint.

### 4.1 Binary Report Export

| Input element | Source | Requirement |
|---|---|---|
| **Report catalog row** | `reports` | Must exist, belong to org |
| **Report Content Representation** | `reports.content_representation` JSONB | Must exist (Sprint 6.6 generation) |
| **Report status** | `reports.status` | `draft` or `ready` |
| **Resolved Localization** | Sprint 6.8 `report_language` | PDF template language |
| **Report Export Preferences** | Sprint 6.8 `report_preferences` extension | Export behavior gates (§5.3) |
| **Organization branding** | `organizations` identity fields | Header/footer enrichment |

### 4.2 User Notification Preferences

| Input element | Source | Requirement |
|---|---|---|
| **Authenticated user** | JWT `current_user` | Must belong to org, active |
| **Org Platform Default Notification Preferences** | Sprint 6.8 resolved settings | Baseline for merge |
| **Persisted user overrides** | User Notification Preferences document (new) | Optional; lazy-init to empty overrides |

**Effective resolution rule (normative):**

1. If org `notifications_enabled = false` → no materialization.
2. Else if user `notifications_enabled = false` → no materialization for that user.
3. Else kind enabled only if kind ∈ org `enabled_notification_kinds` **and** kind ∉ user `muted_notification_kinds`.
4. User cannot enable kinds org has disabled.

### 4.3 Analysis Failure Notifications

| Input element | Source | Requirement |
|---|---|---|
| **Failed analysis run** | `analysis_runs.status = failed` | Emitted by `AnalysisService.fail_run()` |
| **Analysis type** | `analysis_runs.analysis_type` | `financial_waste` → `analysis_failed`; `simulation` → `scenario_failed` |
| **Failure details** | `runtime_metadata.failure` | Set by Decision/Scenario/AI orchestration on failure |
| **Run title** | `analysis_runs.title` | Template enrichment |
| **Initiating user** | Propagated from upstream API | Sole v1 recipient; skip if absent |
| **Effective notification preferences** | §4.2 | Failure kinds must be valid Platform Event kinds in org/user prefs |

**R-05 symmetry (normative):** Simulation failures use `scenario_failed` only — not generic `analysis_failed`.

---

## 5. Outputs

### 5.1 Report Export Record

| Field | Derivation |
|---|---|
| `report_id` | Source report |
| `export_format` | `pdf` (v1) |
| `content_fingerprint` | Hash of source `content_representation` at export time |
| `export_fingerprint` | Hash of generated binary bytes |
| `file_size_bytes` | Binary size |
| `generated_at` | UTC timestamp |
| `storage_reference` | Implementation-defined path/key |

### 5.2 PDF Export Artifact

Deterministic binary document rendered from persisted Report Content Representation — fixed section order per profile (`waste_decision`, `scenario`). No live re-assembly from mutable source tables.

### 5.3 Report Export Preferences (extension)

| Field (conceptual) | Type | Default (v1) | Consumer |
|---|---|---|---|
| `pdf_export_enabled` | boolean | `true` | Export endpoint gate |
| `pdf_include_cover_page` | boolean | `true` | PDF template assembly |
| `pdf_include_provenance_appendix` | boolean | `true` | PDF template assembly |

Stored within existing **`report_preferences`** section of Organization Settings Document — no seventh settings section.

### 5.4 User Notification Preferences Document

| Field | Derivation |
|---|---|
| `user_id` | Authenticated user |
| `organization_id` | Org scope |
| `notifications_enabled` | User master switch (default: `true`) |
| `muted_notification_kinds` | Subset of Platform Event kinds (including failure kinds when enabled) |
| `preferences_version` | Sprint constant (e.g. `"1.0"`) |

### 5.5 Failure notification records

Same Notification record shape as Sprint 6.7 §5.1, with:

| `platform_event_kind` | Trigger |
|---|---|
| `analysis_failed` | `financial_waste` run → `failed` |
| `scenario_failed` | `simulation` run → `failed` |

### 5.6 Intentionally NOT produced

| Excluded output | Reason |
|---|---|
| Dashboard KPI payloads | E-01 Phase 7 |
| Repository summary payloads | E-02 Phase 7 |
| LLM-generated text | AI freeze |
| Excel/PPT binaries | E-07 |
| Modified analysis runs, reports, AI artifacts | Immutability |

---

## 6. Processing Flow

**Sprint 6.9 pipeline (normative):**

```
Existing Platform Artifacts (persisted rows — read-only)
        ↓
Advanced Business Feature Services
  ├── Report Export Service (PDF + report_exports)
  ├── Settings extension (Report Export Preferences)
  ├── User Notification Preference Resolver
  └── Notification Builder extension (failure kinds + effective prefs)
        ↓
Enhanced Business Delivery (export download / preference PATCH / failure notifications)
```

**Explicit non-steps:** LLM invocation, `get_engine().run()`, dashboard aggregation queries, repository metric rollups, triggering analysis/AI/report generation.

### 6.1 PDF export flow

| Step | Actor | Action |
|---|---|---|
| 1 | Report Export Service | Validate report + `content_representation`; check `pdf_export_enabled` |
| 2 | Report Export Service | Resolve `report_language` from Settings Service (read-only) |
| 3 | Report Export Service | Render deterministic PDF applying export preferences |
| 4 | Report Export Service | Compute fingerprints; persist `report_exports` row |
| 5 | API | Return binary stream or export metadata per existing API patterns |

**Idempotency:** Re-export of unchanged content + format may return existing `report_exports` row when fingerprint matches.

### 6.2 User preference flow

| Step | Actor | Action |
|---|---|---|
| 1 | User | PATCH notification preferences |
| 2 | Preferences Service | Validate kinds; reject org-disabled kind enablement |
| 3 | Preferences Service | Persist user document |
| 4 | Notification Builder | Resolve effective prefs → gate → materialize or skip |

### 6.3 Analysis failure notification flow

| Step | Actor | Action |
|---|---|---|
| 1 | Domain orchestration | `AnalysisService.fail_run()` persists failed run (existing behavior) |
| 2 | Notification Builder | Detect failure kind from `analysis_type` |
| 3 | Notification Builder | Build deterministic template from `runtime_metadata.failure` |
| 4 | Notification Builder | Apply effective prefs; persist notification if allowed |
| 5 | Hook | `try_materialize()` — failure on notification side does not roll back `fail_run` |

**Position in platform pipeline:**

```
… → Reports (Sprint 6.6) → Notifications (Sprint 6.7) → Settings (Sprint 6.8)
        ↓
[Sprint 6.9] → PDF Export + User Prefs + Failure Notifications
        ↓
[Phase 7] → Frontend wiring + Dashboard/Repository analytics APIs
```

---

## 7. Deliverables

| # | Deliverable | Description |
|---|---|---|
| D-01 | **Sprint 6.9 Specification (this document)** | Draft v1.1 — TL review required |
| D-02 | **Report Export extension** | PDF renderer, `report_exports` persistence, export endpoint enhancement |
| D-03 | **Report Export Preferences** | Settings resolver/API extension; consumer integration in export service |
| D-04 | **User Notification Preferences** | Persistence, resolver, GET/PATCH API |
| D-05 | **Notification Builder extension** | Failure kinds, templates, effective preference gates, `fail_run` hook |
| D-06 | **Repository + service layer** | Follow existing domain patterns |
| D-07 | **Determinism + isolation test suite** | No `app.ai`; no engines; stable export fingerprints |
| D-08 | **Preference merge + failure notification tests** | Org/user composition; failure materialization |
| D-09 | **`progress.md` update** | Sprint 6.9 completion record (post-implementation only) |

**Explicit non-deliverables:** Dashboard API, Repository Summary API, frontend pages, Excel/PPT, analytics endpoints, preemptive contract documents.

---

## 8. Acceptance Criteria

### 8.1 Binary report export

| ID | Criterion |
|---|---|
| AC-01 | PDF export generates from persisted `content_representation` only |
| AC-02 | Identical content + format + language + preferences → identical export fingerprint |
| AC-03 | `report_exports` row persisted with provenance linkage to `reports.id` |
| AC-04 | `GET .../reports/{id}/export?format=pdf` returns PDF per FRONTEND_SPEC Page 5 |
| AC-05 | `GET .../reports/{id}/export` without `format` preserves existing JSON behavior (AC-23) |
| AC-06 | Org `report_language` influences PDF template language |
| AC-07 | `pdf_export_enabled = false` fails closed on PDF export |

### 8.2 Report Export Preferences

| ID | Criterion |
|---|---|
| AC-08 | Export preference fields persist in `report_preferences` section |
| AC-09 | PATCH settings accepts valid export preference fields |
| AC-10 | Export service consumes preferences read-only at export time |

### 8.3 User notification preferences

| ID | Criterion |
|---|---|
| AC-11 | User can GET/PATCH own notification preferences within org |
| AC-12 | User cannot unmute kinds org has disabled |
| AC-13 | User mute suppresses materialization when org kind is enabled |
| AC-14 | Org master switch overrides all user prefs |
| AC-15 | Effective resolution is deterministic |

### 8.4 Analysis failure notifications

| ID | Criterion |
|---|---|
| AC-16 | `financial_waste` failure materializes `analysis_failed` for initiating user when prefs allow |
| AC-17 | `simulation` failure materializes `scenario_failed` — not `analysis_failed` |
| AC-18 | Duplicate `fail_run` hook is idempotent per fingerprint |
| AC-19 | Missing `initiating_user_id` skips materialization; `fail_run` still succeeds |
| AC-20 | Failure notifications do not invoke AI or engines |

### 8.5 Determinism, isolation, and phase boundary

| ID | Criterion |
|---|---|
| AC-21 | Sprint 6.9 modules do not import or invoke `app.ai` LLM paths |
| AC-22 | Sprint 6.9 modules do not call `get_engine()` or `engine.run()` |
| AC-23 | No dashboard or repository summary endpoints introduced |
| AC-24 | Export and notifications do not mutate upstream domain artifacts (except owned records) |
| AC-25 | Sprint 6.3–6.8 tests remain green |

### 8.6 Documentation

| ID | Criterion |
|---|---|
| AC-26 | This specification approved by Technical Lead before implementation |
| AC-27 | `progress.md` updated on sprint completion |

---

## 9. Technical Risks

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R-01 | **No `report_exports` schema** | Cannot persist export metadata | Gap Discovery Protocol |
| R-02 | **No user notification preferences schema** | Cannot persist user overrides | Gap Discovery Protocol |
| R-03 | **PDF rendering non-determinism** | Fingerprint drift | Pin template version; test byte stability |
| R-04 | **Preference merge complexity** | User/org conflict bugs | Explicit rules §4.2; dedicated tests |
| R-05 | **Simulation failure kind overlap** | Duplicate or wrong kind | `scenario_failed` only for simulation (mirror Sprint 6.7 R-05) |
| R-06 | **Scope creep to dashboard/repository APIs** | Phase boundary violation | E-01, E-02; AC-23 |
| R-07 | **Scope creep to Excel/PPT** | E-07 breach | PDF v1 only |
| R-08 | **`fail_run` missing initiating user** | No failure notification | Propagate from Decision/Scenario/AI API layers |
| R-09 | **Export storage path** | Binary delivery failure | Gap Discovery for storage form |
| R-10 | **Settings section sprawl** | Architectural drift | Export prefs extend `report_preferences` only — no new section |

---

## 10. Dependencies

### 10.1 Hard dependencies (must be complete)

| Dependency | Status | Reference |
|---|---|---|
| Sprint 6.6 Reports + `content_representation` | ✅ Complete | `progress.md` Sprint 6.6 |
| Sprint 6.7 Notifications + Builder | ✅ Complete | `progress.md` Sprint 6.7 |
| Sprint 6.8 Settings + Localization + Report Preferences | ✅ Complete | `progress.md` Sprint 6.8 |
| Sprint 6.3–6.5 Analysis lifecycle + `fail_run` | ✅ Complete | Decision/Scenario services |
| Phase 4 User System + JWT auth | ✅ Complete | `ARCHITECTURE.md` Phase 4 |

### 10.2 Soft dependencies

| Dependency | Notes |
|---|---|
| `runtime_metadata.failure` populated by orchestration | Required for meaningful failure notification body |
| Org `report_language` configured | Falls back to platform default |
| User prefs document absent on first read | Lazy-init to empty overrides |

### 10.3 Downstream consumers (not Sprint 6.9 blockers)

| Consumer | Relationship |
|---|---|
| Frontend Reports export button | Phase 7 |
| Frontend Notifications prefs UI | Phase 7 |
| Executive Dashboard API | Phase 7 analytics |
| Repository Summary API | Phase 7 analytics |
| Excel/PPT export | Future sprint |

---

## 11. Implementation Order

### Step 1 — Specification approval

- This document v1.1 reviewed and approved (Technical Lead sign-off required).
- Resolve R-01, R-02 via Gap Discovery if persistence entities absent.

### Step 2 — Report Export Preferences

- Extend settings constants, resolver, models, and PATCH validation.
- Tests for resolution and validation.

### Step 3 — Report Export Service

- PDF template renderer from persisted content.
- `report_exports` persistence and export endpoint enhancement.
- Integrate Settings Service (read-only).

### Step 4 — User Notification Preferences

- Persistence, resolver, GET/PATCH API.
- Integrate effective resolution into `NotificationBuilder`.

### Step 5 — Failure notifications

- Register `analysis_failed` and `scenario_failed` kinds.
- Templates, fingerprint rules, `fail_run` hook with `initiating_user_id` propagation.

### Step 6 — Tests and regression

- Determinism, isolation, preference merge, export fingerprint, failure idempotency.
- Verify no dashboard/repository routes added.
- Full suite green; update `progress.md`.

---

## 12. Technical Lead Recommendation

### Recommendation: **APPROVED FOR IMPLEMENTATION** *(pending TL sign-off on v1.1)*

| Factor | Assessment |
|---|---|
| **Architectural fit** | Closes documented Phase 6 deferrals (G-01–G-04) without unfreezing AI or engines |
| **Phase discipline** | Removes Phase 7 analytics from scope per TL review |
| **Correct boundary** | Terminal consumers and preference resolution — not aggregation |
| **Pattern reuse** | Report Builder templates, Notification Builder hooks, Settings resolver, Gap Discovery |
| **Scope discipline** | Four concrete business completions — no new products |
| **MVP completion** | Phase 6 business backend ready for Phase 7 frontend + analytics |

### Conditions for implementation start

1. **This specification v1.1 approved** — TL sign-off required.
2. **No dashboard or repository summary endpoints** — Phase 7 analytics remain deferred.
3. **No modification** to frozen `app/ai/` or Business Engine implementations.
4. **No AI or Business Engine work** in Sprint 6.9.
5. **Gap Discovery Protocol** for `report_exports` and user preferences persistence if needed.
6. **PDF v1 only** — Excel/PPT deferred.
7. **User prefs compose atop org defaults** — org Platform Default Notification Preferences remain baseline.
8. **Export preferences extend `report_preferences` only** — no new settings section.

### Suggested next sprint after 6.9

Phase 7 — Frontend wiring (Reports export button, Notifications prefs UI, Organization Management and Settings pages) and **analytics APIs** (Executive Dashboard, Repository Summary) as separate Phase 7 sprint approvals.

---

## Document Control

| Field | Value |
|---|---|
| **Version** | 1.1 |
| **Author** | Platform specification (Sprint 6.9) |
| **Review status** | **Draft** — Awaiting Technical Lead review (revision per TL feedback 2026-07-15) |
| **Implementation authorized** | No — pending approval |
| **Supersedes** | v1.0 (draft — rejected: included Phase 7 analytics) |
