# AI Quality Review

**Date:** 2026-07-16  
**Phase:** 1 — Investigation ONLY  
**Standard:** Board-ready executive consultant tone (McKinsey/BCG/Deloitte class)  
**Blocker:** Production — internal keys MUST NEVER appear in UI or PDF

---

## Executive Summary

AI **routing is correct** (Cloud-only when configured). AI **output quality is NOT executive-grade** because the platform **injects technical metric keys into prompts** and **persists the LLM’s full response without sanitization**.

This is a **systemic pipeline defect**, not a model quality issue.

---

## Quality Requirements vs Actual

| Requirement | Actual | Pass |
|-------------|--------|------|
| Arabic executive prose | Mixed AR/EN; English keys visible | ❌ |
| No `waste.*` / `risk.*` keys | Visible in recommendation cards | ❌ |
| No `facts_contract` exposure | Visible in PDF key_metrics | ❌ |
| No metadata/debug in UI | Partial — some fields hidden | ⚠️ |
| Consultant tone | Reads like structured data dump | ❌ |
| Cloud AI only | Verified in provider factory | ✅ |

---

## Execution Path (Verified)

```
Analysis Run → Facts Assembler → PromptFact(metric=English key)
    → build_user_prompt() → "**waste** / waste.top_category: ..."
    → CloudProvider.chat() → LLM echoes reference block
    → recommendation_parser.py → description = full body
    → DB ai_recommendation_items
    → formatRecommendationDisplay() → strips only "الإجراء المقترح:"
    → UI card + PDF sections
```

---

## Root Cause Chain

### RC-AI-1: English metric keys in prompts

**File:** `backend/app/ai/prompts/builder.py`

```python
lines = [
    f"- **{fact.domain}** / {fact.metric}: {fact.value}",
]
```

`fact.metric` values originate from assemblers as internal identifiers:
- `waste.top_category`
- `waste.category_level`
- `risk.top_category`
- Similar keys across waste/risk facts

Arabic language pack adds header `الحقائق المرجعية:` — instructing the model to treat these as reference facts, which it **quotes verbatim** in recommendations.

### RC-AI-2: Parser stores unsanitized body

**File:** `backend/app/ai_recommendations/recommendation_parser.py`

`_split_title_and_description()` sets `description = body.strip()` — entire chunk including reference facts section.

No post-processing removes:
- Numbered reference blocks
- Dot-notation metric keys
- English domain labels

### RC-AI-3: Frontend minimal display filter

**File:** `frontend/lib/format.ts` — `formatRecommendationDisplay()`

Only removes prefix `الإجراء المقترح:` — does not strip technical keys.

### RC-AI-4: Risk findings English rule names

Risk engine emits English rule identifiers; displayed directly in Risk UI (separate from waste AI but same quality bar).

### RC-AI-5: PDF re-serializes facts contract

Report builder includes `key_metrics.facts` section with raw Facts Contract — full technical dump in executive PDF.

---

## Prompt Leakage Examples (Must Never Appear)

| Leak type | Where seen | Source |
|-----------|------------|--------|
| `waste.top_category` | Waste AI cards | Prompt metric key |
| `waste.category_level` | Waste AI cards | Prompt metric key |
| `facts_contract` | PDF appendix | Report section builder |
| `metadata` | PDF provenance | Report provenance section |
| Raw JSON keys | PDF | Section payload serialization |

---

## AI Provider Audit

| Check | Evidence | Result |
|-------|----------|--------|
| Default provider | `get_ai_provider()` → `CloudProvider` when `AI_PROVIDER=cloud` | ✅ |
| Ollama blocked | `get_ollama_client()` raises if cloud mode | ✅ |
| Logging | Provider logs task/model (verify in Phase 2 E2E) | ⚠️ Needs log capture in demo |
| Parallel AI | Cloud path used for recommendations | ✅ |

**Critical:** If Ollama executes once in production demo → Critical Bug. Code path prevents this when env is cloud.

---

## Language Pack Review

**File:** `backend/app/ai/prompts/languages/ar.py`

- `facts_header` = `الحقائق المرجعية:\n` — causes model to reproduce block in output
- System prompts request structured recommendations but do not forbid echoing input keys

---

## Required Quality Transform (Phase 2 Design)

### Layer 1: Prompt (prevent)
- Map metric keys → Arabic business labels before prompt assembly
- Remove or relocate reference-facts block from user-visible prompt path
- System prompt: "Never output variable names, JSON keys, or internal identifiers"

### Layer 2: Parser (enforce)
- Strip `الحقائق المرجعية:` blocks from description
- Reject items containing `\w+\.\w+` dot-notation keys (or auto-redact)
- Separate `executive_summary` field for UI

### Layer 3: Display (defense in depth)
- `formatRecommendationDisplay()` redact known internal patterns
- Risk findings: localize rule names

### Layer 4: PDF (executive safe)
- Never render raw facts contract in executive sections
- Map metrics to Arabic labels in Financial Highlights

---

## Test Evidence

| Test | Status | Notes |
|------|--------|-------|
| `tests/ai/test_providers.py` | Pass | Cloud routing |
| `test_generate_risk_ai_success` | **FAIL** | Regression — investigate in Sprint 0 |
| `test_risk_pipeline_executes_tasks_in_order` | **FAIL** | Regression |

AI quality is **not fully covered by unit tests** — requires E2E UI inspection per FINAL RULE.

---

## Acceptance Criteria (Phase 2)

1. Zero occurrences of `waste.`, `risk.`, `facts_contract`, `metadata` in waste AI cards (UI inspection)
2. Risk AI summary: Arabic executive prose, no English engine identifiers
3. PDF executive sections: no dot-notation keys
4. Backend logs show `provider=cloud`, model name, latency per AI call
5. Full LAW workflow after fix

**Phase 1 complete. No code modified.**
