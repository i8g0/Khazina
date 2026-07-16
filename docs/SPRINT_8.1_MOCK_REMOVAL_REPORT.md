# Sprint 8.1 — Remove Remaining Mock Data

**Status:** Complete (frontend only)  
**Date:** 2026-07-16  
**Scope:** Remove user-visible fake values; wire existing APIs or show intentional Empty States. No backend changes. No commits.

---

## 1. Placeholders Removed

| Area | Removed |
|------|---------|
| **Dashboard KPIs** | 5 fake KPI values from `dashboardKpis` (amounts, trends, department badges) |
| **Dashboard charts** | `wasteByDepartment` and `wasteTrend` mock chart series |
| **Dashboard analyses** | Hardcoded `"ملف مصدر"` source file label |
| **Dashboard recommendations** | `"—"` confidence fallback |
| **Risk page** | Entire mock page: KPIs, charts, matrix, active table, AI recommendations, mitigation plans |
| **Waste breakdown** | `"—"` department column; empty vendor table |
| **Waste KPIs** | Fake `0` for null savings/opportunities |
| **Simulation** | Static `"—"` forecast placeholders before run; unwired assumptions/impact/actions |
| **Reports** | `"—"` / `"ملف مصدر"` department and source file labels; static department filter |
| **Data Management** | `"—"` department, size, quality score, import record count, validation details |
| **Global heroes** | Hardcoded `"الفترة النشطة"` replaced with live active reporting period (via `OrgLookupsProvider`) |

`placeholder-data.ts` was **not deleted** (archived per sprint rules).

---

## 2. APIs Connected

| API | Consumer |
|-----|----------|
| `GET .../departments` | `OrgLookupsProvider` → department names across Waste, Reports, Data Management |
| `GET .../financial-files` | `OrgLookupsProvider` → source file names on Dashboard, Reports |
| `GET .../reporting-periods` | `OrgLookupsProvider` → active period label on all executive pages |
| `GET .../analysis-runs/{runId}/waste/vendor-findings` | Waste page vendor table |
| `GET .../simulation/scenarios/{id}/assumptions` | Simulation page assumptions panel |
| `GET .../simulation/runs/{runId}/impact-items` | Simulation page impact breakdown |
| `GET .../simulation/runs/{runId}/action-items` | Simulation page action panel |

**New frontend client functions:** `listVendorFindings`, `listScenarioAssumptions`, `listImpactItems`, `listActionItems` in `lib/api/khazina-api.ts`.

**Type additions:** `WasteVendorFindingResponse`, `SimulationAssumptionResponse`, `SimulationImpactItemResponse`, `SimulationActionItemResponse`, `department_id` on `FinancialFileResponse`.

---

## 3. Empty States Introduced

| Location | Message |
|----------|---------|
| **Dashboard KPI cards (×5)** | Cards preserved; values replaced with executive messaging: no aggregation API yet |
| **Dashboard charts (×2)** | Per-chart Empty State: department distribution & waste trend unavailable until dashboard aggregation |
| **Risk page** | Full-page Empty State: Risk Engine not enabled in executive demo path (deferred) |
| **Waste vendor table** | Empty State when no vendor findings for the analysis run |
| **Simulation (pre-run)** | Empty State for forecast summary until scenario is executed |
| **Simulation assumptions** | Empty State when scenario has no assumptions |
| **Page heroes (no active period)** | Badge: `"لم تُحدَّد فترة تقرير نشطة"` |

---

## 4. Placeholders Intentionally Left (Phase 8+)

| Item | Reason |
|------|--------|
| **Dashboard executive KPI aggregation** | No backend aggregation API — Empty State only |
| **Dashboard waste-by-department / trend charts** | No dashboard aggregation API |
| **Risk engine UI** | Backend CRUD exists; product path deferred — Empty State only |
| **Reports Excel / PPTX export** | Disabled in `ReportsExportPanel` (Phase 8+ export formats) |
| **Risk subcomponents** (`risk-charts.tsx`, etc.) | Archived components; no longer mounted on Risk page |
| **Waste chart components** (`waste-charts.tsx`, etc.) | Not on executive demo path; archive retained |
| **`placeholder-data.ts`** | Historical Phase 2 archive — not deleted |
| **Settings / Org admin `"—"` fallbacks** | Admin configuration pages outside judge demo path |

---

## 5. Architectural Decisions

1. **`OrgLookupsProvider`** (`lib/org-lookups.tsx`): Centralized read-only cache for departments, financial files, and active reporting period. Loaded once per session; avoids N+1 lookups on Dashboard, Reports, Waste, and Data Management.

2. **`useOrganizationDisplay`** moved to `org-lookups.tsx` (re-exported from `auth-context.tsx` for compatibility). Uses live `activeReportingPeriod.label` instead of hardcoded Arabic placeholder.

3. **Dashboard KPI cards retained** (5-card grid) but values show contextual empty messaging — satisfies “do not remove cards” without fake numbers.

4. **Risk page** replaced content with a single professional Empty State; mock subcomponents left in repo unmounted.

5. **No invented calculations** — Simulation impact/actions/assumptions come only from API responses after run.

6. **No backend or API contract changes** — frontend types extended to match existing response schemas only.

---

## 6. Files Changed

- `frontend/lib/org-lookups.tsx` (created earlier; `useOrganizationDisplay` added)
- `frontend/lib/api/types.ts`
- `frontend/lib/api/khazina-api.ts`
- `frontend/lib/auth/auth-context.tsx` (re-export only)
- `frontend/components/providers/app-providers.tsx` (provider wrap — prior session)
- `frontend/components/dashboard/dashboard-page.tsx`
- `frontend/components/dashboard/dashboard-charts.tsx`
- `frontend/components/dashboard/dashboard-hero.tsx`
- `frontend/components/risk/risk-page.tsx`
- `frontend/components/waste/waste-page.tsx`
- `frontend/components/waste/waste-breakdown-table.tsx`
- `frontend/components/simulation/simulation-page.tsx`
- `frontend/components/reports/reports-page.tsx`
- `frontend/components/data/data-management-page.tsx`
- `frontend/components/ui/page-hero.tsx`

---

## 7. Validation

- `pnpm exec tsc --noEmit` — **PASS**
- No backend modifications
- No API contract modifications
- No git commits (per sprint spec)

---

## 8. Screenshots (Before / After)

Capture manually after `pnpm dev` at `http://localhost:3000`:

| Page | Before | After |
|------|--------|-------|
| Dashboard | Fake KPI numbers + demo charts | Empty KPI messaging + chart Empty States; live timeline/recommendations/analyses |
| Risk | Full mock KPIs/charts/tables | Single deferred-capability Empty State |
| Waste | Empty vendor table; `"—"` departments | Live vendor findings; department names from API |
| Simulation | `"—"` forecast; no assumptions/impact/actions | Live assumptions; results after run; impact & action panels |
| Reports | `"—"` / `"ملف مصدر"` labels | Real department & file names; department filter from API |
| Data Management | `"—"` department column | Department from `financial_files.department_id` |

---

## Definition of Done Checklist

- [x] No fake financial KPIs on judge-visible demo path
- [x] Every visible value from PostgreSQL (via API) or explicit Empty State
- [x] Quick wins wired (departments, files, period, vendors, simulation nested reads)
- [x] Dashboard & Risk empty states per priority 2 & 3
- [x] Reports labels wired where API supports
- [x] Typecheck passes
- [x] No backend changes
- [x] `placeholder-data.ts` preserved
