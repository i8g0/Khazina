# Sprint 3 — Executive AI Intelligence Layer

**Date:** 2026-07-17  
**Status:** Completed  
**Source of truth:** `EXECUTIVE_AI_PRECISION_ANALYSIS.md`

---

## Executive Summary

Sprint 3 transforms waste AI from a generic summarizer into an **evidence-driven executive advisor**. Recommendations now require named categories, cited amounts, reporting periods, and structured consulting deliverables. A strict parser rejects hallucinated numbers and forbidden vague phrasing before persistence.

**Single source of truth:** `recommendations.title`, `recommendations.description`, and `source_context.executive` — consumed identically by Frontend, Reports, and PDF.

---

## Architecture

```
Financial Snapshot
    ↓
Waste Engine → WasteFactAssembler (Facts Contract v1.1)
    ↓
DecisionService → Gold DB + runtime_metadata.waste_gold_context
    ↓
AiRecommendationService
    ├─ load_facts_contract (v1.0 | v1.1)
    ├─ build_waste_metadata_supplement (Gold + facts)
    ├─ ContextBuilder → fact_to_prompt_fact (metadata + period preserved)
    ├─ build_evidence_blocks (grouped executive prose)
    ├─ PromptComposer (ar v1.1 — 10-section recommendations)
    ├─ LLM
    ├─ parse_executive_recommendation (10 fields)
    └─ EvidenceRegistry.validate_text → reject hallucinations
    ↓
DB → Frontend / Report / PDF (same stored text)
```

---

## Before / After

| Dimension | Before (Sprint 2) | After (Sprint 3) |
|-----------|-------------------|------------------|
| Category in prompt | `مبلغ الفئة = 1075000` (no name) | `الشؤون المالية: 1,075,000 ريال (45.9%)` |
| Period | Dropped in adapter | `الربع الثاني 2026` in evidence blocks |
| Gold data (dept/vendor) | Reports only | `waste_gold_context` + AI supplement |
| Prompt rule | "لا تكرر الأرقام خاماً" | Mandatory numeric citation |
| Recommendation shape | 7 fields (action/why/…) | 10 fields (problem/evidence/…/KPI) |
| Parser | Format only | Evidence validation + forbidden phrases |
| Facts Contract | v1.0, 11 metrics | v1.1, 16 metrics + executive_context extension |

---

## Part 1 — Facts Contract v1.1

**File:** `backend/app/business/assemblers/waste.py`, `business/facts/contract.py`

### New metrics

| Metric | Purpose |
|--------|---------|
| `waste.reporting_period` | Explicit period fact |
| `waste.category_count` | Number of waste categories |
| `waste.currency` | SAR |
| `waste.evidence_source` | Snapshot source dataset |
| `waste.financial_impact` | Alias of total waste (executive framing) |
| `waste.savings_opportunity` | Alias of potential savings |

### Enriched metadata

Every category fact now includes:

- `category_name` (code)
- `category_label_ar` (Arabic display name)

### Extensions

```json
"executive_context": {
  "reporting_period_label": "2026-Q2",
  "organization_id": "…",
  "category_count": 3,
  "top_driver": "الشؤون المالية"
}
```

### Backward compatibility

- Loaders accept **both** `1.0` and `1.1` (`SUPPORTED_CONTRACT_VERSIONS`)
- Old runs rehydrate without migration
- Risk / Scenario engines unchanged

### Fields documented as impossible (no ingest/schema)

| Field | Reason |
|-------|--------|
| Invoice | Not in snapshot ingest or DB |
| Cost center | Not in schema |
| Business unit | Not in schema |
| Budget owner | Not in schema |
| Largest transactions | No line-item ingest |

---

## Part 2 — Prompt Builder / Evidence Blocks

**Files:** `presentation/metric_labels.py`, `ai/prompts/builder.py`, `ai/context/adapter.py`

- `PromptFact` extended with `period`, `organization_id`, `metadata`
- `build_evidence_blocks()` groups waste facts by category
- No raw `waste.xxx` or snake_case exposed to LLM
- Currency formatted as Arabic executive prose (`1.07 مليون ريال`)

---

## Part 3 — Prompts (ar v1.1)

**File:** `ai/prompts/languages/ar.py`, `ai/prompts/version.py`

### Recommendation structure (10 sections)

1. المشكلة  
2. الأدلة  
3. الأثر على الأعمال  
4. السبب الجذري  
5. التوصية التنفيذية  
6. الأولوية  
7. المسؤول  
8. الإطار الزمني  
9. الوفورات المتوقعة  
10. مؤشر النجاح  

### Forbidden phrases (system + validator)

تشير البيانات، قد يكون، ربما، يمكن، من الممكن، High/Low/Medium category, The data suggests, …

---

## Part 4 — Strict Evidence Mode

Example target output:

> خلال **الربع الثاني 2026**، بلغ الهدر في فئة **الشؤون المالية** **1,075,000 ريال** ويمثل **45.9%** من إجمالي الهدر **2,340,000 ريال**.

---

## Part 5 — Parser Validation

**Files:** `presentation/evidence_registry.py`, `ai_recommendations/evidence_validator.py`

Rejects recommendations when:

- Forbidden vague phrases detected
- No category name from facts referenced
- No numeric evidence (amounts ≥ 1,000 or waste %)
- Amounts/percentages not traceable to Facts Contract
- Evidence section empty after parse
- Text too short (< 80 chars)

KPI percentages (≤ 20%) and calendar years (1900–2100) are excluded from strict numeric matching.

---

## Part 6 — Executive Quality

Prompts require **WHY** via `السبب الجذري` and evidence-bound `الأدلة`. Owner defaults to Gold department mapping or `غير محدد في البيانات` — not invented from template examples.

---

## Part 7 — Frontend

**Files:** `frontend/lib/format.ts`, `components/ui/recommendation-card.tsx`, `components/waste/waste-page.tsx`

- Same card layout; content enriched with **الأدلة**, **لماذا**, problem line
- Parses 10-field executive object from `source_context.executive`
- Readable in < 15 seconds per card

---

## Part 8 — Reports / PDF

**Files:** `reports/executive_pdf_layout.py`, `reports/facts_loader.py`

- PDF reads same `title` + `description` + `executive` object from DB
- No separate AI generation for reports
- Reports loader accepts Facts Contract v1.0 and v1.1

---

## Part 9 — Backward Compatibility

| Surface | Status |
|---------|--------|
| Risk AI | ✅ Unchanged prompts path |
| Simulation | ✅ Unchanged |
| Reports | ✅ v1.0 + v1.1 load |
| PDF | ✅ Same recommendation source |
| Dashboard API | ✅ Unchanged contracts |
| Existing tests | ✅ 313 passed |

---

## Part 10–11 — Regression

| Check | Result |
|-------|--------|
| Backend pytest | **313 passed** |
| Frontend TypeScript | **Clean** |
| Frontend ESLint | **Clean** (warnings only) |
| Manual workflow | Re-generate AI after deploy — old DB rows retain pre-Sprint-3 text |

### Manual workflow note

After deployment, users must **Regenerate AI** on existing runs to get Sprint 3 recommendations. Waste analysis re-run stores `waste_gold_context` automatically.

---

## Performance

- Evidence block rendering: O(n facts) — negligible
- Supplement build: one Gold query (breakdowns + vendors) per AI generation — same order as before
- Parser validation: in-memory regex — < 1 ms per recommendation
- No additional LLM calls

---

## Key Files Changed

```
backend/app/business/facts/contract.py
backend/app/business/assemblers/waste.py
backend/app/business/engines/waste/manifest.py
backend/app/presentation/metric_labels.py
backend/app/presentation/evidence_registry.py
backend/app/presentation/executive_recommendation.py
backend/app/presentation/waste_category_labels.py
backend/app/ai/context/adapter.py
backend/app/ai/prompts/builder.py
backend/app/ai/prompts/languages/ar.py
backend/app/ai/prompts/version.py
backend/app/ai_recommendations/waste_metadata.py
backend/app/ai_recommendations/evidence_validator.py
backend/app/ai_recommendations/service.py
backend/app/decision/service.py
frontend/lib/format.ts
frontend/components/ui/recommendation-card.tsx
frontend/components/waste/waste-page.tsx
```

---

## Sprint 4

**Not started** — per mission scope.
