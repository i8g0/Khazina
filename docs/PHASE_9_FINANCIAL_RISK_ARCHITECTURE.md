# Phase 9 — Financial Risk Intelligence Architecture

**Sprint:** 9.1 — Financial Risk Intelligence Architecture  
**Date:** 2026-07-16  
**Role:** Principal Software Architect / Technical Lead  
**Status:** Architecture specification — **no implementation in this sprint**

**Normative references:**

- [ARCHITECTURE.md](ARCHITECTURE.md) — platform layers and integration boundaries
- [BUSINESS_ENGINE_ARCHITECTURE.md](BUSINESS_ENGINE_ARCHITECTURE.md) — deterministic engine lifecycle (ADR 009)
- [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md) — Facts Contract and AI pipeline (ADR 008)
- [ADR 010: Financial Snapshot Architecture](ADR/010-financial-snapshot-architecture.md) — Silver → Gold analysis substrate
- [DATABASE_SCHEMA_DESIGN.md](DATABASE_SCHEMA_DESIGN.md) — existing `risks` / `risk_mitigation_plans` (§3.6, §4.13–4.14, DD-04)
- [API_CONTRACTS.md](API_CONTRACTS.md) — `ApiResponse` envelope, pagination, org-scoped routes
- [FRONTEND_SPECIFICATION.md](FRONTEND_SPECIFICATION.md) — Risk Management page (§ Page 3)
- [FRONTEND_FREEZE.md](FRONTEND_FREEZE.md) — deferred risk UI scope
- [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) — Phase 9 charter
- [progress.md](progress.md) — current project state

**Existing implementation inventory (must extend, not bypass):**

| Layer | Status | Location |
|-------|--------|----------|
| Risk register CRUD | ✅ Implemented | `backend/app/services/risk.py`, `api/v1/risk.py` |
| DB models | ✅ Implemented | `backend/app/db/models/risk.py` |
| RiskEngine (deterministic) | ❌ Not implemented | Planned: `backend/app/business/engines/risk/` |
| Risk analysis orchestration | ❌ Not implemented | `AnalysisType.RISK` enum exists; no workflow |
| Risk-domain AI | ❌ Not implemented | Waste `RISK_ANALYSIS` task is waste-context only |
| Frontend risk page | ❌ Empty state | `frontend/components/risk/risk-page.tsx` |
| Archived UI components | Mock only | `frontend/components/risk/*.tsx` + `placeholder-data.ts` |

---

## 1. Executive Overview

### 1.1 Purpose

Financial Risk Intelligence extends Khazina from **financial waste detection** and **scenario simulation** into **enterprise-grade risk oversight**. The subsystem must:

1. **Detect** financial and operational risks deterministically from validated financial data and cross-domain signals.
2. **Classify and score** risks using a consistent taxonomy and priority model.
3. **Maintain** a living risk register with mitigation planning and lifecycle governance.
4. **Monitor** risk posture over time through re-analysis and score history.
5. **Explain and recommend** mitigation through the existing AI pipeline — Facts-only, domain-isolated from Waste AI.

Phase 9 does **not** introduce a parallel platform. It extends the established patterns:

```
Upload → Snapshot (Silver) → Business Engine (Gold Facts) → Persistence → AI (optional) → Reports / Dashboard / Notifications
```

The Risk subsystem adds a **second Gold path** (`RiskEngine`) and a **standing register** (`risks`) that engine findings may promote into — analogous to how Waste produces episodic `AnalysisRun` results while recommendations persist as domain records.

### 1.2 Architectural Principles

| Principle | Application to Risk |
|-----------|---------------------|
| **Extend, don't duplicate** | Reuse `AnalysisRun`, `AnalysisService`, `DecisionService` orchestration pattern, `Recommendation`, `TimelineEvent`, `NotificationBuilder`, org-scoped auth |
| **Deterministic before probabilistic** | `RiskEngine` produces Facts; LLM never calculates scores or likelihood |
| **Register vs analysis separation** | Per DD-04: `risks` is standing data; `analysis_runs` type `risk` is episodic intelligence |
| **Facts Contract boundary** | AI consumes only `RiskEngine` Facts Contract — never raw snapshot JSON |
| **No frontend redesign** | Wire existing archived components to new APIs; preserve RTL, density, and page layout from `FRONTEND_SPECIFICATION.md` |
| **Closed-state immutability** | Preserve existing `RiskService` rule: closed risks are terminal |

### 1.3 Scope Boundary

**In Phase 9 architecture:**

- Full domain, engine, persistence, API, AI, frontend integration, and sprint plan design.

**Explicitly out of Phase 9.1 (this sprint):**

- Code, migrations, API handlers, frontend pages, engine implementation.

**Deferred beyond Phase 9 (unchanged from prior freezes):**

- Multi-user owner FK (`owner_user_id`) — retain `owner_label` (DD-06)
- Email/SMS/push notification channels
- Excel/PowerPoint export
- Arbitrary Excel layouts
- Full dashboard cross-domain aggregation API (Phase 10) — Risk provides **risk-scoped** summary endpoints only

### 1.4 High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Executive Frontend (Phase 7 shell)                 │
│  Dashboard KPIs │ Risk Page │ Reports │ Simulation │ Notifications        │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │ REST /api/v1 (JWT, org-scoped)
┌───────────────────────────────▼─────────────────────────────────────────────┐
│                         API Layer (FastAPI routers)                          │
│  risk.py (existing CRUD) │ risk_analysis.py (new) │ ai_recommendations     │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
┌───────────────────────────────▼─────────────────────────────────────────────┐
│                          Service Layer                                       │
│  RiskService          │ RiskAnalysisService    │ RiskIntelligenceService    │
│  (register lifecycle) │ (run orchestration)    │ (promotion, monitoring)    │
│  AiRecommendationService.generate_risk_* │ AnalysisService │ DecisionService │
└───────────────────────────────┬─────────────────────────────────────────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
┌───────────────┐     ┌─────────────────┐     ┌──────────────────┐
│  RiskEngine   │     │  Repositories   │     │  AI Pipeline     │
│  (deterministic│     │  risk, risk_    │     │  Facts → LLM →   │
│   Gold facts) │     │  analysis, etc. │     │  recommendations │
└───────┬───────┘     └────────┬────────┘     └──────────────────┘
        │                      │
        ▼                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PostgreSQL                                           │
│  risks │ risk_mitigation_plans │ analysis_runs │ risk_analysis_results    │
│  risk_findings │ risk_score_history │ risk_events │ recommendations        │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Business Domain

### 2.1 What Is a Financial Risk?

In Khazina, a **Financial Risk** is an **organization-scoped condition or exposure** that may adversely affect financial performance, liquidity, compliance posture, operational continuity, or strategic objectives if left unmitigated.

A risk is characterized by:

| Attribute | Meaning |
|-----------|---------|
| **Identity** | Name and narrative description understood by executives |
| **Category** | Taxonomy class (financial, liquidity, operational, etc.) |
| **Likelihood** | Probability the risk materializes (`low` / `medium` / `high`) |
| **Impact** | Severity if materialized (`low` / `medium` / `high`) |
| **Score** | Deterministic composite 0–100 derived from likelihood × impact and category rules |
| **Priority** | Executive band (`high` / `medium` / `low`) derived from score thresholds |
| **Status** | Lifecycle state (`active` / `in_progress` / `closed`) |
| **Ownership** | Display owner (`owner_label`) and optional department / reporting period |
| **Provenance** | Manual registration, engine detection, or promotion from analysis finding |
| **Mitigation** | Zero or more mitigation plans with target dates and statuses |

Khazina treats risks as **governance records**, not transient calculation output. Engine detections are **findings** until reviewed and optionally **promoted** to the register.

### 2.2 Core Entities

| Entity | Role | Persistence |
|--------|------|-------------|
| **Risk** | Authoritative register entry | `risks` (existing) |
| **Risk Mitigation Plan** | Action plan for a risk | `risk_mitigation_plans` (existing) |
| **Risk Category** | Controlled taxonomy | `risk_categories` (new, seeded) |
| **Risk Analysis Run** | Episodic intelligence execution | `analysis_runs` where `analysis_type = risk` (existing parent) |
| **Risk Analysis Result** | Aggregate outcome of one run | `risk_analysis_results` (new, 1:1 with run) |
| **Risk Finding** | Single detected risk signal before promotion | `risk_findings` (new) |
| **Risk Score History** | Point-in-time score snapshot for monitoring | `risk_score_history` (new) |
| **Risk Event** | Immutable lifecycle audit record | `risk_events` (new) |
| **Recommendation** | AI or manual mitigation suggestion | `recommendations` with `domain_source=risk` (existing) |
| **Timeline Event** | Executive activity feed entry | `timeline_events` polymorphic ref (existing) |

### 2.3 Entity Relationships

```
organizations ──1:N──► risks ──1:N──► risk_mitigation_plans
                │           │
                │           ├──1:N──► risk_score_history
                │           ├──1:N──► risk_events
                │           └──1:N──► recommendations (optional risk_id)
                │
                ├──1:N──► analysis_runs (type=risk)
                │              │
                │              └──1:1──► risk_analysis_results
                │                           │
                │                           └──1:N──► risk_findings ──0:1──► risks (promoted_risk_id)
                │
                └──1:N──► risk_categories (reference)

financial_snapshots ──► (via adapter) ──► RiskEngine ──► Facts Contract
waste_analysis_results ──► (optional cross-domain input) ──► RiskEngine
```

**Key relationship rules:**

1. A **Risk Finding** may exist without a register `Risk` until promoted.
2. A **Risk** may exist without a finding (`source_type = manual`).
3. A **Recommendation** links to at most one primary source: `analysis_run_id`, `risk_id`, or `simulation_run_id` (existing CHECK).
4. **Mitigation plans** cascade-delete with parent risk; closed risks reject new plans (existing rule).

### 2.4 Risk vs Waste — Definitive Comparison

Both domains consume financial snapshots and produce Gold-layer intelligence, but they answer different executive questions.

| Dimension | Waste (Financial Waste Detection) | Risk (Financial Risk Intelligence) |
|-----------|-----------------------------------|-------------------------------------|
| **Business question** | "Where is money being lost or spent inefficiently?" | "What could go wrong, and how severe is our exposure?" |
| **Primary output** | Leakage amounts, category breakdown, vendor findings | Risk register signals, likelihood/impact matrix, mitigation posture |
| **Engine** | `WasteEngine` (implemented) | `RiskEngine` (to implement) |
| **Analysis type** | `financial_waste` | `risk` |
| **Standing data** | None — results tied to run | `risks` register persists across runs |
| **Detection focus** | Spend concentration, waste thresholds, vendor anomalies | Liquidity stress, compliance gaps, operational exposure, strategic drift, budget variance |
| **Scoring model** | Waste percentage, category levels | Likelihood × impact matrix → 0–100 score → priority band |
| **AI task namespace** | `EXECUTIVE_SUMMARY`, `RECOMMENDATIONS`, `RISK_ANALYSIS`* | `RISK_EXECUTIVE_SUMMARY`, `RISK_MITIGATION_RECOMMENDATIONS`, `RISK_EXPLANATION` |
| **AI `RISK_ANALYSIS` note** | *Existing task explains **waste severity** in waste report context — **not** risk-domain intelligence | Must not reuse waste task for risk register recommendations |
| **Cross-domain link** | Vendor findings may **feed** RiskEngine vendor-category rules | May consume waste facts as **input signal**, never as substitute for risk detection |
| **Frontend route** | `/financial-waste` | `/risk-management` |
| **Report type** | `analysis` | `risk` |

**Integration rule:** Waste findings inform RiskEngine **deterministic rules** (e.g., high vendor concentration detected by WasteEngine elevates vendor-category risk score). RiskEngine **never** copies waste rows into the register without passing through detection → finding → review → promotion.

---

## 3. Risk Categories

### 3.1 Category Taxonomy

Khazina supports **nine first-class risk categories** in Phase 9. Categories are **system-seeded**, org-neutral, and referenced by stable `code` values.

| Code | Label (AR) | Label (EN) | Primary Signal Sources | Reasoning |
|------|------------|------------|------------------------|-----------|
| `financial` | مخاطر مالية | Financial | Snapshot ratios, profitability trends, debt indicators | Core financial statement stress |
| `liquidity` | مخاطر السيولة | Liquidity | Current ratio, cash equivalents, short-term obligations | Cash runway and payment capacity |
| `operational` | مخاطر تشغيلية | Operational | Process KPIs, department spend volatility | Non-financial execution failures affecting finance |
| `compliance` | مخاطر امتثال | Compliance | Policy thresholds, regulatory limits (rule-based) | Governance and regulatory exposure |
| `vendor` | مخاطر الموردين | Vendor | Waste vendor findings, supplier concentration | Third-party dependency risk |
| `fraud` | مخاطر احتيال | Fraud | Statistical anomaly rules on spend patterns | Deterministic anomaly flags — not ML fraud engine |
| `strategic` | مخاطر استراتيجية | Strategic | Simulation assumptions, long-term forecast variance | Alignment with strategic plan |
| `budget` | مخاطر الموازنة | Budget | Budget vs actual variance from snapshot | Plan deviation |
| `forecast` | مخاطر التوقعات | Forecast | Scenario forecast uncertainty bands | Forward-looking projection risk |

**Design decisions:**

1. **`category_label` migration path:** Existing `risks.category_label` (free text) remains for backward compatibility. New writes use `category_code` FK. Display resolves label from `risk_categories` with Arabic UI labels.
2. **Single primary category per risk:** Multi-category tagging is deferred; findings may reference one primary category with optional `secondary_signals` JSON on findings for audit.
3. **Fraud category scope:** Phase 9 implements **rule-based anomaly detection** only. No ML classifier, no external fraud feeds.
4. **Strategic + forecast distinction:** Strategic risks arise from plan assumptions; forecast risks arise from projection confidence intervals produced by ScenarioEngine outputs when available.

### 3.2 Category → Detection Rule Ownership

Each category maps to one or more **deterministic detector modules** inside `RiskEngine`:

```
RiskEngine
  └── Detector
        ├── financial_detector
        ├── liquidity_detector
        ├── operational_detector
        ├── compliance_detector
        ├── vendor_detector      ← may read waste vendor facts
        ├── fraud_detector
        ├── strategic_detector   ← optional simulation facts input
        ├── budget_detector
        └── forecast_detector
```

Detectors emit **candidate findings** with category code, evidence facts, and proposed likelihood/impact — never narrative text.

---

## 4. Risk Lifecycle

### 4.1 Lifecycle Stages

```
┌────────────┐    ┌───────────────┐    ┌─────────┐    ┌────────────┐    ┌──────────┐    ┌──────────┐    ┌───────────┐
│ Detection  │───►│Classification │───►│ Scoring │───►│ Mitigation │───►│Monitoring│───►│Resolution│───►│ Archiving │
└────────────┘    └───────────────┘    └─────────┘    └────────────┘    └──────────┘    └──────────┘    └───────────┘
```

| Stage | Owner | Description | Persistence |
|-------|-------|-------------|---------------|
| **Detection** | `RiskEngine` + `RiskAnalysisService` | Run deterministic analysis on snapshot (+ optional cross-domain facts) | `analysis_runs`, `risk_findings` |
| **Classification** | `RiskEngine.Detector` | Assign category, likelihood, impact using rules | `risk_findings.category_code`, likelihood, impact |
| **Scoring** | `RiskEngine.Calculator` | Compute 0–100 score and derive priority | `risk_findings.score`, `priority`; promoted to `risks.score` |
| **Mitigation** | `RiskService` | Executives define plans; track plan status | `risk_mitigation_plans` |
| **Monitoring** | `RiskIntelligenceService` | Re-run analysis; append score history; detect drift | `risk_score_history`, new findings vs prior |
| **Resolution** | `RiskService.transition_risk` | Mark mitigated or accepted; `in_progress` → `closed` | `risks.status`, `risk_events` |
| **Archiving** | `RiskService` | Closed risks immutable; excluded from active KPIs | `risks.status = closed` |

### 4.2 Finding Review Workflow (New)

Engine output is not automatically trusted as register truth:

```
detected ──► reviewed ──► promoted ──► (creates/updates Risk)
                │
                └──► dismissed (audit retained)
```

| Finding Status | Meaning |
|----------------|---------|
| `detected` | Engine output, unreviewed |
| `reviewed` | Executive/analyst acknowledged |
| `promoted` | Linked to register `risks` row via `promoted_risk_id` |
| `dismissed` | Rejected — retained for audit, not shown on register |

### 4.3 Register Status Workflow (Existing — Preserved)

```
active ──► in_progress ──► closed
   │
   └──────► closed (direct)
```

Implemented in `RiskService._RISK_TRANSITIONS`. Phase 9 adds **`risk_events`** audit records on each transition but does not change allowed transitions.

### 4.4 Monitoring Cadence

| Trigger | Behavior |
|---------|----------|
| **Manual re-analysis** | Executive triggers `POST .../risk-analyses/execute` on latest snapshot |
| **Post-waste pipeline** | Optional chained risk analysis after waste completion (settings-gated) |
| **Scheduled (future)** | Phase 10+ cron — not Phase 9 MVP |

On re-analysis, `RiskIntelligenceService`:

1. Creates new `analysis_run` type `risk`.
2. Compares findings to open register risks (match by category + similarity key).
3. Appends `risk_score_history` when score changes beyond configured delta.
4. Emits notifications on new high-priority findings or score escalation.

---

## 5. Risk Engine Architecture

### 5.1 Engine Identity

| Property | Value |
|----------|-------|
| `engine_id` | `risk` |
| `engine_name` | Financial Risk Engine |
| `engine_version` | `1.0.0` |
| `facts_contract_version` | `1.0` |
| Package path | `backend/app/business/engines/risk/` |

Conforms to [BUSINESS_ENGINE_ARCHITECTURE.md](BUSINESS_ENGINE_ARCHITECTURE.md) §3–§5.

### 5.2 Package Structure (Planned)

```
backend/app/business/engines/risk/
├── __init__.py
├── engine.py              # RiskEngine(BusinessEngine)
├── manifest.py            # RISK_ENGINE_MANIFEST, SUPPORTED_FACTS
├── input.py               # RiskEngineInput, CategorySignalInput
├── calculator.py          # RiskCalculator → RiskCalculationResult
├── detector.py            # RiskDetector → RiskDetectionResult
├── scoring.py             # likelihood/impact → score → priority
└── rules/                 # per-category rule modules
    ├── financial.py
    ├── liquidity.py
    └── ...
```

Shared assembly:

```
backend/app/business/assemblers/risk.py   # RiskFactAssembler
```

### 5.3 Inputs

**Primary input:** `RiskEngineInput` adapted from `FinancialSnapshot.payload` via `RiskSnapshotAdapterV1` (mirrors `WasteSnapshotAdapterV1` pattern in `app/decision/adapters/`).

| Input field | Source | Required |
|-------------|--------|----------|
| `organization_id` | Run context | Yes |
| `reporting_period` | Snapshot / run | Yes |
| `snapshot_id` | Analysis run | Yes |
| `financial_metrics` | Snapshot Silver normalized metrics | Yes |
| `existing_register_summary` | Aggregated open risk counts by category | No |
| `waste_facts` | Prior completed waste run Facts Contract (same snapshot) | No |
| `simulation_summary` | Latest simulation comparison metrics | No |
| `rule_profile` | Org settings — enabled categories, thresholds | No (defaults) |

**Validation boundaries:**

- Snapshot must be `READY` / linked to analyzable file (same precondition as `DecisionService.execute_waste_analysis`).
- Metrics must pass `RiskEngine._validate_input` — reject missing mandatory liquidity inputs rather than defaulting silently.
- Cross-domain facts are **read-only references** — engine must not mutate waste or simulation persistence.

### 5.4 Processing Pipeline

```
RiskEngineInput
      ↓
Validation                    (engine preconditions, metric completeness)
      ↓
RiskCalculator.calculate()    (ratios, variances, concentration indices)
      ↓
RiskDetector.detect()         (per-category rule evaluation → candidate findings)
      ↓
RiskScoring.apply()           (likelihood × impact matrix, 0–100 score, priority band)
      ↓
RiskFactAssembler.assemble()  (Facts + structured finding payloads)
      ↓
FactsContract                 (versioned, returned to orchestrator)
```

**No LLM in this pipeline.**

### 5.5 Outputs

#### Facts Contract (AI-consumable)

Representative fact keys (final list frozen in Sprint 9.2):

| Fact key | Type | Description |
|----------|------|-------------|
| `risk.total_findings` | int | Count of detected findings |
| `risk.high_priority_count` | int | Findings with priority `high` |
| `risk.medium_priority_count` | int | Findings with priority `medium` |
| `risk.low_priority_count` | int | Findings with priority `low` |
| `risk.overall_posture_level` | enum | `elevated` / `moderate` / `low` |
| `risk.category_count.{code}` | int | Per-category finding counts |
| `risk.top_category` | string | Category code with highest exposure |
| `risk.liquidity_ratio` | decimal | Computed current ratio (deterministic) |
| `risk.score_max` | int | Highest finding score 0–100 |
| `risk.finding.{id}.score` | int | Individual finding scores for AI grounding |

Facts Contract stored on `analysis_runs.runtime_metadata.facts_contract` (same pattern as waste).

#### Structured detection payload (orchestrator-persisted)

Returned alongside Facts Contract to `RiskAnalysisService` for persistence into `risk_findings` rows — not passed to LLM as freeform JSON; each finding maps to typed columns.

### 5.6 Dependencies

| Dependency | Direction | Contract |
|------------|-----------|----------|
| `FinancialSnapshotRepository` | Read | Silver payload |
| `WasteRepository` / prior run metadata | Read | Optional waste facts |
| `SimulationRepository` | Read | Optional forecast metrics |
| `RiskRepository` | Read | Open register summary for deduplication context |
| `SettingsService` | Read | Enabled categories, thresholds |
| `business.registry.get_engine("risk")` | Read | Engine instance |
| AI layer | **None** | Engine never imports `app.ai` |

### 5.7 Integration Points

| Integration | Mechanism |
|-------------|-----------|
| **Decision orchestration** | Extend `DecisionService` with `execute_risk_analysis()` parallel to `execute_waste_analysis()` |
| **Analysis lifecycle** | `AnalysisService.create_run(type=risk)` → `start_run` → `complete_run` / `fail_run` |
| **Gold persistence** | `RiskGoldMapper` maps engine output → `risk_analysis_results` + `risk_findings` |
| **Engine registry** | `register_engine(RiskEngine())` in `app/business/bootstrap.py` |
| **Observability** | `PipelineStage.RISK_ANALYSIS_*` events in existing pipeline timeline |
| **Promotion** | `RiskIntelligenceService.promote_finding()` → `RiskService.register_risk()` or update existing |

---

## 6. Database Design

### 6.1 Existing Entities (Extended — Not Replaced)

#### `risks` (extend)

| Change | Purpose |
|--------|---------|
| Add `category_code` VARCHAR(50) FK → `risk_categories.code` | Normalized taxonomy |
| Add `source_type` VARCHAR(30) | `manual` \| `engine` \| `import` |
| Add `source_analysis_run_id` UUID NULL FK → `analysis_runs.id` | Provenance |
| Add `source_finding_id` UUID NULL FK → `risk_findings.id` | Promotion link |
| Add `detected_at` TIMESTAMPTZ NULL | First detection timestamp |
| Retain `category_label` | Backward compatibility until migration sprint |

**PK:** `id` (UUID) — unchanged  
**FKs:** existing + new columns above  
**Indexes:** add `(organization_id, category_code, status)`  
**Constraints:** retain `ck_risks_score_range`; add `source_type` enum CHECK

#### `risk_mitigation_plans` (minor extend)

| Change | Purpose |
|--------|---------|
| Add `plan_status` VARCHAR(30) | Normalized: `planned`, `in_progress`, `completed`, `cancelled` |
| Retain `status` VARCHAR(50) | Display text / Arabic label during transition |

### 6.2 New Entity: `risk_categories`

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `code` | VARCHAR(50) | **PK** | Stable identifier (`financial`, `liquidity`, …) |
| `label_ar` | VARCHAR(100) | NOT NULL | Arabic UI label |
| `label_en` | VARCHAR(100) | NOT NULL | English documentation label |
| `description` | TEXT | NULL | Category definition |
| `is_active` | BOOLEAN | NOT NULL DEFAULT true | Soft-disable without delete |
| `sort_order` | SMALLINT | NOT NULL | Chart ordering |
| `created_at` | TIMESTAMPTZ | NOT NULL | Audit |

**Indexes:** `(is_active, sort_order)`  
**Seeded rows:** 9 categories from §3.1  
**Relationships:** `risks.category_code` → `risk_categories.code`

### 6.3 New Entity: `risk_analysis_results`

1:1 with `analysis_runs` where `analysis_type = risk`.

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | UUID | **PK** | Surrogate key |
| `analysis_run_id` | UUID | NOT NULL, UNIQUE, FK → `analysis_runs.id` ON DELETE CASCADE | Parent run |
| `organization_id` | UUID | NOT NULL, FK → `organizations.id` | Org scope |
| `total_findings` | INTEGER | NOT NULL DEFAULT 0 | Aggregate count |
| `high_priority_count` | INTEGER | NOT NULL DEFAULT 0 | KPI input |
| `medium_priority_count` | INTEGER | NOT NULL DEFAULT 0 | KPI input |
| `low_priority_count` | INTEGER | NOT NULL DEFAULT 0 | KPI input |
| `overall_posture_level` | VARCHAR(30) | NOT NULL | `elevated` / `moderate` / `low` |
| `top_category_code` | VARCHAR(50) | NULL, FK → `risk_categories.code` | Summary |
| `facts_contract_version` | VARCHAR(20) | NOT NULL | Engine version trace |
| `source_snapshot_id` | UUID | NULL, FK → `financial_snapshots.id` | Silver input reference |
| `created_at` | TIMESTAMPTZ | NOT NULL | Audit |

**Indexes:** `(organization_id, created_at DESC)` for recent analyses list  
**Constraints:** `analysis_run_id` UNIQUE enforces 1:1

### 6.4 New Entity: `risk_findings`

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | UUID | **PK** | Surrogate key |
| `analysis_run_id` | UUID | NOT NULL, FK → `analysis_runs.id` ON DELETE CASCADE | Parent run |
| `organization_id` | UUID | NOT NULL, FK → `organizations.id` | Org scope |
| `category_code` | VARCHAR(50) | NOT NULL, FK → `risk_categories.code` | Classification |
| `name` | VARCHAR(300) | NOT NULL | Finding title |
| `description` | TEXT | NOT NULL | Deterministic description template filled from evidence |
| `likelihood` | VARCHAR(50) | NOT NULL | `low` / `medium` / `high` |
| `impact` | VARCHAR(50) | NOT NULL | `low` / `medium` / `high` |
| `score` | SMALLINT | NOT NULL, CHECK 0–100 | Composite score |
| `priority` | VARCHAR(50) | NOT NULL | `high` / `medium` / `low` |
| `detection_rule_id` | VARCHAR(100) | NOT NULL | Traceability to rule module |
| `evidence` | JSONB | NOT NULL | Structured fact references (not LLM prose) |
| `finding_status` | VARCHAR(30) | NOT NULL DEFAULT `detected` | Review workflow |
| `promoted_risk_id` | UUID | NULL, FK → `risks.id` ON DELETE SET NULL | Register link after promotion |
| `department_id` | UUID | NULL, FK → `departments.id` | Optional attribution |
| `created_at` | TIMESTAMPTZ | NOT NULL | Audit |

**Indexes:**

- `(analysis_run_id, priority)` — run detail views
- `(organization_id, finding_status, priority)` — review queue
- `(promoted_risk_id)` — promotion lookup

**Constraints:** `finding_status` CHECK (`detected`, `reviewed`, `promoted`, `dismissed`)

### 6.5 New Entity: `risk_score_history`

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | UUID | **PK** | Surrogate key |
| `risk_id` | UUID | NOT NULL, FK → `risks.id` ON DELETE CASCADE | Monitored risk |
| `organization_id` | UUID | NOT NULL, FK → `organizations.id` | Org scope |
| `score` | SMALLINT | NOT NULL, CHECK 0–100 | Snapshot score |
| `priority` | VARCHAR(50) | NOT NULL | Snapshot priority |
| `likelihood` | VARCHAR(50) | NULL | Snapshot likelihood |
| `impact` | VARCHAR(50) | NULL | Snapshot impact |
| `source_analysis_run_id` | UUID | NULL, FK → `analysis_runs.id` | Triggering run |
| `recorded_at` | TIMESTAMPTZ | NOT NULL | Monitoring timestamp |

**Indexes:** `(risk_id, recorded_at DESC)` — trend charts  
**Purpose:** Monitoring stage — score drift visibility without mutating closed risks

### 6.6 New Entity: `risk_events`

| Column | Type | Constraints | Purpose |
|--------|------|-------------|---------|
| `id` | UUID | **PK** | Surrogate key |
| `risk_id` | UUID | NOT NULL, FK → `risks.id` ON DELETE CASCADE | Subject risk |
| `organization_id` | UUID | NOT NULL, FK → `organizations.id` | Org scope |
| `event_type` | VARCHAR(50) | NOT NULL | See event types below |
| `from_status` | VARCHAR(50) | NULL | Prior register status |
| `to_status` | VARCHAR(50) | NULL | New register status |
| `actor_user_id` | UUID | NULL, FK → `users.id` | Who triggered (nullable for system) |
| `metadata` | JSONB | NOT NULL DEFAULT `{}` | Context (finding id, plan id, etc.) |
| `created_at` | TIMESTAMPTZ | NOT NULL | Immutable timestamp |

**Event types:** `registered`, `updated`, `status_transitioned`, `mitigation_added`, `mitigation_updated`, `finding_promoted`, `score_changed`, `analysis_linked`

**Indexes:** `(risk_id, created_at DESC)`, `(organization_id, event_type, created_at DESC)`

**Purpose:** Resolution and archiving audit trail — complements immutable closed-state rule

### 6.7 Entity Relationship Summary (New + Extended)

| From | To | Cardinality | On Delete |
|------|-----|-------------|-----------|
| `organizations` | `risk_analysis_results` | 1:N | RESTRICT |
| `analysis_runs` | `risk_analysis_results` | 1:1 | CASCADE |
| `analysis_runs` | `risk_findings` | 1:N | CASCADE |
| `risk_findings` | `risks` | N:0..1 | SET NULL |
| `risks` | `risk_score_history` | 1:N | CASCADE |
| `risks` | `risk_events` | 1:N | CASCADE |
| `risk_categories` | `risks` | 1:N | RESTRICT |
| `risk_categories` | `risk_findings` | 1:N | RESTRICT |

---

## 7. Backend Architecture

### 7.1 Service Responsibilities

| Service | File (planned) | Responsibility |
|---------|----------------|----------------|
| **RiskService** | `services/risk.py` *(existing)* | Register CRUD, lifecycle transitions, mitigation plans, closed-state enforcement |
| **RiskAnalysisService** | `services/risk_analysis.py` *(new)* | Create/execute/complete risk analysis runs; invoke `DecisionService.execute_risk_analysis`; persist results and findings |
| **RiskIntelligenceService** | `services/risk_intelligence.py` *(new)* | Finding review/promotion/dismissal; score history; deduplication; dashboard/matrix aggregations |
| **DecisionService** | `decision/service.py` *(extend)* | Add `execute_risk_analysis()` — snapshot → RiskEngine → Gold mapper |
| **AnalysisService** | `services/analysis.py` *(extend)* | Enable `AnalysisType.RISK` in settings gate; notification hooks on complete/fail |
| **AiRecommendationService** | `ai_recommendations/service.py` *(extend)* | Add `generate_risk_recommendations()` from risk run Facts Contract |

**Domain boundary rules:**

- `RiskService` never calls Ollama.
- `RiskAnalysisService` never writes directly to `risks` except via promotion through `RiskIntelligenceService`.
- `AiRecommendationService` never creates register rows — only `recommendations` and `runtime_metadata.ai_insights`.

### 7.2 Repository Layer

| Repository | File (planned) | Methods |
|------------|----------------|---------|
| **RiskRepository** | `repositories/risk.py` *(extend)* | Existing + `get_open_summary_by_category`, score history writes |
| **RiskAnalysisRepository** | `repositories/risk_analysis.py` *(new)* | Result CRUD, findings batch insert, list runs/findings |
| **RiskCategoryRepository** | `repositories/risk_category.py` *(new)* | List active categories (read-mostly) |
| **RiskEventRepository** | `repositories/risk_event.py` *(new)* | Append-only event writes, list by risk |

All repositories extend `BaseRepository` patterns from Phase 3.

### 7.3 Business Rules

| Rule | Enforcement |
|------|-------------|
| Score range 0–100 | DB CHECK + service validation (existing) |
| Closed risk immutability | `RiskService` — no update, no new mitigation (existing) |
| Finding promotion requires `reviewed` or `detected` with executive role | `RiskIntelligenceService` |
| Dismissed findings cannot promote | `RiskIntelligenceService` |
| One result per risk analysis run | `RiskAnalysisRepository` UNIQUE constraint |
| Org ownership on all reads/writes | `_check_ownership` on every service method |
| AI requires completed run with Facts Contract | `AiRecommendationService._validate_run_preconditions` |
| Disabled analysis type blocked | `SettingsService` — add `risk` to `enabled_analysis_types` |
| Engine detection descriptions are templates | No freeform LLM text in `risk_findings.description` at detection time |

### 7.4 Validation Boundaries

| Layer | Validates |
|-------|-----------|
| **Pydantic schemas** | Request shape, enum values, string lengths |
| **RiskService** | Lifecycle transitions, closed-state guards, org ownership |
| **RiskAnalysisService** | Snapshot readiness, duplicate run prevention, engine errors → `fail_run` |
| **RiskEngine** | Input completeness, metric bounds, rule preconditions |
| **AI validator** | Facts-only responses, recommendation count bounds, priority keyword mapping |

### 7.5 Event Flow — Risk Analysis Execution

```
Client POST /risk-analyses/execute
        ↓
RiskAnalysisService.execute()
        ↓
DecisionService.execute_risk_analysis()
        ├── AnalysisService.create_run(type=risk)
        ├── AnalysisService.start_run()
        ├── RiskSnapshotAdapterV1.adapt(snapshot)
        ├── RiskEngine.run(input) → FactsContract
        ├── RiskGoldMapper.persist(result, findings)
        └── AnalysisService.complete_run(metadata+facts)
        ↓
NotificationBuilder.materialize_risk_analysis_completion()  [try_materialize]
        ↓
TimelineEvent(related_entity_type=analysis_run)           [settings-gated]
        ↓
Response: AnalysisRun + RiskAnalysisResult summary
```

### 7.6 Event Flow — Finding Promotion

```
Client POST /risk-findings/{id}/promote
        ↓
RiskIntelligenceService.promote_finding()
        ├── Validate finding_status
        ├── RiskService.register_risk() OR update_risk() if dedup match
        ├── Link promoted_risk_id, set finding_status=promoted
        ├── Append risk_events(finding_promoted)
        └── Optional: risk_score_history initial row
        ↓
NotificationBuilder.materialize_risk_promoted()  [optional Phase 9.7]
```

---

## 8. API Design

All endpoints follow [API_CONTRACTS.md](API_CONTRACTS.md): `ApiResponse` envelope, org-scoped prefix `/api/v1/organizations/{organization_id}`, JWT Bearer auth, role dependencies consistent with existing routers.

**Role shorthand:** ANALYST+ = `require_org_role(ANALYST)`; EXECUTIVE+ = `RequireOrgExecutive`; ADMIN = `RequireOrgAdmin`.

### 8.1 Existing Endpoints (Preserved — No Breaking Changes)

Router: `app/api/v1/risk.py` — tag `risk`

| Method | Path | Purpose | Auth | Notes |
|--------|------|---------|------|-------|
| POST | `/risks` | Register manual risk | EXECUTIVE+ | Existing |
| GET | `/risks` | List register | ANALYST+ | Add optional `category_code` query in Sprint 9.4 |
| GET | `/risks/{risk_id}` | Get risk detail | ANALYST+ | Existing |
| PATCH | `/risks/{risk_id}` | Update risk fields | EXECUTIVE+ | Existing |
| POST | `/risks/{risk_id}/transition` | Lifecycle transition | EXECUTIVE+ | Existing |
| DELETE | `/risks/{risk_id}` | Delete risk | ADMIN | Existing |
| POST | `/risks/{risk_id}/mitigation-plans` | Add plan | EXECUTIVE+ | Existing |
| GET | `/risks/{risk_id}/mitigation-plans` | List plans for risk | ANALYST+ | Existing |
| GET | `/mitigation-plans` | Org-wide plans | ANALYST+ | Existing |
| PATCH | `/mitigation-plans/{plan_id}` | Update plan | EXECUTIVE+ | Existing |
| DELETE | `/mitigation-plans/{plan_id}` | Delete plan | ADMIN | Existing |

### 8.2 New Endpoints — Risk Analysis

Router: `app/api/v1/risk_analysis.py` *(new)* — tag `risk-analysis`

| Method | Path | Purpose | Input | Output | Auth |
|--------|------|---------|-------|--------|------|
| POST | `/risk-analyses/execute` | Run RiskEngine on snapshot | `{ title, source_file_id?, source_snapshot_id?, reporting_period_id? }` | `AnalysisRunResponse` + `RiskAnalysisResultSummary` | EXECUTIVE+ |
| GET | `/risk-analyses` | List risk analysis runs | Query: pagination, `status` | `list[AnalysisRunResponse]` | ANALYST+ |
| GET | `/risk-analyses/{run_id}` | Run detail | — | Run + result summary | ANALYST+ |
| GET | `/risk-analyses/{run_id}/result` | Full result aggregates | — | `RiskAnalysisResultResponse` | ANALYST+ |
| GET | `/risk-analyses/{run_id}/findings` | Findings for run | Query: `priority`, `category_code`, `finding_status` | `list[RiskFindingResponse]` | ANALYST+ |

### 8.3 New Endpoints — Risk Intelligence

Router: `app/api/v1/risk_intelligence.py` *(new)* — tag `risk-intelligence`

| Method | Path | Purpose | Input | Output | Auth |
|--------|------|---------|-------|--------|------|
| GET | `/risks/summary` | Dashboard KPIs | — | `{ high, medium, low, total_active, closed_count }` | ANALYST+ |
| GET | `/risks/matrix` | Priority matrix cells | Query: `status` (default active) | `list[{ likelihood, impact, count, risks[] }]` | ANALYST+ |
| GET | `/risks/by-department` | Department distribution | — | Chart series data | ANALYST+ |
| GET | `/risks/by-category` | Category distribution | — | Chart series data | ANALYST+ |
| POST | `/risk-findings/{finding_id}/review` | Mark reviewed | `{ notes? }` | `RiskFindingResponse` | EXECUTIVE+ |
| POST | `/risk-findings/{finding_id}/promote` | Promote to register | `{ owner_label?, department_id? }` | `RiskResponse` | EXECUTIVE+ |
| POST | `/risk-findings/{finding_id}/dismiss` | Dismiss finding | `{ reason? }` | `RiskFindingResponse` | EXECUTIVE+ |
| GET | `/risks/{risk_id}/score-history` | Monitoring trend | Pagination | `list[RiskScoreHistoryResponse]` | ANALYST+ |
| GET | `/risks/{risk_id}/events` | Audit trail | Pagination | `list[RiskEventResponse]` | ANALYST+ |
| GET | `/risk-categories` | Taxonomy list | — | `list[RiskCategoryResponse]` | ANALYST+ |

### 8.4 New Endpoints — Risk AI

Router: extend `app/api/v1/ai_recommendations.py`

| Method | Path | Purpose | Input | Output | Auth |
|--------|------|---------|-------|--------|------|
| POST | `/ai-recommendations/risk/generate` | Generate risk-domain AI | `{ analysis_run_id, regenerate? }` | Run + recommendations + `ai_insights` | EXECUTIVE+ |
| POST | `/ai-recommendations/risk/{risk_id}/generate` | AI for standing risk | `{ regenerate? }` | Recommendations linked via `risk_id` | EXECUTIVE+ |

**Second endpoint** uses latest Facts from linked analysis or compact risk register facts assembled deterministically for single-risk explanation — design detail in Sprint 9.5.

### 8.5 Existing Recommendation Endpoints (Extended Usage)

Router: `app/api/v1/recommendation.py`

| Method | Path | Risk usage |
|--------|------|------------|
| GET | `/recommendations?domain_source=risk` | List risk-domain recommendations |
| POST | `/recommendations` | Manual risk recommendation with `risk_id` |

---

## 9. AI Integration

### 9.1 Design Principles (from AI_ARCHITECTURE.md)

1. AI runs **only after** `RiskEngine` produces a Facts Contract on a **completed** analysis run (or after deterministic single-risk fact assembly for register-only AI).
2. AI **never** computes scores, likelihood, or impact.
3. Risk-domain AI tasks are **separate** from waste `PromptTask.RISK_ANALYSIS`.

### 9.2 Prompt Tasks (New — Risk Domain)

Add to `app/ai/prompts/tasks.py`:

| Task | Purpose | Output key |
|------|---------|------------|
| `RISK_EXECUTIVE_SUMMARY` | Executive narrative of posture | `risk_executive_summary` |
| `RISK_MITIGATION_RECOMMENDATIONS` | Action recommendations | `risk_mitigation_recommendations` |
| `RISK_EXPLANATION` | Explain why top findings scored high | `risk_explanation` |

**Execution order:** `RISK_EXECUTIVE_SUMMARY` → `RISK_EXPLANATION` → `RISK_MITIGATION_RECOMMENDATIONS`

**Waste `RISK_ANALYSIS` task:** Unchanged — continues to explain waste severity inside waste reports. Document cross-reference in AI prompts to prevent task confusion.

### 9.3 Facts Consumption

```
analysis_runs.runtime_metadata.facts_contract
        ↓
load_facts_contract(run, domain="risk")
        ↓
AiTaskPipeline.execute(tasks, facts, language)
        ↓
validate_task_results() — Number Guard applies
        ↓
parse_and_map_recommendations(domain=RecommendationDomain.RISK)
        ↓
Persist recommendations (domain_source=risk, analysis_run_id or risk_id)
```

### 9.4 AI Output Persistence

| Store | Content |
|-------|---------|
| `analysis_runs.runtime_metadata.ai_insights` | Narrative keys per task |
| `recommendations` table | Structured cards for UI (`title`, `description`, `priority`, `confidence`) |
| `reports` | Risk report sections reference AI insights by run id |

### 9.5 Risk AI vs Waste AI

| Aspect | Waste AI | Risk AI |
|--------|----------|---------|
| **Trigger** | Completed `financial_waste` run | Completed `risk` run or standing `risk_id` |
| **Facts source** | `WasteEngine` Facts Contract | `RiskEngine` Facts Contract |
| **Domain** | `RecommendationDomain.WASTE` | `RecommendationDomain.RISK` |
| **Recommendation FK** | `analysis_run_id` | `analysis_run_id` and/or `risk_id` |
| **Narrative focus** | Savings, leakage reduction | Mitigation, exposure reduction, governance |
| **Report section** | Waste report + `build_risk_explanation_section` (waste context) | Dedicated risk report sections (Sprint 9.6) |
| **Notification kind** | `ai_recommendations_completed` | `risk_ai_recommendations_completed` *(new)* |

---

## 10. Frontend Integration

**Constraint:** No UI redesign. Reuse archived components in `frontend/components/risk/` and patterns from Waste/Simulation pages.

### 10.1 Risk Management Page (`/risk-management`)

| UI Block (existing component) | Data source (new) |
|-------------------------------|-------------------|
| `RiskOverview` stat cards | `GET /risks/summary` |
| `RiskActiveTable` | `GET /risks?status=active` + pagination |
| `RiskPriorityMatrix` | `GET /risks/matrix` |
| `RiskCharts` (by department / severity) | `GET /risks/by-department`, `GET /risks/by-category` |
| `RiskMitigationPlans` | `GET /mitigation-plans` or per-risk |
| `RiskRecommendationCard` | `GET /recommendations?domain_source=risk` |
| Execute analysis action | `POST /risk-analyses/execute` |
| Finding promotion (executive) | `POST /risk-findings/{id}/promote` |

**States (FRONTEND_SPECIFICATION.md):**

- Loading: `AuthLoadingShell` + skeleton (Phase 8 pattern)
- Empty: retain intentional empty copy when no risks **and** no completed analysis — differentiate "no data" vs "engine not run"
- Error: `PageFeedback` + sanitized Arabic messages

### 10.2 Dashboard Integration

| Dashboard element | Integration |
|-------------------|-------------|
| KPI "عدد المخاطر الحرجة" | `GET /risks/summary`.high |
| Recent analyses row type "مخاطر" | `GET /risk-analyses?limit=3` |
| Priority recommendations | Include `domain_source=risk` in existing recommendation fetch when dashboard aggregation API lands (Phase 10); interim: risk-specific fetch |
| Timeline | Existing timeline API — new events with `related_entity_type=risk` or `analysis_run` |

**Note:** Full cross-domain dashboard aggregation remains Phase 10. Phase 9 delivers **risk-scoped summary endpoints** sufficient for KPI widgets.

### 10.3 Reports Integration

| Integration | Mechanism |
|-------------|-----------|
| Report type `risk` | Existing `ReportType.RISK` enum |
| Generate risk report | Extend report generator to include risk analysis result + AI insights (Sprint 9.6) |
| PDF sections | New sections: posture summary, matrix snapshot, top findings, mitigation status |
| Report list filters | Existing reports page filters by type — no layout change |

### 10.4 Simulation Integration

| Integration | Mechanism |
|-------------|-----------|
| Strategic/forecast risk inputs | `RiskEngineInput.simulation_summary` populated from latest `SimulationRun` when available |
| Simulation page cross-link | Read-only badge: "مخاطر استراتيجية مرتبطة" when strategic findings reference scenario id — link only, no new simulation UI |
| No simulation redesign | SimulationService unchanged; Risk reads simulation outputs |

### 10.5 Notifications Integration

New notification kinds (add to `notifications/constants.py`):

| Kind | Trigger |
|------|---------|
| `risk_analysis_completed` | `AnalysisService.complete_run` for type `risk` |
| `risk_analysis_failed` | `fail_run` for type `risk` |
| `risk_ai_recommendations_completed` | After risk AI generation |
| `risk_escalated` | Score history delta exceeds threshold |
| `risk_promoted` | Finding promoted to register |

Wire through existing `NotificationBuilder` + `try_materialize` — failures never roll back domain transactions.

User preference gates: extend `DEFAULT_ENABLED_NOTIFICATION_KINDS` in settings constants.

### 10.6 Executive Summary / Workflow Indicator

Existing Product Polish workflow indicator gains optional **Risk Analysis** step after waste (settings-gated):

```
Upload → Waste → [Risk Analysis] → AI → Simulation → Report → PDF
```

Implementation reuses workflow state machine patterns from Sprint D2 — step insertion only, no redesign.

---

## 11. Sprint Plan — Phase 9 Implementation

Balanced sprints building on this architecture. Sprint 9.1 is **documentation only** (this document).

### Sprint 9.1 — Financial Risk Intelligence Architecture ✅

| Item | Detail |
|------|--------|
| **Goal** | Freeze domain, engine, persistence, API, AI, frontend, and sprint plan |
| **Scope** | This document |
| **Dependencies** | Phases 1–8 complete |
| **Acceptance criteria** | Tech Lead approval; no code changes; sufficient for 9.2 without redesign |

### Sprint 9.2 — Risk Engine Core

| Item | Detail |
|------|--------|
| **Goal** | Implement deterministic `RiskEngine` with calculator, detector, scorer, fact assembler, manifest |
| **Scope** | `app/business/engines/risk/*`, `assemblers/risk.py`, `RiskSnapshotAdapterV1`, unit tests, engine registry |
| **Dependencies** | Sprint 9.1 approved |
| **Acceptance criteria** | Engine registered; ≥20 unit tests; Facts Contract validates; no AI imports; no API routes |

### Sprint 9.3 — Risk Analysis Orchestration

| Item | Detail |
|------|--------|
| **Goal** | End-to-end risk analysis execution and persistence |
| **Scope** | Alembic migration (new tables §6), repositories, `RiskAnalysisService`, `DecisionService.execute_risk_analysis`, `RiskGoldMapper`, `risk_analysis.py` API routes |
| **Dependencies** | Sprint 9.2 |
| **Acceptance criteria** | `POST /risk-analyses/execute` succeeds on demo snapshot; findings persisted; analysis run completes; pytest coverage for orchestration |

### Sprint 9.4 — Risk Register Enhancement & Intelligence

| Item | Detail |
|------|--------|
| **Goal** | Promotion workflow, score history, events, summary/matrix APIs |
| **Scope** | Extend `risks` table, `RiskIntelligenceService`, `risk_intelligence.py` routes, extend `RiskService` for category_code and provenance |
| **Dependencies** | Sprint 9.3 |
| **Acceptance criteria** | Promote/dismiss/review findings; summary + matrix endpoints return correct counts; closed-risk rules preserved |

### Sprint 9.5 — Risk AI & Recommendations

| Item | Detail |
|------|--------|
| **Goal** | Risk-domain AI pipeline isolated from waste |
| **Scope** | New prompt tasks, `generate_risk_recommendations`, facts loader extension, API route, recommendation persistence with `domain_source=risk` |
| **Dependencies** | Sprint 9.3 (completed run with facts) |
| **Acceptance criteria** | AI generates Arabic recommendations from facts only; waste `RISK_ANALYSIS` unchanged; Number Guard passes; notification on completion |

### Sprint 9.6 — Risk Frontend Integration

| Item | Detail |
|------|--------|
| **Goal** | Wire Risk Management page to live APIs |
| **Scope** | API client hooks, replace empty state, mount archived components with real data, enum label mapping AR ↔ backend |
| **Dependencies** | Sprints 9.4, 9.5 |
| **Acceptance criteria** | `/risk-management` shows live register, matrix, charts; tsc + lint clean; no placeholder-data imports on active page |

### Sprint 9.7 — Cross-Domain Integration (Dashboard, Reports, Notifications)

| Item | Detail |
|------|--------|
| **Goal** | Integrate risk into dashboard KPIs, risk reports, notification kinds, optional workflow step |
| **Scope** | Dashboard KPI fetch, report sections for type `risk`, notification builder handlers, settings gates for `AnalysisType.RISK` |
| **Dependencies** | Sprints 9.5, 9.6 |
| **Acceptance criteria** | Dashboard critical risk KPI live; risk report PDF includes analysis; notifications fire on analysis complete; integration harness extended |

### Sprint 9.8 — Phase 9 QA & Completion

| Item | Detail |
|------|--------|
| **Goal** | Validation, regression, documentation update, Phase 9 acceptance |
| **Scope** | Tests, integration verify script, `PHASE_9_COMPLETION_REPORT.md`, `progress.md` update |
| **Dependencies** | Sprints 9.2–9.7 |
| **Acceptance criteria** | No Phase 8 regression; risk E2E path verified; Tech Lead sign-off; ready for Phase 10 |

---

## 12. Risks & Open Questions

### 12.1 Architecture Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| **Confusion between waste `RISK_ANALYSIS` and risk-domain AI** | High | Separate prompt tasks; document in AI_ARCHITECTURE addendum; distinct API routes |
| **Register drift vs engine findings** | Medium | Promotion workflow; deduplication keys; score history |
| **Over-scoping Phase 9 with full dashboard aggregation** | Medium | Risk-scoped summary APIs only; Phase 10 owns cross-domain aggregation |
| **AI latency on chained waste → risk → AI pipeline** | Medium | Serialize AI requests (Phase 8 learning); optional skip risk step in demo |
| **category_label vs category_code migration** | Low | Dual-write period; display resolver prefers code |
| **Free-text mitigation plan status** | Low | Introduce `plan_status` enum; map Arabic labels in frontend |

### 12.2 Open Questions (Tech Lead Decision Required)

| ID | Question | Options | Recommendation |
|----|----------|---------|----------------|
| OQ-1 | Auto-promote high-priority findings to register? | A) Manual only B) Auto-promote with review flag | **A — Manual only** for MVP (executive trust) |
| OQ-2 | Chain risk analysis automatically after waste in demo pipeline? | A) Settings off by default B) Always chained | **A** — opt-in via org settings |
| OQ-3 | Require ADR-011 for RiskEngine? | A) New ADR B) Extend ADR-009 | **A — ADR-011** documenting RiskEngine adoption |
| OQ-4 | Single-risk AI without analysis run — in Phase 9? | A) Defer B) Include in 9.5 | **B** — needed for register recommendations on manual risks |
| OQ-5 | Deduplication key for finding → existing risk match | A) category + normalized name B) rule_id + entity key | **B** — more deterministic |

### 12.3 Compliance with Existing Architecture

| Check | Status |
|-------|--------|
| Extends Business Engine pattern (ADR 009) | ✅ Designed |
| Facts before Language (ADR 008) | ✅ Designed |
| Snapshot Silver → Gold (ADR 010) | ✅ Designed |
| Org-scoped auth (ADR 007) | ✅ All endpoints org-scoped |
| ApiResponse envelope | ✅ Specified |
| No duplicate waste functionality | ✅ Cross-domain read only |
| No frontend redesign | ✅ Component reuse plan |
| Existing RiskService lifecycle preserved | ✅ |
| No implementation in Sprint 9.1 | ✅ This document only |

---

## 13. Deliverables Index

| Deliverable | Location |
|-------------|----------|
| **This architecture specification** | `docs/PHASE_9_FINANCIAL_RISK_ARCHITECTURE.md` |
| Future ADR | `docs/ADR/011-risk-engine-architecture.md` (Sprint 9.2) |
| Future schema migration | `backend/alembic/versions/*_risk_intelligence.py` (Sprint 9.3) |
| Future completion report | `docs/PHASE_9_COMPLETION_REPORT.md` (Sprint 9.8) |

---

## 14. Sign-Off

| Criterion | Status |
|-----------|--------|
| Complete Risk architecture documented | ✅ |
| All decisions align with existing Khazina architecture | ✅ |
| No implementation code written | ✅ |
| No database migrations created | ✅ |
| No APIs implemented | ✅ |
| Sufficient for future sprints without major redesign | ✅ Pending Tech Lead review |

**Sprint 9.1 — Financial Risk Intelligence Architecture** is ready for Technical Lead review.

---

*End of Phase 9 Financial Risk Intelligence Architecture.*
