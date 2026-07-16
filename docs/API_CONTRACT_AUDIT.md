# API Contract Audit

**Date:** 2026-07-16  
**Commit investigated:** `1db4c16f27ab390164121b87be508bec3aff5e97`  
**Scope:** Frontend ↔ Backend contract compatibility — pagination, query params, list endpoints, documented standards  
**Method:** Static code audit of all list endpoints + all frontend `limit`/`offset` callers; cross-reference with `docs/API_CONTRACTS.md` and `BUG_TRACKER.md`

---

## Executive Summary

| Category | Count |
|----------|-------|
| **Confirmed limit mismatches (422 at runtime)** | **1** |
| Documentation contract drift | 1 |
| API client capability gaps | 10 endpoints |
| Behavioral gaps (no limit passed → unbounded) | 8 call sites |
| Unused backend-only endpoints | 1 |
| **Total contract issues logged** | **21** |

**Highest-impact finding:** `OrgLookupsProvider` requests `limit: 200` on `GET /departments` while backend enforces `limit <= 100`. This produces **HTTP 422** on every app load that mounts org lookups (all authenticated shell routes).

---

## Pagination Policy (Architecture)

### What the backend implements (source of truth)

| Mechanism | Location | Rule |
|-----------|----------|------|
| Shared `PaginationParams` | `backend/app/api/deps.py:72-81` | `limit`: optional, `ge=1`, **`le=100`**; `offset`: optional, `ge=0` |
| Dedicated `limit` on recent analyses | `backend/app/api/v1/analysis.py:86` | default 10, max **100** |
| Dedicated `limit` on dashboard featured recs | `backend/app/api/v1/recommendation.py:89` | default 5, max **50** |

When `limit` is **omitted**, repositories apply **no SQL LIMIT** — full result set returned.

### What the documentation says

`docs/API_CONTRACTS.md:74-102` describes future pagination with `page` and `page_size` (default 20). **This is stale.** The live API uses **`limit` + `offset` only**. No `page` or `page_size` query params exist in backend code.

### What the frontend implements

| Type | Location | Fields |
|------|----------|--------|
| `ListQueryParams` | `frontend/lib/api/types.ts:286-289` | `limit?`, `offset?` |

Frontend correctly uses `limit`/`offset` — not `page`/`page_size`.

### Architectural recommendation

**Backend `le=100` is the correct contract** for hackathon stabilization:

- Enforced consistently across 19 paginated list routes via `PaginationDep`
- Protects DB and API from unbounded queries
- Documented implicitly in shared dependency (not yet in `API_CONTRACTS.md`)

**Frontend must never request `limit > 100`.** For orgs with >100 departments, use pagination (`offset`) or increase backend cap in a dedicated sprint with performance review — do not bypass with `limit: 200`.

---

## Confirmed Contract Mismatch #1 — Departments `limit: 200`

### Evidence

| Layer | Value | File |
|-------|-------|------|
| **Frontend request** | `limit: 200` | `frontend/lib/org-lookups.tsx:47` |
| **Backend validation** | `le=100` | `backend/app/api/deps.py:77` |
| **Endpoint** | `GET /api/v1/organizations/{orgId}/departments` | `backend/app/api/v1/department.py:55` |

### Observed runtime (independently verified)

```
GET /api/v1/organizations/{organizationId}/departments?limit=200&active_only=true
→ HTTP 422 Validation failed
→ query.limit: Input should be less than or equal to 100
```

All other initial requests returned HTTP 200. Authentication succeeded. This was the **only consistently failing request** on app load after commit `1db4c16`.

### Impact chain

```
App shell mounts OrgLookupsProvider (all authenticated routes)
  → refresh() calls listDepartments(..., { limit: 200 })
  → 422
  → departments[] stays empty
  → departmentName() returns null everywhere
  → Waste breakdown department labels missing
  → Risk detail provenance labels wrong/missing
  → Reports page department names in metadata wrong
  → Organization management page works (uses limit: 100) — inconsistent within same app
```

### Root cause

Frontend developer assumed org lookup needed all departments in one call and chose 200 without checking backend `PaginationParams` cap. No shared constant enforces max limit on either side.

### Correct contract

| Parameter | Value |
|-----------|-------|
| `limit` | **1–100** (use 100 for org lookups) |
| `offset` | 0+ for pagination if >100 departments |

### Recommended fix

| Option | Change | Regression risk |
|--------|--------|-----------------|
| **A (recommended)** | Change `org-lookups.tsx:47` to `limit: 100` | **Low** — one line |
| B | Raise backend `le` to 200 globally | **Medium** — affects all 19 paginated endpoints, performance |
| C | Add shared `MAX_PAGE_SIZE = 100` constant in frontend + backend | **Low** — prevents recurrence |

### Regression checklist after fix

- [ ] `GET /departments?limit=100` → 200 on app load
- [ ] Department names appear on waste breakdown table
- [ ] Risk detail provenance shows department labels
- [ ] Org management page still loads departments
- [ ] No 422 in browser Network tab on any route

---

## Complete Pagination Compatibility Matrix

### Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Within backend max |
| ❌ | Exceeds backend max → 422 |
| ⚠️ | No limit sent → unbounded backend response |
| N/A | Endpoint not paginated |

### Frontend-called paginated endpoints

| Endpoint | Backend max | Frontend limit(s) | Match | Evidence |
|----------|-------------|-------------------|-------|----------|
| `GET .../departments` | 100 | **200**, 100 | **❌** | `org-lookups.tsx:47`, `organization-management-page.tsx:71` |
| `GET .../reporting-periods` | 100 | 100 | ✅ | `org-lookups.tsx:52` |
| `GET .../users` | 100 | 50 | ✅ | `users-management-page.tsx:69` |
| `GET .../notifications` | 100 | 8, 20 | ✅ | `notification-bell.tsx:48`, `notifications-center-page.tsx:62` |
| `GET .../risks` | 100 | 50 | ✅ | `risk-page.tsx:142`, `dashboard-page.tsx:104` |
| `GET .../risk-analyses` | 100 | 20 | ✅ | `risk-page.tsx:143` |
| `GET .../mitigation-plans` | 100 | 20 | ✅ | `risk-page.tsx:144` |
| `GET .../risk-analyses/{id}/findings` | 100 | 100 | ✅ (at ceiling) | `risk-page.tsx:161` |
| `GET .../recommendations` | 100 | 20; **none** | ⚠️ | `risk-page.tsx:165`, `dashboard-page.tsx:103` |
| `GET .../risks/{id}/history` | 100 | 50 | ✅ | `risk-detail-page.tsx:77` |
| `GET .../analysis-runs/recent-completed` | 100 (default 10) | **none** | ⚠️ (uses default 10) | `dashboard-page.tsx:102` |
| `GET .../timeline/events` | 100 | **none** | ⚠️ | `dashboard-page.tsx:101` |
| `GET .../financial-files` | 100 | **none** | ⚠️ | `org-lookups.tsx:50`, `data-management-page.tsx:68` |
| `GET .../waste/vendor-findings` | 100 | **none** | ⚠️ | `waste-page.tsx:130` |
| `GET .../reports` | 100 | **none** | ⚠️ | `reports-page.tsx:110` |
| `GET .../simulation/scenarios` | 100 | **none** | ⚠️ | `simulation-page.tsx:111` |

### Backend-only pagination (no frontend caller)

| Endpoint | Backend max | Frontend | Notes |
|----------|-------------|----------|-------|
| `GET .../recommendations/dashboard-featured` | 50 | Not called | Dashboard uses general `listRecommendations` instead |

---

## API Client Capability Gaps

These backend-paginated endpoints have **no `ListQueryParams`** in `khazina-api.ts`, so TypeScript callers cannot pass `limit`/`offset` even when needed:

| Function | File:Line | Backend route |
|----------|-----------|---------------|
| `listFinancialFiles` | `khazina-api.ts:289` | `GET .../financial-files` |
| `listImportRecords` | `khazina-api.ts:299` | `GET .../financial-files/{id}/import-records` |
| `listReports` | `khazina-api.ts:754` | `GET .../reports` |
| `listTimeline` | `khazina-api.ts:872` | `GET .../timeline/events` |
| `listScenarios` | `khazina-api.ts:650` | `GET .../simulation/scenarios` |
| `listRecentAnalyses` | `khazina-api.ts:882` | `GET .../analysis-runs/recent-completed` |
| `listChartPoints` | `khazina-api.ts:699` | simulation run sub-resources |
| `listComparisonMetrics` | `khazina-api.ts:710` | simulation run sub-resources |
| `listScenarioAssumptions` | `khazina-api.ts:721` | simulation scenario sub-resources |
| `listImpactItems` / `listActionItems` | `khazina-api.ts:732-743` | simulation run sub-resources |

**Risk:** Orgs exceeding 100 files/reports/scenarios silently truncate only if a limit is added later; currently unbounded (performance risk, not 422).

---

## Non-Pagination Contract Issues

### Snapshot identifier mutual exclusion (verified consistent post-fix)

Backend enforces **exactly one** of `source_snapshot_id` OR `snapshot_version`:

| Service | File |
|---------|------|
| Decision (waste/risk) | `backend/app/decision/service.py:110` |
| Scenario (simulation) | `backend/app/scenario/service.py:117` |

| Frontend caller | Sends | Status |
|-----------------|-------|--------|
| Waste execute | `source_snapshot_id` only | ✅ Fixed |
| Risk execute | `source_snapshot_id` only | ✅ Fixed (KHZ-014) |
| Simulation execute | `if snapshotId else snapshotVersion` — mutually exclusive | ✅ `simulation-page.tsx:282-286` |

### Report generate body

| Field | Frontend | Backend | Match |
|-------|----------|---------|-------|
| `analysis_run_id` | Required UUID | Required | ✅ |
| `title` | Optional; defaults to waste title in client | Optional; server template if null | ⚠️ **Semantic mismatch** — risk reports get waste default title (KHZ-023) |

### Auth header

| Rule | Frontend | Backend | Match |
|------|----------|---------|-------|
| `Authorization: Bearer <token>` | `client.ts` | All protected routes | ✅ |

### Response envelope

| Field | Both sides expect `ApiResponse<T>` | Match |
|-------|-------------------------------------|-------|
| `success`, `message`, `data`, `errors` | ✅ | ✅ |

---

## Issue Register (API Contract)

| ID | Issue | Severity | Frontend expectation | Backend expectation | Root cause | Recommended fix | Regression impact |
|----|-------|----------|---------------------|---------------------|------------|-----------------|---------------------|
| **AC-001** | Departments `limit: 200` | **Critical** | Up to 200 rows | Max 100 | No shared max constant | FE: `limit: 100` in `org-lookups.tsx` | Low |
| AC-002 | Docs say `page_size`, API uses `limit` | Medium | N/A | `limit`/`offset` | Stale `API_CONTRACTS.md` | Update docs | None |
| AC-003 | 8 call sites omit `limit` | Medium | Full dataset | Unbounded if omitted | Client functions lack pagination params | Add `ListQueryParams` to client functions; pass `limit: 100` | Low–Medium |
| AC-004 | `listRecentAnalyses` no limit param | Low | Default backend 10 | Max 100, default 10 | Client gap | Add optional limit to client | Low |
| AC-005 | `dashboard-featured` unused | Low | N/A | Max 50 | Dashboard uses general list | Wire or remove endpoint | Low |
| AC-006 | Risk report title default | High | Type-specific title in UI label only | Accepts any title | `generateReport()` hardcodes waste title | Pass title param from `handleGenerate` | Low |
| AC-007 | No shared `MAX_PAGE_SIZE` constant | Medium | Ad hoc limits | `le=100` in deps | No cross-repo contract file | Add `constants/pagination.ts` (FE) + document in API_CONTRACTS | Prevents AC-001 recurrence |

---

## Search Coverage (required terms)

| Term | Backend hits | Frontend hits |
|------|-------------|---------------|
| `limit:` | `deps.py`, `analysis.py`, `recommendation.py` | 15 component call sites |
| `Query(... le=` | `deps.py:77`, `analysis.py:86`, `recommendation.py:89` | N/A |
| `PaginationParams` | `deps.py:72` — used by 19 routes | N/A |
| `listDepartments` | `department.py:55` | `org-lookups.tsx`, `organization-management-page.tsx`, `khazina-api.ts` |
| `listUsers` | `user.py:51` | `users-management-page.tsx` |
| `listOrganizations` | N/A (single org model) | N/A |
| `listRisks` | `risk.py:66` | `risk-page.tsx`, `dashboard-page.tsx` |
| `listReports` | `report.py:160` | `reports-page.tsx` |
| `listRecommendations` | `recommendation.py:61` | `risk-page.tsx`, `dashboard-page.tsx`, `risk-detail-page.tsx` |

---

## Definition of Done (API Contract)

| Criterion | Status |
|-----------|--------|
| Every frontend `limit` ≤ backend max documented | ✅ This audit |
| Confirmed 422 mismatch identified with evidence | ✅ AC-001 |
| Architectural recommendation (which side is correct) | ✅ Backend `le=100` |
| Hidden mismatches searched | ✅ Full matrix above |
| Fix recommended with regression impact | ✅ Per issue |

**Next step:** Fix AC-001 in Sprint 1 (see `FINAL_STABILIZATION_AUDIT.md`).

---

## References

- Bug tracker: `docs/BUG_TRACKER.md` (KHZ-018 org lookups cache)
- Full platform audit: `docs/FULL_PLATFORM_QA_AUDIT.md`
- Stabilization sprints: `docs/FINAL_STABILIZATION_AUDIT.md`
