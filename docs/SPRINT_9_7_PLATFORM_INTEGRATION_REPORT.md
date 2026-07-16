# Sprint 9.7 — Financial Risk Platform Integration Report

**Sprint:** 9.7 — Financial Risk Platform Integration  
**Date:** 2026-07-16  
**Status:** Complete  
**Architecture reference:** Sprints 9.1–9.6 (locked), Sprint 6.x platform services

---

## 1. Summary

Sprint 9.7 validates and completes **platform-wide integration** of Financial Risk Intelligence. Work focused on **gaps identified by audit** — not redesign. Risk now participates in reports, notifications, dashboard KPIs, and PDF export using existing Khazina infrastructure.

**Validation:** 290 backend tests (+3), TypeScript pass, ESLint pass. No Risk Engine, scoring, or API redesign.

---

## 2. Integration Matrix

| Platform area | Pre-9.7 | Post-9.7 | Evidence |
|---------------|---------|----------|----------|
| **Dashboard** | Critical risks KPI only | Critical + active risks + executive summary snippet from latest risk run metadata | `dashboard-page.tsx` — single `Promise.all` (no duplicate queries) |
| **Reports** | `risk` analysis type blocked | Full `PROFILE_RISK` report generation | `reports/constants.py`, `loaders.py`, `sections.py`, `service.py` |
| **PDF export** | N/A for risk | Risk section labels in PDF renderer | `pdf_renderer.py` |
| **Notifications** | Risk AI only | Risk analysis completed/failed + existing risk AI | `notifications/builder.py`, `constants.py`, `templates.py` |
| **Simulation** | Waste baseline only | **Unchanged by design** — simulation baselines remain waste runs | `loaders.py:_load_baseline` (documented boundary) |
| **AI** | Waste + Risk separate paths | **Verified unchanged** — shared `AiTaskPipeline`, domain routing | Sprint 9.5 architecture |
| **Observability** | Risk pipeline stages exist | Report generation stage now works for risk runs | `ReportBuilderService` timeline + logs |

---

## 3. Cross-Module Dependencies

```
Financial File Upload
    → Waste Analysis (existing)
    → Risk Analysis (9.3)
        → Risk Register / Findings (9.4)
        → Risk AI (9.5)
            → Recommendations (domain=risk)
            → Notifications (risk_analysis_completed, risk_ai_recommendations_completed)
            → Reports (PROFILE_RISK)
                → PDF Export
    → Simulation (baseline = waste run — unchanged)
    → Executive Dashboard (risks list + recent analyses metadata)
```

**Single source of truth:** Risk Engine deterministic output → Gold persistence → all downstream consumers read persisted artifacts only.

---

## 4. Changes Made (Minimal Integration Only)

### 4.1 Reports backend

| File | Change |
|------|--------|
| `reports/constants.py` | Added `PROFILE_RISK`, `RISK_SECTION_ORDER`, `risk` in supported types/engines |
| `reports/loaders.py` | `RiskReportInputs`, `load_risk_inputs()`, `risk_input_fingerprint()` |
| `reports/sections.py` | `assemble_risk_sections()` — summary, top risks, mitigation, register stats |
| `reports/service.py` | Risk profile branch in `generate_report()` |
| `reports/pdf_renderer.py` | Arabic labels for risk sections |
| `api/deps.py` | Wire `RiskAnalysisRepository` + `RiskRepository` into report builder |

**Report sections (risk profile):**

1. Cover  
2. Executive summary (AI `risk_executive_summary` or Gold fallback)  
3. Key metrics (Facts Contract)  
4. Risk summary (posture, counts)  
5. Top risks (findings)  
6. Mitigation status (plans linked to promoted register risks)  
7. Register statistics  
8. Recommendations (domain=risk)  
9. Provenance  

### 4.2 Notifications backend

| Kind | Trigger |
|------|---------|
| `risk_analysis_completed` | `materialize_analysis_completion()` when `AnalysisType.RISK` |
| `risk_analysis_failed` | `materialize_analysis_failure()` when `AnalysisType.RISK` |
| `risk_ai_recommendations_completed` | Already existed (Sprint 9.5) |

Settings defaults updated in `settings/constants.py`.

### 4.3 Frontend (integration only — no redesign)

| File | Change |
|------|--------|
| `dashboard-page.tsx` | KPI slot 3 → active risks; risk executive summary from latest risk run `runtime_metadata.ai_insights` (no extra API call) |
| `reports-page.tsx` | Second button: generate report from `artifacts.riskRunId` |

---

## 5. Verified Already Working (No Changes)

| Capability | Evidence |
|------------|----------|
| Risk analysis execution + Gold persistence | Sprint 9.3 |
| Risk register governance | Sprint 9.4 |
| Risk AI (5 tasks, shared pipeline) | Sprint 9.5 |
| Risk frontend pages | Sprint 9.6 |
| Timeline events on analysis completion | `AnalysisService.complete_run()` |
| Recent analyses includes risk runs | `list_recent_completed()` all types |
| Waste / Simulation / Settings / Users | Full regression suite green |

---

## 6. E2E Workflow Validation

| Stage | Validated via |
|-------|---------------|
| Login | Existing auth flow |
| Upload workbook | Data management + demo artifacts |
| Waste analysis | Existing waste tests + regression |
| Risk analysis | `tests/services/test_risk_analysis_service.py`, risk AI tests |
| Risk review / promotion | `tests/services/test_risk_register_service.py` |
| Risk AI summary | `tests/ai_recommendations/test_risk_ai_service.py` |
| Simulation | Unchanged — waste baseline |
| Risk report generation | `tests/reports/test_service.py::test_generate_risk_report_success` |
| PDF export | Existing export service (content-driven) |
| Notifications | `tests/notifications/test_builder.py::test_risk_analysis_completion_materializes` |

**Manual E2E path:** Upload → Waste → Risk → Review → Promote → Risk AI → Reports (risk button) → PDF — supported by connected APIs and frontend artifact state (`riskRunId`, `lastReportId`).

---

## 7. Regression Results

| Suite | Result |
|-------|--------|
| Backend `pytest` | **290 passed** (+3 new tests) |
| Frontend `tsc --noEmit` | Pass |
| Frontend `npm run lint` | Pass |
| Risk Engine | Unchanged |
| Deterministic scoring | Unchanged |
| Waste AI | Unchanged |
| Simulation behaviour | Unchanged |
| Frontend page layout | Unchanged (integration buttons/KPIs only) |

### New tests

- `tests/reports/test_service.py::test_generate_risk_report_success`
- `tests/reports/test_report_facts_loader.py::test_load_risk_facts`
- `tests/notifications/test_builder.py::test_risk_analysis_completion_materializes`

---

## 8. Intentional Boundaries (Sprint 9.7)

| Topic | Decision |
|-------|----------|
| Simulation risk baseline | Not extended — baselines remain `AnalysisType.FINANCIAL_WASTE` per locked simulation design |
| Dashboard waste KPI | Remains empty until waste run — avoids extra API calls (no duplicate queries) |
| Dashboard charts | Waste-centric placeholders unchanged — risk charts live on `/risk-management` |
| Promotion / mitigation overdue notifications | Not added — would require new scheduled jobs (out of integration scope) |
| New business features | None |

---

## 9. Remaining Work — Sprint 9.8

1. **Scheduled notifications** — mitigation overdue, new critical risk alerts (requires job runner)  
2. **Simulation optional risk baseline** — if product requires risk-informed scenarios  
3. **Dashboard risk trend chart** — aggregate from historical risk runs (backend aggregation API optional)  
4. **Dedicated E2E Playwright suite** — automated browser workflow for full platform path  
5. **Remove orphaned mock data** in `placeholder-data.ts` (cosmetic cleanup)  
6. **Register lifecycle actions on detail page** — APIs exist; UI read-only today  

---

## 10. Definition of Done

| Criterion | Status |
|-----------|--------|
| Risk integrated across platform surfaces | ✅ |
| E2E workflow supported | ✅ |
| Cross-module integrations validated | ✅ |
| No regression | ✅ (290 tests) |
| Architecture preserved | ✅ |
| Backend tests pass | ✅ |
| Frontend TypeScript pass | ✅ |
| Frontend lint pass | ✅ |
| Minimal necessary code changes | ✅ |
