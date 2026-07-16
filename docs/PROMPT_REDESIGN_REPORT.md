# Prompt Redesign Report

**Sprint:** Emergency — Executive Output Stabilization  
**Date:** 2026-07-17

---

## Objective

Transform AI prompts so the model receives **business context in Arabic** and returns **consulting-grade prose** — never internal variable names.

---

## Leakage Points Identified

| Stage | Issue | Evidence |
|-------|-------|----------|
| Facts → Prompt | `builder.py` rendered `**waste** / waste.top_category: Finance` | `ai/prompts/builder.py` (pre-fix) |
| System prompt | No prohibition on key echo | `ar.py` system_prompt |
| RECOMMENDATIONS task | Required `الحقائق المرجعية:` in output | `ar.py` lines 95–101 (pre-fix) |
| Example in template | Showed `حقيقة_أ، حقيقة_ب` pattern | Encouraged key-like output |

---

## Changes Made

### 1. System prompt (`ar.py`)

Added permanent rules:

- Never use variable names, JSON keys, snake_case, or dot-notation
- Never mention `facts_contract`, `metadata`, `engine_id`
- Transform every fact into executive Arabic sentences

### 2. Output rules (`ar.py`)

- McKinsey/BCG-style executive prose
- Explicit ban on internal field names

### 3. Facts header

| Before | After |
|--------|-------|
| `## الحقائق المقدمة` | `## السياق المالي والتشغيلي` |

Reduces model tendency to quote a "facts block."

### 4. RECOMMENDATIONS task template

**Removed from output format:**
- `الحقائق المرجعية:` section
- Example with fake key names

**New format (mandatory):**
```
1.
الإجراء المقترح:
[executive action]
المبرر:
[executive rationale]
```

### 5. RISK_MITIGATION_OPTIONS template

Same — removed `الحقائق المرجعية`, added bans on technical output.

### 6. Prompt fact formatting (`metric_labels.py` + `builder.py`)

| Before | After |
|--------|-------|
| `**waste** / waste.top_category: finance` | `الهدر المالي: أعلى فئة هدر = finance` |

All known waste/risk/scenario metrics mapped to Arabic labels.

---

## Example Transformation

### BAD (pre-fix prompt input)
```
- **waste** / waste.top_category: finance
- **waste** / waste.potential_savings: 1872000
```

### GOOD (post-fix prompt input)
```
- الهدر المالي: أعلى فئة هدر = finance
- الهدر المالي: الوفورات المحتملة = 1872000
  - الوحدة: عملة
```

### Expected model output
```
1.
الإجراء المقترح:
تعزيز مراجعة المصروفات المالية وفرض ضوابط رقابية على العقود الكبرى.
المبرر:
تشير البيانات إلى تركز الهدر في الشؤون المالية، ما يستدعي تدخلاً فورياً لحماية الهامش التشغيلي.
```

---

## What Was NOT Changed

- Cloud AI provider routing
- Facts Contract structure (engines unchanged)
- Task pipeline order
- Scoring / risk engine logic

---

## Re-validation

Re-run **Generate AI Recommendations** on waste and **Generate Risk AI** after deploy — prompts only affect **new** LLM calls.
