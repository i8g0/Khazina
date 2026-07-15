# Sprint 6.8 — Settings

**Phase:** 6 — Business Features  
**Predecessor:** Sprint 6.7 — Notifications — **Complete and approved**  
**Status:** **APPROVED FOR IMPLEMENTATION** (Technical Lead review, 2026-07-15)  
**Date:** 2026-07-15  

**TL adjustments applied (2026-07-15):**

1. **Notification Preferences renamed and clarified as Platform Default Notification Preferences** — organization-level defaults only; they **do not replace** future user-level notification preferences (Sprint 6.7 E-12).
2. **`prompt_language` moved out of AI Configuration** — new **Localization** section containing **Prompt Language** and **Report Language**. AI Configuration is limited to **feature enablement and behavior selection** only — no deployment configuration, no model selection, no runtime AI tuning.
3. **Implementation may proceed directly** upon this specification approval — no additional contract gates.

**Normative references (frozen — must not be modified in this sprint):**

- [ADR 008: AI Architecture](ADR/008-ai-architecture.md)
- [ADR 009: Business Engine Architecture](ADR/009-business-engine-architecture.md)
- [ADR 010: Financial Snapshot Architecture](ADR/010-financial-snapshot-architecture.md)
- [AI_FREEZE.md](AI_FREEZE.md)
- [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)
- [BUSINESS_ENGINE_ARCHITECTURE.md](BUSINESS_ENGINE_ARCHITECTURE.md)
- [SPRINT_6.3_SPECIFICATION.md](SPRINT_6.3_SPECIFICATION.md) — Decision Engine; `AnalysisService.complete_run`
- [SPRINT_6.4_SPECIFICATION.md](SPRINT_6.4_SPECIFICATION.md) — AI Recommendation Service; deployment-level `AiSettings`
- [SPRINT_6.5_SPECIFICATION.md](SPRINT_6.5_SPECIFICATION.md) — Scenario Analysis completion path
- [SPRINT_6.6_SPECIFICATION.md](SPRINT_6.6_SPECIFICATION.md) — Report Builder; report catalog lifecycle
- [SPRINT_6.7_SPECIFICATION.md](SPRINT_6.7_SPECIFICATION.md) — Notification Builder; Platform Event kinds; E-12 user preferences deferred
- [DATABASE_SCHEMA_DESIGN.md](DATABASE_SCHEMA_DESIGN.md) — §4.1 `organizations`; no settings persistence entity
- [BUSINESS_DOMAIN_DISCOVERY.md](BUSINESS_DOMAIN_DISCOVERY.md) — Settings/Configuration absent from frontend; Organization Management absent
- [ARCHITECTURE.md](ARCHITECTURE.md) — `app/core/config/` deployment settings; org-scoped API nesting
- [FRONTEND_SPECIFICATION.md](FRONTEND_SPECIFICATION.md) — no settings page in MVP header

**Tracker alignment:** `progress.md` (post–Sprint 6.6): *“Next step: Frontend Reports page wiring (Phase 7), binary export (`report_exports`), or simulation-domain AI — separate sprint approval required.”* Sprint 6.7 §12 suggested *“notification preferences”* as a follow-on. Sprint 6.8 addresses the **settings/configuration gap** identified in discovery: *“Settings/Configuration — Not present”* (`BUSINESS_DOMAIN_DISCOVERY.md` §4, §8.3).

**TL pattern expectation (consistent with Sprints 6.5–6.7):** Sprint 6.8 reuses established architectural patterns (org-scoped services, deterministic resolution, composition-only consumer integration, fail-closed validation) instead of introducing preemptive mapping contract documents. Gap Discovery Protocol applies if implementation finds a genuine architectural gap — including inability to persist the Organization Settings Document within approved schema constraints.

---

## Terminology Mapping (Repository Authority)

| Sprint 6.8 term | Repository authority | Meaning |
|---|---|---|
| **Settings** | *Sprint 6.8 product name* | Organization-scoped **configuration only** — defines how Khazina behaves when existing services run; never executes Business Engines or AI |
| **Settings Service** | *Sprint 6.8 orchestration name* | Deterministic service that **reads, merges, validates, and persists** organization configuration — **without AI or Business Engine execution** |
| **Organization Settings Document** | *Sprint 6.8 concept* | The complete, versioned, org-scoped configuration bundle at a point in time (six logical sections below). Defines **what** is stored — not **how**. Storage form is **implementation-defined** (Gap Discovery Protocol if approved schema is insufficient) |
| **Platform Default Configuration** | `app/core/config/` — `backend/app/core/config/` | Deployment-level Pydantic settings (`AiSettings`, `AuthSettings`, `AppSettings`, etc.) loaded from environment — **not mutated** by Sprint 6.8 |
| **Existing Organization Configuration** | `organizations` — `backend/app/db/models/organization.py` | Core org identity fields (`name`, `platform_name`, `executive_title`, `is_active`) managed by `OrganizationService` — **inputs** to settings resolution, not replaced by this sprint |
| **Organization Settings** | *Sprint 6.8 section* | Operational org preferences beyond core identity CRUD (locale/display defaults, feature visibility flags) |
| **Localization** | *Sprint 6.8 section* | Org-level language preferences for prompt and report output — **not** deployment AI infrastructure |
| **AI Configuration** | *Sprint 6.8 section* | Org-level **AI feature enablement and behavior selection** only — **not** deployment configuration, model selection, or runtime AI tuning |
| **Analysis Configuration** | *Sprint 6.8 section* | Org-level preferences governing analysis lifecycle hooks and preconditions |
| **Report Preferences** | *Sprint 6.8 section* | Org-level preferences consumed by `ReportBuilderService` and `ReportService` composition |
| **Platform Default Notification Preferences** | *Sprint 6.8 section* | Organization-level notification defaults governing which Platform Event kinds materialize notifications (Sprint 6.7); **does not replace** future user-level notification preferences |
| **Resolved Configuration** | *Sprint 6.8 output concept* | Deterministic merge of platform defaults + org persisted settings + existing org identity — the effective config existing services read |
| **Consumer Service** | Existing domain services | `AnalysisService`, `AiRecommendationService`, `ReportBuilderService`, `ReportService`, `NotificationBuilder` (Sprint 6.7) — **read** resolved settings at decision points; Settings Service does not call them |

**Critical constraint:** Settings are **configuration only** (`user query` normative rule). Sprint 6.8 **does not invoke AI**, **does not dispatch Business Engines**, and **does not perform business logic**. Settings **never trigger** analysis, AI, report generation, or notification materialization — they only supply values that **existing services** consult when those services are already invoked by API/workflow.

**Deployment vs organization boundary (normative):**

| Layer | Authority | Sprint 6.8 role |
|---|---|---|
| **Deployment configuration** | `app/core/config/` + `.env` | **Input** for default resolution; **read-only** in this sprint |
| **Organization identity** | `organizations` table + `OrganizationService` | **Input**; existing PATCH endpoints unchanged |
| **Organization business settings** | Organization Settings Document (new) | **Output** of Settings Service; persisted per org |

**AI Freeze boundary (normative):** Org-level **AI Configuration** may supply **feature enablement and behavior selection** (e.g., `ai_recommendations_enabled`) that `AiRecommendationService` reads at composition time. Org-level **Localization** may supply **Prompt Language** for prompt composition — a presentation preference, not deployment AI infrastructure. Org settings **must not** override frozen deployment values: `OLLAMA_MODEL`, `OLLAMA_URL`, `AI_TIMEOUT`, thinking mode, `PROMPT_VERSION`, or any frozen `app/ai/` internal behavior. Sprint 6.8 **must not modify** frozen AI modules (`AI_FREEZE.md`).

**Notification preferences boundary (normative):** **Platform Default Notification Preferences** are **organization-level defaults only**. They govern org-wide notification materialization gates in v1. They **do not replace** future **user-level notification preferences** (Sprint 6.7 E-12). When user-level preferences are introduced in a future sprint, they must compose atop — not be superseded by — org defaults.

---

## 1. Sprint Goal

Sprint 6.8 delivers the **first organization-scoped settings path** from persisted configuration to existing service behavior:

> **Organization + Existing Configuration + Platform Default Configuration → Settings Service → Persisted Configuration (Organization Settings Document) → Consumed by Existing Services — with deterministic resolution and zero AI or Business Engine execution.**

After this sprint:

- Each organization has a **persisted, retrievable settings bundle** with six logical sections: Organization Settings, Localization, AI Configuration, Analysis Configuration, Report Preferences, Platform Default Notification Preferences.
- **Resolved Configuration** is **deterministic**: identical org identity + persisted settings + platform defaults always produce identical effective values.
- **Existing services** consult resolved settings at defined decision points (gates, templates, section inclusion, notification kind enablement) — Settings Service never initiates downstream work.
- **Organization identity CRUD** (`name`, `platform_name`, `executive_title`) remains on `OrganizationService`; settings add operational configuration without duplicating identity ownership.
- **No AI module is invoked** by Settings Service (`AI_FREEZE.md`).
- **No Business Engine is executed** by Settings Service (ADR-009).

Sprint 6.8 does **not** deliver frontend settings UI, user-level preference overrides, deployment secret management, or settings-driven workflow automation.

---

## 2. Business Objective

### Capability unlocked

Platform operators and org administrators gain **centralized, auditable configuration** for how Khazina behaves per organization — without embedding preferences in code or environment files:

| Before Sprint 6.8 | After Sprint 6.8 |
|---|---|
| Behavior hardcoded in services or deployment env only | **Org-scoped settings** persisted and API-accessible |
| `AiRecommendationService` uses deployment `DEFAULT_PROMPT_LANGUAGE` only | Org **Localization** can prefer prompt and report languages; deployment remains fallback |
| Report Builder always includes optional sections when data exists | **Report Preferences** control default section inclusion |
| Sprint 6.7 notifications always materialize for all Platform Event kinds | **Platform Default Notification Preferences** allow org-level kind enablement |
| Discovery notes *“Settings/Configuration — Not present”* | Backend **settings APIs** operational for Phase 7 UI consumption |
| No single settings resolution authority | **Settings Service** owns merge, validation, and persistence |

### Executive value

| Stakeholder need | Sprint 6.8 response |
|---|---|
| Consistent org branding in outputs | Organization Settings + existing `platform_name` / `executive_title` inform templates |
| Control AI feature availability per org | AI Configuration enablement gates without unfreezing AI or exposing deployment config |
| Consistent localized outputs per org | Localization section for prompt and report language preferences |
| Tune analysis/report/notification behavior without code deploy | Persisted preferences consumed by existing services |
| Predictable, auditable configuration | Deterministic resolution; settings changes do not execute engines |
| Phase 7 settings page readiness | Stable org-scoped GET/PATCH settings contract |

### Alignment with discovery

`BUSINESS_DOMAIN_DISCOVERY.md` explicitly lists **Settings/Configuration** as absent from the frontend and distinguishes **Organization Context** (implicit) from **Organization Management** (not represented). Sprint 6.8 establishes the **backend configuration layer** that Phase 7 Organization Management and Settings UI will consume — without frontend work in this sprint.

---

## 3. Scope

### 3.1 INCLUDED (strict)

| ID | Item | Repository basis |
|---|---|---|
| I-01 | **Settings Service** (suggested: `app/settings/`) | Mirrors terminal-domain module pattern (`app/reports/`, `app/notifications/`) — configuration authority only |
| I-02 | **Organization Settings Document** persistence | One document per organization; Gap Discovery if schema insufficient |
| I-03 | **Platform Default Configuration registry** | Code-defined defaults merged with persisted org overrides |
| I-04 | **Deterministic resolution** — `platform_defaults ⊕ persisted_org_settings → Resolved Configuration` | Same inputs → same outputs; no randomness, no AI |
| I-05 | **Organization Settings section** | Operational prefs (see §5.1) |
| I-06 | **Localization section** | Prompt Language and Report Language (see §5.2) |
| I-07 | **AI Configuration section** | Feature enablement and behavior selection only (see §5.3) |
| I-08 | **Analysis Configuration section** | Analysis lifecycle preferences (see §5.4) |
| I-09 | **Report Preferences section** | Report Builder / catalog behavior prefs (see §5.5) |
| I-10 | **Platform Default Notification Preferences section** | Org-level Platform Event kind enablement (see §5.6) |
| I-11 | **Settings validation** | Schema validation, enum bounds, fail-closed on invalid patches |
| I-12 | **Org-scoped settings API** | Nested under `/api/v1/organizations/{organization_id}/settings` per `ARCHITECTURE.md` |
| I-13 | **Consumer integration (read-only)** | Minimal settings reads in existing services at defined decision points (§6.3) |
| I-14 | **Permissions** | Read: org analyst minimum; write: org admin (`app/api/permissions.py` patterns) |
| I-15 | **Tests** | Resolution determinism, validation, consumer gate behavior, isolation from AI/engines |
| I-16 | **Lazy initialization** | First read creates persisted document from platform defaults if absent |

### 3.2 EXCLUDED (strict)

| ID | Item | Rationale |
|---|---|---|
| E-01 | **Frontend settings UI** | Phase 7; `FRONTEND_SPECIFICATION.md` has no settings page |
| E-02 | **User-level notification preferences** | Sprint 6.7 E-12 deferred; Platform Default Notification Preferences are org-level defaults only and do not replace future user-level prefs |
| E-03 | **Role/department/watcher recipient settings** | Sprint 6.7 E-15 architecture allowance only |
| E-04 | **Deployment secret or infrastructure mutation** | `JWT`, `DATABASE_URL`, `OLLAMA_*` remain env-only |
| E-05 | **Org override of frozen AI infrastructure** | `OLLAMA_MODEL`, `OLLAMA_URL`, `AI_TIMEOUT`, thinking mode — `AI_FREEZE.md` |
| E-06 | **Modification of frozen `app/ai/` modules** | AI Freeze |
| E-07 | **Business Engine parameter tuning that alters engine output** | Engines frozen; settings must not embed calculation rules |
| E-08 | **Settings-triggered workflows** | Settings do not invoke analysis, AI, reports, or notifications |
| E-09 | **Financial Snapshot / Decision Engine configuration** | No engine execution; engine inputs remain workflow-owned |
| E-10 | **Email/push/SMS channel configuration** | Sprint 6.7 excluded delivery channels |
| E-11 | **Report binary export preferences** | Sprint 6.6 `report_exports` deferred |
| E-12 | **Preemptive architectural contract documents** | Gap Discovery only when needed |
| E-13 | **Multi-organization switching UI** | Organization Management frontend absent |
| E-14 | **Audit log for settings changes** | Future ops sprint |
| E-15 | **Moving `platform_name` / `executive_title` off `organizations` table** | Existing `OrganizationService` ownership preserved |

**Explicit non-deliverables:** Preemptive storage contract documents, AI pipeline changes, Business Engine changes, settings admin UI, user preference store, workflow schedulers driven by settings.

---

## 4. Inputs

### 4.1 Organization

| Input | Source | Role in resolution |
|---|---|---|
| `organization_id` | Path parameter / service context | Scope key for all settings |
| `name` | `organizations.name` | Display enrichment in templates (read-only input) |
| `platform_name` | `organizations.platform_name` (default `"خزينة"`) | Branding input for report/notification templates |
| `executive_title` | `organizations.executive_title` | Display input for executive-facing outputs |
| `is_active` | `organizations.is_active` | Settings reads fail closed for inactive orgs |

**Repository evidence:** `backend/app/db/models/organization.py`; `OrganizationService` (`backend/app/services/organization.py`); `OrganizationResponse` (`backend/app/schemas/organization.py`).

### 4.2 Existing configuration

| Input | Source | Role in resolution |
|---|---|---|
| Persisted Organization Settings Document | Settings store (implementation-defined) | Org overrides atop platform defaults |
| Partial/absent document | First access | Triggers lazy init from platform defaults (I-16) |

If no persisted document exists, resolution uses **platform defaults only** until first PATCH or explicit init on read.

### 4.3 Default platform configuration

| Input | Source | Role in resolution |
|---|---|---|
| `default_prompt_language` | `AiSettings` / `DEFAULT_PROMPT_LANGUAGE` (default `ar`) | Fallback for Localization **Prompt Language** |
| `AppSettings`, `AuthSettings`, `DatabaseSettings`, etc. | `app/core/config/` | Deployment context; **not exposed** for org override in v1 |
| Code-defined settings defaults | Settings Service constants | Authoritative v1 defaults for all six sections when org has no override |

**Repository evidence:** `backend/app/core/config/ai.py`; `ARCHITECTURE.md` §Configuration; `AI_FREEZE.md` §2 Production Configuration.

**Normative rule:** Platform defaults are **read at resolution time** from the Settings Service default registry and deployment `AiSettings` where explicitly referenced (prompt language fallback only). Settings Service **does not write** to `app/core/config/` or `.env`.

---

## 5. Outputs

### 5.0 Organization Settings Document (container)

The **Organization Settings Document** is the persisted, org-scoped configuration bundle containing exactly six logical sections. It is the unit of storage, retrieval, and PATCH semantics.

**Resolution output:** Every GET returns a **Resolved Configuration** object containing all six sections with **effective values** (defaults merged with persisted overrides).

Storage encoding, location, and schema versioning mechanics are **implementation-defined**. If the approved schema cannot hold the document, apply Gap Discovery Protocol (§12) — do not prescribe storage form in this specification.

### 5.1 Organization Settings

Operational preferences beyond core identity CRUD.

| Field (conceptual) | Type | Default (v1) | Consumer |
|---|---|---|---|
| `locale` | string (BCP-47 style, e.g. `ar`, `en`) | `ar` | Template formatters in Report Builder, Notification Builder |
| `date_display_format` | enum: `gregorian`, `hijri` | `gregorian` | Report Content Representation date labels |
| `currency_display_code` | string (ISO 4217, e.g. `SAR`) | `SAR` | Report section formatters |

**Note:** `platform_name` and `executive_title` remain on the `organizations` row. Resolved Configuration **includes** them in an `organization_identity` projection for consumer convenience (read from `OrganizationService`, not duplicated in settings store).

### 5.2 Localization

Org-level **language preferences** for prompt and report output — distinct from deployment AI infrastructure and from general org display locale (§5.1).

| Field (conceptual) | Type | Default (v1) | Consumer |
|---|---|---|---|
| `prompt_language` | string \| null | `null` (use deployment fallback) | `AiRecommendationService` composition — passed to `AiTaskPipeline` when non-null; else `settings.ai.default_prompt_language` |
| `report_language` | string \| null | `null` (use `prompt_language`, then deployment fallback) | `ReportBuilderService` — section headings, labels, and narrative framing in Report Content Representation |

**Resolution order for `report_language`:** persisted org value → org `prompt_language` → deployment `DEFAULT_PROMPT_LANGUAGE` → platform default (`ar`).

**Normative rule:** Localization fields are **presentation preferences only**. They do not select models, alter timeouts, or modify frozen `app/ai/` behavior.

**Repository evidence:** `AiRecommendationService` currently reads `settings.ai.default_prompt_language` at init (`backend/app/ai_recommendations/service.py`); Sprint 6.8 adds **org Localization read** at invocation time — without modifying frozen AI modules.

### 5.3 AI Configuration

Org-level **feature enablement and behavior selection** — not deployment configuration, not model selection, not runtime AI tuning.

| Field (conceptual) | Type | Default (v1) | Consumer |
|---|---|---|---|
| `ai_recommendations_enabled` | boolean | `true` | `AiRecommendationService` — fail closed with domain error when `false` |
| `waste_recommendations_auto_suggest` | boolean | `true` | API response metadata only in v1; **does not** auto-invoke AI |

**Explicitly forbidden in AI Configuration (AI Freeze):** `ollama_model`, `ollama_url`, `ai_timeout`, `thinking_enabled`, `prompt_version`, `prompt_language`, `report_language`, task registry changes, model selection, runtime AI tuning, or any field that modifies frozen `app/ai/` behavior or deployment configuration.

**Repository evidence:** `AiRecommendationService` reads `settings.ai.ollama_model` at init from deployment config (`backend/app/ai_recommendations/service.py`); Sprint 6.8 adds **org enablement gate read** at invocation time only — without modifying frozen AI modules.

### 5.4 Analysis Configuration

| Field (conceptual) | Type | Default (v1) | Consumer |
|---|---|---|---|
| `enabled_analysis_types` | set of `AnalysisType` | `{financial_waste, simulation}` | Analysis creation endpoints — reject disabled types |
| `timeline_on_completion_enabled` | boolean | `true` | `AnalysisService.complete_run` — skip timeline append when `false` |
| `default_analysis_title_template` | string | `"{analysis_type} — {reporting_period_label}"` | Analysis run creation default title |
| `require_ai_insights_before_report` | boolean | `false` | `ReportBuilderService` — optional precondition when generating reports for waste runs |

**Normative rule:** `enabled_analysis_types` gates **whether new runs may be created** — it does not delete existing runs or invoke engines retroactively.

### 5.5 Report Preferences

| Field (conceptual) | Type | Default (v1) | Consumer |
|---|---|---|---|
| `default_report_title_template` | string | `"Executive Report — {analysis_type}"` | `ReportBuilderService.generate_report` when title not supplied |
| `auto_publish_on_generate` | boolean | `false` | Composition after `ReportBuilderService` — call existing `ReportService.publish_report` when `true` |
| `include_ai_sections_when_available` | boolean | `true` | Report Builder section assembly for waste reports |
| `include_recommendations_section` | boolean | `true` | Report Builder section assembly |
| `include_scenario_provenance_section` | boolean | `true` | Report Builder section assembly for simulation reports |

**Repository evidence:** `ReportBuilderService` (`backend/app/reports/service.py`); `ReportService.publish_report` (`backend/app/services/report.py`); Sprint 6.6 Report Content Representation sections.

### 5.6 Platform Default Notification Preferences

**Platform Default Notification Preferences** are **organization-level defaults only** for Sprint 6.7 Platform Event materialization. They establish the org-wide baseline for which notification kinds are enabled in v1.

| Field (conceptual) | Type | Default (v1) | Consumer |
|---|---|---|---|
| `notifications_enabled` | boolean | `true` | `NotificationBuilder` master gate |
| `enabled_notification_kinds` | set of kind strings | All Sprint 6.7 v1 kinds | `NotificationBuilder` per-kind gate |

**Sprint 6.7 v1 kind strings (repository authority):** `analysis_completed`, `scenario_completed`, `ai_recommendations_completed`, `report_generated`, `report_published`.

When `notifications_enabled` is `false`, no notifications materialize regardless of per-kind flags. When a kind is absent from `enabled_notification_kinds`, that kind is skipped; upstream domain work still completes.

**Future user-level preferences (normative):** Sprint 6.7 E-12 (user-configurable notification preferences) remains **excluded** from Sprint 6.8. Platform Default Notification Preferences **do not replace** future user-level notification preferences. When user-level preferences are introduced, they must compose atop these org defaults — org defaults remain the platform baseline; user prefs refine delivery per authenticated user.

---

## 6. Processing Flow

### 6.1 Normative pipeline

```
Organization (identity + scope)
        ↓
Settings Service
  • load platform defaults
  • load persisted Organization Settings Document (or lazy-init)
  • merge deterministically
  • validate
        ↓
Persisted Configuration (Organization Settings Document)
        ↓
Consumed by Existing Services (read-only at decision points)

(No AI execution)
(No Business Engine execution)
```

### 6.2 Settings Service responsibilities

| Step | Action | Constraint |
|---|---|---|
| 1 | Resolve `organization_id`; verify org exists and is active | Fail closed |
| 2 | Load platform default registry | Read-only |
| 3 | Load persisted document or initialize from defaults | Deterministic |
| 4 | Deep-merge PATCH payload (section-scoped partial updates) | Validated fields only |
| 5 | Validate merged document against schema and business bounds | No engine/AI calls |
| 6 | Persist document | Atomic per org |
| 7 | Return Resolved Configuration | Includes effective values + `organization_identity` projection |

**Settings Service must not:** import LLM clients, call `get_engine()`, invoke `AnalysisService.complete_run`, `AiRecommendationService.generate_*`, `ReportBuilderService.generate_report`, or `NotificationBuilder` materialization.

### 6.3 Consumer integration map (read-only)

| Consumer | Settings sections | Decision point (conceptual) |
|---|---|---|
| `AnalysisService` | Analysis Configuration, Platform Default Notification Preferences (indirect via hooks) | `create_run` (enabled types, title template); `complete_run` (timeline gate) |
| `AiRecommendationService` | AI Configuration, Localization | `generate_waste_recommendations` preflight (enabled gate); pipeline invocation (`prompt_language`) |
| `ReportBuilderService` | Report Preferences, Analysis Configuration, Localization | `generate_report` (title, sections, `report_language`, optional AI precondition) |
| `ReportService` | Report Preferences | Post-generate composition (`auto_publish_on_generate`) |
| `NotificationBuilder` | Platform Default Notification Preferences | Pre-materialization gate per Platform Event kind |
| `OrganizationService` | — | Unchanged; identity fields remain separate |

**Composition discipline:** Consumer services receive resolved settings via dependency injection or a thin `SettingsResolver` callable — **not** by Settings Service calling consumers. Auto-publish and notification gating are **composition hooks** in existing orchestration paths (same pattern as Sprint 6.6/6.7 timeline and notification hooks).

### 6.4 PATCH semantics

- PATCH accepts **partial** updates per section.
- Unspecified fields retain prior effective values.
- `null` on nullable Localization fields (e.g. `prompt_language`, `report_language`) means **revert to resolution fallback chain** (§5.2).
- Invalid enum values or forbidden AI infrastructure keys → `422` validation error; no partial persist.

---

## 7. Deliverables

| ID | Deliverable | Notes |
|---|---|---|
| D-01 | **This specification** | Approved by Technical Lead before implementation |
| D-02 | **Settings module** | Suggested `backend/app/settings/` — defaults registry, resolver, validator |
| D-03 | **Settings Service** | `get_resolved_settings`, `get_document`, `patch_settings`, lazy init |
| D-04 | **Organization Settings Document persistence** | Implementation-defined; Gap Discovery if needed |
| D-05 | **API schemas** | Request/response models for Resolved Configuration and PATCH body |
| D-06 | **REST endpoints** | `GET` and `PATCH` `/organizations/{organization_id}/settings` |
| D-07 | **Router registration** | `app/api/v1/` org-scoped router; deps wiring |
| D-08 | **Consumer integration** | Read-only gates in services per §6.3 |
| D-09 | **Test suite** | `backend/tests/settings/` — resolution, validation, isolation, consumer gates |
| D-10 | **`progress.md` update** | On sprint completion only |

---

## 8. Acceptance Criteria

### 8.1 Persistence and resolution

| ID | Criterion |
|---|---|
| AC-01 | Each organization has at most one Organization Settings Document |
| AC-02 | First GET for org without document returns Resolved Configuration equal to platform defaults |
| AC-03 | Identical org identity + persisted settings → identical Resolved Configuration |
| AC-04 | PATCH persists only validated changes; rejected patches do not mutate store |
| AC-05 | Resolved Configuration includes all six sections plus `organization_identity` projection |
| AC-06 | Inactive organization settings access fails closed |

### 8.2 Localization and AI Configuration boundary

| ID | Criterion |
|---|---|
| AC-07 | `ai_recommendations_enabled = false` prevents `AiRecommendationService` LLM invocation (fail closed) |
| AC-08 | Org Localization `prompt_language` overrides deployment fallback when set; `null` uses `settings.ai.default_prompt_language` |
| AC-09 | Org Localization `report_language` resolves per §5.2 fallback chain and is consumed by Report Builder |
| AC-10 | PATCH rejects `ollama_model`, `ollama_url`, `ai_timeout`, or any forbidden AI infrastructure field in any section |
| AC-11 | AI Configuration contains **only** feature enablement and behavior selection — no language, model, or deployment fields |
| AC-12 | Settings Service and tests do not import frozen `app/ai/` LLM execution paths |

### 8.3 Analysis, report, and notification consumption

| ID | Criterion |
|---|---|
| AC-13 | Disabled `AnalysisType` cannot be used to create new analysis runs |
| AC-14 | `timeline_on_completion_enabled = false` skips timeline append on `complete_run` without failing completion |
| AC-15 | Report Builder respects `include_*` section flags when assembling Report Content Representation |
| AC-16 | `auto_publish_on_generate = true` publishes report via existing `ReportService.publish_report` after successful generation |
| AC-17 | Platform Default Notification Preferences: `notifications_enabled = false` or disabled kind prevents Notification Builder materialization for that kind |
| AC-18 | Upstream domain operations succeed even when Platform Default Notification Preferences disable notifications |
| AC-19 | Platform Default Notification Preferences are org-level defaults only — no user-level preference store in Sprint 6.8 |

### 8.4 Isolation and determinism

| ID | Criterion |
|---|---|
| AC-20 | Settings Service does not invoke Business Engines or AI |
| AC-21 | Settings changes do not trigger analysis, AI, report generation, or notifications |
| AC-22 | Settings PATCH does not modify `organizations` identity columns (except via existing Organization API) |
| AC-23 | Settings resolution is free of randomness, wall-clock dependency, and LLM calls |

### 8.5 API and permissions

| ID | Criterion |
|---|---|
| AC-24 | Org analyst can GET resolved settings |
| AC-25 | Org admin can PATCH settings; non-admin PATCH rejected |
| AC-26 | Cross-org settings access rejected by existing org permission model |

### 8.6 Regression

| ID | Criterion |
|---|---|
| AC-27 | Sprint 6.3–6.7 tests remain green with default settings (no behavior change when defaults apply) |
| AC-28 | Full test suite passes after Sprint 6.8 completion |

### 8.7 Documentation

| ID | Criterion |
|---|---|
| AC-29 | This specification marked **Approved for Implementation** with TL sign-off |
| AC-30 | `progress.md` updated on sprint completion |

---

## 9. Technical Risks

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R-01 | **No settings schema in approved design** | Cannot persist Organization Settings Document | Gap Discovery Protocol — document single gap, TL review before migration |
| R-02 | **Settings vs deployment config confusion** | Org overrides frozen AI infrastructure | Localization vs AI Configuration split (§5.2/§5.3); forbidden fields; AC-10/AC-11; AI Freeze boundary in terminology |
| R-03 | **Consumer sprawl** | Every service reads settings ad hoc | Central `SettingsResolver`; documented decision-point map (§6.3) |
| R-04 | **Behavior regression on defaults** | Existing workflows change silently | Defaults must mirror current hardcoded behavior; AC-27 |
| R-05 | **Settings perform business logic** | ADR violation | AC-20/21; Settings Service isolation tests |
| R-06 | **Duplicate org identity ownership** | `platform_name` drift between tables | E-15; identity stays on `organizations`; projection read-only |
| R-07 | **Auto-publish transaction coupling** | Report generation fails if publish fails | Composition hook: generation commit wins; publish failure surfaces separately (Sprint 6.6 publish semantics) |
| R-08 | **Platform Default Notification Preferences vs Sprint 6.7 idempotency** | Skipped notifications confuse tests | Document that disabled kinds produce **no** notification record; upstream unchanged |
| R-09 | **Frozen module modification pressure** | AI/Engine freeze breach | Consumer reads only; no `app/ai/` edits |
| R-10 | **Invalid partial PATCH** | Corrupt document | Section-scoped validation before persist; atomic write |
| R-11 | **Sprint 6.7 not yet in repository** | Platform Default Notification Preferences consumer missing | Soft dependency; gate code guarded; notification tests skip if module absent until 6.7 lands |
| R-12 | **Org vs user notification preference confusion** | Future E-12 blocked or duplicated | §5.6 normative rule: org defaults are baseline; user prefs compose atop in future sprint |

---

## 10. Dependencies

### 10.1 Hard dependencies (must be complete)

| Dependency | Status | Reference |
|---|---|---|
| Sprint 6.3 Decision Engine + `AnalysisService` | ✅ Complete | `progress.md` Sprint 6.3 |
| Sprint 6.4 AI Recommendations | ✅ Complete | `progress.md` Sprint 6.4 |
| Sprint 6.5 Scenario Analysis | ✅ Complete | `progress.md` Sprint 6.5 |
| Sprint 6.6 Reports + `ReportBuilderService` | ✅ Complete | `progress.md` Sprint 6.6 |
| Sprint 6.7 Notifications (spec approved) | ✅ Approved | `SPRINT_6.7_SPECIFICATION.md` |
| Phase 4 User System + org permissions | ✅ Complete | `ARCHITECTURE.md` Phase 4 |
| `OrganizationService` + `organizations` model | ✅ Exists | `backend/app/services/organization.py` |
| Deployment config (`app/core/config/`) | ✅ Exists | `ARCHITECTURE.md` |

### 10.2 Soft dependencies

| Dependency | Notes |
|---|---|
| `NotificationBuilder` implementation | Platform Default Notification Preferences consumer; org-level gates meaningful when 6.7 code present |
| Sprint 6.7 Platform Event kind registry | Kind strings in §5.6 must stay aligned |
| `AnalysisType` enum | `enabled_analysis_types` validation |

### 10.3 Downstream consumers (not Sprint 6.8 blockers)

| Consumer | Relationship |
|---|---|
| Frontend Settings / Organization Management page | Phase 7 |
| User-level notification preferences | Future (Sprint 6.7 E-12) — compose atop Platform Default Notification Preferences |
| Settings change audit log | Future ops sprint |
| Per-user locale overrides | Future |

---

## 11. Implementation Order

### Step 1 — Specification approval ✅

- This document approved (Technical Lead sign-off 2026-07-15).
- **No additional contract gates** — implementation may proceed directly.
- Resolve R-01 via Gap Discovery if settings persistence absent from approved schema.

### Step 2 — Defaults registry and document schema

- Define platform default values for all six sections (code constants).
- Define validation rules and forbidden AI infrastructure keys.
- Define Resolved Configuration and PATCH schema shapes.

### Step 3 — Organization Settings Document persistence

- Persist one document per organization (implementation-defined).
- Lazy initialization on first read.

### Step 4 — Settings Service

- Deterministic merge resolver.
- `get_resolved_settings`, `patch_settings`.
- Fail-closed validation.

### Step 5 — API layer

- GET/PATCH endpoints under org scope.
- Permissions: analyst read, admin write.
- Register router and dependency injection.

### Step 6 — Consumer integration (read-only)

- Wire decision-point reads per §6.3.
- Preserve default behavior when settings are unset.
- Auto-publish composition hook (optional, behind `auto_publish_on_generate`).

### Step 7 — Tests and regression

- Resolution determinism, AI freeze boundary, consumer gates, permissions, isolation.
- Full suite green; update `progress.md`.

---

## 12. Technical Lead Recommendation

### Recommendation: **APPROVED FOR IMPLEMENTATION**

| Factor | Assessment |
|---|---|
| **Architectural fit** | Closes Discovery settings gap without unfreezing AI or Business Engines |
| **Correct boundary** | Configuration-only; existing services remain execution owners |
| **Pattern reuse** | Org-scoped service module, composition consumer reads, Gap Discovery for persistence |
| **AI Freeze compliance** | AI Configuration limited to enablement/behavior; Localization holds language prefs; infrastructure stays env-bound |
| **Determinism** | Explicit merge semantics; no AI or engine calls in settings path |
| **Sprint continuity** | Natural home for Sprint 6.7-deferred Platform Default Notification Preferences |
| **Known schema gap** | R-01 expected — resolve at implementation via Gap Discovery |

### TL adjustments applied (2026-07-15)

1. **Platform Default Notification Preferences** — organization-level defaults only; do not replace future user-level notification preferences (E-12).
2. **Localization section** — `prompt_language` and `report_language` moved out of AI Configuration; AI Configuration limited to feature enablement and behavior selection only.

### Conditions for implementation start

1. **This specification approved** — ✅ TL sign-off recorded (2026-07-15).
2. **No modification** to frozen `app/ai/` internals or Business Engine implementations.
3. **No AI or Business Engine work** in Sprint 6.8 — settings are configuration only.
4. **No preemptive mapping contract documents** — field rules live in code and tests.
5. **Gap Discovery Protocol** — if Organization Settings Document cannot persist within approved schema, document the **single gap** and obtain TL approval before proceeding.
6. **Defaults preserve current behavior** — out-of-box resolved settings must not change existing Sprint 6.3–6.7 workflows.
7. **Forbidden AI infrastructure keys** — PATCH must reject org attempts to override `OLLAMA_*`, timeouts, thinking mode, or place language/model fields in AI Configuration.

### Suggested next sprint after 6.8

Frontend Organization Management and Settings page (Phase 7), user-level notification preferences (Sprint 6.7 E-12), or binary report export — each requires separate sprint approval.

---

## Document Control

| Field | Value |
|---|---|
| **Version** | 1.1 |
| **Author** | Platform specification (Sprint 6.8) |
| **Review status** | **Approved for Implementation** — TL sign-off 2026-07-15 |
| **Implementation authorized** | Yes |
| **Supersedes** | v1.0 (draft) |
