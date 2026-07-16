# Final Stabilization Audit

**Date:** 2026-07-16  
**Commit baseline:** `1db4c16f27ab390164121b87be508bec3aff5e97`  
**Role:** Principal Architect / Backend / Frontend / QA / Integration / Security  
**Scope:** Complete platform — hackathon stabilization (investigation only, no fixes applied in this document)  
**Method:** Read all Phase 8–9 QA reports, Product Polish reports, `BUG_TRACKER.md`, `FULL_PLATFORM_QA_AUDIT.md`; full codebase static audit; sub-agent deep dives on pagination, reports/PDF, workflow persistence; backend regression run

**Companion documents:**
- [API_CONTRACT_AUDIT.md](API_CONTRACT_AUDIT.md) — pagination and FE↔BE contract matrix
- [BUG_TRACKER.md](BUG_TRACKER.md) — 48 issues (46 open at audit start)
- [FULL_PLATFORM_QA_AUDIT.md](FULL_PLATFORM_QA_AUDIT.md) — prior exhaustive QA

---

## 1. Executive Summary

The platform **can complete the master workflow on a rehearsed, single-tab path** after DB migrations and the risk snapshot fix. It **does not** behave like a finished enterprise product without manual presenter intervention.

| Dimension | Assessment |
|-----------|------------|
| Happy path (scripted demo) | **Conditional GO** |
| Refresh / reload / re-upload | **FAIL** — multiple persistence gaps |
| Reports + PDF | **FAIL** — wrong source, broken Arabic, missing data |
| API contracts | **FAIL** — departments 422 on every load |
| Security | **FAIL** — IDOR, credential exposure (acceptable single-tenant demo only) |
| Automated regression | **299/303 pass** — 4 failures (see KHZ-059) |

**New critical finding (post-commit `1db4c16`):** `GET /departments?limit=200` returns **422** on app load, breaking org-wide department lookups. See [API_CONTRACT_AUDIT.md](API_CONTRACT_AUDIT.md) AC-001.

---

## 2. Master Workflow Verification

```
Login → Upload → Snapshot → Waste → Waste AI → Risk → Risk AI → Simulation → Executive Report → PDF
```

| Stage | DB | Backend | API | Frontend | Nav | Persist | Refresh | Revisit | Session | Consistency | Verdict |
|-------|----|---------| ----|-----------|-----|---------|---------|---------|---------|-------------|---------|
| **Login** | ✅ | ✅ | ✅ | ⚠️ auto-login | ✅ | ✅ localStorage | ✅ | ✅ | ⚠️ | ✅ | **Conditional** |
| **Upload** | ✅ | ✅ | ✅ | ⚠️ | ✅ | ⚠️ sessionStorage | ⚠️ | ⚠️ | ⚠️ | ⚠️ | **Partial** |
| **Snapshot** | ✅ | ✅ | ✅ | ⚠️ null snapshot path | ✅ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | ⚠️ | **Partial** |
| **Waste Analysis** | ✅ | ✅ | ✅ | ⚠️ race | ✅ | ✅ DB + artifacts | ⚠️ | ✅ | ⚠️ | ⚠️ | **Partial** |
| **Waste AI** | ✅ | ✅ | ✅ | ❌ no reload | ✅ | ✅ DB | **❌** | ⚠️ | ⚠️ | ⚠️ | **FAIL refresh** |
| **Risk Analysis** | ✅ | ✅ | ✅ | ⚠️ stale UI | ✅ | ✅ DB | ⚠️ | ⚠️ | ⚠️ | ⚠️ | **Partial** |
| **Risk AI** | ✅ | ✅ | ✅ | ⚠️ insights reload | ✅ | ✅ DB | ⚠️ | ✅ | ⚠️ | ✅ | **Partial** |
| **Simulation** | ✅ | ✅ | ✅ | ⚠️ silent errors | ✅ | ⚠️ baseline | ⚠️ | ⚠️ | ⚠️ | ⚠️ | **Partial** |
| **Executive Report** | ✅ | ✅ | ✅ | ❌ wrong title/source | ✅ | ✅ DB | ⚠️ | ✅ | ⚠️ | ❌ | **FAIL** |
| **PDF** | ✅ | ✅ | ✅ | ❌ quality | ✅ | ✅ DB | ⚠️ | ⚠️ | ⚠️ | ❌ | **FAIL** |

**Verdict:** End-to-end journey works **only** with: single tab, no F5 refresh after AI, no re-upload mid-demo, scripted navigation, migrations applied, cloud AI healthy.

---

## 3. Regression Baseline (2026-07-16)

```
pytest: 299 passed, 4 failed, 3 warnings (29.8s)
```

| Failed test | Likely cause |
|-------------|--------------|
| `test_generate_risk_ai_success` | Parallel execution / service trace changes |
| `test_risk_ai_generate_route_registered` | TestClient route registration (pre-existing) |
| `test_risk_analysis_routes_registered` | TestClient route registration (pre-existing) |
| `test_risk_register_routes_registered` | TestClient route registration (pre-existing) |

Frontend `tsc` / `lint`: not re-run in this audit cycle (last known: pass per FULL_PLATFORM_QA_AUDIT).

---

## 4. Complete Issue Register

Issues include all open items from `BUG_TRACKER.md` plus new findings from this audit. Severity re-evaluated for **hackathon business impact**.

### Critical (Demo-blocking or data integrity)

| ID | Module | Issue | Root cause | Reproduction | Files | Deps | Fix complexity | Regression risk |
|----|--------|-------|------------|--------------|-------|------|----------------|-----------------|
| **KHZ-047** | API / Org | **`GET /departments?limit=200` → 422** on every app load | FE `limit:200` vs BE `le=100` | Login → any page → Network tab shows 422 on departments | `org-lookups.tsx:47`, `deps.py:77` | OrgLookupsProvider wraps shell | **Trivial** (1 line) | Low |
| KHZ-001 | Data | Upload memory DoS | Full read before size check | POST file >> 10MB | `financial.py` L81 | Upload pipeline | Medium | Low |
| KHZ-002 | Auth | Dev auto-login unconditional | `hydrateSession()` always logs in | Empty localStorage + backend up | `auth-context.tsx:67-84` | All routes | Low | Medium (demo flow) |
| KHZ-003 | Auth | Login form pre-filled credentials | Default useState values | Open `/login` | `login/page.tsx` | Login | Trivial | Low |
| KHZ-012 | Waste | AI recommendations lost on F5 | No `listRecommendations` on mount | Waste AI → F5 → empty list | `waste-page.tsx:170-181,238-257` | Workflow flags | Low | Low |
| KHZ-013 | Workflow | sessionStorage vs localStorage split | Artifacts tab-scoped | Complete pipeline → close tab → reopen | `demo/state.ts`, `auth/session.ts` | All workflow pages | Medium | Medium |

### High (Visible workflow break or wrong output)

| ID | Module | Issue | Root cause | Reproduction | Files | Fix complexity | Regression risk |
|----|--------|-------|------------|--------------|-------|----------------|-----------------|
| KHZ-011 | Risk | Stale run results after re-upload | No reset when `riskRunId` null | Risk run → new upload → Risk page | `risk-page.tsx:183-201` | Low | Low |
| KHZ-022 | Reports | PDF uses `lastReportId` not selection | Export bound to session artifact | Generate A then B → export → wrong PDF | `reports-page.tsx:178-192` | Medium | Medium |
| **KHZ-048** | Reports | Stale `lastReportId` after re-run analysis | Run ID changes, report ID not cleared | Re-run waste → export → old report | `waste-page.tsx:225`, `reports-page.tsx` | Low | Low |
| **KHZ-049** | PDF | Arabic rendering broken | Helvetica + no RTL/bidi | Export any Arabic report | `pdf_renderer.py:76-80` | High | Medium |
| **KHZ-050** | PDF | List sections show `[N items]` only | Renderer collapses arrays | Export risk report → no risk names | `pdf_renderer.py:48-51` | Medium | Low |
| KHZ-023 | Reports | Risk report gets waste default title | `generateReport()` default title | Generate risk report → wrong title | `khazina-api.ts:774-789` | Trivial | Low |
| **KHZ-062** | Reports | `pdfEnabled` vs export target mismatch | Panel enabled on any published report | Fresh session + published reports → export fails | `reports-page.tsx:402-407` | Low | Low |
| KHZ-005 | Auth | No server-side route protection | No middleware | Disable JS → access `/users` | Missing `middleware.ts` | Medium | Low |
| KHZ-006 | Auth | 401 doesn't clear session | No global interceptor | Expire JWT → API call | `client.ts` | Low | Low |
| KHZ-008 | Security | IDOR `GET /risks/{id}` | No org check on get | Cross-org UUID | `risk/service.py` | Low | Low |
| KHZ-009 | Security | IDOR on 8 other GET-by-ID routes | Same pattern | Cross-org UUID per route | Multiple services | Medium | Medium |
| KHZ-010 | Risk | Dual lifecycle APIs desync | Legacy vs enterprise fields | Legacy transition → lifecycle unchanged | `risk.py`, register service | Medium | Medium |
| **KHZ-053** | Waste/Sim | In-flight fetch race after re-upload | No abort/stale guard | Slow network + re-upload during load | `waste-page.tsx:170-181`, `simulation-page.tsx:303-310` | Medium | Low |
| **KHZ-054** | Data | Upload without snapshot leaves stale artifacts | `beginNewFinancialDataset` only if snapshot truthy | Upload returns null snapshot | `data-management-page.tsx:164-169` | Low | Low |

### Medium (Degraded experience or inconsistency)

| ID | Module | Issue | Root cause | Files | Fix complexity |
|----|--------|-------|------------|-------|----------------|
| KHZ-007 | Auth | No frontend RBAC | Session lacks role | All admin pages | Medium |
| KHZ-015 | Dashboard | Waste KPI always null | Hardcoded null | `dashboard-page.tsx:151-157` | Low |
| KHZ-016 | Dashboard | Charts permanently empty | No API wired | `dashboard-charts.tsx` | Medium |
| KHZ-017 | Workflow | Risk omitted from pipeline stages | Pipeline definition | `pipeline.ts` | Low |
| KHZ-018 | Org | Org lookups cache not refreshed after upload | `refresh()` not called | `data-management-page.tsx` | Trivial |
| KHZ-019 | Risk | Detail provenance wrong file label | `fileName(snapshot_id)` | `risk-detail-page.tsx:102-104` | Low |
| KHZ-020 | Simulation | Hydration errors swallowed | `.catch(() => undefined)` | `simulation-page.tsx:~309` | Low |
| KHZ-021 | Data | Upload success without snapshot | Async processing gap | `data-management-page.tsx:164-169` | Medium |
| KHZ-024 | Reports | AI-insights gate not in UI | Settings not checked | `reports-page.tsx` | Low |
| KHZ-025 | Data | Phantom file registration | Fake storage_path accepted | `financial.py` service | Medium |
| KHZ-026 | Reports | Duplicate reports on re-generate | No idempotency | `reports/service.py` | Medium |
| KHZ-027 | Security | Inconsistent cross-org errors | 403 vs 404 vs 200 | Multiple services | Medium |
| KHZ-028 | Waste | Results race (no cancel) | Parallel analyses | `waste-page.tsx` | Medium |
| KHZ-029 | Workflow | Artifacts flash empty on mount | SSR/hydration | `demo/hooks.ts:11-18` | Low |
| KHZ-030 | Dashboard | Recommendations not domain-filtered | No filter param | `dashboard-page.tsx:103` | Trivial |
| KHZ-031 | Risk | Lifecycle UI unwired on detail | Read-only page | `risk-detail-page.tsx` | Medium |
| KHZ-032 | Security | Public health endpoints | No auth on `/health` | `main.py` | Low |
| **KHZ-051** | Simulation | Scenario report generation unwired | No UI button; `analysis_run` discarded | `simulation-page.tsx:293`, `reports-page.tsx` | Medium |
| **KHZ-052** | Simulation | Stale baseline after waste re-run | Frozen `baseline_analysis_run_id` | Re-upload → sim without re-run waste | `simulation-page.tsx:280` | Medium |
| **KHZ-055** | Auth | Sign-in doesn't clear demo artifacts | Only signOut clears | Login as new user same tab | `auth-context.tsx:34-47` | Trivial |
| **KHZ-056** | Simulation | Can run without waste baseline | `wasteRunId` optional at execute | Re-upload → sim without waste | `simulation-page.tsx:266-281` | Low |
| **KHZ-058** | Risk | AI insights not reloaded on refresh | Only recommendations from DB | Risk AI → F5 → missing summary | `risk-page.tsx:171-174` | Low |
| **KHZ-061** | API | Client missing pagination on 10 list functions | `ListQueryParams` not exposed | Large orgs | `khazina-api.ts` | Low |
| **KHZ-063** | Reports | Backend default title uses enum string | `format_report_title` | API call without title | `resolver.py:304-305` | Low |
| **KHZ-064** | Reports | N+1 content fetches on reports page | Per-row `getReportContent` | Many reports | `reports-page.tsx` | Medium |

### Low / Cosmetic

KHZ-033 through KHZ-046, plus: **KHZ-057** (`clearAnalysisArtifacts` never called), **KHZ-059** (4 test failures), **KHZ-060** (API docs `page_size` drift).

Full detail for KHZ-001–046: see [BUG_TRACKER.md](BUG_TRACKER.md).

---

## 5. Critical Investigation Results

### 5.1 Data Management

| Check | Result | Issue IDs |
|-------|--------|-----------|
| Upload valid Excel | ✅ Pass | — |
| Replace upload clears downstream artifacts | ⚠️ Only if snapshot returned | KHZ-054, KHZ-021 |
| Multiple uploads | ⚠️ Race + stale session | KHZ-053, KHZ-013 |
| Large files (>10MB) | ❌ Memory DoS risk | KHZ-001 |
| Invalid files | ✅ Backend W-1 validation (D4) | — |
| Refresh preserves latest | ⚠️ DB yes; sessionStorage may desync | KHZ-013 |
| Latest upload = active dataset | ❌ Not guaranteed without snapshot | KHZ-054 |
| Department names after upload | ❌ 422 breaks lookups | KHZ-047, KHZ-018 |

### 5.2 Waste Analysis

| Check | Result | Issue IDs |
|-------|--------|-----------|
| Execute | ✅ | — |
| Refresh KPIs/tables | ✅ | — |
| Generate AI | ✅ (cloud path verified separately) | — |
| Recommendations after F5 | ❌ | KHZ-012 |
| Charts/KPIs | ✅ on page | KHZ-041 dead chart code |
| Re-upload stale data | ⚠️ Race | KHZ-053, KHZ-028 |
| DB persistence | ✅ | — |

### 5.3 Risk Analysis

| Check | Result | Issue IDs |
|-------|--------|-----------|
| Execute | ✅ (post KHZ-014 fix) | — |
| Parallel AI | ✅ when cloud | — |
| Findings review/promote | ✅ code path | KHZ-031 UI gaps |
| Register/dashboard | ✅ post KHZ-004 migration | — |
| Stale after re-upload | ❌ | KHZ-011 |
| AI recommendations reload | ✅ | — |
| AI insights reload | ⚠️ | KHZ-058 |
| History run selection | ❌ | KHZ-042 |

### 5.4 Simulation

| Check | Result | Issue IDs |
|-------|--------|-----------|
| Uses latest waste (when artifacts correct) | ⚠️ | KHZ-052, KHZ-056 |
| Scenario create/execute | ✅ | — |
| Refresh persistence | ⚠️ Silent failures | KHZ-020 |
| Report generation | ❌ Unwired | KHZ-051 |

### 5.5 Reports

| Check | Result | Issue IDs |
|-------|--------|-----------|
| Generate waste report | ✅ | — |
| Generate risk report | ⚠️ Wrong title | KHZ-023 |
| Correct analysis_run source | ⚠️ Uses session artifacts | KHZ-048 |
| Correct recommendations/KPIs in content | ✅ (backend assembly tested) | — |
| Export selected report | ❌ Uses lastReportId | KHZ-022 |

### 5.6 PDF

| Check | Result | Issue IDs |
|-------|--------|-----------|
| Generates bytes | ✅ (>3KB in 8.3 harness) | — |
| Arabic text readable | ❌ | KHZ-049 |
| Full section data | ❌ Lists collapsed | KHZ-050 |
| Correct report bound | ❌ | KHZ-022, KHZ-048 |
| Pagination/layout | ⚠️ Truncation at 110 chars | pdf_renderer |
| Styling/sections | ⚠️ Missing Arabic labels | pdf_renderer |

### 5.7 Database Consistency Chain

```
Latest upload → Snapshot → Waste Run → Risk Run → Simulation → Report → PDF
```

| Link | Consistent when | Breaks when |
|------|-----------------|-------------|
| Upload → Snapshot | Snapshot in upload response | KHZ-021 null snapshot |
| Snapshot → Waste run | Artifacts have matching IDs | KHZ-013 session lost |
| Waste → Risk | Same fileId/snapshotId in artifacts | Re-upload partial clear |
| Waste → Simulation baseline | wasteRunId set at execute | KHZ-056 cleared wasteRunId |
| Run → Report | `analysis_run_id` in generate body | KHZ-048 stale lastReportId |
| Report → PDF | `lastReportId` matches intended run | KHZ-022 wrong binding |

**DB is source of truth; sessionStorage is not validated against DB on page load.**

### 5.8 Session

| Check | Result | Issue IDs |
|-------|--------|-----------|
| Auth survives refresh | ✅ localStorage | — |
| Workflow survives refresh | ❌ Partial — flags yes, data no | KHZ-012, KHZ-058 |
| Multi-tab | ❌ Desync | KHZ-013 |
| DB as truth | ❌ Not enforced on FE | KHZ-013, KHZ-054 |

---

## 6. Ten Stabilization Sprints

**Rule:** Before starting Sprint N, re-run regression for Sprints 1…N−1.

### Sprint 1 — Release Blockers (Highest Business Risk)

**Objective:** App loads without 422; master workflow survives one F5 after waste AI; department labels work.

| Files | Acceptance criteria | Regression checklist | Dependencies | Rollback risk |
|-------|---------------------|----------------------|--------------|---------------|
| `org-lookups.tsx` | `GET /departments` → 200 on load | Login → Network: no 422; dept names on waste table | None | Low |
| `waste-page.tsx` | F5 after waste AI shows recommendations | Waste AI → F5 → list populated | `listRecommendations` API | Low |
| `data-management-page.tsx` | Upload always resets artifacts appropriately | Re-upload clears old run IDs | `demo/state.ts` | Low |
| Ops checklist | `alembic upgrade head` documented | GET /risks → 200 | DB | None |

**Issues closed:** KHZ-047, KHZ-012, KHZ-054 (partial KHZ-021)

---

### Sprint 2 — Reports & PDF Truth

**Objective:** Generated report and exported PDF match the intended analysis run with readable Arabic content.

| Files | Acceptance criteria | Regression checklist | Dependencies | Rollback risk |
|-------|---------------------|----------------------|--------------|---------------|
| `reports-page.tsx`, `khazina-api.ts` | Risk report has risk title; export uses selected or current-run report | Generate risk → title correct; PDF matches | Sprint 1 | Medium |
| `demo/state.ts`, waste/risk pages | Clear `lastReportId` when run IDs change | Re-run waste → export fails until new generate | Sprint 1 | Low |
| `pdf_renderer.py` | Arabic TTF + bidi; expand list sections | PDF shows Arabic + risk names | Report content | Medium |

**Issues closed:** KHZ-022, KHZ-023, KHZ-048, KHZ-049, KHZ-050, KHZ-062

---

### Sprint 3 — Workflow Persistence & Data Freshness

**Objective:** Re-upload, navigation, and refresh never show stale run data.

| Files | Acceptance criteria | Regression checklist | Dependencies | Rollback risk |
|-------|---------------------|----------------------|--------------|---------------|
| `risk-page.tsx` | Reset UI when `riskRunId` null | Upload new file → risk page empty | Sprint 1 | Low |
| `waste-page.tsx`, `simulation-page.tsx` | Abort/stale guards on fetch | Slow network re-upload test | Sprint 1 | Low |
| `auth-context.tsx` | Clear artifacts on signIn | Login → empty artifacts | Sprint 1 | Low |
| `demo/state.ts` | Wire `clearAnalysisArtifacts` on failure paths | Failed upload → no stale IDs | Sprint 1 | Low |

**Issues closed:** KHZ-011, KHZ-053, KHZ-055, KHZ-057, KHZ-028 (partial)

---

### Sprint 4 — Risk Subsystem Completion

**Objective:** Risk page fully consistent with waste patterns; detail page accurate.

| Files | Acceptance criteria | Regression checklist | Dependencies | Rollback risk |
|-------|---------------------|----------------------|--------------|---------------|
| `risk-page.tsx` | Reload AI insights on mount | F5 after risk AI → summary visible | Sprint 3 | Low |
| `risk-detail-page.tsx` | Correct file/snapshot labels | Detail shows file name not UUID | Sprint 1 (dept fix) | Low |
| `risk-page.tsx` | History run selectable (if in scope) | Select old run → loads findings | Backend APIs | Medium |

**Issues closed:** KHZ-058, KHZ-019, KHZ-042 (optional), KHZ-031 (partial)

---

### Sprint 5 — Simulation Integrity

**Objective:** Simulation requires valid waste baseline; errors visible; scenario reports reachable.

| Files | Acceptance criteria | Regression checklist | Dependencies | Rollback risk |
|-------|---------------------|----------------------|--------------|---------------|
| `simulation-page.tsx` | Require `wasteRunId`; surface load errors | Re-upload → must re-run waste before sim | Sprint 3 | Low |
| `simulation-page.tsx`, `reports-page.tsx` | Store simulation `analysis_run.id`; add generate button | Sim → report → PDF | Sprint 2 | Medium |

**Issues closed:** KHZ-020, KHZ-051, KHZ-052, KHZ-056

---

### Sprint 6 — Dashboard & Executive Pipeline

**Objective:** Dashboard reflects live data; workflow indicator includes risk.

| Files | Acceptance criteria | Regression checklist | Dependencies | Rollback risk |
|-------|---------------------|----------------------|--------------|---------------|
| `dashboard-page.tsx` | Waste KPI wired or honestly labeled empty | Dashboard shows waste total or N/A | Waste API | Low |
| `dashboard-charts.tsx` | Wire trend API or remove placeholder | Charts show data or hidden | Backend aggregation | Medium |
| `pipeline.ts` | Add risk stage | Indicator shows risk step | Sprint 4 | Low |

**Issues closed:** KHZ-015, KHZ-016, KHZ-017, KHZ-030

---

### Sprint 7 — API Contracts & Client Alignment

**Objective:** No FE↔BE contract mismatches; shared pagination policy.

| Files | Acceptance criteria | Regression checklist | Dependencies | Rollback risk |
|-------|---------------------|----------------------|--------------|---------------|
| `khazina-api.ts` | Add `ListQueryParams` to all list functions | Pass `limit:100` on large lists | Sprint 1 | Low |
| `API_CONTRACTS.md` | Document `limit`/`offset`, max 100 | Docs match code | None | None |
| Shared constants | `MAX_PAGE_SIZE = 100` in FE | Grep finds no limit > 100 | Sprint 1 | Low |

**Issues closed:** KHZ-061, KHZ-060, AC-003 through AC-007

---

### Sprint 8 — Auth Hardening (Demo-Safe)

**Objective:** Predictable login for judges; graceful token expiry.

| Files | Acceptance criteria | Regression checklist | Dependencies | Rollback risk |
|-------|---------------------|----------------------|--------------|---------------|
| `auth-context.tsx`, `login/page.tsx` | Gate auto-login + prefill behind env flag | Production build: empty login | Sprint 3 | Medium |
| `client.ts` | 401 → clearSession + redirect | Expired token → login page | Sprint 3 | Low |

**Issues closed:** KHZ-002, KHZ-003, KHZ-006 (KHZ-005 deferred post-hackathon)

---

### Sprint 9 — Backend Quality & Security

**Objective:** Tests green; IDOR closed; upload safe.

| Files | Acceptance criteria | Regression checklist | Dependencies | Rollback risk |
|-------|---------------------|----------------------|--------------|---------------|
| Risk services | Org ownership on all GET-by-ID | Cross-org → 404 | None | Medium |
| `financial.py` | Chunked upload size check | 15MB file rejected safely | None | Low |
| `tests/` | 303/303 pass | Full pytest | Sprints 1-8 | Low |
| `reports/service.py` | Idempotent generate | Double-click → one report | Sprint 2 | Low |

**Issues closed:** KHZ-008, KHZ-009, KHZ-001, KHZ-026, KHZ-059, KHZ-027 (partial)

---

### Sprint 10 — Polish & Low Priority

**Objective:** Cosmetic fixes; org cache refresh; notification UX.

| Files | Acceptance criteria | Regression checklist | Dependencies | Rollback risk |
|-------|---------------------|----------------------|--------------|---------------|
| `data-management-page.tsx` | Call `orgLookups.refresh()` after upload | Dept list current | Sprint 1, 7 | Low |
| `notification-bell.tsx`, reports cards | RTL badge, formatted dates | Visual check | None | None |
| `placeholder-data.ts` | Remove orphan mocks | No imports | None | None |

**Issues closed:** KHZ-018, KHZ-043–046, KHZ-039, KHZ-038, KHZ-033–037, KHZ-040, KHZ-041

---

## 7. Sprint Dependency Graph

```
Sprint 1 (422 + waste refresh)
    ├── Sprint 2 (Reports/PDF)
    ├── Sprint 3 (Persistence)
    │       ├── Sprint 4 (Risk)
    │       └── Sprint 5 (Simulation) → depends on Sprint 2 for reports
    ├── Sprint 6 (Dashboard)
    └── Sprint 7 (API contracts)

Sprint 8 (Auth) — parallel after Sprint 3
Sprint 9 (Backend/security) — after Sprints 1-2
Sprint 10 (Polish) — last
```

---

## 8. Hackathon Demo Script (Post-Sprint 1 Minimum)

Until sprints complete, presenters MUST:

1. Run `alembic upgrade head`
2. Single browser tab only
3. Do NOT refresh after waste AI (until KHZ-012 fixed)
4. Do NOT re-upload mid-demo (until Sprint 3)
5. Generate report immediately before PDF export
6. Avoid dashboard charts/KPI deep dive
7. Monitor Network tab: fix KHZ-047 before demo if Sprint 1 not done

---

## 9. Definition of Done (Platform)

| Criterion | Current | Target |
|-----------|---------|--------|
| Full workflow without manual intervention | ❌ | ✅ After Sprints 1–5 |
| No stale data on refresh/re-upload | ❌ | ✅ After Sprint 3 |
| Correct report + PDF | ❌ | ✅ After Sprint 2 |
| No API 422 on load | ❌ | ✅ After Sprint 1 |
| 303/303 tests pass | ❌ (299/303) | ✅ After Sprint 9 |
| No regression between sprints | — | Re-run prior sprint checklist each sprint |

---

## 10. Sign-Off

| Role | Assessment |
|------|------------|
| Principal Architect | Architecture sound; persistence layer split is root systemic issue |
| Backend | APIs functional; validation strict (422 on limit); PDF renderer inadequate for Arabic |
| Frontend | Workflow UX strong (D2); sessionStorage coupling is hackathon risk |
| QA | 52+ issues logged; 4 test failures; no Playwright E2E |
| Integration | departments 422 breaks cross-module labels on every load |
| Security | Demo-only; do not claim enterprise multi-tenant readiness |

**Recommendation:** Execute Sprints 1–3 before any hackathon rehearsal. Sprints 1–5 required for "finished product" claim on master workflow.

---

## References

- [API_CONTRACT_AUDIT.md](API_CONTRACT_AUDIT.md)
- [BUG_TRACKER.md](BUG_TRACKER.md)
- [FULL_PLATFORM_QA_AUDIT.md](FULL_PLATFORM_QA_AUDIT.md)
- [PHASE_9_COMPLETION_REPORT.md](PHASE_9_COMPLETION_REPORT.md)
- [PRODUCT_POLISH_COMPLETION_REPORT.md](PRODUCT_POLISH_COMPLETION_REPORT.md)
- [SPRINT_8_5_QA_FREEZE_REPORT.md](SPRINT_8_5_QA_FREEZE_REPORT.md)
- [REAL_WORLD_AI_EXECUTION_TRACE.md](REAL_WORLD_AI_EXECUTION_TRACE.md)
