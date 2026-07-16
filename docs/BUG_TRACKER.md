# Khazina — Bug Tracker

**Audit date:** 2026-07-16  
**Last updated:** 2026-07-17 (Sprint 4 Executive Presentation)  
**Auditor role:** Lead QA / SDET / Security / Product  
**Scope:** Full platform (frontend + backend + demo workflow)  
**Method:** Static code audit, automated test run (290 backend tests), API/log correlation, cross-module pattern analysis

**Legend — Status:** `Open` | `Fixed` | `Deferred` | `Won't Fix (by design)`

---

## Summary by Severity

| Severity | Open | Fixed | Total |
|----------|------|-------|-------|
| Critical | 3 | 1 | 4 |
| High | 3 | 9 | 12 |
| Medium | 17 | 1 | 18 |
| Low | 10 | 0 | 10 |
| Cosmetic | 3 | 1 | 4 |
| **Total** | **37** | **11** | **48** |

---

## Critical

### KHZ-001 — Upload memory DoS (read before size limit)

| Field | Value |
|-------|-------|
| **Severity** | Critical |
| **Status** | Open |
| **Module** | Data / Backend |
| **Description** | Full upload body loaded into memory before `max_upload_size_bytes` check |
| **Reproduction** | POST multipart file >> 10MB to `/financial-files/upload` |
| **Expected** | Reject at size limit without buffering entire file |
| **Actual** | `await upload.read()` then validate — memory exhaustion possible |
| **Root cause** | `financial.py` L81 reads full content before ingestion validation |
| **Proposed fix** | Chunked read with running byte count or proxy body limit |

---

### KHZ-002 — Unconditional dev auto-login in client bundle

| Field | Value |
|-------|-------|
| **Severity** | Critical |
| **Status** | Open |
| **Module** | Auth |
| **Description** | `AuthProvider` auto-logs in with hardcoded demo credentials when no session |
| **Reproduction** | Open app with empty localStorage; backend reachable |
| **Expected** | Redirect to login |
| **Actual** | Silent login as `demo@khazina.sa` |
| **Root cause** | `auth-context.tsx` `hydrateSession()` dev auto-login not env-gated |
| **Proposed fix** | Gate behind `NEXT_PUBLIC_DEV_AUTO_LOGIN`; remove from production builds |

**Demo risk:** Judges may not realize they're on a shared demo account.

---

### KHZ-003 — Login form pre-filled with demo credentials

| Field | Value |
|-------|-------|
| **Severity** | Critical |
| **Status** | Open |
| **Module** | Login |
| **Description** | Email/password defaults expose credentials in UI |
| **Reproduction** | Navigate to `/login` |
| **Expected** | Empty fields |
| **Actual** | Pre-filled `demo@khazina.sa` / `DemoExec2026!` |
| **Root cause** | `login/page.tsx` default `useState` values |
| **Proposed fix** | Empty defaults; dev prefill behind env flag only |

---

### KHZ-004 — Database schema drift (Phase 9 migrations not applied)

| Field | Value |
|-------|-------|
| **Severity** | Critical |
| **Status** | **Fixed** |
| **Module** | Backend / Ops |
| **Description** | Code expects `risks.lifecycle_status`; DB at old revision → 500 on `GET /risks` |
| **Reproduction** | Run app without `alembic upgrade head`; open dashboard/risk after login |
| **Expected** | Risk register loads |
| **Actual** | `UndefinedColumn: risks.lifecycle_status does not exist` → 500 → "فشل الطلب" |
| **Root cause** | Migrations `e8a1c4f03d21`, `f9c2d7a31b44` not applied on demo DB |
| **Proposed fix** | `alembic upgrade head` in dev/demo checklist (**applied 2026-07-16**) |

---

### KHZ-047 — Departments API pagination contract mismatch (422)

| Field | Value |
|-------|-------|
| **Severity** | Critical |
| **Status** | **Fixed** |
| **Module** | API / Organization |
| **Description** | `OrgLookupsProvider` requested `limit: 200`; backend enforces `limit <= 100` |
| **Reproduction** | Login → app load → `GET /departments?limit=200` → 422 |
| **Expected** | 200 + department list |
| **Actual** | 422 Validation failed; empty department lookups |
| **Root cause** | No shared max page size between FE and BE |
| **Fix (Sprint 1)** | `MAX_LIST_LIMIT = 100` in `frontend/lib/api/pagination.ts`; org-lookups uses constant |
| **Verified** | 2026-07-16 — grep confirms no FE `limit > 100` |

---

## High

### KHZ-005 — No server-side route protection (client-only auth)

| Field | Value |
|-------|-------|
| **Severity** | High |
| **Status** | Open |
| **Module** | Auth |
| **Description** | All shell routes render without server auth; protection is client `useEffect` only |
| **Reproduction** | Disable JS or inspect HTML source of `/users` without session |
| **Expected** | Server redirect / 401 |
| **Actual** | Page shell delivered; auth enforced after hydration |
| **Root cause** | No `middleware.ts` |
| **Proposed fix** | Next.js middleware with session cookie check |

---

### KHZ-006 — HTTP 401 does not clear session or redirect

| Field | Value |
|-------|-------|
| **Severity** | High |
| **Status** | Open |
| **Module** | Auth / API |
| **Description** | Expired token shows error but remains in localStorage |
| **Reproduction** | Invalidate JWT server-side; trigger any API call |
| **Expected** | Auto logout + redirect `/login` |
| **Actual** | Error message; stale token persists; repeated 401s |
| **Root cause** | No global 401 handler in `client.ts` |
| **Proposed fix** | Interceptor calling `clearSession()` + redirect |

---

### KHZ-007 — No frontend RBAC (all roles access admin screens)

| Field | Value |
|-------|-------|
| **Severity** | High |
| **Status** | Open |
| **Module** | Users / Organization / Settings |
| **Description** | `useRequireAuth()` checks session only, not role |
| **Reproduction** | Login as analyst; open `/users`, `/settings` |
| **Expected** | Role-based denial |
| **Actual** | Full access if backend allows (backend enforces on mutations) |
| **Root cause** | User role not stored in session snapshot |
| **Proposed fix** | `useRequireRole()` guard + nav hiding |

---

### KHZ-008 — IDOR: `GET /risks/{id}` without org ownership check

| Field | Value |
|-------|-------|
| **Severity** | High |
| **Status** | Open |
| **Module** | Risk / Security |
| **Description** | Any authenticated org user can read another org's risk by UUID |
| **Reproduction** | `GET /organizations/{orgA}/risks/{riskIdFromOrgB}` with orgA token |
| **Expected** | 403 or 404 |
| **Actual** | 200 + foreign risk data |
| **Root cause** | `RiskService.get_risk(risk_id)` — no org parameter |
| **Proposed fix** | Use `_owned_risk(organization_id, risk_id)` |

---

### KHZ-009 — Systemic IDOR on GET-by-ID routes (8 additional endpoints)

| Field | Value |
|-------|-------|
| **Severity** | High |
| **Status** | Open |
| **Module** | Security / API |
| **Description** | Same pattern as KHZ-008 on multiple resources |
| **Affected routes** | `GET analysis-runs/{id}`, `reports/{id}`, `departments/{id}`, `simulation/scenarios/{id}`, `simulation/runs/{id}`, `recommendations/{id}`, `timeline/events/{id}`, `reporting-periods/{id}` |
| **Root cause** | Service `get_* (id_only)` without `_check_ownership` |
| **Proposed fix** | Standardize `_owned_*` on all read paths |

---

### KHZ-010 — Dual risk lifecycle APIs desync `status` vs `lifecycle_status`

| Field | Value |
|-------|-------|
| **Severity** | High |
| **Status** | Open |
| **Module** | Risk Register |
| **Description** | Legacy `POST .../transition` updates `status` only; governance API uses `lifecycle_status` |
| **Reproduction** | Transition to `closed` via legacy API; check `lifecycle_status` |
| **Expected** | Both fields synchronized |
| **Actual** | `status=closed`, `lifecycle_status` unchanged |
| **Root cause** | Two write paths on same `Risk` row |
| **Proposed fix** | Deprecate legacy transition or route through register service |

---

### KHZ-011 — Risk page shows stale run results after new upload

| Field | Value |
|-------|-------|
| **Severity** | High |
| **Status** | Open |
| **Module** | Risk |
| **Description** | After re-upload clears `riskRunId`, old findings/KPIs remain visible |
| **Reproduction** | Run risk → upload new file on Data Management → return to Risk |
| **Expected** | Results cleared (like waste page `resetResults`) |
| **Actual** | Previous run data still shown (`ready=true`) |
| **Root cause** | `refreshAll()` skips reset when `artifacts.riskRunId` is null |
| **Proposed fix** | Add `resetResults()` when `riskRunId` cleared; mirror waste-page effect |

---

### KHZ-012 — Waste AI recommendations lost on page refresh

| Field | Value |
|-------|-------|
| **Severity** | High |
| **Status** | **Fixed** |
| **Module** | Waste |
| **Description** | `aiRecommendationsReady` flag persists but recommendation list not re-fetched |
| **Reproduction** | Run waste → generate AI → F5 refresh |
| **Expected** | Recommendations visible |
| **Actual** | Empty list; workflow shows AI step complete |
| **Root cause** | Recommendations only set in `runAi()`; no mount reload |
| **Fix (Sprint 1)** | `loadResults()` fetches `listRecommendations` from DB; syncs `aiRecommendationsReady` |
| **Verified** | 2026-07-16 — `waste-page.tsx` |

---

### KHZ-013 — Pipeline state in sessionStorage vs auth in localStorage

| Field | Value |
|-------|-------|
| **Severity** | High |
| **Status** | **Partially Fixed** (Sprint 1) |
| **Module** | Workflow |
| **Description** | Closing tab loses artifacts; multi-tab has isolated state |
| **Reproduction** | Complete pipeline → close tab → reopen (still logged in) |
| **Expected** | Workflow progress preserved or recoverable |
| **Actual** | All run IDs lost; user logged in but pipeline empty |
| **Root cause** | Split storage strategy |
| **Fix (Sprint 1)** | Demo artifacts moved to `localStorage` (persists across tabs/restart) |
| **Remaining** | DB hydration when artifacts empty — Sprint 3 |

---

### KHZ-053 — In-flight fetch race after re-upload

| Field | Value |
|-------|-------|
| **Severity** | High |
| **Status** | **Partially Fixed** (Sprint 1 — waste page only) |
| **Module** | Waste / Simulation |
| **Fix (Sprint 1)** | `AbortController` cancels stale `loadResults` when `wasteRunId` changes |
| **Remaining** | Simulation page — Sprint 3 |

---

### KHZ-054 — Upload without snapshot leaves stale artifacts

| Field | Value |
|-------|-------|
| **Severity** | High |
| **Status** | **Fixed** |
| **Module** | Data |
| **Fix (Sprint 1)** | `registerNewFinancialFile()` clears downstream run IDs when snapshot is null |
| **Verified** | 2026-07-16 — `data-management-page.tsx` |

---

### KHZ-014 — Risk execute sent both snapshot identifier fields

| Field | Value |
|-------|-------|
| **Severity** | High |
| **Status** | **Fixed** |
| **Module** | Risk |
| **Description** | Request included both `source_snapshot_id` and `snapshot_version` |
| **Reproduction** | Upload → Run Risk Analysis |
| **Expected** | 201 |
| **Actual** | 400 "Provide either source_snapshot_id or snapshot_version, not both" |
| **Root cause** | `risk-page.tsx` sent both fields from demo artifacts |
| **Proposed fix** | Send `source_snapshot_id` only (**fixed 2026-07-16**) |

---

## Medium

### KHZ-015 — Dashboard waste KPI always null

| Module | Dashboard | **Status** | Open  
| **Description** | First KPI hardcoded `null`; never wired to waste results  
| **Files** | `dashboard-page.tsx` L151–157  

### KHZ-016 — Dashboard charts permanently empty (unwired)

| Module | Dashboard | **Status** | Open  
| **Description** | `DashboardCharts` shows placeholder only; no API integration  
| **Files** | `dashboard-charts.tsx`  

### KHZ-017 — Risk omitted from executive workflow pipeline

| Module | Workflow | **Status** | Open  
| **Description** | `PIPELINE_STAGES` has no risk step; nav includes risk  
| **Files** | `lib/workflow/pipeline.ts`  

### KHZ-018 — Org lookups cache never refreshed after mutations

| Module | Organization / Data | **Status** | Open  
| **Description** | `OrgLookupsProvider.refresh()` not called after upload/create dept  
| **Files** | `org-lookups.tsx`, data/organization pages  

### KHZ-019 — Risk detail provenance shows wrong file label

| Module | Risk | **Status** | Open  
| **Description** | `fileName(source_snapshot_id)` — UUID type mismatch  
| **Files** | `risk-detail-page.tsx` L102–104  

### KHZ-020 — Simulation hydration errors silently swallowed

| Module | Simulation | **Status** | Open  
| **Description** | `.catch(() => undefined)` hides load failures  
| **Files** | `simulation-page.tsx` ~L309  

### KHZ-021 — Upload success when snapshot null leaves pipeline broken

| Module | Data | **Status** | **Partially Fixed** (Sprint 1)  
| **Fix** | `registerNewFinancialFile()` clears stale run IDs; user must wait for snapshot before analysis  

### KHZ-022 — PDF export uses lastReportId not selected report

| Field | Value |
|-------|-------|
| **Severity** | High |
| **Status** | **Fixed** (Sprint 2) |
| **Module** | Reports |
| **Fix** | `resolveExportReportId()` + card selection + per-card PDF export |
| **Verified** | 2026-07-16 — `report-export.ts`, `reports-page.tsx` |

---

### KHZ-023 — Risk report uses waste default title

| Field | Value |
|-------|-------|
| **Severity** | High |
| **Status** | **Fixed** (Sprint 2) |
| **Module** | Reports |
| **Fix** | Required `title` param; `REPORT_TITLES.risk` / waste / simulation |
| **Verified** | 2026-07-16 — `khazina-api.ts`, `reports-page.tsx` |

---
### KHZ-024 — Settings `require_ai_insights_before_report` not enforced in UI

| Module | Settings / Reports | **Status** | Open  
| **Description** | Reports page ignores org setting gate  

### KHZ-025 — Phantom financial file registration bypasses upload

| Module | Data / Backend | **Status** | Open  
| **Description** | POST `/financial-files` with fake storage_path can reach ready-for-analysis  
| **Files** | `financial.py`, `financial.py` service  

### KHZ-026 — Duplicate reports on concurrent generate

| Module | Reports / Backend | **Status** | Open  
| **Description** | No uniqueness on `reports.analysis_run_id`  
| **Files** | `reports/service.py`  

### KHZ-027 — Inconsistent cross-org error semantics (403 vs 404 vs 200)

| Module | Security | **Status** | Open  
| **Description** | Reports mask as 404; risks leak as 200  

### KHZ-028 — Waste results race condition (no request cancellation)

| Module | Waste | **Status** | Open  
| **Description** | Parallel analyses can show stale run data  

### KHZ-029 — `useDemoArtifacts` flashes empty workflow on mount

| Module | Workflow | **Status** | Open  
| **Description** | First render always EMPTY before useEffect reads sessionStorage  

### KHZ-030 — Dashboard recommendations not filtered by domain

| Module | Dashboard | **Status** | Open  
| **Description** | Shows all recommendations; waste/risk mixed  

### KHZ-031 — Enterprise risk lifecycle UI unwired on detail page

| Module | Risk | **Status** | Open  
| **Description** | `updateRiskLifecycleStatus`, `reviewEnterpriseRisk` unused  

### KHZ-032 — Health endpoints expose infrastructure detail without auth

| Module | Backend / Security | **Status** | Open  
| **Description** | `/health`, `/ai/health` public with DB/Ollama/model info  

---

## Low

### KHZ-033 — No login rate limiting

| Module | Auth | **Status** | Open  

### KHZ-034 — Risk likelihood/impact accept arbitrary strings

| Module | Risk / Backend | **Status** | Open  

### KHZ-035 — Manual risk register skips category_code FK

| Module | Risk | **Status** | Open  

### KHZ-036 — Notification materialization skipped when initiating_user_id null

| Module | Notifications | **Status** | Open  

### KHZ-037 — Concurrent decision execute opaque 409

| Module | Waste / Risk | **Status** | Open  

### KHZ-038 — Department patch API unwired in UI

| Module | Organization | **Status** | Open  

### KHZ-039 — Notification bell mark-read no error handling

| Module | Notifications | **Status** | Open  

### KHZ-040 — AI health status inconsistent across pages

| Module | Dashboard / Waste / Risk | **Status** | Open  

### KHZ-041 — Dead code: waste chart components with placeholder data

| Module | Waste | **Status** | Open  

### KHZ-042 — Risk analysis history rows not selectable

| Module | Risk | **Status** | Open  

---

## Cosmetic

### KHZ-043 — Notification badge uses physical `left` in RTL layout

| Module | Notifications | **Status** | Open  
| **Files** | `notification-bell.tsx` L90  

### KHZ-044 — Reports card shows raw ISO date

| Module | Reports | **Status** | **Fixed** (Sprint 2)  
| **Fix** | `formatDate()` in reports-card  

### KHZ-045 — PDF export error message waste-specific only

| Module | Reports | **Status** | Open  

### KHZ-046 — Orphan risk mock data in placeholder-data.ts

| Module | Risk | **Status** | Open  

---

## Demo-Day Priority (Judge Impact)

| Priority | Bug IDs | Why |
|----------|---------|-----|
| **P0 — Fix before demo** | KHZ-004 ✓, KHZ-014 ✓, KHZ-011, KHZ-012, KHZ-013 | Breaks visible workflow |
| **P0 — Verify ops** | KHZ-004 | Run `alembic upgrade head` on demo machine |
| **P1 — Mitigate narratively** | KHZ-015, KHZ-016, KHZ-017 | Empty KPIs/charts — explain as Phase 10 |
| **P1 — Don't demo** | KHZ-002, KHZ-003 | Security optics if judges inspect login |
| **P2 — Post-demo** | KHZ-008–009, KHZ-001 | Security hardening |

---

## Fixed Issues Log

| ID | Fixed date | Verification |
|----|------------|--------------|
| KHZ-004 | 2026-07-16 | `alembic current` → `f9c2d7a31b44`; GET /risks → 200 |
| KHZ-014 | 2026-07-16 | Risk execute sends `source_snapshot_id` only; tsc pass |
| KHZ-012 | 2026-07-16 | Waste page reloads recommendations from DB on mount |
| KHZ-047 | 2026-07-16 | org-lookups uses `MAX_LIST_LIMIT` (100); no FE limit > 100 |
| KHZ-054 | 2026-07-16 | Upload without snapshot calls `registerNewFinancialFile()` |
| KHZ-022 | 2026-07-16 | Export resolves selected/active-run report ID |
| KHZ-055 | 2026-07-17 | Facts adapter drops metadata/period — fixed in Sprint 3 (`adapter.py`) |
| KHZ-056 | 2026-07-17 | Category names invisible in AI prompts — evidence blocks + `category_label_ar` |
| KHZ-057 | 2026-07-17 | Anti-number prompt rule caused vague AI — rewritten in `ar.py` v1.1 |
| KHZ-058 | 2026-07-17 | No waste Gold supplement for AI — `waste_metadata.py` + `waste_gold_context` |
| KHZ-059 | 2026-07-17 | Parser accepted hallucinated numbers — `evidence_registry.py` validation |
| KHZ-060 | 2026-07-17 | English category names in AI output — `business_labels.py` + sanitizer |
| KHZ-061 | 2026-07-17 | Generic category references — structured الدليل + validation |
| KHZ-062 | 2026-07-17 | Repetitive recommendation angles — `assign_executive_angles()` |
| KHZ-063 | 2026-07-17 | PDF/report English category labels — Arabic labels in layout v2.1 |
| KHZ-023 | 2026-07-16 | Domain-specific report titles on generate |
