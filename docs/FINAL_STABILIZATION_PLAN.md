# Final Stabilization Plan

**Date:** 2026-07-16  
**Phase:** 1 complete → Phase 2 implementation roadmap  
**Prerequisite:** All 7 investigation documents approved  
**Rule:** No sprint accepted until full LAW workflow passes manually

---

## Phase 1 Deliverables — Status

| Document | Status |
|----------|--------|
| FINAL_ROOT_CAUSE_ANALYSIS.md | ✅ Complete |
| ENTERPRISE_WORKFLOW_TRACE.md | ✅ Complete |
| API_CONTRACT_VALIDATION.md | ✅ Complete |
| AI_QUALITY_REVIEW.md | ✅ Complete |
| PDF_EXECUTIVE_REVIEW.md | ✅ Complete |
| DATABASE_INTEGRITY_REVIEW.md | ✅ Complete |
| REGRESSION_IMPACT_ANALYSIS.md | ✅ Complete |
| FINAL_STABILIZATION_PLAN.md | ✅ This document |

**No code was written in Phase 1.**

---

## Implementation Sprints Overview

| Sprint | Objective | Est. time | Dependencies |
|--------|-----------|-----------|--------------|
| **S0** | Fix failing tests + ops verification | 2h | None |
| **S3** | Workflow: Risk in pipeline + stale UI reset | 4h | S0 |
| **S4** | AI executive quality (prompt + parse + display) | 6h | S0 |
| **S5** | PDF executive safe mode | 6h | S4 |
| **S6** | Reports idempotency + export correctness | 4h | S3 |
| **S7** | Persistence hardening (multi-tab, hydration) | 4h | S3, S6 |
| **S8** | Risk stability + security (500, IDOR) | 4h | S0 |

**Total estimate:** ~30 hours  
**Recommended demo minimum:** S0 + S3 + S4 + S5 + S6

---

## Sprint 0 — Test Baseline + Ops Gate

### Objective
Restore 100% pytest pass; confirm demo environment migrations and Cloud AI.

### Root cause
- 2 failing risk AI service tests
- Risk 500 on unmigrated DB (ops)

### Files
- `backend/tests/ai_recommendations/test_risk_ai_service.py`
- Related risk AI service / pipeline code (TBD after test inspection)

### Implementation
1. Run failing tests with `--tb=short`; fix mock/contract drift
2. Document demo checklist: `alembic upgrade head`, `AI_PROVIDER=cloud`
3. Capture one Cloud AI log line (provider, model, latency)

### Regression tests
```bash
python -m pytest tests/ -q
```

### Acceptance criteria
- 0 pytest failures
- Risk AI tests green
- Manual: `GET /risks` → 200 on demo DB

### Rollback risk
**Low** — test-only or minimal service fix

### Estimated time
2 hours

---

## Sprint 3 — Workflow Order + Risk Stale UI

### Objective
LAW order enforced: Waste → Waste AI → **Risk → Risk AI** → Simulation → Reports

### Root cause
- RC-3: `pipeline.ts` omits risk stages (KHZ-017)
- RC-1: Risk page no reset when `riskRunId` null (KHZ-011)

### Files
- `frontend/lib/workflow/pipeline.ts` — add `risk`, `riskAi` stages; update `getContinueTarget()`, `isStageCompleted()`, `ROUTE_PIPELINE_STAGE`
- `frontend/lib/demo/state.ts` — ensure `riskAiReady` used for gating
- `frontend/components/risk/risk-page.tsx` — reset results when artifact null; clear downstream IDs on risk re-run
- `frontend/components/waste/waste-page.tsx` — on waste re-run, clear risk/sim/report artifacts
- Nav/workflow UI components consuming pipeline

### Implementation
1. Insert stages after `ai`: `risk` (requires `riskRunId`), `riskAi` (requires `riskAiReady`)
2. `getContinueTarget()`: after AI → risk; after risk → risk AI; after risk AI → simulation
3. Risk page: `useEffect` when `!artifacts.riskRunId` → clear findings/summary state
4. Cross-domain: new waste run clears `riskRunId`, `simulationRunId`, `lastReportId`

### Regression tests
- Frontend: unit tests for `getContinueTarget` / `isStageCompleted` if present; else add
- Manual LAW steps 1–7 through risk AI

### Acceptance criteria
- Workflow indicator shows Risk before Simulation
- Continue button navigates to Risk after Waste AI
- Re-upload → Risk page empty (no previous run)
- No regression on waste F5 reload

### Rollback risk
**Medium** — pipeline touches global navigation; revert single file if broken

### Dependencies
S0

### Estimated time
4 hours

---

## Sprint 4 — AI Executive Quality

### Objective
Zero internal keys in UI; board-ready Arabic recommendations

### Root cause
- RC-AI-1: English metric keys in prompts (`builder.py`)
- RC-AI-2: Parser stores full LLM body
- RC-AI-3: Minimal frontend sanitization

### Files
- `backend/app/ai/prompts/builder.py` — localized metric labels
- `backend/app/ai/prompts/languages/ar.py` — system prompt: forbid key echo
- `backend/app/ai/context/` assemblers — optional label map
- `backend/app/ai_recommendations/recommendation_parser.py` — strip reference block; redact dot-keys
- `frontend/lib/format.ts` — defense-in-depth display sanitization
- `backend/tests/ai_recommendations/` — leakage assertion tests

### Implementation
1. Metric label map: `waste.top_category` → «أعلى فئة هدر»
2. Remove or restructure `الحقائق المرجعية` from user prompt
3. Parser: `_strip_reference_facts()` before persist
4. Display: regex redact `\w+\.\w+` patterns
5. Re-generate recommendations in manual test (old DB rows may still leak until re-run)

### Regression tests
```bash
python -m pytest tests/ai_recommendations/ tests/ai/ -q
```
- New test: parsed description must not match `[a-z]+\.[a-z_]+`

### Acceptance criteria
- Waste AI cards: no English dot-keys visible
- Risk AI summary: executive Arabic tone
- PDF recommendations section clean (pairs with S5)

### Rollback risk
**Low-Medium** — prompt changes affect output style; revert builder if model breaks

### Dependencies
S0

### Estimated time
6 hours

---

## Sprint 5 — PDF Executive Safe Mode

### Objective
Executive PDF structure with no technical metadata; cover shows business data

### Root cause
- RC-4: Facts contract + provenance in PDF
- PDF-01: Cover section skipped

### Files
- `backend/app/reports/pdf_renderer.py` — merge cover fields; executive filter
- `backend/app/reports/sections.py` — optional executive payload builder
- `backend/tests/advanced_features/test_pdf_export.py` — forbidden string assertions

### Implementation
1. Synthetic cover + render org/period/file from `cover` section payload
2. `key_metrics`: headline only; Arabic labels; drop `facts` array from PDF path
3. Default demo: `include_provenance_appendix=False` OR sanitize to one line
4. Fix risk section ordering in profile assembly
5. Localize profile code on cover
6. Increase Arabic wrap limits

### Regression tests
```bash
python -m pytest tests/advanced_features/test_pdf_export.py -q
```
- Assert `waste.top_category` not in PDF bytes
- Assert org name in PDF when in payload

### Acceptance criteria
- PDF sections match required executive structure
- No technical garbage in text search
- Arabic readable on sample data
- Full LAW workflow export passes

### Rollback risk
**Medium** — PDF layout changes visible to judges

### Dependencies
S4 (recommendation text clean)

### Estimated time
6 hours

---

## Sprint 6 — Reports Idempotency + Export

### Objective
Correct report ID always; no duplicate confusion

### Root cause
- KHZ-026: duplicate reports
- G-02: export prioritizes risk over waste

### Files
- `backend/app/reports/service.py` — upsert or return existing report
- `frontend/lib/reports/report-export.ts` — workflow-order fallback; newest `created_at`
- `frontend/components/reports/reports-page.tsx` — select newest per domain
- Migration optional: unique index on reports

### Implementation
1. Generate: if report exists for `(org, analysis_run_id, profile)` → return existing
2. Export fallback order: selected → lastReportId → waste → risk → simulation
3. When multiple matches: newest by timestamp
4. UI: show domain badge on each report card

### Regression tests
- Report service unit tests for idempotency
- Manual: generate twice → one row or same ID returned

### Acceptance criteria
- Report buttons export matching domain PDF
- Unselected export uses last generated report
- KHZ-022 stays fixed

### Rollback risk
**Low**

### Dependencies
S3 (correct run IDs)

### Estimated time
4 hours

---

## Sprint 7 — Persistence Hardening

### Objective
F5, new tab, browser restart, re-upload all consistent

### Root cause
- RC-1: Pointer cache without DB hydration
- Multi-tab React desync

### Files
- `frontend/lib/demo/state.ts` — optional `storage` event listener
- `frontend/hooks/useDemoArtifacts.ts` — hydrate from API when IDs missing
- New backend endpoint optional: `GET /workflow/latest?file_id=`
- `frontend/components/simulation/simulation-page.tsx` — surface errors (KHZ-020)

### Implementation
1. On mount: if `fileId` but no run IDs, fetch latest runs from backend
2. `window.addEventListener('storage', ...)` to sync artifacts across tabs
3. Simulation: show error toast instead of silent empty
4. Logout: optionally clear artifacts

### Regression tests
- Manual: Tab A upload → Tab B refresh shows same state
- Manual: F5 on each page in LAW workflow

### Acceptance criteria
- All LAW persistence scenarios pass
- KHZ-013 closed or documented accepted risk

### Rollback risk
**Medium**

### Dependencies
S3, S6

### Estimated time
4 hours

---

## Sprint 8 — Risk Stability + Security

### Objective
No Risk 500 in demo; EngineError handled gracefully

### Root cause
- Unhandled `EngineError` → 500
- KHZ-008 IDOR on risk detail

### Files
- `backend/app/risk/` service + API routes
- `backend/app/api/routes/risks.py` — org ownership check

### Implementation
1. Catch `EngineError` → 409 with structured message
2. `GET /risks/{id}` → 404 if org mismatch
3. Pre-demo migration verification script

### Regression tests
```bash
python -m pytest tests/risk/ -q
```

### Acceptance criteria
- Risk analyze never 500 on valid input
- Cross-org risk GET returns 404
- Demo script includes migration step

### Rollback risk
**Low**

### Dependencies
S0

### Estimated time
4 hours

---

## Post-Sprint Verification Protocol (MANDATORY)

After **every** sprint, execute in order:

1. Login
2. Upload financial file
3. Waste analysis
4. Waste AI recommendations
5. Risk analysis
6. Risk AI summary
7. Scenario simulation
8. Executive reports (all three domains)
9. PDF export (each selected card)
10. F5 — verify all pages
11. New tab — verify
12. Close browser — reopen — verify
13. Upload **second** dataset
14. Verify old data gone from UI
15. Repeat steps 3–9 on new data only
16. Backend logs: Cloud AI only, no Ollama
17. DB integrity queries (see DATABASE_INTEGRITY_REVIEW.md)

**Sprint REJECTED if any step fails.**

---

## Priority for Hackathon Demo

If time-constrained, minimum viable stabilization:

| Priority | Sprint | Why |
|----------|--------|-----|
| P0 | S0 | Green tests + migrations |
| P0 | S3 | Correct workflow order |
| P0 | S4 | AI doesn't embarrass on stage |
| P0 | S5 | PDF handout quality |
| P1 | S6 | Export correctness |
| P2 | S7, S8 | Polish + security |

---

## Stop Conditions

Per user FINAL RULE:

- If fixing one bug breaks another feature → **STOP**, redesign layer
- Do not close bugs on unit tests alone
- Do not stack temporary fixes

---

## Next Step

**Await user approval of Phase 1 documents**, then begin **Sprint 0** (no feature work until tests green).

**Phase 1 investigation complete.**
