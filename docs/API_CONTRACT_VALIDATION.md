# API Contract Validation

**Date:** 2026-07-16  
**Phase:** 1 — Investigation ONLY  
**Scope:** Frontend request → backend validation → DB → response → frontend parsing

---

## Validation Method

For each critical endpoint:
1. Frontend call site (`frontend/lib/api/khazina-api.ts`, page components)
2. Backend route + Pydantic schema (`backend/app/api/`)
3. Service/repository parameter usage
4. Response model vs frontend TypeScript types

---

## Pagination Contract

| Layer | Contract | Status |
|-------|----------|--------|
| Backend | `PaginationParams`: `limit` le=100, `offset` ge=0 | ✅ Enforced in `deps.py` |
| Frontend | `MAX_LIST_LIMIT = 100` in `pagination.ts` | ✅ Sprint 1 fix |
| **Violation fixed** | Departments used `limit: 200` → 422 | ✅ Fixed KHZ-047 |

**All list endpoints must use `limit ≤ 100`.**

---

## Identity Parameters

| Parameter | Required by | Frontend sends | Backend validates | Match |
|-----------|-------------|----------------|-------------------|-------|
| `organization_id` | Most list endpoints | From org context | Query param / auth scope | ✅ |
| `file_id` | Upload-scoped runs | From selected file | FK validation | ✅ |
| `snapshot_id` | Internal ingest | Backend only | — | N/A UI |
| `analysis_run_id` | Reports, AI recs | From artifacts | FK + org scope | ✅ |
| `risk_run_id` | Risk AI, risk reports | `riskRunId` artifact | Maps to analysis_run | ✅ |
| `simulation_run_id` | Simulation | Simulation page | FK | ✅ |
| `report_id` | PDF export | Resolved selection | UUID + org | ⚠️ IDOR risk KHZ-008 |

---

## Critical Endpoint Matrix

### Auth

| Endpoint | FE | BE | Response FE parse | Status |
|----------|----|----|-------------------|--------|
| `POST /auth/login` | ✅ | ✅ | Token stored | ✅ |
| `POST /auth/logout` | ✅ | ✅ | — | ⚠️ Artifacts not cleared |

### Files

| Endpoint | FE | BE | Notes | Status |
|----------|----|----|-------|--------|
| `POST /files/upload` | `data-management-page` | Multipart + org_id | Returns `file_id` | ✅ |
| `GET /files` | Data page | Paginated | limit≤100 | ✅ |

### Waste

| Endpoint | FE | BE | Key fields | Status |
|----------|----|----|------------|--------|
| `POST /waste/analyze` | `waste-page` | `{ file_id, organization_id }` | Returns `analysis_run_id` | ✅ |
| `GET /waste/runs/{id}` | waste-page reload | Path UUID | Results shape | ✅ |
| `GET /waste/results` | Optional list | `analysis_run_id` query | — | ✅ |

### Waste AI

| Endpoint | FE | BE | Key fields | Status |
|----------|----|----|------------|--------|
| `POST /ai/recommendations` | waste-page | `analysis_run_id`, domain | Async job | ✅ |
| `GET /ai/recommendations` | waste-page F5 reload | `analysis_run_id`, pagination | Items[] title/description | ⚠️ Description contains raw AI |

### Risk

| Endpoint | FE | BE | Key fields | Status |
|----------|----|----|------------|--------|
| `POST /risk/analyze` | risk-page | `file_id`, org | Returns run id | ✅ |
| `GET /risks` | risk-page | `organization_id`, limit, offset | **500 if unmigrated DB** | ❌ Conditional |
| `GET /risks/{id}` | detail | Path id | **IDOR — 200 cross-org** | ❌ KHZ-008 |
| `POST /risk/ai/summary` | risk-page | `analysis_run_id` | Summary text | ✅ |

### Simulation

| Endpoint | FE | BE | Key fields | Status |
|----------|----|----|------------|--------|
| `POST /simulation/run` | simulation-page | params + file | Returns run + analysis_run_id | ✅ |
| `GET /simulation/runs/{id}` | reload | Path UUID | — | ⚠️ Errors swallowed in UI |

### Reports

| Endpoint | FE | BE | Key fields | Status |
|----------|----|----|------------|--------|
| `POST /reports/generate` | reports-page | `analysis_run_id`, **`title` required** | Sprint 2: no waste default | ✅ |
| `GET /reports` | reports-page | org + pagination | `analysisRunId` mapped | ✅ |
| `GET /reports/{id}/pdf` | report-export | Path UUID | Binary PDF | ⚠️ Content quality separate |

---

## Contract Mismatches Found

### M-01: Report generate — duplicate rows (KHZ-026)

| Field | Expected | Actual |
|-------|----------|--------|
| Idempotency | Same `analysis_run_id` + title → one report | New row every POST |

**Impact:** List grows; export heuristics pick wrong row.

### M-02: Export resolution priority (G-02)

| Field | Expected | Actual |
|-------|----------|--------|
| Fallback order | Match user’s last generated domain | `riskRunId` before `wasteRunId` in `resolveExportReportId()` |

**Evidence:** `frontend/lib/reports/report-export.ts:38-42`

### M-03: AI recommendation description schema

| Field | Expected | Actual |
|-------|----------|--------|
| `description` | Executive Arabic prose | Full LLM body including reference facts block |

**Backend stores verbatim; frontend displays verbatim.**

### M-04: Workflow pipeline vs product LAW

| Field | Expected | Actual |
|-------|----------|--------|
| Stage order | waste → ai → risk → risk ai → simulation → report | Pipeline: waste → ai → **simulation** → report (no risk) |

**Evidence:** `frontend/lib/workflow/pipeline.ts`

### M-05: Risk list response — lifecycle fields

| Field | Expected | Actual |
|-------|----------|--------|
| `lifecycle_status` | Present on Risk model | Requires migration `f9c2d7a31b44` |

**Ops contract:** deploy must run `alembic upgrade head`.

---

## Frontend Type Alignment

| Type | Source | Drift |
|------|--------|-------|
| `DemoArtifacts` | `state.ts` | Includes `simulationAnalysisRunId` (Sprint 2) ✅ |
| `ReportExportCandidate` | `report-export.ts` | `analysisRunId` nullable ✅ |
| Recommendation card | waste-page | Uses `formatRecommendationDisplay()` — minimal strip only |

---

## Recommended Contract Fixes (Phase 2)

1. **Reports:** `POST /reports/generate` idempotent on `(organization_id, analysis_run_id, report_profile)` OR return existing
2. **Export:** Fallback order = `lastReportId` domain → explicit workflow order (waste → risk → simulation)
3. **AI items:** Backend response schema adds `executive_summary` stripped of reference block; or sanitize at parse time
4. **Risk GET by id:** 404 when org mismatch
5. **Pipeline:** Add `risk` and `riskAi` stages with correct ordering

---

## Verification Commands (for Phase 2 acceptance)

```bash
# Backend contract tests
cd Khazina/backend && python -m pytest tests/ -q --tb=no

# Frontend types
cd Khazina/frontend && npx tsc --noEmit
```

**Phase 1 complete. No code modified.**
