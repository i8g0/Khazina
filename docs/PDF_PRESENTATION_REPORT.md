# PDF Presentation Report

**Sprint:** Emergency — Executive Output Stabilization  
**Date:** 2026-07-17

---

## Objective

PDF export must read like a **board consulting report** — never a system debug dump.

---

## Problems Fixed

| Issue | Root cause | Fix |
|-------|------------|-----|
| `facts: [16 items]` | `key_metrics.facts` rendered raw | Only render `headline` as Arabic financial highlights |
| `tasks_executed`, `engine_version` | `provenance` section in PDF | Technical sections always excluded |
| `profile: waste_decision` on cover | Raw profile code on synthetic cover | Replaced with org, period, source file from cover section |
| `category_breakdowns (N):` | List count suffix | Lists render without `(N items)` suffix |
| Technical keys in recommendations | `source_context` in item dicts | Forbidden keys filtered in renderer |
| Missing business cover data | Cover section skipped | Cover payload merged into title page |

---

## Executive Section Map

| Internal key | PDF title (Arabic) |
|--------------|-------------------|
| `executive_summary` | الملخص التنفيذي |
| `key_metrics` | أبرز المؤشرات المالية |
| `waste_analysis` | تحليل الهدر |
| `risk_summary` / `risk_explanation` | تحليل المخاطر |
| `top_risks` | أبرز المخاطر |
| `recommendations` | التوصيات التنفيذية |
| `scenario_overview` / `forecast_and_delta` | تحليل السيناريو |
| `impact_and_actions` | الأثر المالي والإجراءات ذات الأولوية |
| *(auto)* | الخلاصة — derived from executive summary |

---

## Sections Never Rendered

- `cover` (data merged into title page)
- `provenance`
- `scenario_provenance`
- `baseline_context`

---

## Forbidden Payload Keys (filtered)

`facts`, `source`, `profile`, `facts_contract_version`, `engine_id`, `engine_version`, `tasks_executed`, `source_snapshot_id`, `metadata`, `ai_metadata`, `source_context`, `traceability`, `scenario_id`, `department_id`, and others.

---

## Files Changed

- `backend/app/reports/pdf_renderer.py` — executive transform layer
- `backend/app/reports/export_service.py` — default `include_provenance=False`
- `backend/tests/advanced_features/test_pdf_export.py` — asserts no technical strings in PDF bytes

---

## Cover Page (post-fix)

Renders when `include_cover_page=True`:

1. Report title
2. Platform name
3. Organization name *(from cover section)*
4. Period label
5. Source file name
6. Completion date

Does **not** render: `profile` code, raw ISO metadata blocks.

---

## Validation Test

```python
test_pdf_render_excludes_technical_metadata()
```

Asserts PDF bytes do not contain:

- `waste.top_category`
- `facts_contract`
- `tasks_executed`
- `engine_id`

---

## Manual Verification

1. Complete LAW workflow through report generate
2. Export PDF for waste, risk, and simulation reports
3. Open PDF — confirm executive sections only
4. Text search PDF for forbidden strings (must be zero matches)

**Note:** Re-generate reports after deploy — old report content in DB was built with pre-fix section payloads; PDF renderer sanitizes at render time but new AI text improves recommendation sections.
