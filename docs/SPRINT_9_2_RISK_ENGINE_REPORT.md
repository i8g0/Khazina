# Sprint 9.2 — Financial Risk Engine Core Report

**Date:** 2026-07-16  
**Role:** Principal Backend Engineer / Technical Lead  
**Sprint scope:** Deterministic Financial Risk Engine foundation (no AI, no frontend, no DB migrations)  
**Architecture reference:** [PHASE_9_FINANCIAL_RISK_ARCHITECTURE.md](PHASE_9_FINANCIAL_RISK_ARCHITECTURE.md) (Sprint 9.1 — locked)

---

## 1. Executive Summary

Sprint 9.2 delivered the **deterministic Financial Risk Engine** and its integration hooks into the existing Khazina decision pipeline. The engine detects, classifies, and scores risks from financial snapshot data, emits **Risk Findings** (analytical outputs only — **not** auto-promoted to the register), and produces a **Facts Contract** for future AI consumption.

**Outcome:** Risk analysis can be orchestrated via `DecisionService.execute_risk_analysis()`, creating standard `AnalysisRun` records (`analysis_type = risk`) with findings and facts stored in `runtime_metadata` until Sprint 9.3 adds dedicated persistence tables.

---

## 2. Engine Architecture

### 2.1 Pipeline (implemented)

```
Financial Snapshot (Silver)
        ↓
RiskSnapshotAdapterV1
        ↓
RiskEngineInput
        ↓
RiskCalculator          → ratios, variances, liquidity proxy
        ↓
RiskDetector            → 9 category rule modules
        ↓
score_risk()            → likelihood × impact matrix
        ↓
RiskFactAssembler       → FactsContract
        ↓
RiskEngineOutput        → facts + findings (detected status)
```

### 2.2 Package layout

```
backend/app/business/engines/risk/
├── __init__.py
├── constants.py          # Category taxonomy (9 codes)
├── input.py              # RiskEngineInput, FinancialMetricsInput
├── scoring.py            # Deterministic score matrix + priority bands
├── findings.py           # CandidateFinding, RiskFinding
├── calculator.py           # RiskCalculator
├── detector.py             # RiskDetector
├── engine.py               # RiskEngine(BusinessEngine)
├── manifest.py             # RISK_ENGINE_MANIFEST
├── output.py               # RiskEngineOutput
└── rules/__init__.py       # Per-category detect_* functions

backend/app/business/assemblers/risk.py
backend/app/decision/adapters/risk_v1.py
backend/app/decision/mappers/risk_metadata.py
```

### 2.3 Design adherence

| Requirement | Status |
|-------------|--------|
| Follow Waste Engine pattern | ✅ Calculator → Detector → Assembler |
| No LLM / no AI imports | ✅ Verified |
| Deterministic scoring | ✅ Fixed 3×3 matrix |
| Findings not auto-promoted | ✅ `finding_status = detected` only |
| Reuse AnalysisRun infrastructure | ✅ `DecisionService.execute_risk_analysis()` |
| No DB schema changes | ✅ Findings in `runtime_metadata` until 9.3 |
| No frontend changes | ✅ |
| No API routes | ✅ Orchestration service only |

---

## 3. Scoring Model

### 3.1 Likelihood × impact matrix

| Likelihood \\ Impact | Low | Medium | High |
|----------------------|-----|--------|------|
| **Low** | 20 | 35 | 50 |
| **Medium** | 40 | 55 | 70 |
| **High** | 60 | 75 | 90 |

Implementation: `app/business/engines/risk/scoring.py`

### 3.2 Priority bands

| Score range | Priority |
|-------------|----------|
| ≥ 70 | `high` |
| 40 – 69 | `medium` |
| < 40 | `low` |

### 3.3 Overall posture

| Condition | Posture |
|-----------|---------|
| ≥ 2 high findings OR max score ≥ 85 | `elevated` |
| ≥ 1 high OR ≥ 2 medium OR max score ≥ 55 | `moderate` |
| Otherwise | `low` |

**Reproducibility:** Same input always yields identical scores and finding IDs (UUID5 over rule id + category + name).

---

## 4. Risk Categories

| Code | Rule module | Example trigger |
|------|-------------|-----------------|
| `financial` | `detect_financial` | Waste % ≥ 5% / 10% |
| `liquidity` | `detect_liquidity` | Liquidity ratio < 1.0 / 1.5 |
| `operational` | `detect_operational` | ≥ 4 waste categories |
| `compliance` | `detect_compliance` | Waste % ≥ 8% governance threshold |
| `vendor` | `detect_vendor` | Top category ≥ 35% of waste |
| `fraud` | `detect_fraud` | Top category ≥ 50% (anomaly rule) |
| `budget` | `detect_budget` | Budget variance ± 10% |
| `strategic` | `detect_strategic` | Simulation variance ≥ 15% (when provided) |
| `forecast` | `detect_forecast` | Projection drift ≥ 20% (when provided) |

Category ownership is centralized in `rules/__init__.py` → `CATEGORY_DETECTORS` map.

---

## 5. Facts Contract

**Engine ID:** `risk`  
**Version:** `1.0.0`  
**Contract version:** `1.0`

### Core facts emitted

| Metric | Description |
|--------|-------------|
| `risk.total_findings` | Finding count |
| `risk.high_priority_count` | High-priority findings |
| `risk.medium_priority_count` | Medium-priority findings |
| `risk.low_priority_count` | Low-priority findings |
| `risk.overall_posture_level` | `elevated` / `moderate` / `low` |
| `risk.waste_percentage` | Derived waste % |
| `risk.category_count` | Category count from snapshot |
| `risk.liquidity_ratio` | Balance-sheet ratio or W-1 spend/waste proxy |
| `risk.score_max` | Highest finding score |
| `risk.top_category` | Category with most findings |
| `risk.category_count.{code}` | Per-category counts |
| `risk.finding.{id}.score` | Individual finding scores for AI grounding |

Stored on completed runs: `analysis_runs.runtime_metadata.facts_contract`

---

## 6. AnalysisRun Integration

### 6.1 Orchestration

`DecisionService.execute_risk_analysis()` mirrors waste execution:

1. Validate file `READY_FOR_ANALYSIS`
2. Resolve snapshot
3. `AnalysisService.create_run(type=risk)` → `start_run()`
4. Adapt snapshot → `RiskEngineInput`
5. `get_engine("risk").run()` → `RiskEngineOutput`
6. `AnalysisService.complete_run()` with metadata:
   - `facts_contract`
   - `risk_analysis` (summary aggregates)
   - `risk_findings` (list of dicts — **not register rows**)
   - `pipeline_timeline`

### 6.2 Observability

New pipeline stages:

- `risk_analysis_started`
- `risk_analysis_completed`

Structured logs via existing `log_pipeline_event()` with `finding_count` extra field.

### 6.3 Settings

`AnalysisType.RISK` added to `DEFAULT_ENABLED_ANALYSIS_TYPES` in `app/settings/constants.py`.

---

## 7. Files Created

| File | Purpose |
|------|---------|
| `app/business/engines/risk/*` | Engine core (13 files) |
| `app/business/assemblers/risk.py` | Facts Contract assembly |
| `app/decision/adapters/risk_v1.py` | Snapshot → RiskEngineInput |
| `app/decision/mappers/risk_metadata.py` | Runtime metadata serialization |
| `tests/business/risk_conftest.py` | Shared fixtures |
| `tests/business/test_risk_scoring.py` | Scoring tests |
| `tests/business/test_risk_engine.py` | Engine lifecycle tests |
| `tests/business/test_risk_assembler.py` | Assembler tests |
| `tests/business/test_risk_registry.py` | Registry smoke test |
| `tests/decision/test_risk_v1_adapter.py` | Adapter tests |
| `tests/decision/test_risk_decision_service.py` | Orchestration tests |

---

## 8. Files Modified

| File | Change |
|------|--------|
| `app/business/bootstrap.py` | Register `RiskEngine()` |
| `app/decision/service.py` | `execute_risk_analysis()`, `RiskDecisionExecutionOutcome` |
| `app/decision/adapters/__init__.py` | Export `RiskSnapshotAdapterV1` |
| `app/observability/pipeline.py` | `RISK_ANALYSIS_*` stages |
| `app/settings/constants.py` | Enable `AnalysisType.RISK` by default |
| `tests/business/test_registry.py` | Expect 3 registered engines |

---

## 9. Test Results

**Command:** `pytest -q` (full backend suite)

| Metric | Result |
|--------|--------|
| **Total tests** | **244 passed** |
| **New risk tests** | 25 |
| **Regression** | Waste engine + DecisionService waste tests pass |
| **Failures** | 0 |

### Risk test coverage areas

- Scoring matrix reproducibility
- Priority and posture classification
- Engine lifecycle and validation errors
- Finding determinism and non-promotion
- Facts Contract required metrics
- Snapshot adapter (W-1 payload)
- DecisionService risk orchestration (mocked)
- Engine registry includes `risk`

---

## 10. Manual Promotion (preserved)

Findings are emitted with `finding_status: detected` only. No code path in this sprint:

- Creates `risks` register rows from findings
- Calls `RiskService.register_risk()` automatically
- Sets `promoted_risk_id`

Promotion workflow remains Sprint 9.4 per architecture.

---

## 11. Remaining Work — Sprint 9.3+

| Sprint | Scope |
|--------|-------|
| **9.3** | Alembic migration (`risk_categories`, `risk_analysis_results`, `risk_findings`, …), `RiskAnalysisService`, `RiskGoldMapper`, REST `POST /risk-analyses/execute` |
| **9.4** | Finding review/promotion/dismiss, summary/matrix APIs, `risk_events` |
| **9.5** | Risk-domain AI (`generate_risk_recommendations`) — separate from waste `RISK_ANALYSIS` |
| **9.6** | Frontend wiring (`/risk-management`) |
| **9.7** | Dashboard KPIs, notifications, reports |
| **9.8** | Phase 9 QA freeze |

---

## 12. Sign-Off

| Criterion | Status |
|-----------|--------|
| Risk Engine implemented | ✅ |
| Deterministic scoring | ✅ |
| Facts Contract | ✅ |
| AnalysisRun integration | ✅ |
| Manual promotion preserved | ✅ |
| No AI generation | ✅ |
| No frontend changes | ✅ |
| Existing functionality unaffected | ✅ (244/244 tests) |
| Documentation complete | ✅ |

**Sprint 9.2 — Financial Risk Engine Core is complete.**

---

*End of Sprint 9.2 Report.*
