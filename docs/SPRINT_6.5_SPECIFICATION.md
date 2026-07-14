# Sprint 6.5 — Scenario Analysis

**Phase:** 6 — Business Features  
**Predecessor:** Sprint 6.4 — AI Recommendations — **Complete and approved**  
**Status:** **APPROVED FOR IMPLEMENTATION** (Technical Lead review, 2026-07-15)  
**Date:** 2026-07-15  

**TL adjustments applied (2026-07-15):**

1. **Three preemptive mapping contracts rejected** — Sprint 6.5 reuses established architectural patterns (ADR-010, Financial Snapshot Contract, Snapshot-to-Engine Mapping Contract pattern, deterministic output-mapping discipline) instead of introducing separate baseline, parameters, and Facts-to-Gold contracts.
2. **Implementation may proceed directly** upon this specification approval — no additional contract gates.
3. **Gap discovery protocol** — if implementation discovers a genuine architectural gap not covered by existing patterns, document that **single gap** and stop for Technical Lead review. Do not create preemptive contracts.

**Normative references (frozen — must not be modified in this sprint):**

- [ADR 008: AI Architecture](ADR/008-ai-architecture.md)
- [ADR 009: Business Engine Architecture](ADR/009-business-engine-architecture.md)
- [ADR 010: Financial Snapshot Architecture](ADR/010-financial-snapshot-architecture.md)
- [AI_FREEZE.md](AI_FREEZE.md)
- [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)
- [BUSINESS_ENGINE_ARCHITECTURE.md](BUSINESS_ENGINE_ARCHITECTURE.md)
- [SPRINT_6.2_SPECIFICATION.md](SPRINT_6.2_SPECIFICATION.md) — §11 Financial Snapshot Contract
- [SPRINT_6.3_SPECIFICATION.md](SPRINT_6.3_SPECIFICATION.md) — Decision Engine pattern; §11 Snapshot-to-Engine Mapping Contract (pattern authority)
- [SPRINT_6.4_SPECIFICATION.md](SPRINT_6.4_SPECIFICATION.md) — §11 deterministic output-mapping discipline (AI out of scope; pattern reused for Facts → Gold)
- [DATABASE_SCHEMA_DESIGN.md](DATABASE_SCHEMA_DESIGN.md) — §4.15–§4.22 simulation tables
- [BUSINESS_DOMAIN_DISCOVERY.md](BUSINESS_DOMAIN_DISCOVERY.md) §5.5, §6.1 Flow 4, §9.5

**Tracker alignment:** `progress.md` (post–Sprint 6.4): *“Next step: Frontend Waste/Dashboard recommendation consumption (Phase 7), Number Guard hardening, or Financial Engine — separate sprint approval required.”* Sprint 6.5 addresses the **simulation engine gap** identified across discovery, schema design, and the existing `SimulationService` docstring: *“Forecast computation is out of scope.”*

---

## Terminology Mapping (Repository Authority)

| Sprint 6.5 term | Repository authority | Meaning |
|---|---|---|
| **Scenario Analysis** | *Sprint 6.5 product name* | Deterministic what-if execution path from Financial Snapshot + scenario parameters to persisted simulation Gold results |
| **Scenario Engine** | *Sprint 6.5 orchestration name* | Binds snapshot baseline, scenario parameters, and optional decision results; dispatches Scenario Business Engine; persists Gold — **without AI** |
| **Scenario Parameters** | `simulation_assumptions` — `backend/app/db/models/simulation.py` | Label/value assumption rows attached to a `simulation_scenarios` record |
| **Scenario Result** | Simulation Gold layer | Completed `analysis_runs` (`analysis_type = simulation`) + `simulation_runs` + result child tables |
| **Delta Analysis** | Engine + mapper output | Baseline vs projected comparison (forecast summary, comparison metrics, chart points, impact items) |
| **Decision Results (baseline)** | Sprint 6.3 Gold output | Optional completed `financial_waste` run with `waste_analysis_results` and `runtime_metadata.facts_contract` |
| **Financial Facts** | `FactsContract` — `backend/app/business/facts/contract.py` | Versioned deterministic engine output (`CONTRACT_VERSION = "1.0"`) — stored on run for audit; **not passed to AI in this sprint** |

**Critical constraint:** The label **“Scenario Engine”** in `AI_ARCHITECTURE.md` §8 refers to *what-if inputs against fixed baseline facts* at the AI layer. Sprint 6.5 introduces a **deterministic orchestration service** with the same product name class — it **does not invoke AI**, **does not modify frozen AI modules**, and **does not modify frozen Waste Engine internals**.

**Existing service boundary:** `SimulationService` (`backend/app/services/simulation.py`) already owns scenario CRUD, run lifecycle, and Gold persistence validation. Sprint 6.5 adds **computation and orchestration** — it must **compose** existing persistence APIs, not redesign CRUD semantics.

---

## 1. Sprint Goal

Sprint 6.5 delivers the **first end-to-end deterministic scenario simulation path** from Silver baseline to simulation Gold:

> **Financial Snapshot (immutable baseline) + Scenario Parameters → Scenario Engine → Scenario Business Engine → Facts Contract → persisted Scenario Results (forecast, delta, impact) — with snapshot provenance and zero mutation of the source snapshot.**

After this sprint:

- A `simulation_scenarios` record with assumptions can be **executed against a bound Financial Snapshot** to produce real baseline vs projected outcomes.
- Scenario execution creates/completes the existing **`analysis_runs` + `simulation_runs`** lifecycle with **`source_snapshot_id` provenance** (ADR-010; column exists from Sprint 6.3 migration).
- **Delta analysis** (forecast summary, comparison metrics, quarterly chart points, departmental impact) is **computed deterministically** and persisted through existing simulation result tables — not supplied manually via `POST /runs/{id}/results`.
- Optional **baseline enrichment** from a completed waste **Decision Result** is supported read-only; it never re-runs the Waste Engine during scenario execution.
- **No AI module is invoked** (`AI_FREEZE.md`; user constraint *“No AI changes”*).
- The original Financial Snapshot row and payload remain **immutable** (ADR-010 §11.7).

Sprint 6.5 does **not** deliver frontend wiring, simulation-domain AI recommendations, reports, Monte Carlo simulation, or Financial Engine ratio analysis.

---

## 2. Business Objective

### Capability unlocked

Executives gain **reproducible what-if scenario analysis** grounded in ingested financial data:

| Before Sprint 6.5 | After Sprint 6.5 |
|---|---|
| Simulation API persists **caller-supplied** results (`SimulationService.record_run_results`) | Scenario execution **computes and persists** results from snapshot + parameters |
| `run_scenario()` creates a processing run but performs **no forecast computation** | Scenario Engine **completes** the run with deterministic Gold outputs |
| Frontend simulation page uses **static placeholder data** (`frontend/lib/placeholder-data.ts`) | Backend produces **real simulation result rows** retrievable via existing simulation GET endpoints |
| Simulation domain depends on **implicit baseline financial data** (discovery §6.2) | Baseline is **explicitly bound** to a Financial Snapshot version (+ optional waste Decision Result) |
| `PromptTask.SCENARIO_ANALYSIS` exists but has **no production Facts pipeline** (Sprint 6.4 E-08) | Facts Contract produced and stored on run — **AI consumption deferred** to a future sprint |
| Scenario assumptions are display-only strings | Assumptions are **parsed into typed Scenario Parameters** driving deterministic engine input |

### Business value

Per `BUSINESS_DOMAIN_DISCOVERY.md` §5.5 and Flow 4:

- **Decision support without commitment:** executives compare baseline vs projected outcomes before operational changes.
- **Auditability:** file → snapshot version → scenario run → computed metrics (extends ADR-010 provenance chain).
- **Determinism:** same snapshot + same parameters + same engine version → identical Facts and Gold results (ADR-009).
- **Separation:** Silver (baseline data) vs Gold (scenario conclusions) vs AI (interpretation — excluded here).

Sprint 6.5 closes the gap between Phase 3 simulation **persistence scaffolding** and Phase 5’s **Business Engine pattern** — making **scenario analysis** operational for the first vertical slice aligned with frozen frontend placeholder archetypes.

### Alignment with discovery

`BUSINESS_DOMAIN_DISCOVERY.md` §6.1 Flow 4 — *Executive selects scenario → reviews assumptions → runs simulation → compares baseline vs projected → reviews impact by department* — is satisfied at the **backend scenario layer**. Frontend loading states and editable parameters remain Phase 7 scope (`FRONTEND_SPECIFICATION.md` §Business Simulation Out of Scope).

---

## 3. Scope

### 3.1 INCLUDED (strict)

| # | Item | Evidence basis |
|---|---|---|
| I-01 | **Scenario Engine orchestration** — snapshot resolution, parameter parsing, optional baseline decision binding, engine dispatch, Gold persistence | `SimulationService` docstring defers computation; Sprint 6.3 `DecisionService` pattern |
| I-02 | **Scenario Business Engine (v1)** — new registered engine following ADR-009 layered pipeline; **does not modify** frozen Waste Engine | `BUSINESS_ENGINE_ARCHITECTURE.md` lists Scenario as planned; only Waste implemented |
| I-03 | **Financial Snapshot baseline adapter (Scenario v1)** — read-only mapping from snapshot payload to baseline financial input, following Sprint 6.3 §11 adapter discipline | ADR-010 §11.9; `WasteSnapshotAdapterV1` precedent |
| I-04 | **Scenario Parameters adapter** — maps `simulation_assumptions` label/value rows to typed `ScenarioEngineInput` using same fail-closed determinism as §11 adapters | `simulation_assumptions` model; placeholder assumption labels in `placeholder-data.ts` |
| I-05 | **Optional Decision Results baseline cross-check** — read completed `financial_waste` run + Gold row for enrichment/validation; **read-only** | Sprint 6.3 outputs; discovery §6.2 “Simulation depends on baseline financial data” |
| I-06 | **Facts Contract production** — Scenario Engine stores `facts_contract` in `analysis_runs.runtime_metadata` on success | Sprint 6.3 `complete_run` pattern |
| I-07 | **Scenario Gold mapper** — deterministic Facts → simulation result tables (mirror `WasteGoldMapper` / Sprint 6.4 mapper discipline) | `DATABASE_SCHEMA_DESIGN.md` §4.18–§4.22; `SimulationService.record_run_results` field validation |
| I-08 | **Analysis run lifecycle integration** — `AnalysisType.SIMULATION`; pending/processing → completed/failed driven by scenario execution | Existing `SimulationService.run_scenario` creates processing run; must complete/fail consistently |
| I-09 | **Snapshot provenance binding** — `analysis_runs.source_snapshot_id` (+ `source_file_id` from snapshot) on every scenario execution | ADR-010; `analysis_runs.source_snapshot_id` column |
| I-10 | **Immutability enforcement** — no writes to `financial_snapshots`, no Bronze re-parse, no snapshot payload mutation | ADR-010 §11.7; user rule |
| I-11 | **Determinism verification tests** — same snapshot + parameters + engine version → identical Facts and Gold payloads | ADR-009; Sprint 6.3 determinism test pattern |
| I-12 | **AI isolation verification** — Scenario Engine module graph excludes `app.ai` | ADR-009 §8; `AI_FREEZE.md` |
| I-13 | **Frozen engine isolation** — Scenario Engine must not modify `app/business/engines/waste/` or frozen registry entries | Business Engine Freeze |
| I-14 | **Execution entry point** — API/service method to execute scenario against snapshot (replaces manual results POST as primary production path) | Existing `POST .../scenarios/{id}/run` creates run only |
| I-15 | **Scenario archetype v1** — three deterministic templates aligned with placeholder scenarios: spending reduction, supplier consolidation, market expansion | `placeholder-data.ts` `sim-001`, `sim-002`, `sim-003` |
| I-16 | **Automated test suite** — adapter, engine, mapper, orchestration, isolation; mocked persistence where appropriate | Phase 6 test patterns (`tests/decision/`, `tests/business/`) |

### 3.2 EXCLUDED (strict)

| # | Item | Deferred to | Evidence |
|---|---|---|---|
| E-01 | **Any AI invocation** — Orchestrator, Context Builder, `PromptTask.SCENARIO_ANALYSIS`, Ollama | Future simulation-AI sprint | Sprint 6.4 scope; `AI_FREEZE.md` |
| E-02 | **Simulation-domain recommendation registration** | Future AI sprint | Sprint 6.4 waste-only; `RecommendationDomain.SIMULATION` exists but not in scope |
| E-03 | **Modification of frozen Waste Engine internals** | Forbidden without ADR | Business Engine Freeze |
| E-04 | **Modification of frozen AI modules** | Forbidden without ADR | `AI_FREEZE.md` §4 |
| E-05 | **Modification of Facts Contract structure** | Forbidden without ADR | `CONTRACT_VERSION = "1.0"` frozen |
| E-06 | **Frontend simulation page wiring** | Phase 7 | `FRONTEND_SPECIFICATION.md` §Business Simulation |
| E-07 | **Editable scenario parameter UI** | Phase 7 | Frontend spec Out of Scope |
| E-08 | **Monte Carlo / probabilistic simulation** | Future sprint | `FRONTEND_SPECIFICATION.md` Risk/Simulation Out of Scope |
| E-09 | **Financial Engine (ratios, liquidity, profitability)** | Future engine sprint | ADR-010 deferred |
| E-10 | **Risk Engine execution** | Future sprint | No risk engine under `app/business/engines/` |
| E-11 | **Report catalog population, export** | Phase 8+ | Discovery §5.6 |
| E-12 | **Number Guard** | Future hardening sprint | Sprint 6.4 §3.3 |
| E-13 | **Re-parse Bronze at scenario time** | Forbidden permanently | ADR-010 |
| E-14 | **Writing engine outputs back to Financial Snapshot** | Forbidden permanently | ADR-010 §11.7 |
| E-15 | **Manual `POST /runs/{id}/results` as primary workflow** | Deprecated for production after execute path ships; endpoint may remain for admin/testing with TL approval | Current Phase 3 CRUD pattern |
| E-16 | **Multi-scenario batch comparison in one request** | Future sprint | Single scenario execution per request |
| E-17 | **New database tables** — use existing simulation Gold schema unless TL approves extension | Schema design §4.15–§4.22 complete |
| E-18 | **Department entity assignment on impact rows** | Future sprint | Discovery §5.8 departments as string literals only |
| E-19 | **Preemptive mapping contracts** — no separate baseline, parameters, or Facts-to-Gold contract documents | Forbidden — TL directive 2026-07-15 |

---

## 4. Inputs

### 4.1 Financial Snapshot

**Role:** Immutable **baseline substrate** for scenario computation. The Scenario Engine **reads** snapshot identity and payload; it never mutates the snapshot.

| Input element | Source | Requirement |
|---|---|---|
| **Snapshot reference** | `financial_snapshots` | Explicit `source_snapshot_id` **or** explicit `snapshot_version` with documented resolution rule (mirror Sprint 6.3 §11) |
| **Source file linkage** | Snapshot row | `financial_file_id` propagated to `analysis_runs.source_file_id` |
| **Organization scope** | Snapshot row | Must match caller org and scenario org |
| **File readiness** | `financial_files.processing_status` | Must be `ready_for_analysis` |
| **Payload body** | `financial_snapshots.payload` JSONB (schema v1) | Read-only; structure per Sprint 6.2 / ADR-010 |
| **Provenance metadata** | `snapshot_version`, `parser_version`, `schema_version`, `reporting_period_id` | Stored on analysis run / runtime metadata for audit |

**Snapshot payload shape (authoritative):**

Per Sprint 6.2 — `ParsedDataset.to_payload()`:

```
source_file_name
sheets[]
  name
  columns[]
  rows[]
    row_number
    values{ column_name → string | null }
```

The Scenario v1 Input Adapter extracts **baseline financial totals and category breakdowns** required by the Scenario Business Engine. Mapping rules follow the **Snapshot-to-Engine Mapping Contract pattern** established in Sprint 6.3 §11 — fail-closed sheet/column resolution, no guessing, deterministic error codes (`unsupported_layout`, `ambiguous_layout`, `ambiguous_column_mapping`, etc.).

### 4.2 Existing Decision Results

**Role:** Optional **baseline enrichment and cross-check** — not a substitute for snapshot binding.

| Input element | Source | Requirement |
|---|---|---|
| **Baseline analysis run reference** | Caller-supplied optional `baseline_analysis_run_id` | If present: run must be `completed`, `analysis_type = financial_waste`, same org |
| **Gold waste result** | `waste_analysis_results` | Must exist for referenced run when baseline run supplied |
| **Facts Contract (read-only)** | `runtime_metadata.facts_contract` | Rehydrated for cross-check only; Scenario Engine **does not** invoke Waste Engine |
| **Usage** | Scenario Engine | May validate snapshot-derived baseline against waste Gold metrics; may enrich category-level impact inputs |

**If no baseline run is supplied:** scenario executes using snapshot-derived baseline only.

**If supplied baseline conflicts with snapshot beyond documented tolerance:** fail execution with deterministic error — do not silently prefer one source.

### 4.3 Scenario Parameters

**Role:** What-if assumptions driving projected outcomes.

| Input element | Source | Requirement |
|---|---|---|
| **Scenario identity** | `simulation_scenarios` | Must exist, belong to org |
| **Scenario status** | `simulation_scenarios.status` | Execution allowed from `draft` or `completed` (re-run creates new run); scenario edited only while `draft` per existing service rules |
| **Assumptions** | `simulation_assumptions` rows | At least one assumption; parsed by Scenario Parameters adapter |
| **Archetype resolution** | Derived from scenario name/description/assumption keys | Must resolve to one of v1 archetypes: `spending_reduction`, `supplier_consolidation`, `market_expansion` |
| **Horizon** | Assumption or default | Default **3 quarters** aligned with placeholder chart series |

**Canonical assumption labels (v1 — aligned with placeholder data):**

| Archetype | Required assumption concepts | Placeholder reference |
|---|---|---|
| `spending_reduction` | reduction percentage, scope, revenue impact (none/flat), time horizon | `sim-001` assumptions |
| `supplier_consolidation` | suppliers before, suppliers after, admin savings rate, implementation duration | `sim-002` assumptions |
| `market_expansion` | revenue growth rate, expansion cost, target markets (informational), payback period (informational) | `sim-003` assumptions |

Assumption parsing follows the same **fail-closed adapter discipline** as Sprint 6.3 §11 — canonical label aliases, archetype resolution, deterministic rejection on ambiguity. Mapping rules are implemented in code and tests; no separate contract document.

### 4.4 Organization Context

| Input element | Source | Requirement |
|---|---|---|
| **Organization ID** | Caller membership scope | Must match scenario, snapshot, and optional baseline run |
| **Reporting period** | `analysis_runs.reporting_period_id` or snapshot binding | Optional; enriches context and display labels |
| **Run title** | Scenario name (default) or caller override | Passed to `analysis_runs.title` |

---

## 5. Outputs

### 5.1 Produced artifacts

| Output | Description | Persistence target (conceptual) |
|---|---|---|
| **Scenario Result** | Completed simulation analysis run + 1:1 simulation run with summary fields | `analysis_runs` (`analysis_type = simulation`, `status = completed`) + `simulation_runs` |
| **Delta Analysis** | Baseline vs projected comparison at summary and metric level | `simulation_forecast_summaries` (1:1); `simulation_comparison_metrics` (1–3 rows v1) |
| **Impact Metrics** | Department/category impact breakdown with direction | `simulation_impact_items` (per archetype template) |
| **Scenario Summary** | Human-readable result title and description derived from engine outcome | `simulation_runs.result_title`, `result_description`, optional `confidence_label` |
| **Chart series** | Quarterly baseline vs projected numeric points | `simulation_chart_points` (3 points default horizon) |
| **Action items** | Deterministic follow-up proposals from engine rules (not AI) | `simulation_action_items` |
| **Facts Contract** | Versioned deterministic facts from Scenario Business Engine | `analysis_runs.runtime_metadata.facts_contract` |
| **Provenance metadata** | Snapshot id/version, scenario id, archetype, engine version, optional baseline run id | `analysis_runs.runtime_metadata.scenario_provenance` (conceptual key) |

**Forecast summary field rules (existing schema):**

Per `DATABASE_SCHEMA_DESIGN.md` §4.18.1:

- `baseline_value`, `projected_value`, `delta_value` on `simulation_forecast_summaries` are **presentation display strings** (Arabic-formatted currency/percentages).
- **Canonical numeric business data** for charts and cross-domain calculation resides in `simulation_chart_points.baseline_amount` / `projected_amount`.

The mapper must derive display strings **deterministically** from numeric engine outputs — never accept caller-formatted strings in the execute path.

### 5.2 Intentionally NOT produced

| Excluded output | Reason |
|---|---|
| AI narrative or `PromptTask.SCENARIO_ANALYSIS` output | AI freeze; user constraint |
| `recommendations` rows (`domain_source = simulation`) | Sprint 6.4 class deferred to simulation-AI sprint |
| Modified Financial Snapshot | ADR-010 immutability |
| Modified waste Gold results | Baseline is read-only |
| Monte Carlo confidence intervals | Out of scope E-08 |
| Reports / PDFs | Reporting sprint |
| Frontend-formatted DTOs | Phase 7 |
| New calculated KPIs outside engine fact keys | Business Engine responsibility |

---

## 6. Processing Flow

**Sprint 6.5 pipeline (normative):**

```
Financial Snapshot (immutable baseline — read-only)
        ↓
Scenario Parameters (simulation_assumptions → typed input)
        ↓
Scenario Engine (orchestration — no AI)
        ↓
Scenario Business Engine (deterministic computation)
        ↓
Facts Contract
        ↓
Scenario Results (simulation Gold persistence)
```

**Optional read-only branch (dashed):**

```
Existing Decision Results (completed financial_waste run)
        ↓ (cross-check / enrich baseline only)
Scenario Engine
```

**Detailed steps:**

| Step | Actor | Action |
|---|---|---|
| 1 | Scenario Engine | Validate org scope, scenario exists, snapshot exists and is `ready_for_analysis` |
| 2 | Scenario Engine | Resolve Financial Snapshot (explicit id/version rule) — **read payload only** |
| 3 | Scenario Engine | Load and parse `simulation_assumptions` → `ScenarioEngineInput` parameters |
| 4 | Scenario Engine | Optionally load baseline Decision Result; cross-check/enrich — **no Waste Engine invocation** |
| 5 | Scenario Engine | Create `analysis_runs` (`simulation`, `processing`) + `simulation_runs` 1:1 (compose existing `SimulationService.run_scenario` or equivalent internal step) |
| 6 | Baseline Adapter | Map snapshot payload → baseline financial structure |
| 7 | Scenario Business Engine | `engine.run(scenario_input)` → `FactsContract` |
| 8 | Scenario Gold Mapper | Map Facts + engine structured output → Gold table payloads (deterministic; no partial persistence on failure) |
| 9 | Scenario Engine | Persist via existing simulation result persistence; complete analysis run; store `facts_contract` + provenance |
| 10 | Scenario Engine | Mark scenario `completed` when first successful run finalizes (existing `SimulationService` behavior) |
| **Failure** | Scenario Engine | Fail analysis run; **no partial Gold persistence** (atomic unit-of-work; mirror Sprint 6.3 / 6.4 failure semantics) |

**Position in platform pipeline (ADR-010):**

```
Bronze → Silver (Snapshot) → [Optional: Decision Engine waste Gold]
        ↓
[Sprint 6.5 Scenario Analysis] → Simulation Gold → [Future: AI SCENARIO_ANALYSIS] → [Future: Frontend]
```

**Explicit non-step:** LLM invocation, prompt composition, AI Recommendation Service.

---

## 7. Deliverables

| # | Deliverable | Description |
|---|---|---|
| D-01 | **Sprint 6.5 Specification (this document)** | Approved — TL sign-off 2026-07-15 |
| D-02 | **ScenarioSnapshotAdapterV1** | Snapshot payload → baseline input; conforms to Sprint 6.3 §11 adapter pattern |
| D-03 | **ScenarioAssumptionsAdapter** | `simulation_assumptions` → typed parameters + archetype resolution; fail-closed |
| D-04 | **Scenario Business Engine (v1)** | New engine under `app/business/engines/scenario/` registered **without modifying** frozen Waste Engine |
| D-05 | **ScenarioGoldMapper** | Facts → simulation Gold tables; mirror `WasteGoldMapper` + Sprint 6.4 deterministic mapper discipline |
| D-06 | **Scenario Engine service** | New module (suggested: `app/scenario/`) composing adapters, engine, mapper, existing `SimulationService` persistence |
| D-07 | **Execution entry point** | API endpoint, e.g. `POST /organizations/{id}/simulation/scenarios/{scenario_id}/execute` with snapshot binding + optional baseline run |
| D-08 | **Immutability guards** | Tests and code review gate: no snapshot mutation imports/paths in scenario module |
| D-09 | **Determinism test suite** | Same inputs → identical Facts + Gold payloads |
| D-10 | **AI isolation test** | Scenario module graph excludes `app.ai` |
| D-11 | **Frozen engine isolation test** | No modifications under frozen `app/business/engines/waste/`; new engine registered via approved bootstrap extension pattern |
| D-12 | **`progress.md` update** | Sprint 6.5 completion record (post-implementation only) |

**Explicit non-deliverables:** Preemptive mapping contract documents (E-19), AI changes, frontend changes, new ORM tables (default), Number Guard, reports, Monte Carlo.

---

## 8. Acceptance Criteria

Sprint 6.5 is **complete only when every criterion passes** Technical Lead review.

### 8.1 Preconditions

| ID | Criterion |
|---|---|
| AC-01 | Scenario execution rejected when Financial Snapshot missing or not org-scoped |
| AC-02 | Scenario execution rejected when source file `processing_status` ≠ `ready_for_analysis` |
| AC-03 | Scenario execution rejected when scenario not found or org mismatch |
| AC-04 | Optional baseline run rejected when not `completed`, not `financial_waste`, or org mismatch |
| AC-05 | Scenario execution rejected when assumptions fail parsing / archetype resolution |

### 8.2 Immutability and determinism

| ID | Criterion |
|---|---|
| AC-06 | Financial Snapshot row and payload **unchanged** after scenario execution |
| AC-07 | Same snapshot + same parameters + same engine version → identical `FactsContract` |
| AC-08 | Same inputs → identical Gold payloads (numeric chart points and fact values) |
| AC-09 | Bronze files not read during scenario execution (snapshot-only baseline) |

### 8.3 Engine and isolation

| ID | Criterion |
|---|---|
| AC-10 | Scenario Business Engine follows ADR-009 pipeline; produces `FactsContract` with `contract_version = "1.0"` |
| AC-11 | Waste Engine **not invoked** during scenario execution path |
| AC-12 | No `app.ai` imports in Scenario Engine module graph |
| AC-13 | Frozen Waste Engine source files unmodified |

### 8.4 Outputs and persistence

| ID | Criterion |
|---|---|
| AC-14 | Completed `analysis_runs` record has `analysis_type = simulation`, `source_snapshot_id` set, `status = completed` |
| AC-15 | `simulation_forecast_summaries` row exists 1:1 with baseline/projected/delta display fields |
| AC-16 | `simulation_chart_points` contains 3 quarterly points with numeric baseline/projected amounts |
| AC-17 | `simulation_comparison_metrics` contains 1–3 metrics with valid `MetricDirection` |
| AC-18 | `simulation_impact_items` populated per archetype template |
| AC-19 | `runtime_metadata.facts_contract` present on successful completion |
| AC-20 | Failed execution leaves no orphan Gold rows (or documents atomic rollback behavior) |

### 8.5 Regression

| ID | Criterion |
|---|---|
| AC-21 | Existing simulation CRUD/list GET endpoints remain functional |
| AC-22 | Sprint 6.3 / 6.4 tests remain green |
| AC-23 | Full backend test suite passes with Sprint 6.5 tests included |

### 8.6 Documentation

| ID | Criterion |
|---|---|
| AC-24 | This specification marked **Approved for Implementation** with TL sign-off |
| AC-25 | `progress.md` updated on sprint completion |

---

## 9. Technical Risks

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R-01 | **No Financial Engine** — snapshot may lack canonical revenue/spend totals | Baseline extraction ambiguity | Apply Sprint 6.3 §11 fail-closed adapter rules; reject ambiguous layouts |
| R-02 | **Assumption label variability** — `simulation_assumptions` are free-text label/value | Parser fragility | Fail-closed assumptions adapter; archetype templates in code + tests |
| R-03 | **Display vs numeric dual storage** — forecast summary VARCHAR vs chart NUMERIC | Calculation errors if mapper uses display fields | Enforce mapper uses engine numerics first; format for display second (schema §4.18.1) |
| R-04 | **Baseline dual-source drift** — snapshot vs optional waste Decision Result | Inconsistent deltas | Documented cross-check rules; fail on material mismatch |
| R-05 | **Existing manual results API** — callers may bypass Scenario Engine | Non-deterministic data entry | Deprecate as primary path; execute endpoint is production entry |
| R-06 | **Engine registry freeze** — adding Scenario Engine requires bootstrap discipline | Startup registration errors | Follow `initialize_business_engines()` pattern; test registry in CI |
| R-07 | **Scope creep to AI** — pressure to wire `SCENARIO_ANALYSIS` prompt | ADR violation | Explicit E-01; AC-12 isolation gate |
| R-08 | **Scope creep to Monte Carlo** | Non-deterministic outputs violate sprint goal | Explicit E-08; TL review |
| R-09 | **Placeholder parity pressure** — frontend expects exact Arabic strings | Over-fitting to placeholder | Test numeric determinism; allow formatted string variance within contract |
| R-10 | **SimulationService coupling** — nested transactions / duplicate run creation | Partial persistence bugs | Scenario Engine owns single transaction boundary; compose, don’t fork CRUD semantics |

---

## 10. Dependencies

### 10.1 Hard dependencies (must be complete)

| Dependency | Status | Reference |
|---|---|---|
| Sprint 6.2 Financial Snapshot | ✅ Complete | `progress.md` Sprint 6.2 |
| Sprint 6.3 Decision Engine (optional baseline path) | ✅ Complete | `progress.md` Sprint 6.3 |
| Phase 5 Business Engine architecture | ✅ Frozen | ADR-009, `BUSINESS_ENGINE_ARCHITECTURE.md` |
| Simulation persistence schema + services | ✅ Exists | `SimulationService`, `DATABASE_SCHEMA_DESIGN.md` §4.15–§4.22 |
| Simulation REST CRUD + run endpoints | ✅ Exists | `backend/app/api/v1/simulation.py` |
| `analysis_runs.source_snapshot_id` | ✅ Exists | Sprint 6.3 migration |
| Facts Contract | ✅ Implemented | `backend/app/business/facts/contract.py` |

### 10.2 Soft dependencies

| Dependency | Notes |
|---|---|
| Completed waste run for baseline enrichment | Optional; scenario can run snapshot-only |
| Reporting period label | Display enrichment only |
| Placeholder frontend archetypes | Inform v1 templates; not runtime authority |

### 10.3 Downstream consumers (not Sprint 6.5 blockers)

| Consumer | Relationship |
|---|---|
| Frontend Business Simulation page | Phase 7 — consume simulation GET APIs |
| AI `SCENARIO_ANALYSIS` task | Future sprint — consumes persisted Facts |
| Simulation recommendations (`rec-s*`) | Future AI + registry sprint |
| Reports (`report_type = simulation`) | Phase 8 |
| Dashboard recent analyses | Phase 7 aggregation |

---

## 11. Established Architectural Patterns

Sprint 6.5 **does not introduce new mapping contract documents**. Implementation reuses the following approved patterns:

### 11.1 ADR-010 — Financial Snapshot immutability

| Rule | Sprint 6.5 application |
|---|---|
| Snapshot is Silver — read-only consumer input | Scenario Engine reads `financial_snapshots.payload`; never writes |
| No Bronze re-parse at analysis time | Baseline derived from persisted snapshot only |
| Provenance on analysis runs | `source_snapshot_id`, `source_file_id`, `snapshot_version` in run metadata |
| Gold distinct from Silver | Simulation result tables are Gold; snapshot unchanged after execution |

**Authority:** [ADR 010](ADR/010-financial-snapshot-architecture.md)

### 11.2 Financial Snapshot Contract (Sprint 6.2 §11)

| Rule | Sprint 6.5 application |
|---|---|
| Snapshot payload structure | Schema v1 per `ParsedDataset.to_payload()` |
| Ownership and lifecycle | Org-scoped; write-once; consumer must not mutate |
| Engine input reference | Snapshot is mandatory baseline substrate for scenario execution |

**Authority:** [SPRINT_6.2_SPECIFICATION.md](SPRINT_6.2_SPECIFICATION.md) §11

### 11.3 Snapshot-to-Engine Mapping Contract pattern (Sprint 6.3 §11)

Scenario baseline extraction **follows the same adapter discipline** as `WasteSnapshotAdapterV1`:

| Principle | Requirement |
|---|---|
| **Never guess** | Ambiguous sheet or column resolution → deterministic failure |
| **Exactly-one rules** | Qualifying sheet count and column-per-role count enforced (mirror §11.2, §11.3) |
| **Fail-closed error codes** | Reuse established codes where applicable (`unsupported_layout`, `ambiguous_layout`, `missing_required_column`, `ambiguous_column_mapping`, etc.) |
| **String cell parsing** | Normalized snapshot cell values parsed to typed numerics in adapter layer |
| **Optional columns** | Recognized but not mapped unless part of resolved semantic roles |

Implementation: `ScenarioSnapshotAdapterV1` (Deliverable D-02) — scenario-specific layout rules live in adapter code and tests, not a separate contract document.

**Authority:** [SPRINT_6.3_SPECIFICATION.md](SPRINT_6.3_SPECIFICATION.md) §11; `backend/app/decision/adapters/waste_v1.py`

### 11.4 Deterministic output-mapping discipline (Sprint 6.4 §11 pattern)

Facts → simulation Gold persistence **follows the same mapping discipline** as Sprint 6.4's AI Response Mapping Contract — applied to **deterministic engine output**, not LLM text:

| Principle | Requirement |
|---|---|
| **Rule-based only** | Mapper derives Gold rows from Facts and engine structured output — no invented numbers |
| **No partial persistence on failure** | Failed execution → no orphan Gold rows; atomic unit-of-work |
| **Display vs numeric separation** | Engine numerics are canonical; `simulation_forecast_summaries` display strings formatted deterministically per `DATABASE_SCHEMA_DESIGN.md` §4.18.1 |
| **Provenance on run** | `facts_contract` + scenario provenance stored in `runtime_metadata` on success |

Implementation: `ScenarioGoldMapper` (Deliverable D-05) — mirror `WasteGoldMapper` (`backend/app/decision/mappers/waste_gold.py`) and Sprint 6.4 mapper module structure.

**Authority:** [SPRINT_6.4_SPECIFICATION.md](SPRINT_6.4_SPECIFICATION.md) §11 (discipline only — no AI in Sprint 6.5); `backend/app/decision/mappers/waste_gold.py`

### 11.5 Gap discovery protocol

If implementation discovers a **genuine architectural gap** not covered by §11.1–§11.4:

1. **Stop** implementation of the affected component.
2. **Document exactly one gap** — description, evidence, proposed resolution, impact on existing patterns.
3. **Submit for Technical Lead review** — do not proceed until approved.
4. **Do not** create preemptive contract documents speculatively.

Permitted gap examples: snapshot layout with no viable §11.3 mapping; simulation table field with no deterministic Facts source.  
Not a gap: routine adapter/mapper implementation detail resolvable within existing patterns.

---

## 12. Implementation Order

### Step 1 — Specification approval ✅

- This document approved (Technical Lead sign-off 2026-07-15).
- **No additional contract gates** — implementation may proceed directly.

### Step 2 — Scenario Business Engine (v1)

- Implement `ScenarioEngine` following Waste Engine structure (input, calculator, detector, assembler, manifest).
- Register in engine bootstrap **without modifying** frozen Waste Engine files.
- Unit tests for deterministic fact output per archetype.

### Step 3 — Input adapters

- `ScenarioSnapshotAdapterV1` — baseline extraction per §11.3 pattern.
- `ScenarioAssumptionsAdapter` — assumptions → typed parameters; fail-closed.
- Optional baseline decision reader (read-only).

### Step 4 — Scenario Gold mapper

- Implement `ScenarioGoldMapper` per §11.4 discipline.
- Deterministic display string formatting from engine numerics.

### Step 5 — Scenario Engine orchestration

- Compose lifecycle: validate → run → map → persist → complete/fail.
- Store `facts_contract` and provenance on success.

### Step 6 — Execution entry point

- New execute API; wire permissions consistent with existing simulation routes (`RequireOrgExecutive` for execution).
- Document deprecation of manual results POST for production workflows.

### Step 7 — Tests and regression

- Determinism, immutability, isolation, precondition, and E2E orchestration tests.
- Full suite green; update `progress.md`.

---

## 13. Technical Lead Recommendation

### Recommendation: **APPROVED FOR IMPLEMENTATION**

| Factor | Assessment |
|---|---|
| **Architectural fit** | Closes the documented simulation computation gap without unfreezing AI or modifying Waste Engine |
| **Correct integration pattern** | Scenario Engine composes existing `SimulationService` Gold persistence; new Scenario Business Engine follows ADR-009 |
| **Pattern reuse** | ADR-010, Financial Snapshot Contract, Snapshot-to-Engine Mapping Contract pattern, and deterministic output-mapping discipline — no preemptive contracts |
| **Scope discipline** | Single domain (`simulation`), three v1 archetypes aligned with placeholder data |
| **Immutability** | Snapshot read-only path respects ADR-010 |
| **Determinism** | No Monte Carlo, no AI, no LLM |

### TL adjustments applied (2026-07-15)

1. **Three preemptive mapping contracts rejected** — reuse established patterns (§11).
2. **Implementation authorized directly** — no contract gates beyond this specification.
3. **Gap discovery protocol** — document single genuine gap and stop; no speculative contracts.

### Conditions for implementation start

1. **This specification approved** — ✅ TL sign-off recorded (2026-07-15).
2. **No modification** to frozen `app/ai/` internals, `app/business/engines/waste/`, or Facts Contract structure.
3. **No AI work** in Sprint 6.5 (including `SCENARIO_ANALYSIS` and simulation recommendations).
4. **No preemptive mapping contract documents** (E-19).

### Suggested next sprint after 6.5

Simulation-domain AI (`SCENARIO_ANALYSIS` + recommendation registry), frontend Business Simulation wiring (Phase 7), Financial Engine snapshot binding, or Number Guard hardening — each requires separate sprint approval.

---

## Document Control

| Field | Value |
|---|---|
| **Author** | AI-assisted specification (Sprint 6.5) |
| **Approver** | Technical Lead |
| **Status** | **APPROVED FOR IMPLEMENTATION** (2026-07-15) |
| **TL adjustments applied** | (1) Preemptive mapping contracts rejected; (2) Pattern reuse §11; (3) Gap discovery protocol |
| **Implementation start** | **Authorized — proceed directly** |
| **Code constraint** | No implementation in this specification update task |
