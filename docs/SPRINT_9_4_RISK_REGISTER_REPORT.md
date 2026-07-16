# Sprint 9.4 — Enterprise Risk Register Report

**Sprint:** 9.4 — Enterprise Risk Register  
**Date:** 2026-07-16  
**Status:** Complete  
**Architecture reference:** [PHASE_9_FINANCIAL_RISK_ARCHITECTURE.md](PHASE_9_FINANCIAL_RISK_ARCHITECTURE.md) §4, §6, §7, §8.3

---

## 1. Summary

Sprint 9.4 implements the **enterprise governance layer** for Financial Risk Intelligence: manual finding promotion, lifecycle management, review actions, provenance preservation, and immutable audit history.

**Validation:** 276 backend tests passing (17 new register tests). Risk Engine, Risk Analysis persistence (9.3), Waste Engine, Simulation, and Reports unaffected.

---

## 2. Architecture Alignment & Conflict Resolution

### Sprint request vs locked architecture (9.1)

| Topic | Sprint 9.4 request | Architecture lock (9.1) | Resolution |
|-------|-------------------|---------------------------|------------|
| Register lifecycle | 7 states including Detected/Under Review | `active → in_progress → closed` preserved | **Two-layer model:** finding workflow (analytical) + `lifecycle_status` (governance). Legacy `status` synced for backward compatibility |
| Service name | `RiskRegisterService` | `RiskIntelligenceService` planned | Implemented as **`RiskRegisterService`** per sprint charter; scope matches intelligence/promotion responsibilities |
| Auto-promotion | Never automatic | Manual only (OQ-1) | **Enforced:** promotion requires `reviewed` finding + EXECUTIVE role |

### Two-layer lifecycle model

**Finding lifecycle (analytical — pre-register):**

```
detected → under_review → reviewed → promoted
              ↓              ↓
           dismissed ←──── dismissed
              ↑
           reopen (→ detected)
```

**Enterprise register lifecycle (governance — post-promotion):**

```
accepted → monitoring → mitigated → resolved → archived
              ↑_______________|          |
              └──── reopen ──────────────┘
```

**Legacy compatibility (`risks.status`):**

| `lifecycle_status` | Synced `status` |
|--------------------|-----------------|
| `accepted` | `active` |
| `monitoring`, `mitigated`, `resolved` | `in_progress` |
| `archived` | `closed` (terminal — immutable via existing `RiskService`) |

Existing `POST /risks/{id}/transition` and `RiskService` rules remain unchanged.

---

## 3. Database Changes

### Migration `f9c2d7a31b44`

**Extended `risks`:**

| Column | Purpose |
|--------|---------|
| `lifecycle_status` | Enterprise governance state |
| `category_code` | FK → `risk_categories.code` |
| `source_type` | `manual` \| `engine` \| `import` |
| `source_analysis_run_id` | Provenance → analysis run |
| `source_finding_id` | Provenance → promoted finding |
| `source_snapshot_id` | Provenance → financial snapshot |
| `detected_at` | First detection timestamp |

**New `risk_events`:** Immutable audit trail (actor, from/to status, reason, metadata JSONB).

**Extended `risk_findings` CHECK:** Added `under_review` to allowed `finding_status` values.

**Head:** `f9c2d7a31b44` (revises `e8a1c4f03d21`)

---

## 4. Business Rules

| Rule | Enforcement |
|------|-------------|
| Only **reviewed** findings may promote | `RiskRegisterService.promote_finding()` |
| Dismissed/promoted findings cannot re-promote | Service guards + finding status transitions |
| Promotion never automatic | No engine/decision path writes to `risks` |
| Full provenance required on promotion | `source_*` columns populated from finding → run → snapshot chain |
| Illegal lifecycle transitions rejected | `FINDING_TRANSITIONS` / `LIFECYCLE_TRANSITIONS` maps |
| Archived register risks immutable | `lifecycle_status == archived` blocks updates |
| Org ownership on all operations | `_check_ownership` on every service method |
| Every governance action audited | `risk_events` row + structured log `governance_action` |
| Manual registration preserved | `RiskService.register_risk()` sets `source_type=manual`, `lifecycle_status=accepted` |

---

## 5. Repository Layer

| Repository | File | Methods |
|------------|------|---------|
| `RiskRepository` *(extended)* | `repositories/risk.py` | `list_for_organization` (+ lifecycle/category/source filters), `get_by_source_finding_id` |
| `RiskAnalysisRepository` *(extended)* | `repositories/risk_analysis.py` | `update_finding` |
| `RiskEventRepository` *(new)* | `repositories/risk_event.py` | `append`, `list_for_risk`, `list_for_organization` |

---

## 6. Application Layer — RiskRegisterService

**File:** `backend/app/services/risk_register.py`

| Method | Responsibility |
|--------|----------------|
| `review_finding()` | Approve / reject / request review / dismiss / reopen on findings |
| `promote_finding()` | Manual finding → enterprise risk with full provenance |
| `update_lifecycle_status()` | Validated register lifecycle transitions |
| `review_risk()` | Governance review actions mapped to lifecycle advances/reopens |
| `get_risk()` / `list_risks()` | Org-scoped register reads |
| `get_risk_history()` | Audit trail from `risk_events` |
| `get_finding_provenance()` | Snapshot → run → finding → risk chain |

**Transition maps:** `backend/app/business/governance/risk_lifecycle.py`

---

## 7. REST APIs

**Router:** `backend/app/api/v1/risk_register.py` — tag `risk-register`

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| POST | `/risk-findings/{finding_id}/promote` | EXECUTIVE+ | Manual promotion |
| POST | `/risk-findings/{finding_id}/review` | EXECUTIVE+ | Finding review action |
| PATCH | `/risks/{risk_id}/status` | EXECUTIVE+ | Lifecycle status update |
| POST | `/risks/{risk_id}/review` | EXECUTIVE+ | Register governance review |
| GET | `/risks/{risk_id}/history` | ANALYST+ | Audit history |
| GET | `/risks/{risk_id}/provenance` | ANALYST+ | Full provenance chain |

**Extended (backward compatible):**

| Method | Path | Change |
|--------|------|--------|
| GET | `/risks` | Added filters: `lifecycle_status`, `category_code`, `source_type`; response includes provenance fields |
| GET | `/risks/{risk_id}` | Response includes `lifecycle_status`, provenance columns |

Sprint 9.3 `/risk-analyses/*` routes unchanged.

---

## 8. Observability

Every governance action emits:

1. **`risk_events` row** — actor, timestamp, from/to status, reason, metadata
2. **Structured log** — `governance_action` via `log_pipeline_event` with entity type/id, actor, status transition, reason

No new logging framework introduced.

---

## 9. Tests

| File | Coverage |
|------|----------|
| `tests/business/test_risk_lifecycle.py` | Transition maps, terminal states, legacy sync |
| `tests/services/test_risk_register_service.py` | Promotion guards, provenance, review, invalid transitions |
| `tests/api/test_risk_register_api.py` | Route registration |
| `tests/db/test_risk_register_models.py` | Constraints, provenance columns, `risk_events` |
| `tests/db/test_risk_analysis_migration.py` | Updated Alembic head |

**Full suite:** `276 passed`

---

## 10. Files Modified / Created

### New

- `backend/app/business/governance/risk_lifecycle.py`
- `backend/app/db/models/risk_event.py`
- `backend/app/repositories/risk_event.py`
- `backend/app/services/risk_register.py`
- `backend/app/schemas/risk_register.py`
- `backend/app/api/v1/risk_register.py`
- `backend/alembic/versions/f9c2d7a31b44_add_enterprise_risk_register.py`
- `tests/business/test_risk_lifecycle.py`
- `tests/services/test_risk_register_service.py`
- `tests/api/test_risk_register_api.py`
- `tests/db/test_risk_register_models.py`
- `docs/SPRINT_9_4_RISK_REGISTER_REPORT.md`

### Modified

- `backend/app/db/models/enums.py` — governance enums
- `backend/app/db/models/risk.py` — provenance + lifecycle columns
- `backend/app/db/models/risk_analysis.py` — `under_review` status, FK relationship fix
- `backend/app/repositories/risk.py`, `risk_analysis.py`, `__init__.py`
- `backend/app/services/risk.py` — manual registration lifecycle/source defaults
- `backend/app/schemas/risk.py` — extended response fields
- `backend/app/api/v1/risk.py` — list filters
- `backend/app/api/deps.py`, `api/v1/router.py`, `services/__init__.py`

### Unchanged (by design)

- Risk Engine core and scoring
- `RiskAnalysisService` / 9.3 APIs
- Waste Engine, Simulation, Reports
- AI generation
- Frontend

---

## 11. Remaining Work — Sprint 9.5

Per architecture sprint plan:

1. **Risk AI & Recommendations** — `generate_risk_recommendations`, new prompt tasks, facts loader extension
2. **`risk_score_history`** — monitoring score drift on re-analysis
3. **Risk intelligence aggregations** — summary KPIs, priority matrix, by-department/category charts
4. **Deduplication** — finding → existing risk match on re-analysis (OQ-5 rule_id + entity key)
5. **Frontend integration** — Sprint 9.6 scope

---

## 12. Definition of Done

| Criterion | Status |
|-----------|--------|
| Enterprise Risk Register implemented | ✅ |
| Manual promotion implemented | ✅ |
| Lifecycle validation enforced | ✅ |
| Governance APIs implemented | ✅ |
| Audit trail implemented | ✅ |
| Authorization enforced (EXECUTIVE+ for mutations) | ✅ |
| Backend tests pass | ✅ (276) |
| No frontend changes | ✅ |
| No AI generation | ✅ |
| Provenance chain preserved | ✅ |
| Architecture conflicts documented | ✅ |
