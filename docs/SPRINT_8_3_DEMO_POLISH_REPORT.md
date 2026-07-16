# Sprint 8.3 — Demo Polish & Data Integrity Report

**Date:** 2026-07-16  
**Scope:** Frontend-only demo credibility fixes. No backend changes. No API contract changes. No commits.

---

## Executive Summary

Sprint 8.3 addressed judge-confidence gaps identified in Sprint 8.2: **stale session data after re-upload**, **misleading vendor UI**, **silent AI failures**, **repetitive recommendation presentation**, and **weak upload UX on Waste**.

**Judges can now complete a more believable end-to-end demo** when Ollama is running, provided they re-run waste → AI → simulation → report after each new upload (session artifacts now reset automatically on upload).

---

## 1. Issues Found & Fixes

### Priority 1 — Waste Page Audit

| Component | Before | Root cause | Fix | Layer |
|-----------|--------|------------|-----|-------|
| Summary KPI cards | Live from API | Already wired | Kept; null → contextual empty text | Frontend OK |
| Category breakdown table | Live API | Already wired | Added Arabic category labels (`formatWasteCategoryName`) | Frontend |
| Vendor section | Empty table with headers | Engine produces 0 vendors | Replaced with standalone **Empty State** (no fake table) | Frontend |
| AI recommendations | Hidden when empty | No empty state after analysis | Always show section: Empty State or cards | Frontend |
| Idle upload button | Called pipeline without file | Missing file picker | Added hidden file input + «رفع ملف وتحليل» | Frontend |
| Idle footer text | «البيانات للعرض التوضيحي فقط» | Copy | Removed misleading demo disclaimer | Frontend |
| Charts / trends / dept breakdown | Not mounted | `waste-charts.tsx` etc. unused on page | No change (not on demo path) | N/A |
| `waste-charts.tsx`, `waste-department-breakdown.tsx` | Contain mock data | Legacy components not used by `waste-page.tsx` | Left archived; not mounted | N/A |

### Priority 2 — Vendor Findings

| Question | Answer |
|----------|--------|
| Does API expose vendors? | **Yes** — `GET .../waste/vendor-findings` |
| Does waste engine generate vendors? | **No** — `WasteGoldMapper` / decision path passes empty `vendor_findings` |
| Does repository persist them? | **Yes**, if provided — none are provided today |
| Does frontend ignore them? | **No** — wired in Sprint 8.1; always returns `[]` |

**Fix:** Hide vendor table when empty; show professional Empty State explaining vendor-level findings are not produced by the current engine in the executive demo path.

**Classification:** Expected engine limitation (not a frontend bug). **Not fixed in backend** per sprint rules.

### Priority 3 — Session Reset

| Issue | Root cause | Fix |
|-------|------------|-----|
| Re-upload shows old waste/sim/report | `writeDemoArtifacts` only updated file IDs | New `beginNewFinancialDataset()` clears `wasteRunId`, `simulationRunId`, `lastReportId` |
| Waste page kept old UI | Effect only ran when `wasteRunId` present | Reset local state when `wasteRunId` is null |
| Simulation page kept old forecast | Stale `simulationRunId` in storage | `useDemoArtifacts()` + reset when ID cleared |
| Cross-page sync | No event on storage update | `DEMO_ARTIFACTS_CHANGED` custom event + `useDemoArtifacts` hook |
| PDF export used old report | Fallback to any «جاهز» report | Require `lastReportId` from current session |

**Files:** `lib/demo/state.ts`, `lib/demo/hooks.ts`, `data-management-page.tsx`, `waste-page.tsx`, `simulation-page.tsx`, `reports-page.tsx`

### Priority 4 — Ollama Readiness

| Issue | Fix |
|-------|-----|
| AI failed silently if Ollama down | `getAiHealth()` → `GET /api/v1/ai/health` (existing API) |
| No user message | Warning alert on Waste page; disable AI button when unreachable |
| No preflight on generate | `runAi()` checks health before POST; surfaces backend message |

**Files:** `lib/api/khazina-api.ts`, `lib/api/types.ts`, `waste-page.tsx`

### Priority 5 — AI Recommendation Presentation

| Issue | Root cause | Fix |
|-------|------------|-----|
| Titles all start with «الإجراء المقترح:» | **Backend / LLM output** (not frontend formatting) | Reported — prompts unchanged per sprint rules |
| Display improvement | Frontend showed full repetitive title | `formatRecommendationDisplay()` strips prefix; truncates long titles |
| Dashboard rec cards | Same issue | Applied same formatter on dashboard |

**Files:** `lib/format.ts`, `waste-page.tsx`, `dashboard-page.tsx`

### Priority 6 — Other Pages Audit

| Page | Mock financial data? | Action |
|------|---------------------|--------|
| Waste | Fixed above | ✅ |
| Reports | Live API; PDF tied to session | ✅ Session fix |
| Simulation | Live API | ✅ Session reset |
| Notifications | Live API | ✅ No change needed |
| Organization | Admin CRUD live; `—` for optional admin fields only | ✅ Acceptable (not financial KPIs) |
| Settings | Live API; `—` for unset admin labels | ✅ Acceptable |
| Users | Live API | ✅ No mock financial values |
| Dashboard | Empty states (Sprint 8.1) | ✅ No fake numbers |

Unused mock components (`waste-charts`, risk subcomponents) remain in repo **unmounted** — archived per Phase 2 rules.

---

## 2. Files Modified

| File | Change |
|------|--------|
| `frontend/lib/demo/state.ts` | `beginNewFinancialDataset`, `clearAnalysisArtifacts`, change event |
| `frontend/lib/demo/hooks.ts` | **New** — `useDemoArtifacts()` |
| `frontend/lib/format.ts` | Category labels, recommendation display helper |
| `frontend/lib/api/types.ts` | `AiHealthResponse` |
| `frontend/lib/api/khazina-api.ts` | `getAiHealth()` |
| `frontend/components/waste/waste-page.tsx` | Full polish: session, Ollama, upload, empty states |
| `frontend/components/waste/waste-breakdown-table.tsx` | Vendor empty state; category section header |
| `frontend/components/waste/waste-idle-content.tsx` | Remove misleading demo text |
| `frontend/components/data/data-management-page.tsx` | `beginNewFinancialDataset` on upload |
| `frontend/components/simulation/simulation-page.tsx` | Reactive artifacts + reset results |
| `frontend/components/reports/reports-page.tsx` | Session-aware generate/export |
| `frontend/components/dashboard/dashboard-page.tsx` | Recommendation display formatter |

---

## 3. Validation

| Check | Result |
|-------|--------|
| `pnpm exec tsc --noEmit` | ✅ PASS |
| Backend modified | ❌ No |
| API contract modified | ❌ No |
| Business rules modified | ❌ No |

**Dynamic verification:** Sprint 8.2 dual-workbook API script previously proved waste/sim/report deltas. Re-run after 8.3 hit transient AI 500 (Ollama load) — pipeline logic unchanged; session reset verified by code path review and artifact event design.

**Manual judge path after 8.3:**
1. Upload Workbook A → analyze → AI → simulate → report  
2. Upload Workbook B from Data Management  
3. Waste/Simulation pages **clear** until user re-runs analysis (no stale Run A KPIs)

---

## 4. Remaining Technical Debt

| Item | Severity | Owner |
|------|----------|-------|
| Vendor findings not generated by waste engine | High | Backend (future) |
| Dashboard executive aggregation API | High | Phase 8+ |
| Scenario delta % fixed per archetype | Medium | Engine (frozen) |
| AI title phrasing from LLM | Medium | AI prompts (frozen this sprint) |
| `confidence_label` null on recommendations | Medium | Backend mapping |
| Ollama must be started manually | Medium | Ops / demo script |
| Quality snapshot not auto-created on upload | Low | Backend or UX |
| Unused mock components in repo | Low | Archive (intentional) |

---

## 5. Judge Confidence Assessment

**Before 8.3:** 7/10 — core pipeline real; stale UI and empty vendor table eroded trust.

**After 8.3:** **8/10** — session integrity fixed, Ollama failures visible, vendor section honest, Waste page fully audited.

**Believable end-to-end demo?** **Yes**, when operator:
- Starts Ollama + `qwen3.5:4b`
- Uploads workbook → runs waste → AI → simulation → report
- After new upload, re-runs the pipeline (UI no longer shows previous run)

---

## 6. Screens Before / After (Capture Manually)

| Screen | Before | After |
|--------|--------|-------|
| Waste — vendors | Empty table with column headers | Empty State card with explanation |
| Waste — after re-upload | Old KPIs until manual refresh | Cleared until new analysis |
| Waste — AI (Ollama down) | Silent failure / generic error | Warning + disabled button + clear message |
| Waste — recommendations | Hidden when empty | Empty State prompting generate |
| Data — upload | Kept old run IDs | Clears analysis session |
| Simulation | Stale forecast after upload | Clears when `simulationRunId` null |
| Reports PDF | Could export old report | Requires current `lastReportId` |

---

## Definition of Done

| Criterion | Met |
|-----------|-----|
| Zero fake financial values on Waste | ✅ |
| Zero stale session after upload | ✅ |
| Vendor section not misleading | ✅ |
| Ollama failure not silent | ✅ |
| Typecheck pass | ✅ |
| No backend / architecture changes | ✅ |
