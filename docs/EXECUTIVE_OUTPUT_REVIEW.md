# Executive Output Review

**Sprint:** Emergency — Executive Output Stabilization  
**Date:** 2026-07-17  
**Scope:** Presentation layer only — no business logic, scoring, engines, or schema changes

---

## Verdict

| Area | Before | After |
|------|--------|-------|
| AI recommendation cards | Leaked `waste.*` keys, mixed AR/EN | Sanitized at parse + display |
| Risk AI summaries | Raw LLM text with technical echo | Sanitized at mapper + UI |
| Report preview | Raw section text | `sanitizeExecutiveText()` |
| PDF export | Facts contract, provenance, `(N items)` | Executive-safe renderer |

---

## Root Cause Summary

Technical identifiers entered the **user-visible path** at five points:

1. **Prompt builder** — raw metric keys (`waste.top_category`) in user prompt
2. **Arabic task template** — required `الحقائق المرجعية:` block → LLM echoed keys
3. **Parser** — stored full LLM body including reference block
4. **Mapper** — persisted unsanitized text to DB
5. **PDF renderer** — serialized all payload keys verbatim including `facts`, `provenance`

---

## Fixes Applied

| Layer | File | Change |
|-------|------|--------|
| Prompt labels | `presentation/metric_labels.py`, `ai/prompts/builder.py` | Arabic business labels instead of metric keys |
| Prompt templates | `ai/prompts/languages/ar.py` | Executive tone; removed reference-facts output format |
| Parser | `recommendation_parser.py`, `risk_recommendation_parser.py` | Extract action + rationale only; sanitize |
| Persistence | `mapper.py`, `risk_mapper.py` | Sanitize all narrative and recommendation text |
| Report build | `reports/sections.py` | Sanitize AI executive summary in sections |
| PDF | `reports/pdf_renderer.py` | Executive section filter; hide technical keys; cover business fields |
| Frontend | `lib/format.ts`, `risk-ai-summary.tsx`, `reports-page.tsx` | Defense-in-depth display sanitization |

---

## Validation

- `20` targeted tests passed (sanitizer + PDF + parser)
- Full backend suite: run after deploy
- **Re-generate AI recommendations** after deploy — old DB rows may still contain pre-fix text until re-run

---

## Manual Demo Checklist

After restart, verify in UI (not unit tests alone):

- [ ] Waste AI cards: no English dot-keys, no `facts_contract`
- [ ] Risk AI summary: fluent Arabic, no snake_case
- [ ] Report preview: executive prose only
- [ ] PDF text search: no `engine_id`, `tasks_executed`, `waste.`

**Audience standard:** CEO / Board / Hackathon judges — not developers.
