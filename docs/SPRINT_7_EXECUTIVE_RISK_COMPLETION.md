# Sprint 7.1 — Executive Risk Intelligence Completion

**Status:** Sprint 7.1 deliverable — executive risk experience completion (not Sprint 8).

## Problem

Sprint 7 backend risk logic was in place, but the **Executive Risk Experience** remained incomplete: English labels, vague narratives, weak charts, no simulation linkage, and non-board-ready reports/PDF.

## Architecture

```
Upload → Waste → Risk → Risk AI → Simulation → Reports → PDF
                              ↑                    ↑
                         risk_context         assemble_risk_sections
                         (S7.1)               (Deloitte-style AR)
```

### Risk → Simulation bridge

- **`backend/app/scenario/risk_context.py`** — loads findings, exposure, departments, suppliers, and recommendations from `risk_analysis_run_id`.
- **`AISimulationExecuteRequest.risk_analysis_run_id`** — optional API field.
- **`AISimulationService`** — passes context to interpreter + explainer; persists `risk_context` in run metadata.
- **Frontend simulation page** — sends `artifacts.riskRunId`; shows «كيف تؤثر المخاطر على السيناريو؟» panel.

### Executive Arabic layer

- **`backend/app/presentation/business_labels.py`** — `risk_posture_ar`, `risk_priority_ar`, `risk_category_ar`, `risk_level_ar`.
- **`backend/app/business/engines/risk/rules/evidence.py`** — every finding gets: `detection_reason_ar`, `financial_impact_ar`, `waste_value_label`, `if_ignored_ar`, `executive_summary_ar`.
- **`frontend/lib/format.ts`** — no English fall-through on posture/priority/status.
- **`frontend/lib/executive-language.ts`** — `ensureExecutiveArabic()` strips technical tokens and vague words (قد، ربما، …).
- **`frontend/lib/risk/mappers.ts`** — sanitizes all display strings; builds waste-by-department and risk-trend charts.

### Reports & PDF (Deloitte-style)

New risk report sections (Arabic only in payloads):

| Section key | Arabic title |
|---|---|
| `executive_summary` | الملخص التنفيذي |
| `current_situation` | الوضع الحالي |
| `top_risks` | أعلى المخاطر |
| `financial_impact` | الأثر المالي |
| `operational_impact` | الأثر التشغيلي |
| `evidence` | الأدلة |
| `recommendations` | التوصيات |
| `proposed_decisions` | القرارات المقترحة |
| `next_steps` | الخطوات التالية |

PDF renderer maps all section keys to Arabic executive titles.

## Files changed

### Backend
- `app/scenario/risk_context.py` (new)
- `app/scenario/ai_simulation_service.py`
- `app/scenario/ai_interpreter.py`
- `app/scenario/ai_explainer.py`
- `app/schemas/scenario.py`
- `app/api/v1/scenario.py`
- `app/api/deps.py`
- `app/presentation/business_labels.py`
- `app/business/engines/risk/rules/evidence.py`
- `app/business/engines/risk/rules/__init__.py` (supplier narrative + strategic bugfix)
- `app/reports/constants.py`
- `app/reports/sections.py`
- `app/reports/pdf_renderer.py`
- `tests/business/test_risk_executive_s7.py`
- `tests/scenario/test_risk_simulation_context.py` (new)

### Frontend
- `lib/format.ts`, `lib/executive-language.ts`
- `lib/risk/mappers.ts`, `lib/risk/view-types.ts`
- `lib/api/khazina-api.ts`
- `components/risk/risk-executive-card.tsx`
- `components/risk/risk-priority-matrix.tsx`
- `components/risk/risk-charts.tsx`
- `components/risk/risk-page.tsx`
- `components/simulation/simulation-page.tsx`

## Before / After

| Area | Before | After |
|---|---|---|
| Risk cards | Generic English/mixed labels | 16+ Arabic executive fields with evidence |
| Matrix | Empty cells, weak tooltips | Title, dept, exposure, why-tooltip, click-to-select |
| Charts | Basic severity only | الهدر حسب الإدارة، التعرّض، الموردين، الوفورات، اتجاه المخاطر |
| Simulation | Ignored risk run | Reads `riskRunId`, AI explains risk impact on scenario |
| Reports | Technical codes in payload | Deloitte-style Arabic sections |
| PDF | Partial English keys | Arabic section titles + sanitized payloads |
| Supplier risk | «Vendor concentration» style | «تركّز X% من الهدر على N موردين» with counts |

## Acceptance tests

```bash
cd Khazina/backend
pytest tests/business/test_risk_executive_s7.py \
       tests/scenario/test_risk_simulation_context.py \
       tests/scenario/test_financial_reality.py -q
```

### Manual regression (enterprise workflow)

1. Upload `Demo_Enterprise_Dataset_v2.xlsx`
2. Waste → Waste AI
3. Risk → Risk AI
4. Simulation (verify risk linkage banner + risks panel)
5. Reports (risk profile)
6. PDF export

Verify: ✓ Arabic only ✓ executive wording ✓ charts ✓ cards ✓ simulation↔risk ✓ reports ✓ PDF

## Known limitations

- Strategic/forecast risk rules still need `simulation_summary` injected in DecisionService (pre-existing).
- Budget variance rule needs `budget`/`actual` columns; enterprise dataset uses `planned_amount`/`spent_amount`.
- AI explainer quality depends on Cloud AI availability; deterministic fallback narratives use gold sections.
- RBAC gaps KHZ-007/KHZ-008 remain out of S7.1 scope.

## Performance

- Risk context load: O(n) findings (limit 20) + recommendations — negligible vs simulation AI call.
- Report section assembly: linear in findings count; no extra DB round-trips beyond existing loaders.
- Frontend chart builders: in-memory on ≤100 findings — sub-ms.

---

**Sprint 7.1 completion criteria:** executive Arabic UX, matrix/charts/cards, simulation↔risk, reports/PDF, regression tests documented above.

**Sprint 8:** blocked until product owner signs off S7.1 acceptance.
