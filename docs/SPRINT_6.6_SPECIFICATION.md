# Sprint 6.6 — Reports

**Phase:** 6 — Business Features  
**Predecessor:** Sprint 6.5 — Scenario Analysis — **Complete and approved**  
**Status:** **APPROVED FOR IMPLEMENTATION** (Technical Lead review, 2026-07-15)  
**Date:** 2026-07-15  

**TL adjustments applied (2026-07-15):**

1. **“Content artifact” replaced with “Report Content Representation”** — the specification defines the concept only. Storage encoding, location, and retrieval mechanics are **implementation-defined**. The spec must not imply a new table, JSON document, blob, or file as the storage form.
2. **Implementation may proceed directly** upon this specification approval — no additional contract gates.
3. **Gap discovery protocol** — if implementation discovers that the approved schema cannot accommodate the full Report Content Representation, document that **single gap** and stop for Technical Lead review. Do not create preemptive contracts or prescribe storage forms in advance.

**Normative references (frozen — must not be modified in this sprint):**

- [ADR 008: AI Architecture](ADR/008-ai-architecture.md)
- [ADR 009: Business Engine Architecture](ADR/009-business-engine-architecture.md)
- [ADR 010: Financial Snapshot Architecture](ADR/010-financial-snapshot-architecture.md)
- [AI_FREEZE.md](AI_FREEZE.md)
- [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)
- [BUSINESS_ENGINE_ARCHITECTURE.md](BUSINESS_ENGINE_ARCHITECTURE.md)
- [SPRINT_6.2_SPECIFICATION.md](SPRINT_6.2_SPECIFICATION.md) — §11 Financial Snapshot Contract
- [SPRINT_6.3_SPECIFICATION.md](SPRINT_6.3_SPECIFICATION.md) — Decision Engine; Facts Contract; Gold persistence pattern
- [SPRINT_6.4_SPECIFICATION.md](SPRINT_6.4_SPECIFICATION.md) — AI Insights artifact shape; recommendation registry mapping discipline (read-only consumption)
- [SPRINT_6.5_SPECIFICATION.md](SPRINT_6.5_SPECIFICATION.md) — Scenario Gold persistence; `scenario_provenance`; deterministic mapper discipline
- [DATABASE_SCHEMA_DESIGN.md](DATABASE_SCHEMA_DESIGN.md) — §3.8, §4.23 `reports`; §14.3 future `report_exports`; ambiguity A-01, A-05
- [BUSINESS_DOMAIN_DISCOVERY.md](BUSINESS_DOMAIN_DISCOVERY.md) §5.6, §6.1 Flow 5, §6.2
- [FRONTEND_SPECIFICATION.md](FRONTEND_SPECIFICATION.md) — Page 5 Reports (Phase 7/8 consumer)

**Tracker alignment:** `progress.md` (post–Sprint 6.5): *“Next step: Frontend Business Simulation wiring (Phase 7), simulation-domain AI (`SCENARIO_ANALYSIS`), or Financial Engine — separate sprint approval required.”* Sprint 6.6 addresses the **report generation gap** identified across discovery, schema design, and the existing `ReportService` docstring: *“Content generation is out of scope; this service manages the catalog workflow.”*

**TL pattern expectation (consistent with Sprint 6.5):** Sprint 6.6 reuses established architectural patterns (ADR-010, Facts Contract, deterministic output-mapping discipline, analysis-vs-report boundary) instead of introducing preemptive mapping contract documents. Gap discovery protocol applies if implementation finds a genuine architectural gap — including inability to persist the full Report Content Representation within approved schema constraints.

---

## Terminology Mapping (Repository Authority)

| Sprint 6.6 term | Repository authority | Meaning |
|---|---|---|
| **Executive Report** | *Sprint 6.6 product name* | Deterministic, versioned document assembled from persisted platform artifacts for executive review |
| **Report Builder** | *Sprint 6.6 orchestration name* | Read-only aggregation service that maps Analysis Run + linked artifacts → structured report sections — **without AI or Business Engine execution** |
| **Report catalog row** | `reports` — `backend/app/db/models/reporting.py` | Published or draft report metadata (`title`, `report_type`, `status`, `summary`, FK links) managed by existing `ReportService` |
| **Decision Results** | Sprint 6.3 Gold output | Completed `analysis_runs` (`analysis_type = financial_waste`) + `waste_analysis_results` + breakdowns + optional `runtime_metadata.facts_contract` |
| **AI Insights** | Sprint 6.4 artifact | Run-scoped `runtime_metadata.ai_insights` (executive summary, risk explanation, narrative bundle) — **consumed read-only; never regenerated** |
| **Recommendations** | `recommendations` table | Registry rows linked via `analysis_run_id` (Sprint 6.4 waste domain in v1) |
| **Scenario Results** | Sprint 6.5 Gold output | Completed `analysis_runs` (`analysis_type = simulation`) + `simulation_runs` + result child tables + `runtime_metadata.scenario_provenance` |
| **Financial Facts** | `FactsContract` — `backend/app/business/facts/contract.py` | Versioned deterministic engine output rehydrated from `runtime_metadata.facts_contract` — **read-only in this sprint** |
| **Report Content Representation** | *Sprint 6.6 concept* | The complete, immutable, point-in-time structural rendering of an Executive Report (ordered sections + extended metadata) bound to a catalog row at generation time. Defines **what** is stored — not **how**. Storage form is **implementation-defined** (see §5.1.1) |
| **Exportable Report** | *Sprint 6.6 concept* | Deterministic, retrievable serialization of the Report Content Representation suitable for API delivery and future PDF/Excel export (A-05 deferred). Wire format is **implementation-defined**; must be stable and testable |

**Critical constraint:** Reporting is a **terminal consumer** domain (Discovery §6.2). Sprint 6.6 **does not invoke AI**, **does not dispatch Business Engines**, and **does not mutate** Financial Snapshots, analysis runs, Gold result tables, or recommendation rows.

**Existing service boundary:** `ReportService` (`backend/app/services/report.py`) already owns draft/create, list/filter, publish, and timeline integration. Sprint 6.6 adds **deterministic content generation and structured section assembly** — it must **compose** existing catalog APIs, not redesign publication semantics.

---

## 1. Sprint Goal

Sprint 6.6 delivers the **first end-to-end deterministic executive report path** from persisted analysis artifacts to catalog-ready reports:

> **Analysis Run + Facts Contract + AI Insights (optional) + Recommendations (optional) + Scenario Results (when applicable) → Report Builder → Executive Report (structured sections + export payload) — with full provenance and zero AI or Business Engine execution.**

After this sprint:

- A completed **waste Decision Result** (`financial_waste` run) can produce an **`analysis`-type executive report** that presents Gold metrics, persisted Facts, optional AI narratives, and linked recommendations.
- A completed **Scenario Result** (`simulation` run) can produce a **`simulation`-type executive report** that presents forecast summary, delta metrics, impact items, action items, and scenario provenance — optionally enriched from a linked baseline waste run referenced in `scenario_provenance.baseline_analysis_run_id`.
- Report generation is **deterministic**: identical persisted inputs produce identical section payloads and export serialization.
- Reports are stored in the existing **`reports` catalog** (`draft` → optional `ready` via existing publish workflow) with **`analysis_run_id` provenance**.
- **No AI module is invoked** (`AI_FREEZE.md`).
- **No Business Engine is executed** (ADR-009; Waste and Scenario engines remain frozen consumers-only).

Sprint 6.6 does **not** deliver frontend wiring, binary export (PDF/Excel/PowerPoint), risk/procurement/compliance report profiles, report-scheduling, or Number Guard hardening.

---

## 2. Business Objective

### Capability unlocked

Executives gain **board-ready, reproducible reports** that consolidate prior analytical work without re-running engines or AI:

| Before Sprint 6.6 | After Sprint 6.6 |
|---|---|
| `ReportService` manages **caller-supplied** title/summary drafts only | Report Builder **generates** structured content from completed analysis runs |
| Reports page uses **static placeholder data** (`frontend/lib/placeholder-data.ts`) | Backend produces **real report rows** with deterministic section payloads retrievable via API |
| Analysis, AI, and scenario outputs exist **in isolation** | Outputs are **composed** into a single Executive Report with a persisted Report Content Representation |
| Export buttons are UI placeholders (FRONTEND_SPEC §Page 5) | Backend exposes **deterministic export** of the frozen Report Content Representation (binary formats deferred per A-05) |
| Discovery Flow 5 (*“Reports generated from prior analyses”*) is **unimplemented** | Flow 5 is **operational at the API/catalog layer** |

### Executive value

| Stakeholder need | Sprint 6.6 response |
|---|---|
| Single report for board preparation | One Executive Report per generation request, sectioned and provenance-complete |
| Trust in numbers | Facts and Gold metrics copied from persisted artifacts — no recalculation |
| Auditability | Report metadata records source run ids, engine/facts versions, snapshot binding, AI artifact timestamps (when present) |
| Separation of analysis vs publication | Analysis can complete without a report; report references run optionally (schema decision #5) |

---

## 3. Scope

### 3.1 INCLUDED (strict)

| ID | Item | Repository basis |
|---|---|---|
| I-01 | **Report Builder orchestration module** (suggested: `app/reports/`) | New; mirrors `app/decision/`, `app/scenario/`, `app/ai_recommendations/` composition pattern |
| I-02 | **Generate executive report from completed analysis run** | Primary entry point bound to `analysis_runs.id` |
| I-03 | **Waste Decision Report profile** (`report_type = analysis`) | `AnalysisType.FINANCIAL_WASTE`; maps to `ReportType.ANALYSIS` per A-01 |
| I-04 | **Scenario Report profile** (`report_type = simulation`) | `AnalysisType.SIMULATION`; maps to `ReportType.SIMULATION` |
| I-05 | **Deterministic section assembly** from Facts Contract, Gold tables, `ai_insights`, recommendations, scenario child tables | Read-only repository/service reads |
| I-06 | **Optional baseline waste enrichment** for simulation reports via `scenario_provenance.baseline_analysis_run_id` | Sprint 6.5 provenance — read-only; no Waste Engine |
| I-07 | **Report Content Representation persistence** at generation time (immutable point-in-time binding of assembled sections + extended metadata to catalog row) | Storage form implementation-defined; gap discovery if approved schema is insufficient (see §5.1.1, §12) |
| I-08 | **Populate `reports.summary`** with executive-summary section text (AI insights when present; deterministic Facts/Gold fallback when absent) | `DATABASE_SCHEMA_DESIGN.md` §4.23.1 |
| I-09 | **Report metadata / provenance block** part of Report Content Representation | Engine ids, facts version, snapshot id, AI `generated_at`/`model`/`prompt_version` when consumed |
| I-10 | **Export endpoint** for frozen Report Content Representation | Extends catalog API; wire format implementation-defined; binary formats excluded (A-05) |
| I-11 | **Integration with existing catalog workflow** — generated reports start as `draft`; existing publish/delete/list APIs remain | `ReportService` composition |
| I-12 | **Organization + reporting period + department context** on report rows from run/snapshot binding | Existing FK columns on `reports` |
| I-13 | **Analysis type → report type mapping** (application layer) | Resolves ambiguity A-01 |
| I-14 | **Automated tests** — determinism, read-only isolation (no `app.ai`, no engine registry), precondition validation, section completeness | Phase 6 test patterns |
| I-15 | **`progress.md` update** | Post-implementation only |

### 3.2 EXCLUDED (strict)

| ID | Item | Reason / deferral |
|---|---|---|
| E-01 | **AI invocation, prompt composition, LLM calls, AI regeneration** | AI freeze; reports consume `runtime_metadata.ai_insights` only |
| E-02 | **Business Engine execution** (`get_engine`, `engine.run`, Waste/Scenario engines) | ADR-009; reports are terminal consumers |
| E-03 | **Modification of frozen modules** — `app/ai/`, `app/business/engines/waste/`, Facts Contract structure | Phase 5/6 freeze |
| E-04 | **Frontend Reports page wiring** | Phase 7 (`FRONTEND_SPECIFICATION.md` §Page 5) |
| E-05 | **Binary export** — PDF, Excel, PowerPoint | A-05; `report_exports` table deferred (`DATABASE_SCHEMA_DESIGN.md` §14.3) |
| E-06 | **Report scheduling, email delivery, notifications** | Discovery §5.6; FRONTEND_SPEC out of scope |
| E-07 | **Risk report profile** (`report_type = risk`) | No completed risk analysis engine path producing Gold artifacts |
| E-08 | **Procurement / compliance report profiles** | Placeholder report types only; no domain Gold artifacts |
| E-09 | **Generating recommendations from reports** | Discovery §14.3 future extension; no `report_id` on recommendations in MVP |
| E-10 | **Number Guard** | Deferred hardening sprint (Sprint 6.4 §3.3) |
| E-11 | **Monte Carlo or stochastic sections** | Non-deterministic; violates sprint goal |
| E-12 | **Re-parsing Financial Snapshot payload at report time for new metrics** | Reports use persisted Facts/Gold only — not Silver recomputation |
| E-13 | **Multi-run composite reports** (merge unrelated runs in one report) | v1 anchors on single primary `analysis_run_id`; baseline via provenance only |
| E-14 | **Preemptive mapping contract documents** | TL pattern from Sprint 6.5 — implement in code/tests |
| E-15 | **User Management / cross-org report access hardening** | Known MVP gap on read-by-ID ownership (`progress.md` Sprint 4.x) |

---

## 4. Inputs

All inputs are **read-only persisted artifacts**. The Report Builder must fail closed when required inputs for the selected profile are missing or incomplete.

### 4.1 Analysis Run (primary anchor)

| Input element | Source | Requirement |
|---|---|---|
| **Run identity** | `analysis_runs.id` | Must exist, belong to org |
| **Run status** | `analysis_runs.status` | Must be `completed` |
| **Analysis type** | `analysis_runs.analysis_type` | `financial_waste` or `simulation` in v1 |
| **Provenance links** | `source_snapshot_id`, `source_file_id`, `reporting_period_id` | Copied to report row and metadata |
| **Run title / timestamps** | `title`, `started_at`, `completed_at` | Display and metadata sections |
| **Runtime metadata** | `runtime_metadata` JSONB | Source for `facts_contract`, `ai_insights`, `scenario_provenance` |

### 4.2 Facts Contract

| Input element | Source | Requirement |
|---|---|---|
| **Facts payload** | `runtime_metadata.facts_contract` | Required for both v1 profiles; rehydrate via same discipline as `ai_recommendations/facts_loader.py` (read-only) |
| **Contract version** | `FactsContract.contract_version` | Recorded in report metadata (`CONTRACT_VERSION = "1.0"`) |
| **Engine identity** | `engine_id`, `engine_version` | Provenance; no engine dispatch |

Facts are **presented** in the Key Metrics / Facts section — not reinterpreted or recalculated.

### 4.3 AI Insights (optional — waste profile)

| Input element | Source | Requirement |
|---|---|---|
| **Executive summary** | `runtime_metadata.ai_insights.executive_summary` | Used when present; **not generated** if absent |
| **Risk explanation** | `runtime_metadata.ai_insights.risk_explanation` | Optional section when present |
| **Narrative audit bundle** | `runtime_metadata.ai_insights.narrative` | Appendix/provenance; read-only |
| **AI provenance** | `generated_at`, `model`, `prompt_version`, `tasks_executed`, `source_snapshot_id` | Report metadata when insights consumed |

**Precondition:** AI insights are **never required** for report generation. Missing insights trigger deterministic fallback executive summary derived from Facts + Gold (template-based string assembly from persisted values only — no LLM).

### 4.4 Recommendations (optional — waste profile)

| Input element | Source | Requirement |
|---|---|---|
| **Linked recommendations** | `recommendations` where `analysis_run_id` matches | Zero or more rows |
| **Row fields** | `title`, `description`, `priority`, `confidence_label`, `estimated_savings_amount`, `source_context` | Copied into Recommendations section at generation time |
| **Domain filter** | `domain_source = waste` | v1 waste profile only |

Recommendations are **snapshotted** into the Report Content Representation at generation time so later registry changes do not alter published report documents.

### 4.5 Scenario Results (simulation profile — required when type is simulation)

| Input element | Source | Requirement |
|---|---|---|
| **Simulation run** | `simulation_runs` 1:1 with analysis run | Must exist for simulation profile |
| **Forecast summary** | `simulation_forecast_summaries` | Required |
| **Chart points** | `simulation_chart_points` | Required (default 3-quarter horizon from Sprint 6.5) |
| **Comparison metrics** | `simulation_comparison_metrics` | Required |
| **Impact items** | `simulation_impact_items` | Required |
| **Action items** | `simulation_action_items` | Required |
| **Scenario provenance** | `runtime_metadata.scenario_provenance` | `scenario_id`, `archetype`, `source_snapshot_id`, optional `baseline_analysis_run_id` |
| **Optional baseline waste Gold** | Via `baseline_analysis_run_id` → waste Gold tables + optional baseline `ai_insights` | Read-only enrichment; no engine execution |

Existing GET APIs under `backend/app/api/v1/simulation.py` demonstrate the retrievable Gold shape; Report Builder reads via repositories/services — not by re-invoking scenario execution.

### 4.6 Decision Results — Gold tables (waste profile)

| Input element | Source | Requirement |
|---|---|---|
| **Summary result** | `waste_analysis_results` | Required for waste profile |
| **Category breakdowns** | `waste_category_breakdowns` | Required when rows exist for run |
| **Vendor findings** | `waste_vendor_findings` | Optional section when rows exist |

### 4.7 Organization Context

| Input element | Source | Requirement |
|---|---|---|
| **Organization ID** | Caller membership scope | Must match run and all linked artifacts |
| **Organization identity** | `organizations` record | Name in cover/metadata section |
| **Reporting period** | `analysis_runs.reporting_period_id` → `reporting_periods.label` | Optional FK on report row |
| **Department** | Caller override or derived from dominant breakdown department (deterministic rule in code) | Optional FK on report row |
| **Source file** | `analysis_runs.source_file_id` → `financial_files` | Provenance on report row (`DATABASE_SCHEMA_DESIGN.md` §4.23) |
| **Authorization** | Existing org role model | Generate: executive-tier consistent with analysis execution routes; read: analyst minimum per existing report router |

### 4.8 Analysis type → report type mapping (A-01)

| `analysis_runs.analysis_type` | `reports.report_type` | Profile |
|---|---|---|
| `financial_waste` | `analysis` | Waste Decision Report |
| `simulation` | `simulation` | Scenario Report |
| `risk`, `operational`, `human_resources` | — | **Unsupported in v1** — fail with explicit error |

---

## 5. Outputs

### 5.1 Executive Report

The **Executive Report** is a versioned, deterministic document composed of ordered **Report Sections** plus a **Report Metadata** block. It represents a **point-in-time snapshot** of all consumed inputs at generation time.

#### 5.1.1 Report Content Representation (concept)

The **Report Content Representation** is the persisted binding of a complete Executive Report to its catalog row at generation time. It comprises:

- All **Report Sections** (§5.2) in profile-defined order
- **Extended metadata** (§5.4) — builder version, input fingerprint, sections included, consumption flags
- Stable identity linkage to `reports.id` and `source_analysis_run_id`

**Conceptual properties (normative):**

| Property | Requirement |
|---|---|
| **Immutability** | Once written at generation time, content does not change when source runs, recommendations, or Gold rows are later modified |
| **Completeness** | Sufficient to render content/export endpoints without re-assembly from mutable source tables |
| **Determinism** | Same consumed inputs → same Report Content Representation |
| **Storage form** | **Implementation-defined** — this specification does not prescribe table, column, encoding, or file layout |

If implementation determines the approved schema cannot hold the full Report Content Representation, **stop** and document the **single gap** per Gap Discovery Protocol (§12). Do not introduce preemptive storage contracts or schema prescriptions in advance.

**Document identity fields (conceptual minimum):**

| Field | Derivation |
|---|---|
| `report_document_version` | Sprint constant (e.g. `"1.0"`) |
| `profile` | `waste_decision` \| `scenario` |
| `generated_at` | UTC timestamp at build time (stored once; stable on re-read) |
| `source_analysis_run_id` | Primary run FK |
| `organization_id` | Org scope |

### 5.2 Report Sections

Sections are assembled **deterministically** in fixed order per profile. Missing optional inputs omit the section or use empty collection — never hallucinated content.

**Waste Decision Report (`profile = waste_decision`):**

| Order | Section key | Primary sources |
|---|---|---|
| 1 | `cover` | Org name, period, run title, completion date, source file reference |
| 2 | `executive_summary` | `ai_insights.executive_summary` **or** deterministic Facts/Gold fallback |
| 3 | `key_metrics` | Selected Facts from `facts_contract` + `waste_analysis_results` headline fields |
| 4 | `waste_analysis` | Category breakdowns, vendor findings (when present) |
| 5 | `risk_explanation` | `ai_insights.risk_explanation` (omit if absent) |
| 6 | `recommendations` | Snapshotted recommendation rows |
| 7 | `provenance` | Snapshot id/version, facts/engine versions, AI artifact metadata (if used), generation provenance |

**Scenario Report (`profile = scenario`):**

| Order | Section key | Primary sources |
|---|---|---|
| 1 | `cover` | Org name, period, scenario/run title, completion date |
| 2 | `executive_summary` | Deterministic summary from `simulation_runs.result_title` + `result_description` + forecast summary fields |
| 3 | `scenario_overview` | Archetype, scenario id, assumptions count (from linked scenario via provenance) |
| 4 | `forecast_and_delta` | Forecast summary, comparison metrics, chart points |
| 5 | `impact_and_actions` | Impact items, action items |
| 6 | `key_metrics` | Facts from `facts_contract` |
| 7 | `baseline_context` | Optional waste Gold + AI snippets from `baseline_analysis_run_id` |
| 8 | `provenance` | `scenario_provenance`, snapshot binding, engine versions |

Section payloads use **stable key ordering** in serialization to support determinism tests.

### 5.3 Exportable Report

The **Exportable Report** is the deterministic, retrievable serialization of the Report Content Representation for API consumers. It is a **delivery concept** — distinct from the storage form of the Report Content Representation.

| Output | Description | v1 scope |
|---|---|---|
| **Exportable Report** | Deterministic serialization of Report Content Representation (sections + metadata) | Content and export retrieval endpoints |
| **Stable content fingerprint** | Hash over canonical export serialization for audit and determinism tests | Required in tests; optional in extended metadata |
| **PDF / Excel / PPT** | Binary formats | **Excluded** (E-05, A-05) |

Export and content retrieval return the **persisted Report Content Representation** — not a live re-assembly from mutable source tables. Wire format and export parameters are **implementation-defined**; they must be deterministic and testable.

### 5.4 Report Metadata

**Catalog row (`reports` table — existing columns):**

| Field | Derivation |
|---|---|
| `title` | Caller override or deterministic default from run title + profile label |
| `report_type` | Mapped from analysis type (§4.8) |
| `status` | `draft` on generation |
| `summary` | Text extracted from `executive_summary` section (truncation rules in code if needed) |
| `analysis_run_id` | Primary source run |
| `source_file_id`, `reporting_period_id`, `department_id` | From run/context rules |
| `published_at` | Set only via existing `publish_report` workflow |

**Extended metadata (part of Report Content Representation — conceptual):**

| Field | Purpose |
|---|---|
| `builder_version` | Report Builder release identifier |
| `input_fingerprint` | Hash of consumed artifact ids + versions at generation time |
| `sections_included` | List of section keys present |
| `ai_insights_consumed` | Boolean + timestamp when AI artifact was copied |
| `baseline_run_id` | When simulation report enriched from waste baseline |

**Timeline integration:** Unchanged — `publish_report` continues to append `TimelineEventType.REPORT` events.

### 5.5 Intentionally NOT produced

| Excluded output | Reason |
|---|---|
| New calculated KPIs or recomputed waste/simulation totals | Business Engine responsibility |
| Modified Facts Contract, Gold rows, AI insights, or recommendations | Immutability of source artifacts |
| LLM-generated missing sections | AI freeze |
| `report_exports` persistence rows | Schema extension deferred (§14.3) |
| Frontend-formatted DTOs / Arabic preview layout | Phase 7 |
| Reports for unsupported analysis types | v1 scope |

---

## 6. Processing Flow

**Sprint 6.6 pipeline (normative):**

```
Analysis Run (completed — read-only)
        ↓
Facts Contract + AI Insights (optional) + Recommendations (optional) + Scenario Results (if applicable)
        ↓
Report Builder (deterministic assembly — no AI, no Business Engine)
        ↓
Executive Report (structured sections + metadata)
        ↓
Report catalog row (draft) + persisted Report Content Representation
```

**Explicit non-steps:** LLM invocation, prompt composition, `get_engine().run()`, snapshot payload parsing for new metrics, scenario/waste re-execution.

**Detailed steps:**

| Step | Actor | Action |
|---|---|---|
| 1 | Report Builder | Validate org scope, run `completed`, supported `analysis_type` |
| 2 | Report Builder | Resolve profile (`waste_decision` \| `scenario`) from analysis type |
| 3 | Report Builder | Load `facts_contract` from runtime metadata — fail if missing |
| 4 | Report Builder | Load profile-specific Gold tables via existing repositories |
| 5 | Report Builder | Load optional `ai_insights` and recommendations (waste); load `scenario_provenance` + child tables (simulation) |
| 6 | Report Builder | Optionally load baseline waste artifacts via `baseline_analysis_run_id` — read-only |
| 7 | Section assemblers | Map each input slice → deterministic section payloads (fixed ordering) |
| 8 | Report Builder | Build Executive Report document + metadata + input fingerprint |
| 9 | Report Builder | Persist catalog row via `ReportService.create_draft()` (or internal equivalent) + Report Content Representation |
| 10 | API | Return report id + summary; full Report Content Representation via content/export endpoints |
| **Failure** | Report Builder | No partial catalog row with incomplete content (atomic unit-of-work; mirror Sprint 6.3/6.5 failure semantics) |

**Position in platform pipeline (ADR-010):**

```
Bronze → Silver → Decision Engine (6.3) → Gold → AI Recommendations (6.4) → [Optional: Scenario (6.5)]
        ↓
[Sprint 6.6 Reports] → Executive Report (catalog) → [Future: Frontend Reports page, binary export]
```

---

## 7. Deliverables

| # | Deliverable | Description |
|---|---|---|
| D-01 | **Sprint 6.6 Specification (this document)** | Approved — TL sign-off 2026-07-15 |
| D-02 | **Report Builder module** | Suggested `app/reports/` — service, section assemblers, content model, exceptions |
| D-03 | **Input loaders** | Read-only loaders for facts, insights, recommendations, waste Gold, simulation Gold, baseline enrichment |
| D-04 | **Profile registry** | `waste_decision` and `scenario` profiles with fixed section order |
| D-05 | **Deterministic fallback executive summary** | Template assembly from Facts/Gold when `ai_insights` absent (waste profile) |
| D-06 | **Report Content Representation persistence** | Immutable point-in-time binding at generation; storage form implementation-defined; gap discovery if approved schema insufficient |
| D-07 | **Generate API endpoint** | e.g. `POST /organizations/{id}/reports/generate` with `analysis_run_id` (+ optional title overrides) |
| D-08 | **Content retrieval endpoint** | e.g. `GET /organizations/{id}/reports/{id}/content` — returns Report Content Representation |
| D-09 | **Export endpoint** | e.g. `GET /organizations/{id}/reports/{id}/export` — deterministic Exportable Report serialization |
| D-10 | **ReportService integration** | Compose existing draft/publish/list/delete; extend deps/router wiring |
| D-11 | **Determinism + isolation test suite** | Same inputs → identical Report Content Representation and export serialization; module graph excludes `app.ai` and business engine runners |
| D-12 | **Precondition + profile tests** | Missing facts, incomplete simulation Gold, unsupported analysis type, org ownership |
| D-13 | **`progress.md` update** | Sprint 6.6 completion record (post-implementation only) |

**Explicit non-deliverables:** Preemptive mapping contract documents (E-14), AI changes, Business Engine changes, frontend changes, binary export, new domain profiles (risk/procurement/compliance), Number Guard, Monte Carlo.

---

## 8. Acceptance Criteria

### 8.1 Preconditions and provenance

| ID | Criterion |
|---|---|
| AC-01 | Report generation rejected when analysis run is not `completed` |
| AC-02 | Report generation rejected for unsupported `analysis_type` with explicit error |
| AC-03 | Report generation rejected when required `facts_contract` is missing from runtime metadata |
| AC-04 | Simulation profile rejected when simulation Gold prerequisites are incomplete |
| AC-05 | Generated report row includes correct `analysis_run_id`, `organization_id`, and mapped `report_type` |
| AC-06 | `source_file_id` and `reporting_period_id` propagated from run when present |

### 8.2 Content assembly

| ID | Criterion |
|---|---|
| AC-07 | Waste profile includes `key_metrics`, `waste_analysis`, and `provenance` sections |
| AC-08 | Waste profile includes `executive_summary` from AI insights when present |
| AC-09 | Waste profile produces deterministic fallback executive summary when AI insights absent |
| AC-10 | Waste profile includes `recommendations` section when registry rows exist; empty collection when none |
| AC-11 | Simulation profile includes `forecast_and_delta`, `impact_and_actions`, and `provenance` sections |
| AC-12 | Simulation profile optionally includes `baseline_context` when `baseline_analysis_run_id` is valid and readable |
| AC-13 | `reports.summary` populated from executive summary section text |
| AC-14 | Content/export endpoints return the persisted Report Content Representation — not a live re-assembly |

### 8.3 Determinism and isolation

| ID | Criterion |
|---|---|
| AC-15 | Identical persisted inputs → identical Report Content Representation and deterministic export serialization |
| AC-16 | Report Builder module does not import or invoke `app.ai` LLM/prompt/orchestrator paths |
| AC-17 | Report Builder does not call `get_engine()` or Business Engine `run()` |
| AC-18 | Report generation does not mutate analysis runs, snapshots, Gold tables, or recommendations |
| AC-19 | Regenerating report for same run (if allowed) produces new catalog row — does not overwrite unless explicit regenerate flag approved in implementation |

### 8.4 Catalog workflow regression

| ID | Criterion |
|---|---|
| AC-20 | Existing list/filter/publish/delete report endpoints remain functional |
| AC-21 | Publish still sets `ready`, stamps `published_at`, creates timeline event |
| AC-22 | Sprint 6.3 / 6.4 / 6.5 tests remain green |

### 8.5 Documentation

| ID | Criterion |
|---|---|
| AC-23 | This specification marked **Approved for Implementation** with TL sign-off |
| AC-24 | `progress.md` updated on sprint completion |

---

## 9. Technical Risks

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R-01 | **Approved schema may not accommodate full Report Content Representation** | Cannot serve content/export endpoints faithfully | Apply Gap Discovery Protocol — document single gap, stop, TL review; do not prescribe storage form in spec |
| R-02 | **Missing AI insights on waste runs** — executives expect narrative | Thin reports | Deterministic Facts/Gold fallback summary (I-05, AC-09); document in API that AI is optional upstream |
| R-03 | **A-01 taxonomy mismatch** — analysis types ≠ all report types | Wrong catalog filters | Strict v1 mapping table (§4.8); reject unsupported types |
| R-04 | **Recommendation drift** — registry rows change after report generation | Audit inconsistency | Snapshot recommendations into Report Content Representation at build time (I-04, §5.2) |
| R-05 | **Simulation display vs numeric fields** — forecast summary VARCHAR vs chart NUMERIC | Section inconsistency if wrong source used | Follow Sprint 6.5 discipline: present both as persisted; do not recompute |
| R-06 | **Baseline enrichment complexity** — optional cross-run reads | Partial reports on bad baseline id | Fail closed or omit `baseline_context` section with provenance flag — rule fixed in code/tests |
| R-07 | **Scope creep to AI** — pressure to “refresh” stale narratives | ADR violation | Explicit E-01; AC-16 isolation gate |
| R-08 | **Scope creep to binary export** | A-05 deferral breach | Export endpoint only; binary formats excluded (E-05) |
| R-09 | **ReportService coupling** — duplicate draft logic | Inconsistent validation | Report Builder composes `ReportService`; single transaction boundary |
| R-10 | **Read-by-ID ownership gap** on reports | Cross-org read in multi-tenant future | Align generate/list with ownership checks; note E-15 for get-by-id hardening follow-up |

---

## 10. Dependencies

### 10.1 Hard dependencies (must be complete)

| Dependency | Status | Reference |
|---|---|---|
| Sprint 6.3 Decision Engine (waste Gold + facts on run) | ✅ Complete | `progress.md` Sprint 6.3 |
| Sprint 6.4 AI Recommendations (optional insights + recommendations) | ✅ Complete | `progress.md` Sprint 6.4 |
| Sprint 6.5 Scenario Analysis (simulation Gold + provenance) | ✅ Complete | `progress.md` Sprint 6.5 |
| Report catalog schema + `ReportService` + REST router | ✅ Exists | `backend/app/services/report.py`, `backend/app/api/v1/report.py` |
| Facts Contract rehydration pattern | ✅ Exists | `backend/app/ai_recommendations/facts_loader.py` (read-only reuse) |
| Simulation Gold retrieval | ✅ Exists | `SimulationService`, simulation GET endpoints |
| Waste Gold retrieval | ✅ Exists | `WasteService`, waste GET endpoints |
| ADR-010 snapshot provenance on runs | ✅ Exists | `analysis_runs.source_snapshot_id` |

### 10.2 Soft dependencies

| Dependency | Notes |
|---|---|
| AI insights present on waste run | Improves executive summary; not blocking |
| Recommendations registered for waste run | Optional section |
| Baseline waste run for simulation | Optional enrichment via provenance |
| Reporting period / department labels | Display enrichment |
| Placeholder frontend report cards | Inform section labels; not runtime authority |

### 10.3 Downstream consumers (not Sprint 6.6 blockers)

| Consumer | Relationship |
|---|---|
| Frontend Reports page | Phase 7 — consume list/content/export APIs |
| Binary export (`report_exports`) | Future sprint after A-05 resolution |
| Dashboard “recent reports” aggregation | Phase 7 |
| Report-derived recommendations | Discovery §14.3 future extension |
| Email/board-pack delivery | Ops / future |

---

## 11. Implementation Order

### Step 1 — Specification approval ✅

- This document approved (Technical Lead sign-off 2026-07-15).
- **No additional contract gates** — implementation may proceed directly.
- If R-01 materializes, apply Gap Discovery Protocol before continuing.

### Step 2 — Content model and profile registry

- Define Executive Report document shape, section keys, metadata block, serialization rules (stable ordering).
- Implement `waste_decision` and `scenario` profile section order.

### Step 3 — Read-only input loaders

- Facts rehydration (reuse loader pattern).
- Waste Gold, simulation Gold, recommendations, ai_insights, baseline reader.
- Precondition validation with fail-closed errors.

### Step 4 — Section assemblers

- Deterministic mapping from loaded inputs → section payloads.
- Fallback executive summary templates for waste profile.
- Input fingerprint and provenance block builder.

### Step 5 — Report Builder orchestration

- Single transaction: validate → assemble → persist catalog row + Report Content Representation.
- Compose `ReportService` for draft creation and FK validation.

### Step 6 — API endpoints

- Generate, content GET, export GET.
- Wire permissions consistent with existing report and analysis routes.
- Register in `router.py` and `deps.py`.

### Step 7 — Tests and regression

- Determinism, isolation (no AI/engine), precondition, profile E2E, catalog workflow regression.
- Full suite green; update `progress.md`.

---

## 12. Technical Lead Recommendation

### Recommendation: **APPROVED FOR IMPLEMENTATION**

| Factor | Assessment |
|---|---|
| **Architectural fit** | Closes Discovery Flow 5 and `ReportService` content gap without unfreezing AI or Business Engines |
| **Correct integration pattern** | Terminal consumer composes persisted artifacts; respects analysis-vs-report boundary (schema decision #5) |
| **Pattern reuse** | Facts rehydration, deterministic mapper discipline, fail-closed preconditions — no preemptive contracts |
| **Scope discipline** | Two v1 profiles aligned with completed Sprints 6.3–6.5; unsupported report types explicitly excluded |
| **Determinism** | No AI, no engine execution; Report Content Representation frozen at generation time |
| **Storage neutrality** | Report Content Representation defines concept only; R-01 handled via Gap Discovery Protocol at implementation time |

### TL adjustments applied (2026-07-15)

1. **“Content artifact” replaced with “Report Content Representation”** — concept-only; storage form implementation-defined (§5.1.1).
2. **Implementation authorized directly** — no contract gates beyond this specification.
3. **Gap discovery protocol** — document single genuine gap and stop; no speculative storage prescriptions.

### Conditions for implementation start

1. **This specification approved** — ✅ TL sign-off recorded (2026-07-15).
2. **No modification** to frozen `app/ai/` internals, Business Engine implementations, or Facts Contract structure.
3. **No AI or Business Engine work** in Sprint 6.6 (including narrative regeneration and metric recomputation).
4. **No preemptive mapping contract documents** — section mapping rules live in code and tests.
5. **Gap discovery protocol** — if the full Report Content Representation cannot be persisted within approved schema, document the **single gap** and obtain TL approval before proceeding. Do not prescribe storage form in advance.

### Suggested next sprint after 6.6

Frontend Reports page wiring (Phase 7), binary export (`report_exports` + A-05 resolution), simulation-domain AI (`SCENARIO_ANALYSIS`), risk report profile (after risk Gold path exists), or Number Guard hardening — each requires separate sprint approval.

---

## Document Control

| Field | Value |
|---|---|
| **Version** | 1.1 |
| **Author** | Platform specification (Sprint 6.6) |
| **Review status** | **Approved for Implementation** — TL sign-off 2026-07-15 |
| **Implementation authorized** | Yes |
| **Supersedes** | v1.0 (draft) |
