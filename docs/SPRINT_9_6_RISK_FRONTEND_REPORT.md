# Sprint 9.6 — Financial Risk Frontend Integration Report

**Sprint:** 9.6 — Financial Risk Frontend Integration  
**Date:** 2026-07-16  
**Status:** Complete  
**Architecture reference:** Sprints 9.1–9.5 backend (locked), Sprint 6.x AI infrastructure

---

## 1. Summary

Sprint 9.6 connects the existing Khazina frontend Risk UI to the completed Financial Risk backend. All Risk screens consume **real APIs only** — no mock data, no backend changes, no UI redesign.

**Validation:** TypeScript (`tsc --noEmit`) passes. ESLint passes. Backend suite unchanged at **287 passed**.

---

## 2. Pages Connected

| Route | Component | Purpose |
|-------|-----------|---------|
| `/risk-management` | `RiskPage` | Dashboard KPIs, charts, analysis execution, findings review, register, AI summary, recommendations |
| `/risk-management/risks/[riskId]` | `RiskDetailPage` | Risk detail, AI explanation, provenance, mitigation, audit history |

**Navigation:** Risk moved from deferred group **"وحدات لاحقة"** into primary executive path: `data → waste → risk → simulation → reports`.

---

## 3. APIs Consumed

All via `lib/api/khazina-api.ts` (native `fetch` + envelope pattern).

### Risk analysis (9.3)

| Function | Endpoint |
|----------|----------|
| `executeRiskAnalysis` | `POST .../risk-analyses/execute` |
| `listRiskAnalyses` | `GET .../risk-analyses` |
| `getRiskAnalysis` | `GET .../risk-analyses/{runId}` |
| `getRiskResult` | `GET .../risk-analyses/{runId}/result` |
| `listRiskFindings` | `GET .../risk-analyses/{runId}/findings` |

### Risk register & governance (9.4)

| Function | Endpoint |
|----------|----------|
| `listRisks` | `GET .../risks` |
| `getRisk` | `GET .../risks/{riskId}` |
| `reviewRiskFinding` | `POST .../risk-findings/{findingId}/review` |
| `promoteRiskFinding` | `POST .../risk-findings/{findingId}/promote` |
| `getRiskHistory` | `GET .../risks/{riskId}/history` |
| `getRiskProvenance` | `GET .../risks/{riskId}/provenance` |

### Mitigation & AI (9.5 + existing)

| Function | Endpoint |
|----------|----------|
| `listMitigationPlans` | `GET .../mitigation-plans` |
| `listRiskMitigationPlans` | `GET .../risks/{riskId}/mitigation-plans` |
| `generateRiskAi` | `POST .../ai-recommendations/risk/generate` |
| `listRecommendations` | `GET .../recommendations?domain_source=risk` |

### Shared / dashboard

| Function | Usage |
|----------|-------|
| `getAiHealth` | AI availability gate |
| `listTimeline` | Executive dashboard timeline (unchanged) |
| `listRecentAnalyses` | Includes risk runs with `mapAnalysisType("risk")` |
| `listRisks` | Dashboard critical-risk KPI |

---

## 4. Components Reused vs Extended

### Reused (props wired to API — no mock imports)

| Component | Change |
|-----------|--------|
| `risk-active-table.tsx` | Accepts `data: RiskItemView[]`; links to detail page |
| `risk-charts.tsx` | Accepts severity/department/category chart props |
| `risk-priority-matrix.tsx` | Accepts `items: RiskMatrixItemView[]` |
| `risk-mitigation-plans.tsx` | Accepts `plans: RiskMitigationPlanView[]` |
| `risk-recommendation-card.tsx` | Accepts API-mapped recommendation; removed fake confidence maps |

### New (same design system)

| Component | Role |
|-----------|------|
| `risk-findings-table.tsx` | Review workflow: request_review, approve, reject, dismiss, promote |
| `risk-analyses-table.tsx` | Analysis history |
| `risk-ai-summary.tsx` | Executive summary, brief, explanation, board report |
| `risk-idle-content.tsx` | Empty/onboarding when no analysis yet |
| `risk-detail-page.tsx` | Full risk detail with provenance & audit |
| `risk-page.tsx` | Main orchestrator (replaces EmptyState placeholder) |

### Supporting modules

| Module | Role |
|--------|------|
| `lib/risk/view-types.ts` | UI view models |
| `lib/risk/mappers.ts` | API → UI mapping |
| `lib/format.ts` | Risk labels (priority, lifecycle, categories, posture) |
| `lib/demo/state.ts` | Added `riskRunId`, `riskAiReady` session persistence |

---

## 5. Feature Coverage vs Sprint Tasks

| Task | Status |
|------|--------|
| Risk Dashboard (KPIs, charts, latest analyses, executive summary) | ✅ |
| Risk Analysis (execute, history, details, findings, categories, AI) | ✅ |
| Findings Review (review, approve, reject, dismiss, promote) | ✅ |
| Risk Register (lifecycle, priority, severity, owner, provenance) | ✅ |
| Risk Detail (summary, AI, recommendations, history, provenance) | ✅ |
| Dashboard integration (critical risks KPI, analysis type label) | ✅ |
| Loading / empty / error / AI unavailable states | ✅ |
| Waste / simulation / reports regression | ✅ (no changes to those modules) |
| TypeScript + lint | ✅ |

---

## 6. Workflow & State

1. User uploads financial file via Data Management (`fileId`, `snapshotId` in session).
2. **Risk page** → `executeRiskAnalysis` → stores `riskRunId`.
3. Parallel fetch: result, findings, register, mitigation plans.
4. Optional: `generateRiskAi` → insights in `runtime_metadata.ai_insights` + `Recommendation` rows.
5. Finding review actions call register governance APIs.
6. Promoted findings appear in register table; detail page at `/risk-management/risks/{id}`.

---

## 7. Loading & Empty States

Every Risk section handles:

- **Loading:** `OperationLoadingPanel`, `LoadingSkeleton`
- **Empty:** `EmptyState` with executive copy (no placeholders)
- **Error:** `ErrorState` + retry via `formatApiError`
- **AI unavailable:** `getAiHealth` + `EXECUTIVE_MESSAGES.aiUnavailable`
- **No file uploaded:** Link to Data Management + idle content

---

## 8. Mock Data Removal

Risk components **no longer import** from `lib/placeholder-data.ts`. Legacy mock exports remain in that file for reference only (orphaned). All displayed values originate from backend responses.

---

## 9. Validation Results

| Check | Result |
|-------|--------|
| `npx tsc --noEmit` | Pass |
| `npm run lint` | Pass (no warnings) |
| Backend `pytest` | 287 passed |
| Backend API changes | None |
| Risk Engine / Register / AI changes | None |
| Waste / Simulation pages | Unchanged |

---

## 10. Remaining UI Work (Future Sprints)

1. **Dedicated analysis detail route** — e.g. `/risk-management/analyses/[runId]` (currently inline on main page).
2. **Register lifecycle actions on detail page** — PATCH status / governance review buttons (APIs exist; detail page shows read-only lifecycle today).
3. **Dashboard KPI full wiring** — waste/savings KPIs still show empty until waste pipeline runs (by design).
4. **Pipeline indicator** — optional `risk` stage in `PIPELINE_STAGES` after waste.
5. **Remove orphaned mock exports** from `placeholder-data.ts` once confirmed unused in docs/scripts.
6. **English locale** — prompts are Arabic; UI labels remain Arabic per product default.

---

## 11. Files Created / Modified

### New

- `frontend/lib/risk/view-types.ts`
- `frontend/lib/risk/mappers.ts`
- `frontend/components/risk/risk-findings-table.tsx`
- `frontend/components/risk/risk-analyses-table.tsx`
- `frontend/components/risk/risk-ai-summary.tsx`
- `frontend/components/risk/risk-idle-content.tsx`
- `frontend/components/risk/risk-detail-page.tsx`
- `frontend/app/(shell)/risk-management/risks/[riskId]/page.tsx`
- `docs/SPRINT_9_6_RISK_FRONTEND_REPORT.md`

### Modified

- `frontend/lib/api/types.ts` — Risk + extended Recommendation types
- `frontend/lib/api/khazina-api.ts` — Risk API client functions
- `frontend/lib/format.ts` — Risk label mappers
- `frontend/lib/demo/state.ts`, `hooks.ts` — `riskRunId`, `riskAiReady`
- `frontend/lib/app-nav.tsx` — Risk in primary nav
- `frontend/components/risk/*.tsx` — Props-based, API-driven
- `frontend/components/dashboard/dashboard-page.tsx` — Critical risks KPI from `listRisks`

### Unchanged

- Backend (all modules)
- Waste, simulation, reports, data-management pages
- Design system components

---

## 12. Definition of Done

| Criterion | Status |
|-----------|--------|
| Risk pages use only real backend APIs | ✅ |
| No mock data in Risk UI | ✅ |
| Risk Register functional | ✅ |
| Findings review workflow | ✅ |
| AI summaries visible | ✅ |
| Dashboard integrated | ✅ |
| TypeScript passes | ✅ |
| Lint passes | ✅ |
| No backend changes | ✅ |
| No redesign introduced | ✅ |
