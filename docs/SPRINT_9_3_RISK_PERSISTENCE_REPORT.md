# Sprint 9.3 — Financial Risk Persistence & Application Layer Report

**Sprint:** 9.3 — Financial Risk Persistence & Application Layer  
**Date:** 2026-07-16  
**Status:** Complete  
**Architecture reference:** [PHASE_9_FINANCIAL_RISK_ARCHITECTURE.md](PHASE_9_FINANCIAL_RISK_ARCHITECTURE.md) §6, §7, §8.2

---

## 1. Summary

Sprint 9.3 implements the approved Gold persistence layer and application services for Financial Risk Intelligence. Deterministic Risk Engine output (Sprint 9.2) is now persisted to PostgreSQL via `RiskAnalysisService`, while the engine remains fully independent of ORM models.

**Validation:** 259 backend tests passing (15 new risk-persistence tests). No changes to Risk Engine scoring, Waste Engine, Simulation, Reports, or frontend.

---

## 2. Database Entities

| Table | Model | Purpose |
|-------|-------|---------|
| `risk_categories` | `RiskCategory` | Seeded taxonomy (9 categories); PK = `code` |
| `risk_analysis_results` | `RiskAnalysisResult` | 1:1 aggregate outcome per `analysis_runs` row (`analysis_type = risk`) |
| `risk_findings` | `RiskFinding` | Scored detections before register promotion |

**Deferred to Sprint 9.4:** `risk_score_history`, `risk_events`, `risks` table extensions, register/promotion APIs.

### Relationships added

- `AnalysisRun.risk_analysis_result` (1:1, cascade delete)
- `AnalysisRun.risk_findings` (1:N, cascade delete)
- `RiskFinding.promoted_risk_id` → `risks.id` (nullable, SET NULL — no auto-promotion)

### Enum

- `RiskFindingStatus`: `detected`, `reviewed`, `promoted`, `dismissed`

---

## 3. Migrations

| Revision | File | Description |
|----------|------|-------------|
| `e8a1c4f03d21` | `backend/alembic/versions/e8a1c4f03d21_add_risk_analysis_persistence.py` | Creates three tables, indexes, CHECK constraints; seeds 9 `risk_categories` |

**Head:** `e8a1c4f03d21` (revises `d2f6b8a14e37`)

Backward compatible — no changes to existing tables.

---

## 4. Repository Layer

| Repository | File | Methods |
|------------|------|---------|
| `RiskAnalysisRepository` | `backend/app/repositories/risk_analysis.py` | `create_result`, `get_result`, `get_result_for_run`, `add_findings`, `get_finding`, `list_findings` |
| `RiskCategoryRepository` | `backend/app/repositories/risk_category.py` | `get`, `list_active` |

Both extend `BaseRepository` — thin data access only, no business logic.

---

## 5. Application Layer

### RiskGoldMapper

**File:** `backend/app/decision/mappers/risk_gold.py`

Maps `RiskEngineOutput` → persistence payload dict (result row + finding rows). Engine finding UUID5 strings map to DB primary keys. Keeps engine types independent from SQLAlchemy models.

### RiskAnalysisService

**File:** `backend/app/services/risk_analysis.py`

| Method | Responsibility |
|--------|----------------|
| `execute()` | Calls `DecisionService.execute_risk_analysis()`, maps via `RiskGoldMapper`, persists result + findings |
| `list_runs()` | Delegates to `AnalysisService.list_runs(analysis_type=risk)` |
| `get_run_detail()` | Run + optional result summary |
| `get_result()` | Full `RiskAnalysisResult` aggregates |
| `list_findings()` | Filtered findings for a run |
| `get_finding()` | Single finding scoped to run + org |

**Layering preserved:**

```
RiskEngine (deterministic)
    ↓
DecisionService.execute_risk_analysis()  — engine + runtime metadata
    ↓
RiskAnalysisService.execute()            — business rules + Gold persistence
    ↓
RiskAnalysisRepository                   — thin CRUD
    ↓
PostgreSQL
```

**Observability:** Structured log event `risk_gold_persisted` via `log_pipeline_event` after successful persistence (org, run, snapshot, finding count, posture level).

---

## 6. REST APIs

**Router:** `backend/app/api/v1/risk_analysis.py` — tag `risk-analysis`

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/organizations/{org_id}/risk-analyses/execute` | EXECUTIVE+ | Execute analysis + persist |
| GET | `/organizations/{org_id}/risk-analyses` | ANALYST+ | List risk runs |
| GET | `/organizations/{org_id}/risk-analyses/{run_id}` | ANALYST+ | Run detail + result summary |
| GET | `/organizations/{org_id}/risk-analyses/{run_id}/result` | ANALYST+ | Full result aggregates |
| GET | `/organizations/{org_id}/risk-analyses/{run_id}/findings` | ANALYST+ | List findings (filters: priority, category_code, finding_status) |
| GET | `/organizations/{org_id}/risk-analyses/{run_id}/findings/{finding_id}` | ANALYST+ | Finding detail |

**Schemas:** `backend/app/schemas/risk_analysis.py`

**DI:** `RiskAnalysisServiceDep` in `backend/app/api/deps.py`

Register management, promotion, and intelligence endpoints remain Sprint 9.4 scope.

---

## 7. Tests

| File | Coverage |
|------|----------|
| `tests/decision/test_risk_gold_mapper.py` | Mapper payload shape, deterministic finding IDs |
| `tests/services/test_risk_analysis_service.py` | Execute persistence, duplicate guard, run type validation, list delegation |
| `tests/db/test_risk_analysis_models.py` | Table names, constraints, AnalysisRun relationships |
| `tests/db/test_risk_analysis_migration.py` | Alembic head + revision chain |
| `tests/api/test_risk_analysis_api.py` | Route registration, auth gate on execute |

**Full suite:** `259 passed`

Existing Sprint 9.2 risk engine/decision tests unchanged and passing.

---

## 8. Files Modified / Created

### New files

- `backend/app/db/models/risk_analysis.py`
- `backend/alembic/versions/e8a1c4f03d21_add_risk_analysis_persistence.py`
- `backend/app/repositories/risk_analysis.py`
- `backend/app/repositories/risk_category.py`
- `backend/app/decision/mappers/risk_gold.py`
- `backend/app/services/risk_analysis.py`
- `backend/app/schemas/risk_analysis.py`
- `backend/app/api/v1/risk_analysis.py`
- `tests/decision/test_risk_gold_mapper.py`
- `tests/services/test_risk_analysis_service.py`
- `tests/db/test_risk_analysis_models.py`
- `tests/db/test_risk_analysis_migration.py`
- `tests/api/test_risk_analysis_api.py`
- `docs/SPRINT_9_3_RISK_PERSISTENCE_REPORT.md`

### Modified files

- `backend/app/db/models/enums.py` — `RiskFindingStatus`
- `backend/app/db/models/analysis.py` — risk relationships
- `backend/app/db/models/__init__.py` — exports
- `backend/app/repositories/__init__.py` — exports
- `backend/app/decision/mappers/__init__.py` — `RiskGoldMapper`
- `backend/app/decision/mappers/risk_metadata.py` — docstring update
- `backend/app/services/__init__.py` — `RiskAnalysisService` export
- `backend/app/api/deps.py` — DI wiring
- `backend/app/api/v1/router.py` — router registration

### Unchanged (by design)

- Risk Engine core (`backend/app/business/engines/risk/`)
- Scoring model and detection rules
- `DecisionService.execute_risk_analysis()` engine path
- Waste Engine, Simulation, Reports
- Frontend
- Risk register CRUD (`api/v1/risk.py`)
- AI generation

---

## 9. Remaining Work — Sprint 9.4

Per [PHASE_9_FINANCIAL_RISK_ARCHITECTURE.md](PHASE_9_FINANCIAL_RISK_ARCHITECTURE.md):

1. **Tables:** `risk_score_history`, `risk_events`; extend `risks` with `category_code`, `source_type`, etc.
2. **RiskIntelligenceService:** Finding review, promote, dismiss; deduplication
3. **APIs:** `/risk-intelligence` router, `/risk-categories`, register promotion endpoints
4. **Timeline/notifications:** Risk-specific completion hooks
5. **Frontend wiring:** Risk page to new APIs (when frontend freeze lifts)

---

## 10. Definition of Done Checklist

| Criterion | Status |
|-----------|--------|
| Database persistence implemented | ✅ |
| Alembic migrations created | ✅ |
| SQLAlchemy models implemented | ✅ |
| RiskAnalysisService implemented | ✅ |
| RiskGoldMapper implemented | ✅ |
| Execute + read APIs implemented | ✅ |
| Findings persist correctly | ✅ |
| AnalysisRun links remain valid | ✅ |
| Backend tests pass | ✅ (259) |
| No frontend changes | ✅ |
| No AI generation | ✅ |
| No Risk Register implementation | ✅ |
