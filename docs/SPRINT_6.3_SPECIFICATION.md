# Sprint 6.3 — Decision Engine

**Phase:** 6 — Business Features  
**Predecessor:** Sprint 6.2 — Financial Statements (Ingestion & Financial Snapshot) — **Complete and approved**  
**Status:** Specification — awaiting Technical Lead approval before implementation  
**Date:** 2026-07-15  

**Normative references (frozen — must not be modified in this sprint):**

- [ADR 008: AI Architecture](ADR/008-ai-architecture.md)
- [ADR 009: Business Engine Architecture](ADR/009-business-engine-architecture.md)
- [ADR 010: Financial Snapshot Architecture](ADR/010-financial-snapshot-architecture.md)
- [AI_FREEZE.md](AI_FREEZE.md)
- [BUSINESS_ENGINE_ARCHITECTURE.md](BUSINESS_ENGINE_ARCHITECTURE.md)
- [SPRINT_6.2_SPECIFICATION.md](SPRINT_6.2_SPECIFICATION.md) — especially §11 Financial Snapshot Contract
- [DATABASE_SCHEMA_DESIGN.md](DATABASE_SCHEMA_DESIGN.md)
- [BUSINESS_DOMAIN_DISCOVERY.md](BUSINESS_DOMAIN_DISCOVERY.md) §5.2, §6.1, §9.2

**Tracker alignment:** `progress.md` (post–Sprint 6.2): *“Next step: Engine sprint — bind Business Engines to Financial Snapshot references.”* Sprint 6.2 §7 explicitly deferred Business Engine execution against snapshots and `analysis_runs` snapshot provenance to this sprint.

---

## Terminology Mapping (Repository Authority)

The label **“Decision Engine”** does **not** appear in the repository. This sprint adopts it as the **Sprint 6.3 product name** for the deterministic Gold-layer execution path. It must **not** introduce a competing architecture to the frozen **Business Engine** layer (ADR-009).

| Sprint 6.3 term | Repository authority | Meaning |
|---|---|---|
| **Decision Engine** | *New sprint label* | Orchestration that binds a Financial Snapshot to a frozen Business Engine, drives the run lifecycle, and persists Gold decision results — **without AI** |
| **Business Rules** | `BUSINESS_ENGINE_ARCHITECTURE.md` §3 — **Calculator** + **Detector** | Deterministic calculations and threshold-based classifications inside the frozen Waste Engine |
| **Financial Facts** | `FactsContract` — `backend/app/business/facts/contract.py` | Versioned, immutable fact collection (`CONTRACT_VERSION = "1.0"`) |
| **Decision Results** | Gold-layer persisted outcomes | Completed `analysis_runs` plus domain result entities (e.g. `waste_analysis_results`, `waste_category_breakdowns`) |

**Not in scope as a separate component:** PROJECT_ROADMAP Phase 6 “rule engine” — mentioned as a future component; **no implementation exists** in the repository. Sprint 6.3 uses the **existing Calculator/Detector pattern** inside the frozen Waste Engine only.

---

## 1. Sprint Goal

Sprint 6.3 delivers the **first end-to-end deterministic decision path** from Silver to Gold:

> **Financial Snapshot (immutable parsed dataset) → frozen Business Engine (Business Rules) → Facts Contract → persisted Decision Results — with explicit snapshot provenance on every analysis run.**

After this sprint:

- A `ready_for_analysis` financial file with an associated Financial Snapshot can trigger **deterministic waste analysis** without re-parsing Bronze files.
- Every completed waste analysis run is **bound to a specific snapshot version**, not to the file alone (ADR-010 §Relationship; Sprint 6.2 deferred item).
- The frozen **Waste Engine** (`backend/app/business/engines/waste/`) executes against snapshot-derived input — not manually supplied DTOs in isolation.
- Gold waste outcomes are **persisted** through the existing waste result model and services — not returned only as ephemeral engine output.
- **No AI module is invoked** anywhere in this path (`AI_FREEZE.md`; ADR-008).

Sprint 6.3 does **not** implement new Business Engines, AI narrative, frontend integration, or report publication.

---

## 2. Business Objective

### Capability unlocked

Executives and analysts gain **reproducible, auditable financial waste decisions** grounded in ingested data:

| Before Sprint 6.3 | After Sprint 6.3 |
|---|---|
| Financial Snapshots exist but have **no consumer** | Snapshots are the **mandatory input reference** for waste analysis |
| Waste Engine runs only against manually constructed `WasteEngineInput` in tests | Waste Engine runs against **snapshot-derived input** in the production service path |
| `analysis_runs` reference `source_file_id` only | Completed runs record **which snapshot version** was analyzed |
| Analysis lifecycle endpoints exist but **do not execute** engines | Decision path **creates, executes, and completes** a waste analysis run deterministically |
| Dashboard/waste domain expects analysis outcomes (`BUSINESS_DOMAIN_DISCOVERY.md` Flow 2) | Backend produces **real Gold waste metrics** from ingested files — frontend wiring remains deferred |

### Business value

Per ADR-010 and platform identity (*Enterprise Financial Decision Intelligence Platform*), decision defense requires:

- **Provenance:** file → snapshot version → analysis → metrics
- **Reproducibility:** same snapshot + same engine version → same facts and Gold results (ADR-009 determinism rule)
- **Separation:** Silver (data as understood at parse time) vs Gold (business conclusions) vs AI (interpretation only — excluded here)

Sprint 6.3 closes the architectural gap between Sprint 6.2 ingestion and Phase 5’s frozen Waste Engine — making **deterministic decision intelligence** operational for the first domain (financial waste).

### Alignment with discovery

`BUSINESS_DOMAIN_DISCOVERY.md` §6.1 Flow 2 — *Executive uploads file → analysis runs → waste categories and savings produced* — is satisfied at the **backend decision layer** for the waste domain. Frontend simulation and loading states remain Phase 7 scope.

---

## 3. Scope

### 3.1 INCLUDED (strict)

| # | Item | Evidence basis |
|---|---|---|
| I-01 | **Decision Engine orchestration** — snapshot resolution, engine dispatch, lifecycle coordination, Gold persistence | `progress.md` next step; ADR-010 pipeline; `AnalysisService` lifecycle exists but does not execute engines |
| I-02 | **Snapshot provenance binding** on analysis runs — explicit reference to Financial Snapshot identity and version | ADR-010 §Relationship (`analysis_runs` must reference snapshot version); Sprint 6.2 §7 deferred item |
| I-03 | **Snapshot-to-Engine Input Adapter (Waste v1)** — maps Financial Snapshot payload (schema v1) to `WasteEngineInput` | ADR-010 §11.9; `ParsedDataset.to_payload()` in `backend/app/ingestion/types.py`; `WasteEngineInput` in `backend/app/business/engines/waste/input.py` |
| I-04 | **Waste Engine execution** via frozen registry — `WasteEngine.run()` producing `FactsContract` | `AI_FREEZE.md` §Implemented Components; ADR-009 |
| I-05 | **Facts-to-Gold mapping** — translate `WasteCalculationResult` / detection outputs into persistable waste result structures | `WasteService.record_result()`; `waste_analysis_results`, `waste_category_breakdowns` tables (`DATABASE_SCHEMA_DESIGN.md` §4.9) |
| I-06 | **Analysis run lifecycle integration** — pending → processing → completed/failed driven by decision execution | `AnalysisService` transitions (`backend/app/services/analysis.py`); design §4.5 lifecycle |
| I-07 | **Precondition enforcement** — source file `processing_status = ready_for_analysis`; snapshot must exist and match org scope | Sprint 6.2 contract §11.5; existing `create_run` file status check |
| I-08 | **Explicit snapshot version selection** — consumer specifies version or an approved default-resolution rule documented in §11 | ADR-010 §11.6 consumer binding — not implicit “latest” without documented rule |
| I-09 | **Failure recording** — adapter validation failures and engine rule violations fail the run with captured failure details | `AnalysisService.fail_run()`; business exception hierarchy (`app/business/exceptions.py`) |
| I-10 | **Determinism verification tests** — same snapshot + engine version → identical Facts Contract output | ADR-009; existing waste engine unit test pattern (`backend/tests/business/test_waste_engine.py`) |
| I-11 | **AI isolation verification** — decision path imports no `app.ai` modules | ADR-009 §8; `AI_FREEZE.md` |
| I-12 | **Timeline event emission** on completed/failed waste decision runs (where analysis lifecycle already records events) | Existing `TimelineEvent` pattern in analysis services |

### 3.2 EXCLUDED (strict)

| # | Item | Deferred to | Evidence |
|---|---|---|---|
| E-01 | **Any AI invocation** — Orchestrator, Context Builder, Prompt Engine, Ollama | Post–Phase 5 ADR sprint | `AI_FREEZE.md`; user constraint “No AI” |
| E-02 | **Facts → narrative, recommendations, reports** | AI / reporting sprints | `BUSINESS_ENGINE_ARCHITECTURE.md` §2; `recommendations` entity exists but is AI-adjacent output |
| E-03 | **New Business Engine implementations** — Financial, Risk, Simulation | Future engine sprints | `AI_ARCHITECTURE.md` §8 Financial Engine planned; `AI_FREEZE.md` §5 |
| E-04 | **Modification of frozen engine internals** — Calculator thresholds, Detector thresholds, Fact Assembler fact keys, manifest, registry | Forbidden without ADR | ADR-009 change control; `BUSINESS_ENGINE_ARCHITECTURE.md` §1 |
| E-05 | **Frontend waste page wiring** | Phase 7 | `PROJECT_ROADMAP.md` Phase 7; Sprint 6.2 §7 |
| E-06 | **Vendor deviation findings persistence** | Future engine/adapter sprint | Waste Engine has **no vendor logic** (`grep` — no vendor references under `engines/waste/`); `waste_vendor_findings` table exists but engine does not populate it |
| E-07 | **Waste trend point generation** | Future sprint | `WasteService` trend upsert exists; not produced by current Waste Engine |
| E-08 | **Department filter / department_id assignment on breakdowns** | Future sprint | Frontend gap noted in discovery; department linkage not defined in engine |
| E-09 | **Re-parse Bronze at analysis time** | Forbidden permanently | ADR-010 Alternative A rejected |
| E-10 | **Snapshot content mutation or engine results written back to snapshot** | Forbidden permanently | ADR-010 §11.7 |
| E-11 | **Financial Engine (ratios, liquidity, profitability)** | Future engine sprint | ADR-010 §Consequences deferred |
| E-12 | **PROJECT_ROADMAP “rule engine” as standalone component** | Phase 6+ scoped delivery | No code exists; not equivalent to Calculator/Detector |
| E-13 | **Report catalog population, export, notifications** | Phase 8+ / ops | Sprint 6.2 §7 |
| E-14 | **Multi-engine batch orchestration in one run** | Future sprint | Single vertical slice: waste only |

---

## 4. Inputs

### 4.1 What enters the Decision Engine?

The Decision Engine accepts a **decision execution request** comprising:

| Input element | Source | Requirement |
|---|---|---|
| **Organization context** | Caller membership scope | Must match snapshot and file ownership |
| **Analysis type** | `AnalysisType` enum | Sprint 6.3: **`financial_waste` only** |
| **Source financial file reference** | `financial_files` | File must exist, belong to org, and be `ready_for_analysis` |
| **Financial Snapshot reference** | `financial_snapshots` | Explicit snapshot identity **or** explicit version with documented resolution rule (§11) |
| **Run title / optional reporting period** | Caller | Passed through to `analysis_runs` per existing model |
| **Optional runtime metadata** | Caller | May supplement but **must not replace** formal snapshot provenance binding |

The Decision Engine **does not** accept:

- Raw uploaded file bytes for calculation
- LLM prompts or AI session identifiers
- Caller-supplied waste KPIs that bypass engine execution (no “manual result injection” path in this sprint)

### 4.2 What data comes from the Financial Snapshot?

Per Sprint 6.2 implementation and ADR-010:

**Snapshot row metadata (identity and provenance):**

| Field | Role |
|---|---|
| `id` | Primary snapshot identity for provenance binding |
| `financial_file_id` | Bronze provenance link |
| `organization_id`, `reporting_period_id` | Scope validation |
| `snapshot_version` | Version binding for reproducibility |
| `parser_version`, `schema_version` | Traceability |
| `record_count`, `materialized_at` | Audit context |
| `import_record_id` | Import accountability link |

**Snapshot payload body (`payload` JSONB — schema v1):**

Structure produced by `ParsedDataset.to_payload()` (`backend/app/ingestion/types.py`):

```
source_file_name
sheets[]
  name
  columns[]
  rows[]
    row_number
    values{ column_name → string | null }
```

Cell values are **normalized strings or null** — not typed business amounts at the Silver layer.

**Companion metadata (not in snapshot body):**

Parse metadata on `financial_files.metadata` — column mappings, sheet names, row counts, parser/schema versions (`ParseMetadata.to_dict()`). The Input Adapter may **read** this metadata to interpret columns; it must **not** treat metadata as the authoritative dataset (ADR-010 §11.2).

**Quality context (read-only gate):**

Snapshot existence implies the ingestion pipeline passed validation and quality thresholds (Sprint 6.2). The Decision Engine **does not re-run** ingestion validation unless an explicit preflight check is added — default: trust snapshot materialization gate.

### 4.3 What assumptions already exist in the repository?

**Frozen Business Engine assumptions (Waste):**

| Assumption | Location | Value / rule |
|---|---|---|
| Engine identity | `WASTE_ENGINE_MANIFEST` | Registered in immutable registry |
| Input shape | `WasteEngineInput` | `total_spend`, `total_waste_amount`, `categories[]`, optional org/period/source_dataset |
| Recoverable savings rate | `WasteCalculator.RECOVERABLE_SAVINGS_RATE` | `0.80` (80%) |
| Savings opportunity threshold | `WasteCalculator.SAVINGS_OPPORTUNITY_THRESHOLD` | Category share ≥ 15% of waste |
| Overall waste level thresholds | `WasteDetector` | High ≥ 10%, Medium ≥ 5% (percentage of spend) |
| Category waste level thresholds | `WasteDetector` | High ≥ 30%, Medium ≥ 15% (percentage of waste) |
| Facts Contract version | `CONTRACT_VERSION` | `"1.0"` |
| Engine output interface | `WasteEngine.run()` | Returns `FactsContract` — no narrative fields |

**Existing Gold persistence assumptions:**

| Assumption | Location |
|---|---|
| Waste results attach 1:1 to `financial_waste` analysis runs | `WasteService` docstring |
| Breakdown rows require category name, amount, percentage | `WasteCategoryBreakdownInput` schema |
| Vendor findings are optional on persist | `WasteResultCreate.vendor_findings` optional — engine does not supply |

**Existing lifecycle assumptions:**

| Assumption | Location |
|---|---|
| Run states: pending → processing → completed/failed | `AnalysisService` |
| File-based runs require `ready_for_analysis` | `AnalysisService.create_run()` |
| Upload sources `repository` and `waste_analysis` share ingestion | `DATABASE_SCHEMA_DESIGN.md` DD-01 |

**Gap assumption (must be resolved in §11 contract — not yet in repository):**

How schema v1 tabular snapshot rows map to `WasteEngineInput` aggregates (which columns represent category, amount, spend, waste). **No mapping specification exists today.** Implementation is gated on §11 approval.

---

## 5. Outputs

### 5.1 What does the Decision Engine produce?

| Output | Layer | Description |
|---|---|---|
| **`analysis_runs` record** | Gold process | Created and driven through lifecycle to `completed` or `failed` |
| **Snapshot provenance record** | Gold process metadata | Binding to specific Financial Snapshot identity and version (§11) |
| **`FactsContract`** | Gold analytical facts (in-memory artifact) | Produced by `WasteEngine.run()`; may be stored in `runtime_metadata` or a dedicated facts store if approved — minimum: reproducible from persisted Gold + snapshot binding |
| **`waste_analysis_results`** | Gold domain | Total waste, waste percentage, top category, potential savings, opportunity count |
| **`waste_category_breakdowns`** | Gold domain | Per-category amounts and percentages aligned with engine calculation output |
| **`TimelineEvent`(s)** | Cross-cutting audit | Analysis completion/failure visible in org timeline |
| **Deterministic decision outcome** | Business | Quantified waste metrics suitable for downstream dashboard aggregation and **future** AI interpretation |

### 5.2 What is intentionally NOT produced?

| Excluded output | Reason |
|---|---|
| AI-generated Arabic/English narrative | AI layer; frozen and out of scope |
| `recommendations` rows | AI-adjacent; discovery notes overlap with dashboard rec IDs — not engine output |
| `reports` rows | Reporting sprint; distinct lifecycle from analysis |
| `waste_vendor_findings` rows | Engine has no vendor detection logic |
| `waste_trend_points` | Not produced by current engine |
| Modified or supplemental snapshot payload | ADR-010 immutability |
| Parse metadata updates on `financial_files` | Bronze metadata owned by ingestion |
| Simulation or risk analysis results | Engines not implemented |
| Frontend-ready presentation DTOs | Phase 7 |

---

## 6. Processing Flow

**Sprint 6.3 pipeline (No AI):**

```
Financial Snapshot (Silver — immutable payload + version metadata)
        ↓
Snapshot-to-Engine Input Adapter (Waste v1)
        ↓
Business Rules (frozen Waste Engine: Calculator → Detector)
        ↓
Financial Facts (Facts Contract v1.0)
        ↓
Decision Results (Gold: analysis_run + waste_analysis_results + breakdowns)
```

**Detailed steps:**

| Step | Actor | Action |
|---|---|---|
| 1 | Decision Engine | Validate org scope, file `ready_for_analysis`, snapshot exists and matches file/org |
| 2 | Decision Engine | Create `analysis_runs` row (`pending`) with file + snapshot provenance |
| 3 | Decision Engine | Transition run → `processing` |
| 4 | Input Adapter | Read snapshot `payload` (+ permitted metadata); produce `WasteEngineInput` |
| 5 | Waste Engine | `run(input)` → Calculator → Detector → Fact Assembler → `FactsContract` |
| 6 | Decision Engine | Map calculation/detection outputs to Gold persist model |
| 7 | Waste persistence path | Record `waste_analysis_results` and `waste_category_breakdowns` |
| 8 | Decision Engine | Transition run → `completed`; emit timeline event |
| **Failure anywhere** | Decision Engine | Transition run → `failed` with structured failure details; **no partial Gold result** unless explicitly approved in §11 |

**Architectural position (ADR-010):**

```
Bronze (file) → [Sprint 6.2 complete] → Silver (snapshot) → [Sprint 6.3] → Gold (facts + results) → [Future] AI → Reports
```

AI sits **strictly downstream** of Facts Contract. Sprint 6.3 **must not** invoke or modify the AI pipeline.

---

## 7. Deliverables

| # | Deliverable | Description |
|---|---|---|
| D-01 | **Sprint 6.3 Specification (this document)** | Approved before implementation |
| D-02 | **Snapshot-to-Engine Input Mapping Contract (§11)** | Normative mapping rules for Waste v1 — **implementation gate** |
| D-03 | **Analysis provenance extension design** | Formal snapshot binding on `analysis_runs` per ADR-010 (field design approved by TL — not specified here as SQL/ORM) |
| D-04 | **Decision Engine orchestration module** | Service-layer component coordinating adapter, engine registry lookup, lifecycle, persistence |
| D-05 | **Snapshot Input Adapter (Waste v1)** | Deterministic, testable mapper: snapshot payload → `WasteEngineInput` |
| D-06 | **Gold result mapper** | Deterministic mapping from engine outputs to waste result persistence model |
| D-07 | **Integration with existing services** | Uses frozen `AnalysisService` lifecycle and `WasteService` persistence — no duplication of CRUD rules |
| D-08 | **Automated test suite** | Unit tests: adapter, mapper, orchestration; integration test: snapshot fixture → completed run with Gold rows |
| D-09 | **AI isolation test** | Static or import-graph verification that decision modules do not depend on `app.ai` |
| D-10 | **Determinism regression test** | Two executions with identical snapshot version and engine version produce byte-identical `FactsContract.to_json()` |
| D-11 | **`progress.md` update** | Sprint 6.3 completion record and next-step pointer |

**Explicit non-deliverables:** REST endpoint specifications, SQL migrations, ORM model code, AI wiring, frontend changes, new engine implementations.

---

## 8. Acceptance Criteria

Sprint 6.3 is **complete only when every criterion passes** Technical Lead review.

### 8.1 Preconditions and provenance

| ID | Criterion |
|---|---|
| AC-01 | Decision execution rejected when source file `processing_status` ≠ `ready_for_analysis` |
| AC-02 | Decision execution rejected when requested snapshot does not belong to the same organization as the run |
| AC-03 | Decision execution rejected when requested snapshot’s `financial_file_id` does not match the run’s source file |
| AC-04 | Completed waste analysis run records **identifiable snapshot provenance** (snapshot identity and version) retrievable alongside the run |
| AC-05 | Explicit snapshot version is used for execution — execution does not re-parse Bronze file bytes |

### 8.2 Input adaptation

| ID | Criterion |
|---|---|
| AC-06 | Input Adapter accepts schema v1 payload shape (`source_file_name`, `sheets[]`, `rows[].values`) |
| AC-07 | Adapter failure (unmapped columns, invalid numeric conversion, empty categories) fails the run with non-empty failure details — no Gold rows persisted |
| AC-08 | Successful adaptation produces `WasteEngineInput` passing existing engine validation rules |

### 8.3 Engine execution (Business Rules → Facts)

| ID | Criterion |
|---|---|
| AC-09 | Waste Engine invoked via frozen registry — not by instantiating ad hoc calculator/detector bypassing `BusinessEngine.run()` |
| AC-10 | Engine execution produces `FactsContract` with `contract_version = "1.0"` and `engine_id` matching waste manifest |
| AC-11 | Facts include at minimum: `waste.total_amount`, `waste.percentage` metrics (per existing assembler) |
| AC-12 | No `app.ai` import in decision engine module graph (verified by automated test) |

### 8.4 Decision Results (Gold persistence)

| ID | Criterion |
|---|---|
| AC-13 | Successful execution creates exactly one `waste_analysis_results` row linked to the analysis run |
| AC-14 | Persisted `total_waste_amount` and `waste_percentage` match engine calculation output (numeric equality within existing money rounding rules) |
| AC-15 | Persisted category breakdown row count equals engine category count; names and amounts match |
| AC-16 | Run lifecycle ends in `completed` with non-null `completed_at` |
| AC-17 | Failed executions end in `failed` with failure details; no orphan `waste_analysis_results` row |

### 8.5 Determinism and isolation

| ID | Criterion |
|---|---|
| AC-18 | Two decision executions against the same snapshot version and frozen engine version produce identical `FactsContract.to_json()` |
| AC-19 | Snapshot payload bytes unchanged after decision execution (immutability spot-check) |
| AC-20 | Full backend test suite passes with Sprint 6.3 tests included |

### 8.6 Documentation

| ID | Criterion |
|---|---|
| AC-21 | `progress.md` records Sprint 6.3 completion, deliverables, and next step |
| AC-22 | §11 Input Mapping Contract marked **Approved** in `progress.md` with TL sign-off date before implementation began |

---

## 9. Technical Risks

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R-01 | **No snapshot→waste mapping exists** — schema v1 is generic tabular; `WasteEngineInput` expects aggregates | Adapter cannot be implemented without arbitrary guesses | §11 contract gate; TL approval before coding |
| R-02 | **Heterogeneous departmental files** — discovery lists budget, procurement, payroll formats | Adapter may work for one template only | Document supported template(s) in §11; explicit adapter failure for unsupported layouts |
| R-03 | **String cell values in snapshot** — amounts are strings at Silver layer | Parsing/ locale errors | Adapter validation with row-level error messages; fail run cleanly |
| R-04 | **Vendor findings expected by domain model but not by engine** | Frontend/domain discovery expects vendor deviations | Explicitly excluded (E-06); document empty vendor findings as expected for 6.3 |
| R-05 | **Provenance schema extension** — ADR-010 requires snapshot binding; field not present in Sprint 6.2 | Migration/design drift | Approve provenance design (D-03) before orchestration |
| R-06 | **“Latest snapshot” ambiguity** — ADR-010 forbids implicit latest without rule | Wrong version analyzed | §11 must define version resolution (explicit only recommended) |
| R-07 | **Scope creep into AI** — temptation to “complete” Flow 2 with narrative | Violates freeze | AC-12; code review gate; no `app.ai` imports |
| R-08 | **Frozen engine modification pressure** — adapter gaps may push threshold changes | ADR violation | Adapter adapts data; engine thresholds change only via new ADR |
| R-09 | **Duplicate persistence paths** — manual `record_waste_result` API vs automated path | Inconsistent Gold data | Decision path becomes canonical producer; document manual path as test/admin only if retained |
| R-10 | **Large snapshot payloads** — memory/time for adaptation | Timeouts on run | Adapter streams sheet rows; fail with performance budget in tests for approved fixture size |

---

## 10. Dependencies

### 10.1 Hard dependencies (must be complete)

| Dependency | Status | Reference |
|---|---|---|
| Sprint 6.2 ingestion pipeline | ✅ Complete | `progress.md` |
| ADR-010 Financial Snapshot | ✅ Accepted | `docs/ADR/010-financial-snapshot-architecture.md` |
| Financial Snapshot persistence | ✅ Implemented | `financial_snapshots` entity |
| Frozen Waste Engine + Facts Contract | ✅ Phase 5 complete | `AI_FREEZE.md` |
| Analysis run lifecycle service | ✅ Exists | `AnalysisService` |
| Waste Gold persistence service | ✅ Exists | `WasteService` |
| Engine registry (frozen) | ✅ Exists | `app/business/registry.py` |

### 10.2 Soft dependencies (inform design, not blockers)

| Dependency | Notes |
|---|---|
| `financial_files.metadata` column mappings | May assist adapter; not authoritative dataset |
| Timeline event conventions | Align with existing analysis events |
| Placeholder frontend waste templates | Inform §11 supported layouts — not runtime dependency |

### 10.3 Downstream consumers (not Sprint 6.3 blockers)

| Consumer | Relationship |
|---|---|
| AI Orchestrator + Context Builder | Future: consumes Facts from completed runs |
| Frontend Waste page | Phase 7: consumes Gold API |
| Dashboard KPI aggregation | Phase 7–8 |
| Reports | Phase 8 |

---

## 11. Snapshot-to-Engine Input Mapping Contract (Waste v1)

**Status:** **APPROVED FOR IMPLEMENTATION** (Technical Lead review, 2026-07-15)  
**Scope:** Financial Snapshot schema v1 → frozen Waste Engine input  
**Gate:** Sprint 6.3 implementation may begin. Adapter must conform to this contract.

**Authority:** ADR-010 (snapshot immutability); `ParsedDataset.to_payload()` / schema v1 (`backend/app/ingestion/types.py`); Waste Engine input validation (`backend/app/business/engines/waste/engine.py`); ingestion column conventions (`backend/tests/ingestion/`); primary business file `Procurement_Q2.xlsx` (`PLACEHOLDER_DATA.md`, `placeholder-data.ts`).

**Determinism principle:** The adapter **never guesses**. Ambiguous sheets or columns are **rejected** — never silently resolved.

---

### 11.1 Supported spreadsheet layout(s)

Sprint 6.3 supports **one layout** for Waste v1:

| ID | Name | Business reference | Row model |
|---|---|---|---|
| **W-1** | **Waste Category Detail** | `Procurement_Q2.xlsx` and equivalent waste uploads | One or more data rows per waste category; duplicate category labels are **aggregated** (summed) |

**Sheet selection (deterministic):** A sheet **qualifies** for W-1 only when §11.2 column resolution succeeds on that sheet (all required semantics resolve to exactly one column; denominator resolves via exactly one path). Then:

| Qualifying sheets | Outcome |
|---|---|
| **0** | Fail: `unsupported_layout` |
| **1** | Process **that sheet only** |
| **>1** | Fail: `ambiguous_layout` — failure detail must list all qualifying sheet names |

The adapter **must not** select a sheet because it appears first in payload order. Order is irrelevant to selection.

**W-1 does not support:** multi-sheet cross-references, pivot tables, headerless sheets, or accounting statement schemas (balance sheet / P&L layouts). Budget-only files (e.g. `Budget_Q2_2026.xlsx`) without waste columns are **unsupported** for the Waste Engine.

---

### 11.2 Column semantics

Header matching is **case-insensitive** and **trimmed**, on snapshot `columns[]` strings.

**Column resolution (deterministic):** Each semantic role must map to **exactly one** column on the candidate sheet. Count every column whose header matches any alias in that role’s set.

| Match count | Outcome |
|---|---|
| **0** | Fail: `missing_required_column` (required roles) or `missing_denominator_column` (denominator) — see §11.5 |
| **1** | Role resolved to that column |
| **>1** | Fail: `ambiguous_column_mapping` — failure detail must name the semantic role and all matching column headers |

The adapter **must not** choose one column when multiple match the same semantic role.

#### Required columns

| Semantic role | Accepted header aliases | Maps to |
|---|---|---|
| **category** | `category`, `waste_category`, `category_name`, `type`, `فئة`, `تصنيف`, `التصنيف` | Waste category name (one per aggregated group) |
| **waste_amount** | `amount`, `waste`, `waste_amount`, `detected_waste`, `cost`, `مبلغ`, `مبلغ_الهدر`, `الهدر` | Per-row waste amount before aggregation |

#### Denominator — exactly one path required

Denominator uses **mutually exclusive** semantic paths. **Exactly one** path below must resolve to exactly one column; all other denominator paths must resolve to **zero** columns. If more than one path has ≥1 matching column → `ambiguous_column_mapping`.

| Path | Semantic role | Accepted header aliases | Derivation rule |
|---|---|---|---|
| **Fixed** | `total_spend_fixed` | `total_spend`, `spend`, `total`, `total_budget`, `إجمالي`, `إجمالي_الإنفاق`, `الميزانية` | **Single distinct positive value** across non-null rows. If multiple distinct values → `ambiguous_total_spend` |
| **Summed (budget)** | `budget` | `budget` | **SUM** of parsed non-null row values |
| **Summed (actual)** | `actual` | `actual` | **SUM** of parsed non-null row values |

If no path satisfies the exclusivity rule → `missing_denominator_column`.

#### Optional columns (recognized but not required)

Optional columns are **not** semantic roles for engine mapping. If an optional header matches aliases in §11.2 required/denominator sets, it participates in resolution counting and can cause `ambiguous_column_mapping` — the adapter does not ignore conflicting headers.

| Header aliases | Adapter behaviour |
|---|---|
| `date`, `period`, `تاريخ`, `فترة` | **Not mapped** to engine input (§11.8) |
| `department`, `dept`, `department_name`, `قسم`, `الإدارة` | **Not mapped** (department breakdown deferred — Sprint 6.3 §3.2 E-08) |
| `vendor`, `vendor_name`, `supplier`, `مورد` | **Not mapped** (no vendor engine logic) |
| `percentage`, `percent`, `pct`, `نسبة` | **Not mapped** — percentages are engine output |
| `description`, `notes`, `comment`, `ملاحظات` | **Not mapped** |

---

### 11.3 Mapping rules

1. **Sheet resolution:** Evaluate every sheet independently per §11.1. Proceed only when exactly one sheet qualifies.
2. **Column resolution:** On the qualified sheet, resolve every required semantic role and exactly one denominator path per §11.2 before reading row data.
3. **Row filter:** Skip rows where all cell values are null/empty. Skip rows with empty/whitespace `category`. Skip rows with null/empty `waste_amount` (non-counting).
4. **Numeric parse:** Strip commas and spaces; allow optional trailing `%` (stripped before parse). Must parse to finite float ≥ 0. Same rules as ingestion validator intent (`backend/app/ingestion/validator.py`).
5. **Aggregation:** Group by trimmed `category`; `categories[].amount` = **SUM** of row `waste_amount` values per group. Preserve first-seen category label spelling after trim.
6. **total_waste_amount:** **SUM** of aggregated category amounts (not read from a spreadsheet total column).
7. **total_spend:** Apply §11.2 denominator derivation on the **qualified sheet** only.
8. **Context fields (not from spreadsheet):**

| Field | Source |
|---|---|
| `organization_id` | Snapshot / analysis run organization (string UUID) |
| `period` | Reporting period label from run or snapshot `reporting_period_id` context; null if unscoped |
| `source_dataset` | Literal `financial_snapshot_v1` |
| `generated_at` | Adapter execution timestamp (UTC) |

9. **Determinism:** Same snapshot payload bytes → identical engine input object.

---

### 11.4 Validation rules

Adapter validates **before** invoking Waste Engine. Engine validation (`total_spend > 0`, category sum = `total_waste_amount`, etc.) remains authoritative on the produced input.

| ID | Rule | On violation |
|---|---|---|
| V-01 | Snapshot payload conforms to schema v1 (`source_file_name`, `sheets[]`, `rows[].values`) | Fail: `invalid_snapshot_schema` |
| V-02 | Exactly one sheet qualifies for W-1 (§11.1) | Fail: `unsupported_layout` or `ambiguous_layout` |
| V-03 | Each required semantic role resolves to exactly one column (§11.2) | Fail: `missing_required_column` or `ambiguous_column_mapping` |
| V-04 | Exactly one denominator path resolves (§11.2) | Fail: `missing_denominator_column` or `ambiguous_column_mapping` |
| V-05 | After row filter, ≥ 1 category with amount > 0 | Fail: `no_waste_categories` |
| V-06 | All parsed waste amounts ≥ 0 | Fail: `invalid_waste_amount` + sheet/row |
| V-07 | Denominator resolves to value > 0 | Fail: `invalid_total_spend` |
| V-08 | `total_waste_amount` ≤ `total_spend` | Fail: `waste_exceeds_spend` |
| V-09 | Aggregated category sum equals `total_waste_amount` (±0.01 after round half-up to 2 dp) | Fail: `category_sum_mismatch` |
| V-10 | Category names non-empty after trim | Fail: `empty_category` + row |

---

### 11.5 Missing-column and ambiguous-column behavior

| Condition | Error code | Failure detail must include |
|---|---|---|
| Zero sheets qualify for W-1 | `unsupported_layout` | All sheet names scanned |
| Required semantic role: zero matching columns | `missing_required_column` | Sheet name; semantic role name |
| Required semantic role: >1 matching columns | `ambiguous_column_mapping` | Sheet name; semantic role; all matching headers |
| Denominator: no exclusive path resolves | `missing_denominator_column` | Sheet name; accepted path/alias list |
| Denominator: >1 path has matching columns | `ambiguous_column_mapping` | Sheet name; conflicting paths or roles |
| Denominator path `total_spend_fixed`: >1 distinct positive values | `ambiguous_total_spend` | Distinct value count |
| Required cell null on non-skipped row | Row skipped if waste_amount null; category null → `empty_category` | Sheet + row_number |

All failures above → analysis run **`failed`**; **no** engine invocation; **no** Gold persistence.

---

### 11.6 Unsupported-layout and ambiguous-layout behavior

| Condition | Error code | Outcome |
|---|---|---|
| Payload not schema v1 | `unsupported_snapshot_schema` | Fail run |
| Zero qualifying W-1 sheets | `unsupported_layout` | Fail run; message states Waste v1 requires layout W-1 |
| **More than one qualifying W-1 sheet** | **`ambiguous_layout`** | Fail run; list all qualifying sheet names |
| File ingested but no sheet achieves unambiguous column resolution | `unsupported_layout` or `ambiguous_column_mapping` | Fail run per §11.5 |
| Semantic columns match no alias set (e.g. payroll-only columns) | `unsupported_layout` | Fail run |

Unsupported or ambiguous layout is **not** a partial map. The adapter must not guess sheet intent, column intent, or denominator path beyond §11.2 rules.

---

### 11.7 Engine input object (conceptual)

The adapter output is one **Waste Engine input** structure conceptually equivalent to:

| Field | Type (conceptual) | Origin |
|---|---|---|
| `total_spend` | Positive decimal (2 dp) | §11.2 denominator rule |
| `total_waste_amount` | Non-negative decimal (2 dp) | Sum of aggregated categories |
| `categories` | Ordered list (stable sort: category name ascending Unicode) | |
| `categories[].category_name` | Non-empty string | Aggregated group key |
| `categories[].amount` | Non-negative decimal (2 dp) | Aggregated sum |
| `organization_id` | String or null | Run/snapshot context |
| `period` | String or null | Reporting period context |
| `source_dataset` | `"financial_snapshot_v1"` | Constant |
| `generated_at` | UTC datetime | Adapter timestamp |

This object is passed to frozen `WasteEngine.run()`. The adapter **does not** compute waste percentages, severity levels, savings, or facts.

---

### 11.8 Explicitly NOT mapped

| Snapshot / spreadsheet content | Reason |
|---|---|
| Vendor / supplier columns | Waste Engine has no vendor logic (Sprint 6.3 §3.2 E-06) |
| Department columns | Gold `department_id` on breakdowns deferred |
| Date / period columns | Period comes from org reporting context only |
| Percentage columns | Computed by Calculator, not read from file |
| Quality scores, parse metadata, `financial_files.metadata` | Not authoritative dataset (ADR-010 §11.2) |
| Sheets that do not qualify as the sole W-1 sheet | Out of scope once single sheet is resolved |
| Row numbers, sheet names, file name | Audit context only; not engine fields |
| AI narrative fields | AI isolated |

---

### 11.9 Snapshot version rule

Execution uses the **explicit snapshot version** supplied with the decision request. If policy allows defaulting: highest `snapshot_version` for the source file — must be recorded in run provenance. Adapter reads **only** the bound snapshot payload; never Bronze bytes.

---

### 11.10 Contract approval

| Field | Requirement |
|---|---|
| **Approver** | Technical Lead |
| **Prerequisite for** | Sprint 6.3 implementation |
| **Status** | **APPROVED FOR IMPLEMENTATION** (2026-07-15) |
| **TL changes applied** | (1) Exactly-one qualifying sheet — `ambiguous_layout` when >1; (2) Exactly-one column per semantic role — `ambiguous_column_mapping` when >1 |
| **Deviation policy** | Alias or layout changes → TL approval; architectural changes → ADR |

---

## 12. Implementation Order

Logical sequence for implementation engineers. **Do not skip ordering** — each step depends on prior steps.

### Step 1 — Specification and contract approval

- Approve this document (Sprint 6.3 Specification).
- Approve §11 Snapshot-to-Engine Input Mapping Contract (Waste v1) — including supported template column mapping.
- Approve analysis provenance extension design (D-03).
- Record approvals in `progress.md`.

### Step 2 — Provenance model

Implement approved snapshot binding on analysis runs. Verify org/file/snapshot integrity constraints.

### Step 3 — Input Adapter (Waste v1)

Implement deterministic adapter with unit tests against schema v1 fixture payloads (valid, missing column, bad numeric, empty categories).

### Step 4 — Gold result mapper

Implement mapping from `WasteCalculationResult` (+ category rows) to waste persistence model fields. Unit test numeric alignment with calculator output.

### Step 5 — Decision Engine orchestration

Wire: precondition checks → run creation → processing → adapter → registry engine execution → Gold persist → complete/fail → timeline.

### Step 6 — Integration tests

End-to-end: ingest fixture file (or use snapshot fixture) → decision execute → assert run completed, provenance set, Gold rows match engine output, Facts JSON deterministic.

### Step 7 — Isolation and regression

AI isolation test; full suite green; update `progress.md`.

---

## 13. Technical Lead Recommendation

### Recommendation: **APPROVE specification — conditional on §11 Input Mapping Contract approval**

| Factor | Assessment |
|---|---|
| **Architectural fit** | Directly implements ADR-010 deferred consumer binding and `progress.md` next step without violating ADR-008/009 freezes |
| **Scope discipline** | Single vertical slice (waste only) avoids Phase 6 roadmap scope creep (Financial Engine, rule engine, simulation) |
| **Reuse** | Maximizes existing Waste Engine, Facts Contract, AnalysisService, WasteService — minimal new concepts |
| **AI safety** | Pipeline ends at Gold; no Orchestrator involvement — aligns with user “No AI” mandate |
| **Primary gate** | §11 mapping contract — **do not implement adapter without TL-approved column semantics** |
| **Known gap acceptance** | Vendor findings and trend points explicitly deferred — document for frontend/domain stakeholders |

### Conditions for implementation start

1. **This specification approved** — TL sign-off recorded.
2. **§11 Input Mapping Contract approved** — at least one waste spreadsheet layout with confirmed column mapping.
3. **Provenance binding design (D-03) approved** — satisfies ADR-010 audit question.
4. **No concurrent modification** to frozen `app/business/engines/waste/` internals or `app.ai/`.

### Suggested next sprint after 6.3

Per PROJECT_ROADMAP and ADR-010 deferred items: **Financial Engine snapshot binding**, **AI orchestration wired to completed run Facts**, or **frontend Waste page integration** — each requires separate sprint approval.

---

## Document Control

| Field | Value |
|---|---|
| **Author** | AI-assisted specification (Sprint 6.3) |
| **Approver** | Technical Lead — pending |
| **Implementation start** | **Approved after §11 contract sign-off** |
| **Code constraint** | No implementation in this specification task |
