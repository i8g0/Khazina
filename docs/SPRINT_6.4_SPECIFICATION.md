# Sprint 6.4 — AI Recommendations

**Phase:** 6 — Business Features  
**Predecessor:** Sprint 6.3 — Decision Engine — **Complete and approved**  
**Status:** **APPROVED FOR IMPLEMENTATION** (Technical Lead review, 2026-07-15)  
**Date:** 2026-07-15  

**Normative references (frozen — must not be modified in this sprint):**

- [ADR 008: AI Architecture](ADR/008-ai-architecture.md)
- [ADR 009: Business Engine Architecture](ADR/009-business-engine-architecture.md)
- [ADR 010: Financial Snapshot Architecture](ADR/010-financial-snapshot-architecture.md)
- [AI_FREEZE.md](AI_FREEZE.md)
- [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md)
- [BUSINESS_ENGINE_ARCHITECTURE.md](BUSINESS_ENGINE_ARCHITECTURE.md)
- [SPRINT_6.3_SPECIFICATION.md](SPRINT_6.3_SPECIFICATION.md)
- [DATABASE_SCHEMA_DESIGN.md](DATABASE_SCHEMA_DESIGN.md) — §4.24 `recommendations`
- [BUSINESS_DOMAIN_DISCOVERY.md](BUSINESS_DOMAIN_DISCOVERY.md) §5.7, §6.1 Flow 2

**Tracker alignment:** `progress.md` (post–Sprint 6.3): *“Next step: AI orchestration wired to completed run Facts.”* Sprint 6.3 §3.2 E-02 explicitly deferred Facts → narrative and recommendations to this sprint class of work.

---

## Terminology Mapping (Repository Authority)

| Sprint 6.4 term | Repository authority | Meaning |
|---|---|---|
| **AI Recommendations** | *Sprint 6.4 product name* | Post-decision AI layer that consumes persisted Facts and produces executive narrative + registered recommendations |
| **AI Recommendation Service** | *Sprint 6.4 service name* | Orchestrates recommendation generation only — **does not perform business analysis**; composes frozen AI components against completed Facts |
| **Decision Results** | Gold layer from Sprint 6.3 | Completed `analysis_runs` + domain outcomes (`waste_analysis_results`, breakdowns) + snapshot provenance |
| **Facts Contract** | `FactsContract` — `backend/app/business/facts/contract.py` | Sole AI input (`CONTRACT_VERSION = "1.0"`) — never snapshots, never raw spreadsheets |
| **Structured AI Response** | `ParsedResponse` — `backend/app/ai/parsers/response_parser.py` | Deterministic parse output from LLM text/JSON |
| **Recommendations (persisted)** | `recommendations` table + `RecommendationService` | Centralized recommendation registry (DD-03) |

**Critical constraint:** The frozen **`AiOrchestrator`** (`backend/app/ai/services/orchestrator.py`) **re-executes** `engine.run(request.engine_input)`. Sprint 6.4 must **not** use that path for production recommendations. The **AI Recommendation Service** composes frozen AI components against **already-persisted Facts** from completed decision runs — without modifying frozen AI modules. Business analysis is complete before this service runs (Sprint 6.3).

---

## 1. Sprint Goal

Sprint 6.4 delivers the **first production AI interpretation path** connected to the completed business pipeline:

> **Completed waste decision run (Gold) → rehydrated Facts Contract → Context Builder → Prompt Engine → LLM → Structured AI Response → persisted executive insights and recommendations.**

After this sprint:

- A **completed** `financial_waste` analysis run (Sprint 6.3 output) can trigger **Arabic executive AI interpretation** grounded exclusively in its persisted Facts Contract.
- **Recommendations** are registered in the centralized `recommendations` table, linked to the source `analysis_run_id`, with AI provenance in `source_context`.
- **Executive summary, risk explanation, and supporting narrative** are retrievable artifacts tied to the analysis run — not placeholder frontend data.
- **No Business Engine re-execution**, **no snapshot access**, and **no LLM calculations** occur in this path.
- Frozen Phase 5 AI components are **composed**, not redesigned.

Sprint 6.4 does **not** deliver frontend wiring, reports, **Number Guard** (deferred — see §3.3), or AI for risk/simulation domains.

---

## 2. Business Objective

### Capability unlocked

Executives gain **AI-assisted actionable insights** grounded in auditable deterministic analysis:

| Before Sprint 6.4 | After Sprint 6.4 |
|---|---|
| AI pipeline validated in isolation (Phase 5); orchestrator accepts manual engine input | AI consumes **persisted Facts** from completed decision runs |
| Recommendations are static placeholder data (`BUSINESS_DOMAIN_DISCOVERY.md` §5.7) | Recommendations are **registered from LLM output** via `RecommendationService` |
| Waste page “AI findings” and Dashboard top-3 recs are UI-only | Backend produces **real recommendation rows** linkable to analysis runs |
| Sprint 6.3 stores `facts_contract` in run `runtime_metadata` | Facts become the **mandatory AI input** for interpretation |
| No executive narrative tied to analysis runs | Executive summary and risk explanation stored as **run-scoped AI artifacts** |

### Business value

Per `AI_ARCHITECTURE.md` §2 and platform identity (*Enterprise Financial Decision Intelligence Platform*):

- **Deterministic before probabilistic:** Waste metrics are fixed before any LLM invocation.
- **Facts before language:** AI explains decisions already made — it does not recalculate them.
- **Auditability:** Provenance chain extends: file → snapshot → analysis → facts → AI output → recommendations.

Sprint 6.4 closes the gap noted in Phase 5 (`progress.md` Sprint 5.3B next step: *“Wire Facts Contract to orchestration”*) at the **production integration layer**, without unfreezing AI architecture.

### Alignment with discovery

`BUSINESS_DOMAIN_DISCOVERY.md` §5.7 — *AI-Assisted Recommendations* cross-cutting concept — becomes operational at the **backend registry layer** for the **waste domain** first. Dashboard/Waste/Risk/Simulation UI consumption remains Phase 7.

---

## 3. Scope

### 3.1 INCLUDED (strict)

| # | Item | Evidence basis |
|---|---|---|
| I-01 | **AI Recommendation Service** — orchestrates frozen AI components against persisted Facts; **no business analysis** | `AiOrchestrator` re-runs engine (unsuitable); Sprint 6.4 integration gap |
| I-02 | **Facts rehydration** from completed `analysis_runs.runtime_metadata.facts_contract` | Sprint 6.3 `DecisionService` stores on `complete_run` |
| I-03 | **Precondition enforcement** — run `completed`, type `financial_waste`, Facts present, org scope | `AnalysisService`; Sprint 6.3 lifecycle |
| I-04 | **Context Builder** invocation with frozen `ContextBuildOptions` | `backend/app/ai/context/builder.py`; `AI_FREEZE.md` |
| I-05 | **Prompt Engine** invocation for approved tasks via frozen `PromptComposer` | `PromptTask`: `EXECUTIVE_SUMMARY`, `RECOMMENDATIONS`, `RISK_ANALYSIS` (`tasks.py`) |
| I-06 | **LLM invocation** via frozen `OllamaClient` | `AI_FREEZE.md` production config (`qwen3.5:2b`, thinking disabled) |
| I-07 | **Response Parser** for structured AI output | `backend/app/ai/parsers/response_parser.py` |
| I-08 | **Executive Summary** generation (`PromptTask.EXECUTIVE_SUMMARY`) | Arabic template in `ar.py` |
| I-09 | **Recommendations** generation (`PromptTask.RECOMMENDATIONS`) + persistence | `RecommendationService.register_recommendation()` |
| I-10 | **Risk Explanation** generation (`PromptTask.RISK_ANALYSIS`) from waste severity facts | Template exists; waste facts include `waste.overall_level`, `waste.category_level` |
| I-11 | **Supporting narrative** — persisted parsed LLM artifacts per task | `ParsedResponse`; provenance for audit |
| I-12 | **Recommendation registry mapping** — LLM output → `recommendations` rows (`domain_source = waste`) | `RecommendationDomain.WASTE`; exclusive-source FK rule |
| I-13 | **`source_context` population** — model, prompt version, task, timestamps | `DATABASE_SCHEMA_DESIGN.md` §11 — `source_context` JSONB |
| I-14 | **Gold cross-check (read-only)** — verify run has `waste_analysis_results` before AI | Sprint 6.3 Gold persistence; not passed to LLM |
| I-15 | **Snapshot provenance preserved** — AI path reads run metadata only; never snapshot payload | ADR-010 §11.10; ADR-008 |
| I-16 | **Organization + reporting period context** in prompts via Facts metadata and run scope | Facts carry `organization_id`, `period`; run carries `reporting_period_id` |
| I-17 | **Idempotency guard** — prevent duplicate AI generation for same run unless explicit regenerate | Avoid duplicate recommendation rows |
| I-18 | **Automated tests** — mocked Ollama, Facts-only input verification, recommendation mapping, business-layer isolation | Phase 5 test patterns (`tests/ai/`) |
| I-19 | **AI isolation verification** — AI Recommendation Service must not import or invoke Business Engine execution | ADR-009 |

### 3.2 EXCLUDED (strict)

| # | Item | Deferred to | Evidence |
|---|---|---|---|
| E-01 | **Modification of frozen AI modules** — Orchestrator, Prompt Engine, Context Builder, Parser, Ollama client internals | Forbidden without ADR | `AI_FREEZE.md` §4 |
| E-02 | **Business Engine re-execution** | Forbidden — Sprint 6.3 owns calculation | `AiOrchestrator.execute()` pattern |
| E-03 | **Financial Snapshot / Bronze access by AI** | Forbidden permanently | ADR-010 §11.10 |
| E-04 | **LLM calculations or new metrics** | Forbidden permanently | `AI_ARCHITECTURE.md` §12 |
| E-05 | **Number Guard** | **Out of scope — future hardening sprint** (§3.3) | `AI_FREEZE.md` §4 deferred; `AI_ARCHITECTURE.md` §13 normative but not implemented in Phase 5 |
| E-06 | **Response Validation / regeneration loop** | Separate sprint | `AI_FREEZE.md` §4 deferred |
| E-07 | **Persistent conversation storage** | Post-MVP | In-memory `ConversationService` only |
| E-08 | **`PromptTask.SCENARIO_ANALYSIS`** | Simulation sprint | No simulation facts pipeline |
| E-09 | **Risk / Simulation domain AI** | Future domain sprints | Only `financial_waste` runs in scope |
| E-10 | **Frontend Dashboard/Waste recommendation cards** | Phase 7 | `PROJECT_ROADMAP.md` Phase 7 |
| E-11 | **Report generation / PDF export** | Phase 8 | `DATABASE_SCHEMA_DESIGN.md` reports |
| E-12 | **New Business Engines or Financial Engine** | Future engine sprints | `AI_FREEZE.md` §5 |
| E-13 | **Cloud LLM providers** | Not in repository | Local Ollama only |
| E-14 | **Department assignment on recommendations** | Deferred (Sprint 6.3 E-08) | Waste breakdowns lack department linkage |
| E-15 | **Dashboard featuring automation** | Optional manual via existing API | `feature_on_dashboard` endpoint exists |
| E-16 | **Multi-analysis batch AI** | Future sprint | Single run per invocation |

### 3.3 Future hardening — Number Guard (explicitly out of scope)

Sprint 6.4 **does not implement** Number Guard (`AI_ARCHITECTURE.md` §13). This is a **documented deferral**, not a sprint expansion item.

| Aspect | Rule |
|---|---|
| **Sprint 6.4 scope** | Number Guard is **excluded** — no additive module, no partial implementation |
| **Compensating control** | AC-20 — `estimated_savings_amount` on recommendations must exactly match an existing fact value; never LLM-invented |
| **Known limitation** | LLM numeric output in narrative fields is **not verified** against facts in Sprint 6.4 |
| **Future sprint** | Dedicated **Number Guard hardening** sprint — additive verification layer per `AI_ARCHITECTURE.md` §13; accepts, rejects, or requests regeneration; never corrects output |
| **Prerequisite for production hardening** | ADR or TL approval if implementation touches frozen AI modules |

Sprint 6.4 must **not** expand scope to absorb Number Guard responsibilities.

---

## 4. Inputs

### 4.1 Facts Contract (primary — sole LLM grounding)

**Source:** `analysis_runs.runtime_metadata.facts_contract` — persisted by Sprint 6.3 on successful waste decision completion.

| Field | Requirement |
|---|---|
| `contract_version` | Must equal `"1.0"` (`CONTRACT_VERSION`) |
| `engine_id` | Must be `"waste"` for Sprint 6.4 scope |
| `engine_version` | Recorded for provenance; must match run’s engine execution |
| `facts[]` | Rehydrated via `FactsContract.from_dict()` |
| Immutability | Read-only; AI must not mutate or supplement with calculated facts |

**Rehydration failure** (missing, malformed, version mismatch) → AI invocation **rejected**; no LLM call.

**Explicit prohibition:** AI must **not** receive snapshot payload, Bronze files, `waste_analysis_results` rows, or raw Gold tables as prompt input. Gold existence is a **precondition check only**.

### 4.2 Decision Results (preconditions and provenance — not prompt body)

| Input element | Source | Role |
|---|---|---|
| **Analysis run** | `analysis_runs` | Must be `status = completed`, `analysis_type = financial_waste` |
| **Snapshot provenance** | `source_snapshot_id`, `runtime_metadata.snapshot_version` | Audit context in `source_context`; not LLM input |
| **Gold waste result** | `waste_analysis_results` (+ breakdowns) | Precondition: proves decision path completed; optional cross-check against facts metrics |
| **Source file reference** | `source_file_id` | Provenance only |

### 4.3 Organization context

| Element | Source |
|---|---|
| `organization_id` | Run scope + membership authorization |
| Organization identity | Organization record (name available for prompt enrichment if approved — must not replace Facts) |
| Authorization | Existing org role model (`RequireOrgExecutive` / analyst read patterns) |

### 4.4 Reporting period

| Element | Source |
|---|---|
| `reporting_period_id` | From `analysis_runs.reporting_period_id` or snapshot binding |
| Period label | `reporting_periods.label` — may enrich prompt metadata; Facts `period` field is authoritative for metrics |

### 4.5 Frozen AI configuration (implicit inputs)

Per `AI_FREEZE.md`:

| Setting | Value |
|---|---|
| Model | `qwen3.5:2b` (`OLLAMA_MODEL`) |
| Thinking | Disabled |
| Default language | Arabic (`ar`) |
| Prompt version | `1.0` |
| Production timeout | 180s |

---

## 5. Outputs

### 5.1 Produced artifacts

| Output | Description | Persistence target (conceptual) |
|---|---|---|
| **Executive Summary** | Arabic executive narrative from `EXECUTIVE_SUMMARY` task | Run-scoped AI insights artifact (see §11) |
| **Recommendations** | 3–6 actionable items from `RECOMMENDATIONS` task | `recommendations` rows via `RecommendationService` |
| **Risk Explanation** | Severity interpretation from `RISK_ANALYSIS` task | Run-scoped AI insights artifact |
| **Supporting narrative** | Raw/parsed LLM text per task (`ParsedResponse`) | Run-scoped AI insights artifact + `source_context` on recommendations |
| **Structured AI Response** | Parser output (`format`, `text`, `data`) | Embedded in insights artifact for audit |
| **Provenance record** | Model, prompt version, task list, timestamps, conversation id | `recommendations.source_context`; run `runtime_metadata` |

**Recommendation row mapping (conceptual minimum per row):**

| Field | Derivation |
|---|---|
| `domain_source` | `waste` (`RecommendationDomain.WASTE`) |
| `title` | From parsed recommendation item |
| `description` | From parsed recommendation item (action + rationale) |
| `priority` | Mapped to `high` / `medium` (`RecommendationPriority`) — mapping rules in §11 |
| `confidence_label` | Optional; only if present in LLM output and traceable to fact confidence fields |
| `estimated_savings_amount` | Optional; **only** if value matches an existing fact (e.g. `waste.potential_savings`) — no new numbers |
| `analysis_run_id` | Source run FK |
| `source_context` | AI provenance blob |

### 5.2 Intentionally NOT produced

| Excluded output | Reason |
|---|---|
| New calculated KPIs or waste totals | Business Engine responsibility |
| Modified Facts Contract | Immutability |
| Snapshot or file content in AI storage | ADR-010 boundary |
| Risk register entries | Risk domain out of scope |
| Simulation outputs | Simulation out of scope |
| Reports / PDFs | Reporting sprint |
| Frontend-formatted DTOs | Phase 7 |
| Regenerated Business Engine results | Sprint 6.3 owns decision path |
| Number Guard | **Out of scope** — future hardening sprint (§3.3) |

---

## 6. Processing Flow

**Sprint 6.4 pipeline:**

```
Decision Results (completed analysis_run + Gold waste results + snapshot provenance)
        ↓
Facts Contract (rehydrated from runtime_metadata — read-only)
        ↓
Context Builder (frozen — fact selection and ordering)
        ↓
Prompt Engine (frozen — EXECUTIVE_SUMMARY | RECOMMENDATIONS | RISK_ANALYSIS)
        ↓
LLM (Ollama — frozen client)
        ↓
Response Parser (frozen — Structured AI Response)
        ↓
AI Response Mapper → Executive insights artifact + Recommendation registry rows
```

**Detailed steps:**

| Step | Actor | Action |
|---|---|---|
| 1 | AI Recommendation Service | Validate org, run completed, type `financial_waste`, Gold result exists |
| 2 | AI Recommendation Service | Load and rehydrate `FactsContract` from run metadata |
| 3 | AI Recommendation Service | Verify no prior AI artifacts (unless regenerate flag) |
| 4 | Context Builder | Build `PromptContext` per task with `domain="waste"` |
| 5 | Prompt Composer | Compose system + user prompts (Arabic default) |
| 6 | Ollama Client | Invoke LLM per task (sequential — 3 tasks in Sprint 6.4) |
| 7 | Response Parser | Parse each response to `ParsedResponse` |
| 8 | AI Response Mapper | Map RECOMMENDATIONS output → `register_recommendation()` calls |
| 9 | AI Recommendation Service | Persist executive summary, risk explanation, narratives on run |
| 10 | AI Recommendation Service | Record AI completion metadata on run |
| **Failure** | Service | No partial recommendation persistence unless TL approves compensating transaction rules in §11 |

**Position in platform pipeline (ADR-010):**

```
Bronze → Silver → Decision Engine (6.3) → Gold → [Sprint 6.4 AI] → Recommendations / Insights → [Future] Frontend
```

---

## 7. Deliverables

| # | Deliverable | Description |
|---|---|---|
| D-01 | **Sprint 6.4 Specification (this document)** | Approved before implementation |
| D-02 | **AI Response Mapping Contract (§11)** | Normative mapping from `ParsedResponse` → recommendations + insights — **implementation gate** |
| D-03 | **AI Recommendation Service** | New module composing frozen AI components; **does not modify** `AiOrchestrator`; **does not perform business analysis** |
| D-04 | **Facts rehydration adapter** | `FactsContract.from_dict()` with validation |
| D-05 | **AI Response Mapper** | RECOMMENDATIONS → `RecommendationService` payloads; task narratives → insights artifact |
| D-06 | **Run AI insights persistence design** | TL-approved storage for executive summary / risk explanation (§11) |
| D-07 | **Execution entry point** | API or service method to trigger AI generation for a completed waste run |
| D-08 | **Idempotency / regenerate policy** | Documented and enforced |
| D-09 | **Automated test suite** | Mocked Ollama; Facts-only verification; mapper tests; no engine re-run test |
| D-10 | **Business-engine isolation test** | AI Recommendation Service module graph excludes `engine.run()` |
| D-11 | **Facts-only input test** | Assert prompts contain fact values; no snapshot/Gold SQL in AI path |
| D-12 | **`progress.md` update** | Sprint 6.4 completion record |

**Explicit non-deliverables:** Modifications to frozen `app/ai/` or `app/business/` internals; **Number Guard** (§3.3); frontend changes; report generation.

---

## 8. Acceptance Criteria

Sprint 6.4 is **complete only when every criterion passes** Technical Lead review.

### 8.1 Preconditions

| ID | Criterion |
|---|---|
| AC-01 | AI generation rejected when analysis run `status` ≠ `completed` |
| AC-02 | AI generation rejected when `analysis_type` ≠ `financial_waste` |
| AC-03 | AI generation rejected when `runtime_metadata.facts_contract` is missing or invalid |
| AC-04 | AI generation rejected when org scope does not match run ownership |
| AC-05 | AI generation rejected when `waste_analysis_results` row missing for run |

### 8.2 Facts-only input

| ID | Criterion |
|---|---|
| AC-06 | LLM prompts built exclusively from Context Builder output derived from rehydrated Facts Contract |
| AC-07 | No Financial Snapshot payload, Bronze bytes, or Gold table rows injected into prompts |
| AC-08 | `BusinessEngine.run()` is **not** invoked during AI generation |
| AC-09 | Rehydrated contract has `contract_version = "1.0"` and `engine_id = "waste"` |

### 8.3 AI pipeline (frozen components)

| ID | Criterion |
|---|---|
| AC-10 | Context Builder, Prompt Composer, Ollama Client, Response Parser used without source modification |
| AC-11 | Three tasks execute successfully: `EXECUTIVE_SUMMARY`, `RECOMMENDATIONS`, `RISK_ANALYSIS` |
| AC-12 | Default prompt language is Arabic (`ar`) per `AI_FREEZE.md` |
| AC-13 | Parsed responses are non-empty for successful LLM calls |

### 8.4 Outputs and persistence

| ID | Criterion |
|---|---|
| AC-14 | Executive summary retrievable from run-scoped AI insights artifact |
| AC-15 | Risk explanation retrievable from run-scoped AI insights artifact |
| AC-16 | ≥1 and ≤6 recommendation rows persisted per successful generation |
| AC-17 | Each recommendation has `domain_source = waste` and `analysis_run_id` = source run |
| AC-18 | Each recommendation `source_context` includes model id and prompt version |
| AC-19 | Duplicate generation without regenerate flag is rejected |
| AC-20 | `estimated_savings_amount` on recommendations, if set, matches a fact value exactly — never LLM-invented |

### 8.5 Isolation and regression

| ID | Criterion |
|---|---|
| AC-21 | AI Recommendation Service module graph does not import `app.business.engines` for execution |
| AC-22 | Full backend test suite passes with Sprint 6.4 tests included |
| AC-23 | Ollama unreachable → graceful failure with no orphan recommendation rows |

### 8.6 Documentation

| ID | Criterion |
|---|---|
| AC-24 | `progress.md` records Sprint 6.4 completion and next step |
| AC-25 | §11 AI Response Mapping Contract marked **Approved** before implementation began |

---

## 9. Technical Risks

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R-01 | **Number Guard deferred** — `AI_ARCHITECTURE.md` §13 not implemented; **out of scope for Sprint 6.4** | LLM may emit untraceable numbers in narrative fields | Documented limitation (§3.3); AC-20 for savings amounts; future Number Guard hardening sprint |
| R-02 | **AiOrchestrator unsuitable** — re-runs engine | Accidental use breaks determinism / doubles computation | AI Recommendation Service; AC-08; code review gate |
| R-03 | **RECOMMENDATIONS template is prose, not JSON** — mapper ambiguity | Fragile recommendation extraction | §11 mapping contract with fallback failure semantics |
| R-04 | **Arabic LLM output variability** | Inconsistent recommendation count/quality | Sequential tasks; parser tests; mocked + live smoke |
| R-05 | **Ollama availability** | AI generation fails in demo | AC-23; health check exists (`GET /ai/health`) |
| R-06 | **180s timeout × 3 tasks** | Long-running requests | Sequential execution budget; failure partial-state rules in §11 |
| R-07 | **Facts / Gold drift** | Metadata facts differ from Gold rows | Pre-flight fact-key cross-check optional; same Sprint 6.3 run binding |
| R-08 | **Idempotency gaps** | Duplicate recommendations on retry | AC-19; run-level AI completion flag |
| R-09 | **Scope creep to Risk/Simulation AI** | Violates sprint boundary | Single domain: waste runs only |
| R-10 | **Frozen AI modification pressure** | ADR violation | All changes in AI Recommendation Service module; compose, don’t edit |

---

## 10. Dependencies

### 10.1 Hard dependencies (must be complete)

| Dependency | Status | Reference |
|---|---|---|
| Sprint 6.3 Decision Engine | ✅ Complete | `progress.md` Sprint 6.3 |
| Facts persisted on completed runs | ✅ Implemented | `runtime_metadata.facts_contract` |
| Phase 5 AI layer frozen | ✅ Complete | `AI_FREEZE.md` |
| Context Builder + Prompt Engine + Parser | ✅ Frozen | `app/ai/` |
| Ollama client + config | ✅ Operational | `app/ai/client.py`, `.env` |
| Recommendation registry | ✅ Exists | `RecommendationService`, `recommendations` table |
| Waste Gold persistence | ✅ Exists | `WasteService`, Sprint 6.3 |

### 10.2 Soft dependencies

| Dependency | Notes |
|---|---|
| `GET /ai/health` | Pre-flight Ollama check optional |
| Reporting period label | Enriches context; not blocking |
| Placeholder frontend rec IDs (`rec-w01`…) | Inform mapping only; not runtime |

### 10.3 Downstream consumers (not Sprint 6.4 blockers)

| Consumer | Relationship |
|---|---|
| Frontend Dashboard/Waste pages | Phase 7 — consume recommendation APIs |
| Reports | Phase 8 |
| Number Guard | **Future hardening sprint** — explicitly out of Sprint 6.4 scope (§3.3) |

---

## 11. AI Response Mapping Contract

**Status:** Pending Technical Lead approval  
**Scope:** Structured AI response → persistent recommendation records + run-scoped insights  
**Gate:** Sprint 6.4 implementation may begin **immediately after this contract is approved**.  
**Authority:** `ParsedResponse` (`app/ai/parsers/types.py`); frozen Arabic templates (`ar.py`); `recommendations` entity + `RecommendationService` (DD-03); Sprint 6.4 §3.3 (Number Guard out of scope).

**Determinism principle:** Mapping is **rule-based only**. No LLM re-invocation, no numeric invention, no partial persistence on failure.

---

### 11.1 Purpose

Define exactly how the **AI Recommendation Service** transforms three frozen `PromptTask` outputs into:

1. **Run-scoped AI insights** (executive narrative artifacts on the completed analysis run).
2. **`recommendations` rows** (one row per parsed recommendation item only).

The mapper **does not perform business analysis**. It persists language output from completed Facts interpretation.

---

### 11.2 AI response sections used

Sprint 6.4 executes **three tasks in fixed order**. Each produces one `ParsedResponse`:

| # | PromptTask | AI response section | Frozen template output shape |
|---|---|---|---|
| 1 | `EXECUTIVE_SUMMARY` | **Executive Summary** | Opening paragraph + bullet list (Arabic prose) |
| 2 | `RECOMMENDATIONS` | **Recommendations** | Numbered list, 3–6 items; each item: action, rationale, fact references |
| 3 | `RISK_ANALYSIS` | **Risk Analysis** | Priority-ordered risk list; each item: title, brief description, supporting facts |

**Supporting Narrative** is **not a fourth LLM task**. It is the **audit bundle** of per-task parsed text captured during mapping (§11.3).

---

### 11.3 Section → persistence model mapping

| AI response section | Primary persistence target | Conceptual location |
|---|---|---|
| **Executive Summary** | Run AI insights artifact | `analysis_runs.runtime_metadata.ai_insights.executive_summary` |
| **Risk Analysis** | Run AI insights artifact | `analysis_runs.runtime_metadata.ai_insights.risk_explanation` |
| **Recommendations** (each parsed item) | Recommendation registry | One `recommendations` row per item via `RecommendationService.register_recommendation()` |
| **Supporting Narrative** | Run AI insights artifact | `analysis_runs.runtime_metadata.ai_insights.narrative.{task}` for all three tasks |
| **Generation provenance** | Recommendation `source_context` + insights metadata | Per-row `source_context`; insights-level `generated_at`, `prompt_version`, `model`, `tasks_executed` |

**Insights artifact (conceptual minimum keys):** `generated_at`, `prompt_version`, `model`, `tasks_executed[]`, `executive_summary`, `risk_explanation`, `narrative`, `facts_contract_version`, `engine_id`, `engine_version`, `source_snapshot_id`.

---

### 11.4 Mandatory fields

#### Run AI insights artifact (written only on full success)

| Field | Requirement |
|---|---|
| `generated_at` | UTC timestamp of successful completion |
| `prompt_version` | `"1.0"` (frozen) |
| `model` | Active Ollama model id from config |
| `tasks_executed` | `["executive_summary", "recommendations", "risk_analysis"]` |
| `executive_summary` | Non-empty Arabic text |
| `risk_explanation` | Non-empty Arabic text |
| `narrative.executive_summary` | Non-empty — same source as executive summary parse |
| `narrative.recommendations` | Non-empty — raw parsed recommendations text |
| `narrative.risk_analysis` | Non-empty — raw parsed risk text |
| `facts_contract_version` | From rehydrated Facts (`"1.0"`) |
| `engine_id` / `engine_version` | From rehydrated Facts |
| `source_snapshot_id` | From completed run provenance |

#### Each `recommendations` row

| Field | Requirement |
|---|---|
| `organization_id` | From analysis run |
| `domain_source` | `waste` (`RecommendationDomain.WASTE`) |
| `title` | Non-empty; derived from recommendation **action** clause |
| `description` | Non-empty; **action + rationale** (and fact references if present in item text) |
| `priority` | `high` or `medium` (`RecommendationPriority`) |
| `analysis_run_id` | Source completed run id |
| `source_context` | Non-empty provenance object (§11.4 optional lists allowed keys) |

**Exclusive-source rule:** `risk_id` and `simulation_run_id` must be **null**.

---

### 11.5 Optional fields

| Target | Field | Rule |
|---|---|---|
| `recommendations` | `confidence_label` | Set only if value **exactly matches** a `confidence` field on a fact in the run’s Facts Contract |
| `recommendations` | `estimated_savings_amount` | Set only if value **exactly matches** a numeric fact value (e.g. `waste.potential_savings`) — no rounding, no conversion |
| `recommendations` | `external_ref` | Not set by Sprint 6.4 mapper (placeholder IDs are frontend-only) |
| `recommendations` | `department_id` | **Not set** — deferred (Sprint 6.3 E-08) |
| `recommendations` | `is_dashboard_featured` | Default `false`; featuring is manual via existing service |
| `source_context` | `task`, `prompt_task`, `conversation_id`, `parsed_format`, `item_index` | Provenance enrichment permitted |

---

### 11.6 Validation rules

| ID | Rule | On violation |
|---|---|---|
| V-01 | Executive Summary `ParsedResponse.text` non-empty after trim | Fail generation |
| V-02 | Risk Analysis `ParsedResponse.text` non-empty after trim | Fail generation |
| V-03 | Recommendations list yields **3–6** distinct items after parse | Fail generation |
| V-04 | Each recommendation item has non-empty **action** (→ title) | Fail generation |
| V-05 | Each recommendation `priority` maps to `high` or `medium` only | Fail generation |
| V-06 | `estimated_savings_amount`, if set, equals a fact numeric value exactly | Fail that row → fail entire generation |
| V-07 | `confidence_label`, if set, equals a fact confidence value exactly | Fail that row → fail entire generation |
| V-08 | No recommendation row created without valid `analysis_run_id` | Fail generation |
| V-09 | Insights artifact complete only if **all three tasks** pass V-01–V-07 | Fail generation |

**Recommendations parse strategy (Arabic numbered list — approved):**

1. Split `RECOMMENDATIONS` `ParsedResponse.text` on numbered line starts (`1.` … `6.`, Arabic `١.` … or equivalent).
2. **Action** = first sentence or line of each item → `title` (max 500 chars, truncate with ellipsis if needed).
3. **Remainder** of item → `description`.
4. **Priority mapping:** if item text contains `عالية` or `عالي` or `high` (case-insensitive) → `high`; else if `متوسطة` or `متوسط` or `medium` → `medium`; else → `medium` (default).

---

### 11.7 Missing-field behavior

| Condition | Error code | Outcome |
|---|---|---|
| Empty executive summary text | `missing_executive_summary` | Fail generation; no insights; no recommendation rows |
| Empty risk explanation text | `missing_risk_explanation` | Fail generation |
| Fewer than 3 or more than 6 recommendation items | `invalid_recommendation_count` | Fail generation |
| Recommendation item missing action/title | `missing_recommendation_title` | Fail generation; cite item index |
| Required insights metadata missing at write time | `incomplete_ai_insights` | Fail generation |

Missing optional fields (`confidence_label`, `estimated_savings_amount`, `department_id`) → **omit**; do not fail.

---

### 11.8 Parser failure behavior

| Condition | Error code | Outcome |
|---|---|---|
| LLM returns empty string | `empty_llm_response` | Fail generation for that task; abort remaining tasks |
| `ResponseParser` raises `ResponseParseError` | `response_parse_failed` | Fail generation; no persistence |
| `ParsedResponse.format = "json"` but `data` unusable for section | `unsupported_response_shape` | Fail generation |
| Any task fails before insights commit | — | **No** partial insights artifact; **no** recommendation rows |

All parser failures → analysis run remains `completed` (Gold unchanged); AI generation attempt recorded in failure metadata only if a separate attempt log is used — **must not** mutate existing `facts_contract` or `ai_insights` on failure.

---

### 11.9 Idempotency rules

| Condition | Behavior |
|---|---|
| `runtime_metadata.ai_insights` **absent** | Proceed with generation |
| `ai_insights` **present** and regenerate **not** requested | Reject: `ai_insights_already_exist` |
| `regenerate=true` | Delete all `recommendations` rows where `analysis_run_id` = run and `domain_source = waste`; replace `ai_insights` atomically on success |
| Successful generation | Write-once `ai_insights`; recommendation rows immutable except via regenerate |

Regenerate must not re-run Business Engine or alter Gold waste results.

---

### 11.10 Intentionally NOT persisted

| Content | Reason |
|---|---|
| Financial Snapshot payload | ADR-010 — AI consumes Facts only |
| Bronze file bytes | Same |
| Raw Facts Contract body (duplicate) | Already on run as `facts_contract` |
| `waste_analysis_results` / breakdown rows as AI input | Gold precondition only |
| In-memory conversation turns | `ConversationService` not persisted (AI_FREEZE) |
| Unparsed full LLM raw response (separate store) | Supporting narrative holds parsed text; no second raw store required |
| `PromptTask.SCENARIO_ANALYSIS` output | Out of Sprint 6.4 scope |
| `risk_id` / `simulation_run_id` on recommendations | Exclusive-source rule; waste runs only |
| `department_id` on recommendations | Deferred |
| Auto `is_dashboard_featured` | Manual featuring only |
| Number Guard results | Out of scope (§3.3) |
| Reports, vendor findings, trend points | Other domains / sprints |
| LLM-invented numeric KPIs | Forbidden — optional fields must match facts exactly |

---

### 11.11 Relationship with completed Analysis Run

| Rule | Requirement |
|---|---|
| **Precondition** | Run `status = completed`, `analysis_type = financial_waste` |
| **Facts** | `runtime_metadata.facts_contract` present and rehydratable (`contract_version = "1.0"`, `engine_id = waste`) |
| **Gold** | `waste_analysis_results` row exists for run |
| **Provenance** | Every recommendation row links via `analysis_run_id`; insights artifact stores `source_snapshot_id` from run |
| **Lifecycle** | AI mapping **never** changes run status, snapshot binding, or Gold metrics |
| **Ordering** | AI generation runs **only after** Sprint 6.3 decision path has completed |

---

### 11.12 Contract approval

| Field | Requirement |
|---|---|
| **Approver** | Technical Lead |
| **Prerequisite for** | Sprint 6.4 implementation (immediate upon approval) |
| **Status** | **Pending approval** |
| **Deviation policy** | Mapping rule changes → TL approval; persistence model changes → ADR |

---

## 12. Implementation Order

### Step 1 — Specification and contract approval

- Approve this document (TL adjustments applied).
- Approve §11 AI Response Mapping Contract.
- Record approvals in `progress.md`.

### Step 2 — Run AI insights persistence design

TL-approved storage shape (§11.6) — no schema migration unless TL requires dedicated table (default: `runtime_metadata` extension).

### Step 3 — Facts rehydration adapter

Validate and rehydrate `facts_contract` from completed runs.

### Step 4 — AI Recommendation Service (core)

Compose Context Builder → Prompt Composer → Ollama → Parser for three tasks; no Orchestrator, no engine.run(); no business analysis logic.

### Step 5 — AI Response Mapper

Implement §11 mapping; wire `RecommendationService.register_recommendation()`.

### Step 6 — Execution entry point + preconditions

Trigger API/service; idempotency; failure semantics.

### Step 7 — Tests and regression

Mocked Ollama E2E; AC-06–AC-08 isolation; full suite green; update `progress.md`.

---

## 13. Technical Lead Recommendation

### Recommendation: **APPROVED FOR IMPLEMENTATION** — conditional on §11 AI Response Mapping Contract approval

| Factor | Assessment |
|---|---|
| **Architectural fit** | Closes Phase 5 → Phase 6 integration gap without unfreezing AI or re-running engines |
| **Correct integration pattern** | **AI Recommendation Service** composes frozen AI components; does **not** extend `AiOrchestrator`; does **not** perform business analysis |
| **Scope discipline** | Waste / `financial_waste` runs only — matches Sprint 6.3 vertical slice |
| **Registry reuse** | `recommendations` table and service already designed for AI outcomes (DD-03) |
| **Primary gate** | §11 AI Response Mapping Contract |
| **Number Guard** | **Out of scope** — documented future hardening (§3.3); AC-20 compensates for savings fields only |

### TL adjustments applied (2026-07-15)

1. Renamed **Analysis Intelligence Service** → **AI Recommendation Service** — recommendation generation only; no business analysis.
2. **Number Guard excluded** from Sprint 6.4 — future hardening sprint; no scope expansion.

### Conditions for implementation start

1. **This specification approved** — TL sign-off recorded.
2. **§11 AI Response Mapping Contract approved** — including Arabic list parsing strategy.
3. **No modification** to frozen `app/ai/` internals, `app/business/engines/`, or Facts Contract structure.
4. **No Number Guard work** in Sprint 6.4.

### Suggested next sprint after 6.4

Number Guard hardening, frontend recommendation consumption (Phase 7), or Financial Engine + AI path — each requires separate sprint approval.

---

## Document Control

| Field | Value |
|---|---|
| **Author** | AI-assisted specification (Sprint 6.4) |
| **Approver** | Technical Lead |
| **Status** | **APPROVED FOR IMPLEMENTATION** (2026-07-15) |
| **TL adjustments applied** | (1) AI Recommendation Service naming; (2) Number Guard out of scope (§3.3) |
| **Implementation start** | **Approved after §11 AI Response Mapping Contract sign-off** |
| **Code constraint** | No implementation in this specification task |
