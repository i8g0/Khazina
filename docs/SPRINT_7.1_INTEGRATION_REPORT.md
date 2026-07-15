# Sprint 7.1 — Frontend Integration Report

**Status:** Complete (frontend-only)  
**Date:** 2026-07-15  
**Constraint:** Phase 6 backend frozen — no API/backend changes; stop on contract gaps

---

## 1. Page × endpoint matrix

| Page | Route | Backend Connected | Status | Endpoints | Notes |
|------|-------|-------------------|--------|-----------|-------|
| Login | `/login` | Yes | **Live** | `POST /auth/login`, `GET /organizations/active` | Demo credentials prefilled only |
| Dashboard | `/` | Partial | **Hybrid** | `GET .../timeline/events`, `.../analysis-runs/recent-completed`, `.../recommendations` | KPIs + charts remain mock — **no aggregation API** (Phase 7 analytics deferred) |
| Data Management | `/data-management` | Yes | **Live** | upload, list files, import-records (per file), quality snapshot + checks | Department column `"—"` (API has `department_id` only) |
| Financial Waste | `/financial-waste` | Yes | **Live** | upload, waste execute, result, breakdowns, AI generate | Department name not on breakdown response |
| Business Simulation | `/business-simulation` | Yes | **Live** | list/create scenarios, execute, forecast, chart-points, comparison-metrics | Create form wired to `POST .../simulation/scenarios` |
| Reports | `/reports` | Yes | **Live** | list, content, generate, PDF export | Excel/PPTX export deferred by design; dept/file names → `"—"` / `"ملف مصدر"` |
| Risk Management | `/risk-management` | No | **Mock by design** | — | No Phase 6 risk engine for demo path |
| Settings | `/settings` | Yes | **Live (new)** | `GET/PATCH .../settings` | Six editable sections + read-only identity |
| Notifications | Header bell (no route) | Yes | **Live** | list, unread-count, mark read | Poll 30s; no dedicated page |

---

## 2. Removed / replaced mock data

| Was mock | Now |
|----------|-----|
| Data Management import history + quality KPIs | Live import-records + quality snapshot/checks |
| Wrong import-records path (`/import-records`) | Corrected to `/financial-files/{fileId}/import-records` |
| Org name/period from `placeholder-data.organization` on Waste / Simulation / Reports / Risk / Data / Dashboard | Session via `useOrganizationDisplay()` |
| Reports fake `الشؤون المالية` / `Procurement_Q2.xlsx` | Neutral placeholders where API has IDs only |
| Waste hardcoded title `Procurement_Q2` + dept `المشتريات` | Generic title; department `"—"` |
| Settings page missing | New page consuming GET/PATCH settings |
| Scenario create missing in client | `createScenario` + minimal create controls |
| `apiRequest` treating successful `data: null` as error | `allowNull` for quality snapshot + forecast summary |

---

## 3. Remaining placeholders (intentional)

| Item | Reason |
|------|--------|
| Dashboard KPI cards (`dashboardKpis`) | No executive aggregation API in Phase 6 freeze |
| Dashboard charts (`wasteByDepartment`, `wasteTrend`) | Same — deferred analytics |
| Risk Management full page mock | No risk engine in Phase 6 demo baseline |
| Report Excel / PPTX export buttons | Backend PDF only (Excel/PPTX deferred) |
| `reportingPeriod` label `"الفترة النشطة"` | No active reporting-period label on session/active-org response used by UI |
| Department **names** on waste/reports/files | API returns `department_id` only; no name-resolution endpoint wired |
| Orphan mock components (`waste-charts.tsx`, etc.) | Not mounted; left untouched (no redesign) |

---

## 4. Backend / frontend contract mismatches (STOP items)

### 4.1 Settings PDF preferences not in API response schema — **STOP**

- **Domain** (`app/settings/models.py` / resolver) and consumers honor `pdf_export_enabled`, `pdf_include_cover_page`, `pdf_include_provenance_appendix`.
- **API schema** `ReportPreferencesSectionResponse` / patch **omit** these fields.
- **Frontend action:** Settings UI exposes only fields returned by GET settings. Does **not** invent PDF prefs controls or PATCH keys.
- **Recommended backend fix:** Add PDF fields to `ReportPreferencesSectionResponse` and `ReportPreferencesSectionPatch` so they round-trip with `to_api_dict`.

### 4.2 No token refresh / logout API — **documented deferral**

- Backend auth: `POST /auth/login` → `{ access_token, token_type }` only.
- Frontend: logout clears `localStorage` + demo artifacts; 401 surfaces as re-login message.
- **Not invented:** refresh-token client or fake refresh endpoint.

### 4.3 No dashboard KPI/chart aggregation API — **documented deferral**

- Freeze explicitly deferred Executive Dashboard aggregation.
- UI keeps mock KPIs/charts with existing Phase 7 badge copy.
- **Not invented:** client-side “aggregation” from unrelated endpoints.

### 4.4 Nullable success payloads vs client (fixed on frontend)

- Backend: `GET .../data-quality-snapshots/latest` and forecast-summary may return `success` with `data: null`.
- Previous client threw on any `null` data.
- **Fixed:** `apiRequest(..., { allowNull: true })` for those two calls only.

### 4.5 Department / source file display names

- List/report/waste responses expose UUIDs, not Arabic names.
- Frontend shows `"—"` / generic “ملف مصدر” rather than inventing names.

---

## 5. Recommended fixes (backend — separate approval)

1. Expose `pdf_export_*` on settings report_preferences response + patch schemas.
2. Optional: add executive dashboard aggregation endpoint(s) for KPIs/charts.
3. Optional: `POST /auth/logout` + refresh token pair if product requires server-side session revoke.
4. Optional: include department **name** (or expand) on breakdown/report/file list DTOs if UI must show department labels.
5. Optional: dedicated Notifications Center route (API already exists).

---

## 6. Priority checklist (Done)

| Priority | Area | Result |
|----------|------|--------|
| 1 | Auth — login, session, logout, route gate | Done (no refresh API) |
| 2 | Dashboard | Live lists; KPIs/charts remain deferred mock |
| 3 | Data Management | Live upload/list/quality/import |
| 4 | Financial Waste | Live pipeline |
| 5 | Scenario | Create + execute + results + comparison |
| 6 | Reports | List/details/generate/PDF |
| 7 | Notifications | Bell: unread, list, mark read |
| 8 | Settings | Six sections on `/settings` |

---

## 7. Definition of Done

**Met:** Every existing page that has corresponding Phase 6 APIs consumes those APIs. Mock remains only where capability is missing by freeze design (dashboard aggregation, risk engine, Excel/PPTX).

**Contract STOP respected:** Settings PDF fields not faked; dashboard aggregation not invented; auth refresh not invented.
