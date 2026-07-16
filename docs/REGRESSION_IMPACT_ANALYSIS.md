# Regression Impact Analysis

**Date:** 2026-07-16  
**Phase:** 1 — Investigation ONLY  
**Baseline:** Sprint 1 + Sprint 2 merged; BUG_TRACKER 52+ items

---

## Test Suite Status (Verified 2026-07-16)

```
301 passed, 2 failed, 2 warnings
Duration: ~33s
```

### Current Failures

| Test | File | Likely cause | Sprint introduced? |
|------|------|--------------|-------------------|
| `test_generate_risk_ai_success` | `test_risk_ai_service.py` | Risk AI pipeline mock/contract drift | Investigate — may pre-date Sprint 2 |
| `test_risk_pipeline_executes_tasks_in_order` | `test_risk_ai_service.py` | Task ordering assertion | Same |

**Note:** Prior session reported 5 failures (3 route registration + 2 risk AI). Route registration failures **no longer reproduce** — 301 passed suggests improvement or environment difference.

---

## Sprint 1 Change Impact

| File | Change | Regression risk | Verified |
|------|--------|-----------------|----------|
| `org-lookups.tsx` | limit 100 | Low — fixes 422 | ✅ Departments load |
| `demo/state.ts` | sessionStorage → localStorage | **Medium** — cross-session persistence | ✅ Intended |
| `data-management-page.tsx` | artifact reset on upload | Medium — may clear mid-demo | ✅ Required by LAW |
| `waste-page.tsx` | DB reload + abort | Low | ✅ KHZ-012 fixed |

### Sprint 1 — Bugs Fixed (no regression observed)

| Bug | Fix validated |
|-----|---------------|
| KHZ-047 | Pagination 422 gone |
| KHZ-012 | Waste AI survives F5 |
| KHZ-054 | Upload resets artifacts |
| KHZ-013 | Partial — localStorage aligned with auth |

### Sprint 1 — Open / Partial

| Bug | Status |
|-----|--------|
| KHZ-011 | **Still open** — risk stale UI |
| KHZ-013 | Partial — multi-tab desync remains |
| KHZ-053 | Partial — abort on waste; not all pages |

---

## Sprint 2 Change Impact

| File | Change | Regression risk | Verified |
|------|--------|-----------------|----------|
| `report-export.ts` | resolveExportReportId | Medium — changes export target | ✅ Fixes KHZ-022 |
| `khazina-api.ts` | require explicit title | Low | ✅ Fixes KHZ-023 |
| `reports-page.tsx` | domain titles + selection | Low | ✅ |
| `pdf_renderer.py` | Arabic font + bidi | Medium — layout changes | ✅ test_pdf_export passes |
| `simulation-page.tsx` | simulationAnalysisRunId | Low | ✅ |
| `risk-page.tsx` | clear lastReportId on re-run | Low | ✅ |

### Sprint 2 — Bugs Fixed

| Bug | Status |
|-----|--------|
| KHZ-022 | Fixed |
| KHZ-023 | Fixed |
| KHZ-044 | Fixed (formatDate) |

### Sprint 2 — Not addressed (still open)

| Bug | Notes |
|-----|-------|
| KHZ-026 | Duplicate reports |
| KHZ-017 | Risk not in pipeline |
| AI leakage | New critical — not in original tracker |
| PDF executive quality | Partial |

---

## Cross-Sprint Interaction Risks

### R-01: Export resolution vs duplicate reports

Sprint 2 improved selection logic but **KHZ-026 duplicates** can still cause wrong PDF if heuristic matches older row.

**Risk level:** High for demo  
**Mitigation:** Sprint 3 — newest report wins + idempotent generate

### R-02: localStorage + multi-tab

Sprint 1 made persistence stronger (localStorage) but **without `storage` event listeners** Tab B shows stale React state until navigation/F5.

**Risk level:** Medium  
**Mitigation:** Sprint 4 — storage sync or backend workflow state

### R-03: AI sanitization vs existing DB rows

If Phase 2 sanitizes at parse time, **old recommendation rows** still contain leaked text until re-generated.

**Risk level:** Medium for demo  
**Mitigation:** Re-run waste AI after deploy; or display-time sanitization

### R-04: Pipeline reorder vs getContinueTarget

Adding risk stages requires updating **both** `PIPELINE_STAGES` and `getContinueTarget()` and `ROUTE_PIPELINE_STAGE` — partial update causes regression.

**Risk level:** High if incomplete  
**Mitigation:** Single PR for all pipeline touchpoints

### R-05: PDF cover merge vs synthetic cover

Rendering cover section fields AND synthetic title may duplicate titles if not designed carefully.

**Risk level:** Low  
**Mitigation:** Design: synthetic = branding; section = business metadata

---

## BUG_TRACKER Regression Matrix

| ID | Description | Pre-sprint | Post-sprint | Regressed? |
|----|-------------|------------|-------------|------------|
| KHZ-004 | Schema drift | Open | Fixed on dev | No |
| KHZ-011 | Risk stale UI | Open | Open | No |
| KHZ-012 | Waste AI F5 | Open | Fixed | No |
| KHZ-017 | Risk not in pipeline | Open | Open | No |
| KHZ-022 | Wrong PDF export | Open | Fixed | No |
| KHZ-023 | Wrong report title | Open | Fixed | No |
| KHZ-047 | Departments 422 | Open | Fixed | No |
| KHZ-054 | Stale artifacts upload | Open | Fixed | No |

**No confirmed regressions from Sprint 1/2 fixes in automated tests**, except 2 risk AI service tests failing (need root cause — may be pre-existing).

---

## Features That Must Not Break (Demo Path)

| Step | Regression test |
|------|-----------------|
| Login | Manual + auth tests |
| Upload | File API tests |
| Waste analyze | waste test suite |
| Waste AI | ai_recommendations tests |
| Risk analyze | risk tests (20+ pass) |
| Risk AI | **2 failing** ⚠️ |
| Simulation | simulation tests |
| Report generate | report builder tests |
| PDF export | test_pdf_export.py |
| F5 persistence | Manual E2E only |
| Re-upload reset | Manual E2E only |

---

## Phase 2 Regression Strategy

After **each sprint:**
1. `pytest tests/ -q` — must be 0 failures
2. `npx tsc --noEmit` — frontend
3. **Full LAW workflow manual** (user FINAL RULE)
4. PDF text grep for forbidden strings
5. Update BUG_TRACKER with CLOSED only after manual pass

**If sprint fixes one bug but fails LAW workflow → sprint REJECTED.**

---

## Rollback Inventory

| Sprint | Files | Rollback complexity |
|--------|-------|---------------------|
| S1 | 4 frontend files | Low — isolated |
| S2 | 8 files FE+BE | Medium — PDF deps |

Phase 2 sprints should be independently revertable per vertical (AI / workflow / PDF / reports).

**Phase 1 complete. No code modified.**
