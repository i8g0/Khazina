# Sprint 9.5 — Financial Risk AI Intelligence Report

**Sprint:** 9.5 — Financial Risk AI Intelligence  
**Date:** 2026-07-16  
**Status:** Complete  
**Architecture reference:** [PHASE_9_FINANCIAL_RISK_ARCHITECTURE.md](PHASE_9_FINANCIAL_RISK_ARCHITECTURE.md) §5 (AI layer), Sprint 6.4 AI infrastructure

---

## 1. Summary

Sprint 9.5 implements the **AI intelligence layer** for Financial Risk. The AI **explains, summarizes, prioritizes attention, and recommends mitigation** — it never detects, scores, or alters deterministic engine output.

**Principle:** The engine decides. The AI explains.

**Validation:** 287 backend tests passing (11 new risk AI tests). Risk Engine, deterministic scoring, Risk Register (9.4), Waste AI, Simulation, and existing recommendation persistence remain compatible and unchanged.

---

## 2. Architecture Alignment

### Locked constraints (honoured)

| Constraint | Implementation |
|------------|----------------|
| Do not redesign Risk Engine | No changes under `app/business/engines/risk/` |
| Do not modify deterministic scoring | AI prompts explicitly forbid score/category/lifecycle changes |
| Do not redesign Risk Register | No changes to `RiskRegisterService` or register APIs |
| Do not build frontend | Backend-only |
| AI consumes structured facts only | `FactsContract` + `runtime_metadata` dicts — no ORM in prompts |
| Reuse existing AI infrastructure | Extended `AiRecommendationService`, `AiTaskPipeline`, `Recommendation` model |
| No parallel AI system | Single service with domain-specific entry points |

### Data flow

```
Risk Engine (deterministic)
    → DecisionService.execute_risk_analysis()
    → runtime_metadata { facts_contract, risk_analysis, risk_findings, ... }
    → RiskAnalysisService persists Gold (9.3)
    → AiRecommendationService.generate_risk_recommendations()  ← Sprint 9.5
        → load_risk_facts_contract(metadata)
        → build_risk_metadata_supplement(metadata)
        → AiTaskPipeline (5 risk tasks)
        → validate + map + persist
```

If AI output conflicts with engine results, **deterministic results always win**.

---

## 3. AI Architecture

### Entry point

**Service method:** `AiRecommendationService.generate_risk_recommendations()`

**API:** `POST /api/v1/organizations/{organization_id}/ai-recommendations/risk/generate`

| Parameter | Purpose |
|-----------|---------|
| `analysis_run_id` | Completed RISK analysis run |
| `regenerate` | Replace existing risk AI insights (deletes prior RISK-domain recommendations) |

**Auth:** EXECUTIVE+ (same gate as waste AI generation)

### Reused components

| Component | Role |
|-----------|------|
| `AiTaskPipeline` | Task routing, prompt composition, Ollama invocation |
| `AiRecommendationService` | Orchestration, transaction, idempotency, observability |
| `Recommendation` model | Persisted mitigation items with `domain_source=risk` |
| `analysis_runs.runtime_metadata.ai_insights` | Narrative storage (same key as waste; runs are type-separated) |
| `PipelineTimeline` / `log_pipeline_event` | Stage tracking and structured logs |
| `classify_exception` | Error categorization on failure |
| Notification builder | `risk_ai_recommendations_completed` event |

### New risk-domain modules

| Module | Responsibility |
|--------|----------------|
| `risk_constants.py` | Task order, narrative keys, recommendation categories |
| `risk_metadata.py` | Deterministic context supplement from metadata dict |
| `facts_loader.load_risk_facts_contract()` | Rehydrate Facts Contract with `engine_id=risk` |
| `risk_validator.py` | Ensure all 5 tasks returned non-empty output |
| `risk_mapper.py` | Build `ai_insights` payload + recommendation rows |
| `risk_recommendation_parser.py` | Parse categorized mitigation text |

---

## 4. AI Tasks

Five dedicated `PromptTask` values (distinct from legacy waste-context `RISK_ANALYSIS`):

| Task | Narrative key | Purpose |
|------|---------------|---------|
| `RISK_EXECUTIVE_SUMMARY` | `risk_executive_summary` | Executive overview, top findings, business/financial/operational impact |
| `RISK_EXECUTIVE_BRIEF` | `risk_executive_brief` | Short C-suite brief — what needs attention now |
| `RISK_EXPLANATION` | `risk_explanation` | Why risks were detected; links to facts — no rescoring |
| `RISK_MITIGATION_OPTIONS` | `risk_mitigation_options` | Categorized actionable recommendations (also parsed into DB rows) |
| `RISK_BOARD_REPORT` | `risk_board_report` | Board-ready summary |

**Execution order:**

```
RISK_EXECUTIVE_SUMMARY → RISK_EXECUTIVE_BRIEF → RISK_EXPLANATION
    → RISK_MITIGATION_OPTIONS → RISK_BOARD_REPORT
```

**Not in scope:** scoring, detection, lifecycle changes, register promotion.

---

## 5. Prompt Strategy

### Inputs (only)

1. **Facts Contract** — rehydrated from `runtime_metadata.facts_contract` (`engine_id=risk`)
2. **Risk metadata supplement** — built from plain dict fields:
   - `risk_analysis` — posture, counts, liquidity, waste %, top category
   - `risk_findings` — top findings with scores, priorities, detection rules
   - `risk_register_context` — optional register metadata when present

### Explicit prohibitions (in every risk prompt)

- Do not modify scores, categories, priorities, or lifecycle states
- Do not invent risks absent from deterministic context
- Do not recalculate or probabilistically score

### Language

Arabic templates in `app/ai/prompts/languages/ar.py` for all five tasks.

### Pipeline extension

`AiTaskPipeline.execute_task()` accepts optional `prompt_supplement` appended to the user message after facts context — shared mechanism, no duplicate prompt engine.

### Context builder

Risk domain tasks receive severity-prioritized fact selection via `_RISK_DOMAIN_TASKS` in `app/ai/context/builder.py`.

---

## 6. Recommendation Model

`RISK_MITIGATION_OPTIONS` output is parsed into structured `Recommendation` rows.

### Categories

| Arabic label | Code |
|--------------|------|
| إجراءات فورية | `immediate_action` |
| إجراءات المراقبة | `monitoring_action` |
| ضوابط مالية | `financial_control` |
| ضوابط تشغيلية | `operational_control` |
| حوكمة | `governance` |
| امتثال | `compliance` |

### Separation from deterministic findings

Each recommendation `source_context` includes:

- `deterministic_source: true` — marks AI-generated advisory content
- `recommendation_category` — mitigation type
- `traceability` — links back to analysis run, Gold result, findings
- `task` / `prompt_task` — `risk_mitigation_options`
- Facts contract version and engine metadata

Recommendations are **advisory**; they do not create register entries or alter finding status.

### Count bounds

Parser enforces 3–8 items; prompts require exactly 5 structured items.

---

## 7. Persistence & Traceability

### AI insights (`runtime_metadata.ai_insights`)

```json
{
  "domain": "risk",
  "generated_at": "...",
  "model": "...",
  "prompt_version": "...",
  "tasks_executed": ["risk_executive_summary", "..."],
  "facts_contract_version": "...",
  "engine_id": "risk",
  "narrative": { "...": { "text", "model", "generated_at", ... } },
  "traceability": {
    "analysis_run_id": "...",
    "risk_analysis_result_id": "...",
    "source_snapshot_id": "...",
    "finding_ids": ["..."],
    "promoted_risk_ids": ["..."]
  },
  "risk_executive_summary": "...",
  "risk_executive_brief": "...",
  "risk_explanation": "...",
  "risk_mitigation_options": "...",
  "risk_board_report": "..."
}
```

### Traceability references

| Entity | Source |
|--------|--------|
| `AnalysisRun` | Run ID from request + ownership check |
| `RiskAnalysisResult` | `RiskAnalysisRepository.get_result_for_run()` |
| `RiskFinding` | DB findings or `runtime_metadata.risk_findings` fallback |
| Enterprise Risk | `promoted_risk_ids` when findings were promoted |

### Idempotency

Generation blocked if `ai_insights` already exists unless `regenerate=true`. Regeneration deletes existing `domain_source=risk` recommendations for the run.

---

## 8. Observability

Integrated into existing framework:

| Signal | Detail |
|--------|--------|
| **Timeline** | `AI_STARTED` → `AI_COMPLETED` (or failed) appended to `pipeline_timeline` |
| **Structured logs** | `pipeline_stage` events with `domain=risk`, duration, recommendation count |
| **Error classification** | `classify_exception()` on failure; timeline stage marked failed |
| **Notifications** | `KIND_RISK_AI_RECOMMENDATIONS_COMPLETED` materialized on success |
| **Health** | Reuses Ollama client health from existing AI stack |

---

## 9. Tests

| File | Coverage |
|------|----------|
| `tests/ai_recommendations/risk_conftest.py` | Sample risk facts, mock Ollama by task |
| `tests/ai_recommendations/test_risk_facts_loader.py` | Facts rehydration, engine_id guard |
| `tests/ai_recommendations/test_risk_metadata.py` | Metadata supplement from dict |
| `tests/ai_recommendations/test_risk_recommendation_parser.py` | Category extraction |
| `tests/ai_recommendations/test_risk_ai_service.py` | Full orchestration, guards, task order, idempotency |
| `tests/api/test_risk_ai_api.py` | Route registration |

**Verified behaviours:**

- Facts → AI pipeline (mocked Ollama)
- Prompt supplement generation
- Five-task execution order
- Recommendation persistence with `domain_source=risk`
- Rejection of non-RISK runs and runs without Gold result
- Idempotency guard
- Failure path raises after timeline update (existing pattern)

**Full suite:** `287 passed`

**Regression:** Waste AI tests unchanged; optional `risk_analysis_repository` on service constructor defaults to `None` (waste path unaffected).

---

## 10. Files Created / Modified

### New

- `backend/app/ai_recommendations/risk_constants.py`
- `backend/app/ai_recommendations/risk_metadata.py`
- `backend/app/ai_recommendations/risk_validator.py`
- `backend/app/ai_recommendations/risk_mapper.py`
- `backend/app/ai_recommendations/risk_recommendation_parser.py`
- `backend/tests/ai_recommendations/risk_conftest.py`
- `backend/tests/ai_recommendations/test_risk_facts_loader.py`
- `backend/tests/ai_recommendations/test_risk_metadata.py`
- `backend/tests/ai_recommendations/test_risk_recommendation_parser.py`
- `backend/tests/ai_recommendations/test_risk_ai_service.py`
- `backend/tests/api/test_risk_ai_api.py`
- `docs/SPRINT_9_5_RISK_AI_REPORT.md`

### Modified (AI layer only — no engine/register changes)

- `backend/app/ai/prompts/tasks.py` — five new PromptTask values
- `backend/app/ai/prompts/languages/ar.py` — risk prompt templates
- `backend/app/ai/context/builder.py` — risk domain fact prioritization
- `backend/app/ai_recommendations/facts_loader.py` — `load_risk_facts_contract()`
- `backend/app/ai_recommendations/pipeline.py` — `prompt_supplement` parameter
- `backend/app/ai_recommendations/service.py` — `generate_risk_recommendations()`
- `backend/app/api/v1/ai_recommendations.py` — risk generate endpoint
- `backend/app/api/deps.py` — wire `RiskAnalysisRepository`
- `backend/app/schemas/ai_recommendations.py` — risk request/response schemas
- `backend/app/notifications/builder.py` — risk AI completion notification
- `backend/app/notifications/constants.py` — notification kind
- `backend/app/settings/constants.py` — default notification kind

### Unchanged (validated)

- `app/business/engines/risk/` — Risk Engine
- `app/services/risk_register.py` — Enterprise Risk Register
- `app/decision/service.py` — deterministic orchestration
- Waste AI task order and `PromptTask.RISK_ANALYSIS` (waste-context only)
- Simulation module
- Alembic head — `f9c2d7a31b44` (no new migration required)

---

## 11. Definition of Done Checklist

| Criterion | Status |
|-----------|--------|
| Risk AI Service implemented | ✅ `generate_risk_recommendations()` |
| New Risk AI tasks implemented | ✅ 5 dedicated PromptTasks |
| Dedicated prompt templates | ✅ Arabic templates in `ar.py` |
| AI explanations from Facts only | ✅ Facts Contract + metadata dict |
| Recommendations persisted | ✅ `Recommendation` rows with categories |
| Full traceability preserved | ✅ `traceability` block on insights + source_context |
| Existing AI architecture reused | ✅ Single service + pipeline |
| Backend tests pass | ✅ 287 passed |
| No frontend changes | ✅ |

---

## 12. Remaining Work — Sprint 9.6

Suggested follow-ups (not in 9.5 scope):

1. **Integration tests with live Ollama** — optional E2E against real model output quality
2. **Register context enrichment** — populate `risk_register_context` in metadata when promoted risks exist for the run
3. **Read APIs** — dedicated GET endpoints for risk AI insights (currently stored in run metadata; may reuse existing analysis run detail)
4. **English prompt templates** — if multi-language org settings expand beyond Arabic
5. **Recommendation workflow** — executive accept/dismiss actions on risk AI recommendations (governance layer)
6. **Dashboard hooks** — wire risk AI narratives into reporting/export pipelines (backend only, no new pages in 9.6 unless chartered)
7. **Validator hardening** — assert mitigation parser categories cover all six types when model output varies

---

## 13. API Quick Reference

```
POST /api/v1/organizations/{organization_id}/ai-recommendations/risk/generate
Authorization: Bearer <token> (EXECUTIVE+)

{
  "analysis_run_id": "uuid",
  "regenerate": false
}
```

**Preconditions:**

- Analysis run `analysis_type = risk`
- Analysis run `status = completed`
- Gold `risk_analysis_results` row exists
- `runtime_metadata.facts_contract` with `engine_id = risk`

**Response:** analysis run (updated metadata), `ai_insights`, `recommendations[]`, `traceability`.
