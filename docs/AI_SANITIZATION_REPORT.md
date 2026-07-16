# AI Sanitization Report

**Sprint:** Emergency — Executive Output Stabilization  
**Date:** 2026-07-17

---

## Architecture

```
Cloud LLM response
    ↓
recommendation_parser / risk_recommendation_parser
    ↓ extract_recommendation_executive_text()
    ↓ sanitize_executive_text()
mapper / risk_mapper
    ↓ sanitize_executive_text() on all narratives
Database (title, description, ai_insights)
    ↓
Frontend formatRecommendationDisplay() / sanitizeExecutiveText()
    ↓
User UI + Report sections + PDF
```

**Defense in depth:** sanitize at parse, persist, display, and PDF render.

---

## Module: `app/presentation/executive_sanitize.py`

### Functions

| Function | Purpose |
|----------|---------|
| `sanitize_executive_text()` | Remove dot-keys, snake_case, forbidden literals, UUIDs |
| `extract_recommendation_executive_text()` | Keep الإجراء المقترح + المبرر only |
| `contains_technical_leakage()` | Test helper / validation gate |

### Patterns Removed

| Pattern | Example |
|---------|---------|
| Dot-notation | `waste.top_category`, `risk.score_max` |
| Forbidden literals | `facts_contract`, `metadata`, `engine_id` |
| Reference block | `الحقائق المرجعية: ...` |
| UUIDs | `550e8400-e29b-...` |
| snake_case tokens | `source_snapshot_id`, `tasks_executed` |

### Patterns Preserved

- Arabic executive prose
- Numbers and currency values
- Priority keywords (عالية، متوسطة)

---

## Integration Points

| File | Sanitized fields |
|------|------------------|
| `recommendation_parser.py` | `title`, `description` |
| `risk_recommendation_parser.py` | `title`, `description` |
| `mapper.py` | `executive_summary`, `risk_explanation`, narrative `text`, recommendation payloads |
| `risk_mapper.py` | All risk summary keys, recommendation payloads |
| `sections.py` | AI executive summary, risk explanation in reports |
| `format.ts` | All recommendation display + report preview |
| `risk-ai-summary.tsx` | All AI insight sections |

---

## Tests

`tests/presentation/test_executive_sanitize.py`:

- Removes `waste.top_category`
- Strips reference facts block
- Removes `facts_contract`, `metadata`, `engine_id`
- Extracts action + rationale only

---

## Important Note

**Existing DB rows** created before this sprint may still contain leaked text.  
**Action:** Re-run Waste AI and Risk AI generation in the demo workflow after deploy.

---

## Acceptance

Sanitizer **fails** if output still contains:

- English variable names
- snake_case identifiers  
- `facts_contract` / `metadata` strings
- Dot-notation metric keys

Use `contains_technical_leakage()` in tests or manual grep on UI/PDF.
