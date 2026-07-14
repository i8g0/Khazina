# Sprint 6.7 — Notifications

**Phase:** 6 — Business Features  
**Predecessor:** Sprint 6.6 — Reports — **Complete and approved**  
**Status:** **APPROVED FOR IMPLEMENTATION** (Technical Lead review, 2026-07-15)  
**Date:** 2026-07-15  

**TL adjustments applied (2026-07-15):**

1. **Recipients (v1): initiating user only** — notifications are delivered to the authenticated user who initiated the upstream action, not broadcast to all active organization users.
2. **Future recipient expansion (architecture allowance only — no v1 implementation)** — the design must allow later extension to role-based recipients, department-based recipients, and watchers/subscriptions without breaking v1 records.
3. **Implementation may proceed directly** upon this specification approval — no additional contract gates.

**TL pattern expectation (consistent with Sprints 6.5–6.6):** Sprint 6.7 reuses established architectural patterns (terminal consumer discipline, deterministic mapper/output assembly, polymorphic source reference pattern from Timeline, fail-closed preconditions) instead of introducing preemptive mapping contract documents. Gap discovery protocol applies if implementation finds a genuine architectural gap — including inability to persist the Notification Store within approved schema constraints.

**Normative references (frozen — must not be modified in this sprint):**

- [ADR 008: AI Architecture](ADR/008-ai-architecture.md)
- [ADR 009: Business Engine Architecture](ADR/009-business-engine-architecture.md)
- [ADR 010: Financial Snapshot Architecture](ADR/010-financial-snapshot-architecture.md)
- [AI_FREEZE.md](AI_FREEZE.md)
- [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)
- [BUSINESS_ENGINE_ARCHITECTURE.md](BUSINESS_ENGINE_ARCHITECTURE.md)
- [SPRINT_6.3_SPECIFICATION.md](SPRINT_6.3_SPECIFICATION.md) — Decision Engine completion; `AnalysisService.complete_run` timeline hook pattern
- [SPRINT_6.4_SPECIFICATION.md](SPRINT_6.4_SPECIFICATION.md) — AI insights artifact on `runtime_metadata`; recommendation registry
- [SPRINT_6.5_SPECIFICATION.md](SPRINT_6.5_SPECIFICATION.md) — Scenario completion via `AnalysisService.complete_run`
- [SPRINT_6.6_SPECIFICATION.md](SPRINT_6.6_SPECIFICATION.md) — Report generation and publication lifecycle
- [DATABASE_SCHEMA_DESIGN.md](DATABASE_SCHEMA_DESIGN.md) — §3.9 `timeline_events`, §4.25 polymorphic references; `users` (Phase 4)
- [BUSINESS_DOMAIN_DISCOVERY.md](BUSINESS_DOMAIN_DISCOVERY.md) §8.3, §9.9
- [FRONTEND_SPECIFICATION.md](FRONTEND_SPECIFICATION.md) — notification bell deferred (MVP header)
- [ARCHITECTURE.md](ARCHITECTURE.md) — Phase 4 User System and JWT auth (frozen)

**Tracker alignment:** `progress.md` (post–Sprint 6.6): *“Next step: Frontend Reports page wiring (Phase 7), binary export (`report_exports`), or simulation-domain AI — separate sprint approval required.”* Sprint 6.7 addresses the **notifications gap** identified in discovery: *“Notifications center — Not present; timeline serves partial purpose”* (Discovery §8.3) and *“Notification delivery or alerting infrastructure”* explicitly excluded from Timeline ownership (Discovery §9.9).

---

## Terminology Mapping (Repository Authority)

| Sprint 6.7 term | Repository authority | Meaning |
|---|---|---|
| **Platform Event** | *Sprint 6.7 concept* | A **persisted state transition** or **artifact availability** in an upstream domain that qualifies for notification materialization — detected read-only, never synthesized by AI or engines |
| **Notification Builder** | *Sprint 6.7 orchestration name* | Deterministic service that maps Platform Event + source artifacts → notification records — **without AI or Business Engine execution** |
| **Notification Store** | *Sprint 6.7 concept* | Persisted notification records and per-user read state. Defines **what** is stored — not **how**. Storage form is **implementation-defined** (Gap Discovery Protocol if approved schema is insufficient) |
| **User Notification** | *Sprint 6.7 delivery concept* | A notification record as presented to an authenticated org member via API (title, body, status, read state, provenance link) |
| **Executive Timeline** | `timeline_events` — `backend/app/db/models/timeline.py` | Org-scoped **dashboard activity feed** — append-only, no read/unread, no user targeting (`TimelineService`) |
| **Analysis Run completion** | `analysis_runs.status = completed` | Emitted by `AnalysisService.complete_run()` — already appends timeline event (`TimelineEventType.ANALYSIS`) |
| **Report lifecycle** | `reports.status` — `draft` → `ready` | Draft on Sprint 6.6 generation; `ready` + `published_at` on `ReportService.publish_report()` — already appends timeline event (`TimelineEventType.REPORT`) |
| **AI Recommendation completion** | `runtime_metadata.ai_insights` + `recommendations` rows | Sprint 6.4 `AiRecommendationService.generate_waste_recommendations()` persistence — **no timeline hook today** |
| **Scenario completion** | Completed `analysis_runs` (`analysis_type = simulation`) | Sprint 6.5 `ScenarioService` → `AnalysisService.complete_run()` — shares analysis completion path |
| **Initiating user** | `users` — authenticated caller on upstream API | v1 sole notification recipient; identity passed through orchestration hooks |
| **Organization context** | `organizations`, `users`, `reporting_periods` | Org scope + initiating user membership for delivery and read state |

**Critical constraint:** Notifications are a **presentation and communication layer** (Discovery §9.9 boundary). Sprint 6.7 **does not invoke AI**, **does not dispatch Business Engines**, and **does not mutate** upstream domain artifacts except notification-owned read-state records.

**Timeline boundary (normative):** Timeline and Notifications are **complementary, not interchangeable**. Timeline remains org-scoped dashboard history. Notifications add **user-targeted delivery** and **read/unread state**. Sprint 6.7 must **not** replace, migrate, or overload `timeline_events` to store notifications.

---

## 1. Sprint Goal

Sprint 6.7 delivers the **first end-to-end deterministic notification path** from persisted platform events to user-retrievable notification records:

> **Platform Event (analysis completion, report lifecycle, AI recommendation completion, scenario completion) → Notification Builder → Notification Store → User Notification (list, read/unread) — with full provenance and zero AI or Business Engine execution.**

After this sprint:

- Completing a **waste Decision Result** can materialize a notification for the **initiating user**.
- Completing a **Scenario Result** can materialize a notification for the **initiating user** (distinct template from generic analysis where applicable).
- Completing **AI Recommendations** on a waste run can materialize a notification for the **initiating user**, referencing persisted insights/recommendation counts.
- **Report generation** (draft) and **report publication** (ready) can materialize notifications for the **initiating user**, tied to report catalog rows.
- Notification generation is **deterministic**: identical source artifacts at event time produce identical notification payloads.
- **No AI module is invoked** (`AI_FREEZE.md`).
- **No Business Engine is executed** (ADR-009).

Sprint 6.7 does **not** deliver frontend notification bell/UI, email/push/SMS delivery, websockets, or notification-triggered re-analysis.

---

## 2. Business Objective

### Capability unlocked

Executives and analysts gain **actionable, personal notification history** when platform work completes — without polling dashboards or re-running engines:

| Before Sprint 6.7 | After Sprint 6.7 |
|---|---|
| Timeline provides org-level activity feed only (`timeline_events`) | Notifications provide **user-targeted** records with **read/unread** state |
| AI recommendation completion is silent beyond persisted artifacts | AI completion produces **deterministic notifications** referencing run and recommendation count |
| Report generation/publication visible on timeline only | Report lifecycle events also surface in **notification history** |
| Discovery notes *“Notifications center — Not present”* | Backend **notification APIs** operational for Phase 7 UI consumption |
| No personal unread state | Users can list unread notifications and mark read |

### Executive value

| Stakeholder need | Sprint 6.7 response |
|---|---|
| Awareness when analyses finish | Notification on analysis/scenario completion |
| Awareness when AI insights are ready | Notification on AI recommendation completion (optional upstream step) |
| Awareness when reports are ready | Notifications on report generated and published |
| Auditability | Notification provenance links to source entity (polymorphic pattern) |
| No false triggers | Notifications consume persisted events only — never initiate downstream work |

---

## 3. Scope

### 3.1 INCLUDED (strict)

| ID | Item | Repository basis |
|---|---|---|
| I-01 | **Notification Builder orchestration module** (suggested: `app/notifications/`) | Mirrors `app/reports/` terminal-consumer pattern |
| I-02 | **Platform Event detection** from persisted artifacts (read-only) | No message bus required in v1 |
| I-03 | **Waste analysis completion notifications** | `analysis_runs` (`financial_waste`, `completed`) |
| I-04 | **Scenario completion notifications** | `analysis_runs` (`simulation`, `completed`) — distinct notification kind from I-03 |
| I-05 | **AI recommendation completion notifications** | `runtime_metadata.ai_insights` + optional `recommendations` count for run |
| I-06 | **Report generated notifications** | Sprint 6.6 `ReportBuilderService.generate_report()` success |
| I-07 | **Report published notifications** | `ReportService.publish_report()` success (`status = ready`) |
| I-08 | **Deterministic notification payload assembly** | Template-based title/body from source fields — no LLM |
| I-09 | **Notification Store persistence** | Implementation-defined; gap discovery if schema insufficient |
| I-10 | **Per-user read/unread state** | Phase 4 `users` table; v1 recipient is initiating user only |
| I-11 | **Notification history API** — list, filter (unread/read), mark read, mark all read | Initiating user's org-scoped notifications |
| I-17 | **Initiating user propagation** | Upstream API/orchestration passes authenticated `user_id` into notification hooks |
| I-12 | **Idempotent materialization** — same platform event does not duplicate notifications | Source fingerprint / unique constraint (implementation-defined) |
| I-13 | **Organization + reporting period context** on notifications | From source run/report rows |
| I-14 | **Composition hooks** in orchestration services (not frozen engine internals) | Mirror existing timeline hook sites |
| I-15 | **Automated tests** — determinism, isolation (no `app.ai` LLM, no engine registry), idempotency, read state | Phase 6 test patterns |
| I-16 | **`progress.md` update** | Post-implementation only |

### 3.2 EXCLUDED (strict)

| ID | Item | Reason / deferral |
|---|---|---|
| E-01 | **AI invocation, LLM-composed notification text** | AI freeze |
| E-02 | **Business Engine execution** | ADR-009; notifications never trigger analysis |
| E-03 | **Modification of frozen modules** — `app/ai/`, `app/business/engines/waste/` | Phase 5/6 freeze |
| E-04 | **Frontend notification bell / Notifications Center UI** | FRONTEND_SPEC — deferred; Phase 7 consumer |
| E-05 | **Email, SMS, push, webhooks, Slack** | Discovery §9.9; Sprint 6.2 E-16 |
| E-06 | **Real-time delivery (WebSocket, SSE)** | Out of scope |
| E-07 | **Replacing or merging Timeline domain** | Discovery §9.9 boundary |
| E-08 | **Analysis failure notifications** | v1 focuses on successful completion paths; failures deferred |
| E-09 | **Risk, procurement, compliance notification kinds** | No completed engine paths in v1 scope |
| E-10 | **Cross-org notifications** | MVP single-org user model |
| E-11 | **Notification-triggered workflows** (auto-run analysis, auto-generate report) | Violates terminal consumer rule |
| E-12 | **User-configurable notification preferences / mute rules** | Future sprint |
| E-15 | **Role-based, department-based, and watcher/subscription recipient models** | Architecture allowance only — no v1 implementation |
| E-13 | **Preemptive mapping contract documents** | TL pattern — implement in code/tests |
| E-14 | **Backfill job for historical events** | Optional soft deliverable; not required for AC unless TL adds |

---

## 4. Inputs

All inputs are **read-only persisted artifacts** or **already-committed lifecycle transitions**. The Notification Builder must fail closed when required source data is missing.

### 4.1 Analysis Runs

| Input element | Source | Requirement |
|---|---|---|
| **Run identity** | `analysis_runs.id` | Must exist, belong to org |
| **Run status** | `analysis_runs.status` | Must be `completed` for completion events |
| **Analysis type** | `analysis_runs.analysis_type` | `financial_waste` or `simulation` in v1 |
| **Run title** | `analysis_runs.title` | Notification title/body enrichment |
| **Completion timestamp** | `analysis_runs.completed_at` | Event ordering |
| **Provenance** | `source_snapshot_id`, `source_file_id`, `reporting_period_id` | Copied to notification metadata |
| **Runtime metadata** | `runtime_metadata` JSONB | Optional enrichment; not required for basic completion notification |

**Platform Event kinds (v1):**

| Kind | Trigger condition |
|---|---|
| `analysis_completed` | `financial_waste` run transitions to `completed` |
| `scenario_completed` | `simulation` run transitions to `completed` |

When a simulation run completes, **both** timeline analysis event (existing) and `scenario_completed` notification (new) may materialize — they serve different domains (org feed vs user notification).

### 4.2 Report lifecycle

| Input element | Source | Requirement |
|---|---|---|
| **Report identity** | `reports.id` | Must exist, belong to org |
| **Report status** | `reports.status` | `draft` (generated) or `ready` (published) |
| **Report type** | `reports.report_type` | `analysis` or `simulation` in v1 |
| **Title / summary** | `reports.title`, `reports.summary` | Notification body |
| **Analysis link** | `reports.analysis_run_id` | Provenance |
| **Publication date** | `reports.published_at` | Required for publish event |

**Platform Event kinds (v1):**

| Kind | Trigger condition |
|---|---|
| `report_generated` | Sprint 6.6 report successfully created (`draft`) |
| `report_published` | `ReportService.publish_report()` succeeds (`ready`) |

### 4.3 AI Recommendation completion

| Input element | Source | Requirement |
|---|---|---|
| **Analysis run** | Completed `financial_waste` run | Same run that received AI artifacts |
| **AI insights artifact** | `runtime_metadata.ai_insights` | Must exist after Sprint 6.4 generation |
| **AI provenance** | `generated_at`, `model`, `prompt_version`, `tasks_executed` | Notification metadata — read-only |
| **Recommendations** | `recommendations` where `analysis_run_id` matches and `domain_source = waste` | Count for body text; rows not mutated |

**Platform Event kind (v1):**

| Kind | Trigger condition |
|---|---|
| `ai_recommendations_completed` | `AiRecommendationService.generate_waste_recommendations()` succeeds and persists `ai_insights` |

Notifications **consume** the persisted artifact — they do **not** call `AiRecommendationService` or Ollama.

### 4.4 Scenario completion

Scenario completion inputs are a **specialization** of §4.1 (`simulation` analysis run) plus optional Sprint 6.5 Gold context:

| Input element | Source | Requirement |
|---|---|---|
| **Simulation run** | `simulation_runs` 1:1 with analysis run | Must exist |
| **Scenario provenance** | `runtime_metadata.scenario_provenance` | `scenario_id`, `archetype` for body enrichment |
| **Result summary** | `simulation_runs.result_title`, `result_description` | Deterministic body fields |

Notification kind: `scenario_completed` (§4.1). Scenario-specific templates use provenance fields — no Scenario Engine re-execution.

### 4.5 Organization context

| Input element | Source | Requirement |
|---|---|---|
| **Organization ID** | Source artifact org scope | Must match all linked entities |
| **Initiating user** | Authenticated caller on the upstream API that triggered the platform event | Must belong to org; must be active; **sole v1 recipient** |
| **Recipient users (future)** | Not implemented in v1 | Architecture must allow: role-based, department-based, watchers/subscriptions |
| **Reporting period label** | `reporting_periods.label` via run/report FK | Optional display enrichment |
| **Authorization** | Existing JWT + org role model | Materialization requires initiating user context; list/mark-read scoped to current user |

---

## 5. Outputs

### 5.1 Notification records

A **Notification record** is a persisted, immutable-at-creation message materialized from a Platform Event.

**Conceptual fields (normative minimum):**

| Field | Derivation |
|---|---|
| `notification_version` | Sprint constant (e.g. `"1.0"`) |
| `organization_id` | Org scope |
| `recipient_user_id` | Initiating user (v1 sole recipient) |
| `platform_event_kind` | One of v1 kinds (§4) |
| `title` | Deterministic template from source artifact |
| `body` | Deterministic template from source artifact |
| `source_entity_type` | Polymorphic discriminator — reuse `RelatedEntityType` vocabulary where applicable (`analysis_run`, `report`) |
| `source_entity_id` | UUID of primary source row |
| `reporting_period_id` | From source when present |
| `materialized_at` | UTC timestamp at creation (stable on re-read) |
| `event_fingerprint` | Hash of `(kind, source_entity_type, source_entity_id, recipient_user_id, source_status_or_version)` for idempotency |

#### 5.1.1 Recipient model (v1)

| Rule | Requirement |
|---|---|
| **v1 recipient** | **Initiating user only** — the authenticated user who invoked the upstream API that caused the platform event |
| **No broadcast** | Notifications must not be sent to all active organization users in v1 |
| **Propagation** | Orchestration hooks receive `initiating_user_id` from API layer (`get_current_user()`) |
| **Fail closed** | If initiating user cannot be resolved, notification materialization is skipped or rejected — domain work is not rolled back |

#### 5.1.2 Future recipient expansion (architecture allowance — not v1)

The Notification Store design must **allow** future extension without breaking v1 records:

| Future model | Description | v1 status |
|---|---|---|
| **Role-based recipients** | Notify users matching a role (e.g. all executives) | Not implemented |
| **Department-based recipients** | Notify users associated with a department | Not implemented |
| **Watchers / subscriptions** | Users who opt in to events on entities they follow | Not implemented |

No schema or API for these models is required in Sprint 6.7 — only architectural headroom (e.g. extensible recipient reference on notification records).

### 5.2 Notification status

| Status | Meaning (v1) |
|---|---|
| `active` | Visible in notification history |
| `archived` | Hidden from default list (optional v1 — may defer to read-only `active` only) |

**Default v1:** `active` only. Archival is a soft future extension.

### 5.3 Read / unread state

Read state is **per user**, not on the notification record alone:

| Concept | Requirement |
|---|---|
| **Unread** | No read receipt for `(notification_id, user_id)` |
| **Read** | Read receipt exists with `read_at` timestamp |
| **Mark read** | Creates idempotent read receipt |
| **Mark all read** | Bulk read receipts for current user's unread set |

Storage form for read receipts is **implementation-defined** (Gap Discovery Protocol).

### 5.4 Notification history

| Output | Description | v1 delivery |
|---|---|---|
| **Notification list** | Current user's notifications within org, newest first, unread filter | `GET .../notifications` |
| **Unread count** | Count of unread for current user | `GET .../notifications/unread-count` or list meta |
| **Single notification** | By ID with read state | `GET .../notifications/{id}` |
| **Mark read** | Single or bulk | `POST .../notifications/{id}/read`, `POST .../notifications/read-all` |

History returns **persisted Notification Store records** — not live re-assembly from source tables.

### 5.5 Notification Payload Representation (concept)

The **Notification Payload Representation** is the complete deterministic content bound to a notification record at materialization time (title, body, metadata, provenance). Defines **what** is stored — not **how**. Same Gap Discovery discipline as Sprint 6.6 Report Content Representation.

### 5.6 Intentionally NOT produced

| Excluded output | Reason |
|---|---|
| LLM-generated notification text | AI freeze |
| Push/email delivery receipts | E-05 |
| Modified analysis runs, reports, AI artifacts | Immutability of source domains |
| Timeline event rows | Separate domain — hooks may run in parallel, not merged |
| Workflow side effects | Terminal consumer |

---

## 6. Processing Flow

**Sprint 6.7 pipeline (normative):**

```
Platform Event (persisted lifecycle transition detected)
        ↓
Notification Builder (deterministic assembly — no AI, no Business Engine)
        ↓
Notification Store (records + per-user unread state)
        ↓
User Notification (API retrieval / mark read)
```

**Explicit non-steps:** LLM invocation, `get_engine().run()`, re-fetching Silver snapshots for new metrics, triggering analysis/report/AI generation.

**Hook sites (composition — mirror timeline pattern):**

| Platform Event | Existing orchestration | Notification hook (new) |
|---|---|---|
| `analysis_completed` | `AnalysisService.complete_run()` | After run persisted + timeline event — if `financial_waste`; pass `initiating_user_id` |
| `scenario_completed` | `AnalysisService.complete_run()` | After run persisted — if `simulation`; pass `initiating_user_id` |
| `ai_recommendations_completed` | `AiRecommendationService.generate_waste_recommendations()` | After insights + recommendations persisted; pass `initiating_user_id` |
| `report_generated` | `ReportBuilderService.generate_report()` | After catalog row + content persisted; pass `initiating_user_id` |
| `report_published` | `ReportService.publish_report()` | After status `ready` + timeline event; pass `initiating_user_id` |

**Detailed steps:**

| Step | Actor | Action |
|---|---|---|
| 1 | Domain orchestration | Completes upstream work (existing sprint behavior) |
| 2 | Notification Builder | Detect Platform Event kind from committed artifact state |
| 3 | Notification Builder | Load read-only source context (run, report, insights, counts) |
| 4 | Notification Builder | Compute `event_fingerprint`; skip if already materialized for recipient (idempotent) |
| 5 | Notification Builder | Build deterministic title/body + payload representation |
| 6 | Notification Builder | Resolve recipient — **initiating user only (v1)** |
| 7 | Notification Builder | Persist notification record + unread state for initiating user |
| 8 | API | Users list/mark-read via notification endpoints |
| **Failure** | Notification Builder | Upstream transaction already committed; notification failure **must not roll back** domain work — log and fail closed on notification side only (mirror timeline best-effort if nested, or separate transaction — implementation choice) |

**Position in platform pipeline (ADR-010):**

```
Bronze → Silver → Decision Engine → Gold → AI Recommendations → Scenario → Reports
        ↓
[Sprint 6.7 Notifications] → User Notification history → [Future: Frontend Notifications Center]
```

**Parallel path (unchanged):**

```
Domain completion → Timeline event (org dashboard feed)
```

---

## 7. Deliverables

| # | Deliverable | Description |
|---|---|---|
| D-01 | **Sprint 6.7 Specification (this document)** | Approved — TL sign-off 2026-07-15 |
| D-02 | **Notification Builder module** | Suggested `app/notifications/` — event registry, templates, service, exceptions |
| D-03 | **Platform Event registry** | v1 kinds mapped to source types and template selectors |
| D-04 | **Deterministic payload templates** | Arabic-friendly strings from persisted fields (mirror Reports fallback discipline) |
| D-05 | **Notification Store persistence** | Records + read receipts; storage form implementation-defined |
| D-06 | **Idempotency guard** | Fingerprint deduplication per platform event |
| D-07 | **Composition hooks** | Wire into `AnalysisService`, `AiRecommendationService`, `ReportBuilderService`, `ReportService` |
| D-08 | **Notification API** | List, get, unread count, mark read, mark all read |
| D-09 | **Repository + service layer** | Follow existing domain repository pattern |
| D-10 | **Determinism + isolation test suite** | Same inputs → identical payloads; no `app.ai` LLM; no engine execution |
| D-11 | **Idempotency + read-state tests** | Duplicate hooks, mark read, unread count |
| D-12 | **`progress.md` update** | Sprint 6.7 completion record (post-implementation only) |

**Explicit non-deliverables:** Preemptive mapping contract documents (E-13), AI changes, Business Engine changes, frontend bell, email/push, websocket delivery, notification preferences UI.

---

## 8. Acceptance Criteria

### 8.1 Materialization and idempotency

| ID | Criterion |
|---|---|
| AC-01 | Waste analysis completion materializes `analysis_completed` notification for the initiating user |
| AC-02 | Simulation completion materializes `scenario_completed` notification |
| AC-03 | AI recommendation success materializes `ai_recommendations_completed` notification |
| AC-04 | Report generation materializes `report_generated` notification |
| AC-05 | Report publication materializes `report_published` notification |
| AC-06 | Duplicate hook invocation for same platform event and recipient does not create duplicate notifications (idempotent) |
| AC-07 | Notification includes correct polymorphic source reference and `recipient_user_id` |

### 8.2 Read state and history

| ID | Criterion |
|---|---|
| AC-08 | New notification appears as **unread** for the initiating user |
| AC-09 | Mark read transitions notification to read for current user only |
| AC-10 | Mark all read clears initiating user's unread set |
| AC-11 | List endpoint returns only current user's notifications |
| AC-12 | Unread count matches current user's unread notifications |
| AC-13 | Non-initiating org users do not receive notifications from another user's platform events (v1) |

### 8.3 Determinism and isolation

| ID | Criterion |
|---|---|
| AC-14 | Identical source artifacts → identical notification title/body/payload |
| AC-15 | Notification Builder does not import or invoke `app.ai` LLM/prompt/orchestrator paths |
| AC-16 | Notification Builder does not call `get_engine()` or Business Engine `run()` |
| AC-17 | Notification materialization does not mutate analysis runs, reports, recommendations, or AI insights |
| AC-18 | Notification materialization does not trigger analysis, AI, or report generation |

### 8.4 Regression

| ID | Criterion |
|---|---|
| AC-19 | Timeline events still created on analysis complete and report publish (unchanged behavior) |
| AC-20 | Sprint 6.3–6.6 tests remain green |

### 8.5 Documentation

| ID | Criterion |
|---|---|
| AC-21 | This specification marked **Approved for Implementation** with TL sign-off |
| AC-22 | `progress.md` updated on sprint completion |

---

## 9. Technical Risks

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R-01 | **No notification schema in approved design** | Cannot persist store | Gap Discovery Protocol — document single gap, TL review before migration |
| R-02 | **Timeline vs Notification confusion** | Duplicate product concepts | Explicit boundary §Terminology; parallel hooks, separate stores |
| R-03 | **Transaction coupling** | Notification failure rolls back analysis | Separate transaction or post-commit hook; domain commit wins |
| R-04 | **Initiating user not propagated** | Notification delivered to wrong user or no user | Require `user_id` on orchestration hooks; fail closed if missing in v1 |
| R-05 | **Simulation double notification** | `analysis_completed` + `scenario_completed` overlap | v1 uses `scenario_completed` only for simulation type; skip generic waste kind |
| R-06 | **AI optional path** | Notification without prior AI step | `ai_recommendations_completed` only on explicit AI service success — not on analysis alone |
| R-07 | **Scope creep to push/email** | E-05 breach | Explicit exclusion; API-only delivery |
| R-08 | **Scope creep to workflow triggers** | ADR violation | AC-17; terminal consumer tests |
| R-09 | **Frozen module modification pressure** | ADR violation | Hooks only in orchestration services (composition) |
| R-10 | **Read-state schema** | Unread count incorrect | Unique constraint on `(notification_id, user_id)` read receipts |

---

## 10. Dependencies

### 10.1 Hard dependencies (must be complete)

| Dependency | Status | Reference |
|---|---|---|
| Sprint 6.3 Decision Engine + `AnalysisService.complete_run` | ✅ Complete | `progress.md` Sprint 6.3 |
| Sprint 6.4 AI Recommendations | ✅ Complete | `progress.md` Sprint 6.4 |
| Sprint 6.5 Scenario Analysis | ✅ Complete | `progress.md` Sprint 6.5 |
| Sprint 6.6 Reports | ✅ Complete | `progress.md` Sprint 6.6 |
| Phase 4 User System + JWT auth | ✅ Complete | `ARCHITECTURE.md` Phase 4 |
| Timeline domain (parallel, not replaced) | ✅ Exists | `TimelineService`, `timeline_events` |
| Org-scoped API + role model | ✅ Exists | `app/api/permissions.py` |

### 10.2 Soft dependencies

| Dependency | Notes |
|---|---|
| Reporting period labels | Display enrichment |
| Recommendation counts on AI notification | Zero count valid |
| Simulation provenance fields | Body enrichment |

### 10.3 Downstream consumers (not Sprint 6.7 blockers)

| Consumer | Relationship |
|---|---|
| Frontend notification bell / Notifications Center | Phase 7 |
| Email/push delivery | Future ops sprint |
| User notification preferences | Future |
| Role / department / watcher recipient models | Future — architecture allowance in v1 schema (E-15) |
| Dashboard timeline | Unchanged — continues separate API |

---

## 11. Implementation Order

### Step 1 — Specification approval ✅

- This document approved (Technical Lead sign-off 2026-07-15).
- **No additional contract gates** — implementation may proceed directly.
- Resolve R-01 via Gap Discovery if notification schema absent.

### Step 2 — Notification model and event registry

- Define Platform Event kinds, fingerprint rules, payload representation shape.
- Template registry per kind (deterministic strings).

### Step 3 — Notification Store

- Persistence for records and read receipts (implementation-defined).
- Idempotency constraint on fingerprint.

### Step 4 — Notification Builder service

- Read-only source loaders per event kind.
- Recipient resolution — **initiating user only (v1)**; schema must allow future recipient models (E-15).
- Materialization with fail-closed validation.

### Step 5 — Composition hooks

- Wire into analysis complete, AI recommendation success, report generate, report publish.
- Ensure domain transactions remain primary.

### Step 6 — API endpoints

- List, get, unread count, mark read, mark all read.
- Register router, deps, permissions (analyst read minimum).

### Step 7 — Tests and regression

- Determinism, isolation, idempotency, read state, hook integration mocks.
- Full suite green; update `progress.md`.

---

## 12. Technical Lead Recommendation

### Recommendation: **APPROVED FOR IMPLEMENTATION**

| Factor | Assessment |
|---|---|
| **Architectural fit** | Closes Discovery notifications gap without unfreezing AI or Business Engines |
| **Correct boundary** | Terminal consumer; distinct from Timeline (§9.9) |
| **Pattern reuse** | Timeline hook composition, polymorphic source refs, deterministic templates, Gap Discovery for store |
| **Scope discipline** | Five v1 platform event kinds; initiating-user-only delivery avoids broadcast anti-pattern |
| **Determinism** | Template-based payloads; idempotent fingerprints per recipient |
| **Future extensibility** | Recipient model allows role/department/watcher expansion without v1 implementation |
| **Known schema gap** | R-01 expected — resolve at implementation via Gap Discovery |

### TL adjustments applied (2026-07-15)

1. **Recipients (v1): initiating user only** — not broadcast to all active org users.
2. **Future recipient models** — role-based, department-based, watchers/subscriptions allowed in architecture; not implemented in v1 (E-15).
3. **Implementation authorized directly** — no contract gates beyond this specification.

### Conditions for implementation start

1. **This specification approved** — ✅ TL sign-off recorded (2026-07-15).
2. **No modification** to frozen `app/ai/` internals or Business Engine implementations.
3. **No AI or Business Engine work** in Sprint 6.7.
4. **No preemptive mapping contract documents** — event/template rules live in code and tests.
5. **Gap discovery protocol** — if Notification Store cannot persist within approved schema, document the **single gap** and obtain TL approval before proceeding.
6. **Timeline preserved** — notification work must not deprecate or merge `timeline_events`.
7. **Initiating user required** — upstream hooks must propagate authenticated user identity; no org-wide broadcast in v1.

### Suggested next sprint after 6.7

Frontend Notifications Center (Phase 7), email/push delivery channel, notification preferences, or binary report export — each requires separate sprint approval.

---

## Document Control

| Field | Value |
|---|---|
| **Version** | 1.1 |
| **Author** | Platform specification (Sprint 6.7) |
| **Review status** | **Approved for Implementation** — TL sign-off 2026-07-15 |
| **Implementation authorized** | Yes |
| **Supersedes** | v1.0 (draft) |
