# Final Root Cause Analysis

**Date:** 2026-07-16  
**Phase:** 1 — Investigation ONLY (no code changes)  
**Role:** Principal Architect / Staff Engineering / QA Lead / Product Owner  
**Baseline:** Sprint 1 + Sprint 2 complete; 52+ bugs tracked in `BUG_TRACKER.md`

---

## Executive Summary

The platform **can complete the hackathon workflow on a rehearsed path** when:
- Alembic is at head (`f9c2d7a31b44`)
- Cloud AI is configured and healthy
- Presenter uses a **single tab** and understands Risk is **off the workflow indicator**

It **does not yet behave as one integrated enterprise product** because failures cluster in four systemic root causes:

| # | Systemic root cause | Impact |
|---|---------------------|--------|
| **RC-1** | **Pointer state (localStorage) vs DB truth** — UI uses artifact IDs without validating against latest upload or hydrating from DB | Stale data after re-upload, partial refresh gaps |
| **RC-2** | **AI prompt → parser → UI chain preserves internal metric keys** | Executive recommendations leak `waste.top_category`, `facts_contract` semantics |
| **RC-3** | **Workflow indicator omits Risk entirely** | Users skip Risk or run Simulation before Risk; export resolution prioritizes risk run |
| **RC-4** | **PDF renderer exports technical Facts Contract + provenance verbatim** | Executive PDF contains engine IDs, metric keys, UUIDs |

Sprint 1 and Sprint 2 **fixed specific symptoms** (departments 422, waste AI refresh, report titles, basic Arabic font, export selection) but **did not resolve RC-1 through RC-4**.

---

## Known Issues — Re-Investigation Results

| # | User-reported issue | Status | Root cause (evidence) |
|---|---------------------|--------|------------------------|
| 1 | Risk Management Internal Server Error | **CONFIRMED (conditional)** | Missing migrations → 500 on `GET /risks`; OR unhandled `EngineError` on execute; OR missing `risk_analysis_results` tables. **Not reproduced in 20/20 risk unit tests today.** Alembic head verified: `f9c2d7a31b44`. |
| 2 | Mixed Arabic/English in waste recommendations | **CONFIRMED** | Prompt includes English metric keys (`builder.py:17`); parser stores full body including `الحقائق المرجعية:` block; `formatRecommendationDisplay` only strips action prefix |
| 3 | AI leaks internal variable names | **CONFIRMED** | End-to-end: assemblers → prompts → LLM echo → parser → DB → UI cards + PDF `key_metrics` |
| 4 | Reports use wrong report IDs | **PARTIALLY FIXED** | Sprint 2 `resolveExportReportId()` helps; **remaining:** duplicate reports (KHZ-026), risk-first priority when unselected (G-02), `lastReportId` fallback bypasses validation (G-03) |
| 5 | PDF exports wrong reports | **PARTIALLY FIXED** | Same as #4; card selection fixes happy path; heuristic fallback still ambiguous |
| 6 | Arabic PDF rendering poor | **PARTIALLY FIXED** | Noto + bidi added; **remaining:** 120-char truncation, ISO dates, English profile codes, untranslated enums |
| 7 | PDF hides important business data | **CONFIRMED** | Cover section payload built then **skipped** when synthetic cover enabled; org/period/file not rendered |
| 8 | PDF shows technical garbage | **CONFIRMED** | `key_metrics.facts` dumps Facts Contract; provenance appendix exposes engine/model/UUIDs |
| 9 | Re-upload causes stale state | **PARTIALLY FIXED** | Upload clears artifact IDs (Sprint 1); **Risk page UI not reset** (KHZ-011); waste re-run doesn't clear risk/sim IDs |
| 10 | Refresh sometimes loses data | **PARTIALLY FIXED** | Waste recs fixed (Sprint 1); risk AI insights depend on metadata; simulation errors swallowed (KHZ-020) |
| 11 | Multi-tab consistency | **PARTIAL** | localStorage shared (Sprint 1); **no cross-tab React sync** — Tab B stale until F5 |
| 12 | Report buttons select wrong report | **PARTIALLY FIXED** | Per-card export added; unselected export uses risk-first run match |
| 13 | Risk before Simulation in workflow | **CONFIRMED WRONG** | `pipeline.ts` has **no risk stage**; `getContinueTarget()` goes waste AI → simulation, skipping risk |

---

## Critical Bug Classification (LAW workflow violations)

| Violation | Severity | Root cause ID |
|-----------|----------|---------------|
| Re-upload → Risk page shows previous run | **Critical** | RC-1 + KHZ-011 |
| Workflow skips Risk in guided path | **Critical** | RC-3 + KHZ-017 |
| AI recommendations show `waste.*` keys | **Critical** | RC-2 |
| PDF contains Facts Contract metrics | **Critical** | RC-4 |
| Risk 500 on unmigrated DB | **Critical (ops)** | Migration not applied |
| Export without selection may pick wrong domain report | **High** | RC-1 + G-02 |

---

## Layer-by-Layer Findings

### Frontend
- **Storage:** `localStorage` (`khazina_demo_artifacts`) — Sprint 1 migration from sessionStorage
- **React state:** Ephemeral; re-fetched from DB when artifact run IDs present
- **Gaps:** Risk no reset on null `riskRunId`; simulation silent errors; pipeline omits risk; `riskAiReady` written never read

### Backend
- **Report builder:** Correct profile selection by `AnalysisType`; titles fixed when frontend passes them
- **PDF:** Arabic infrastructure present; content assembly still executive-hostile
- **Risk:** IDOR on `GET /risks/{id}` (200 cross-org); EngineError → 500

### AI
- **Routing:** Cloud-only when `AI_PROVIDER=cloud`; `get_ollama_client()` raises if not ollama
- **Quality:** Prompts explicitly request reference-facts blocks that models echo into UI

### Database
- **Integrity:** FK constraints present in migrations; orphan risk possible if Gold persist fails after run marked completed
- **Duplicates:** No uniqueness on `(organization_id, analysis_run_id)` for reports

---

## What Sprint 1 + 2 Actually Fixed (verified in code)

| Sprint | Fix | Still holds? |
|--------|-----|--------------|
| S1 | `MAX_LIST_LIMIT=100` departments | ✅ |
| S1 | Waste recommendations reload from DB | ✅ |
| S1 | localStorage artifacts | ✅ |
| S1 | Upload artifact reset | ✅ |
| S2 | Domain report titles | ✅ |
| S2 | Export selection + card PDF | ✅ |
| S2 | Arabic font in PDF | ✅ (basic) |
| S2 | Simulation report button | ✅ |

---

## What Remains Broken (production blockers for enterprise demo)

1. **Executive AI output quality** — internal keys in UI
2. **Workflow completeness** — Risk not in pipeline; wrong continue order
3. **Cross-domain stale state** — Risk UI after re-upload
4. **Executive PDF** — technical metadata, missing cover business fields
5. **Report idempotency** — duplicate reports confuse export
6. **Risk 500** — ops + EngineError handling (environment-dependent)

---

## Recommended Fix Strategy (Phase 2 — not implemented here)

Fix at **root**, not symptom:

| Priority | Fix | Addresses |
|----------|-----|-----------|
| P0 | Sanitize AI output at parser + forbid reference-facts echo in prompts | RC-2 |
| P0 | Add Risk + Risk AI stages to `pipeline.ts`; fix `getContinueTarget()` order | RC-3 |
| P0 | Risk page `resetResults()` when `riskRunId` null | RC-1, KHZ-011 |
| P0 | PDF: executive-safe renderer (hide facts/provenance tech fields; render cover business data) | RC-4 |
| P1 | Export: newest report per `analysis_run_id`; clear cross-domain IDs on partial re-run | RC-1 |
| P1 | DB hydration fallback when localStorage empty | RC-1 |
| P2 | Risk EngineError → structured 409; IDOR fix | Security/stability |

**Rule:** If fixing one bug breaks another — stop and redesign the layer (RC-1 pointer model), do not stack patches.

---

## Evidence Sources

- Code audit: frontend `lib/demo/`, `lib/workflow/pipeline.ts`, all page components
- Code audit: backend `ai/prompts/`, `ai_recommendations/`, `reports/`
- Tests: `298 passed, 5 failed` (2026-07-16); alembic `f9c2d7a31b44 (head)`
- Prior docs: `BUG_TRACKER.md`, `SPRINT_1_STABILIZATION_REPORT.md`, `SPRINT_2_REPORT_STABILIZATION_REPORT.md`

**No code was modified in Phase 1.**
