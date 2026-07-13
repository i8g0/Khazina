# Khazina AI Architecture

Official specification for the Khazina AI subsystem. **All AI-related implementation in Phase 5 and future phases must conform to this document.**

For platform architecture, see [ARCHITECTURE.md](ARCHITECTURE.md). For Ollama infrastructure, see [ADR 006: Ollama for Local AI Inference](ADR/006-ollama.md). For adoption rationale, see [ADR 008: AI Architecture](ADR/008-ai-architecture.md). For AI-assisted development workflow, see [AI_GUIDELINES.md](AI_GUIDELINES.md).

Cross-references: [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) · [progress.md](progress.md) · [GLOSSARY.md](GLOSSARY.md)

---

## 1. Purpose

This document defines the official **responsibilities, boundaries, and data flow** of the Khazina AI subsystem.

Khazina separates **deterministic business analysis** from **probabilistic language generation**. Business engines produce trusted facts; the LLM transforms those facts into executive intelligence. This separation protects financial accuracy, auditability, and system reliability.

This specification is the **single source of truth** for every AI-related design and implementation decision during Phase 5 and beyond. Implementation sprints must reference this document before writing code.

**Change control:** Any modification to the responsibilities, boundaries, or pipeline defined here requires a new or updated Architecture Decision Record (ADR) and Tech Lead approval.

**Status:** Frozen as of Sprint 5.2 (Pre-Implementation) — documentation only; implementation follows in subsequent sprints.

---

## 2. Design Philosophy

The AI architecture is governed by four principles. These are non-negotiable constraints on design and implementation.

### Business Logic belongs to the System

All calculations, metric derivation, KPI evaluation, and deterministic pattern detection belong to the **business layer** — not the LLM. The system owns truth; the LLM interprets truth that the system has already established.

### LLM interprets. It does not calculate.

The language model reads structured facts and produces narrative, prioritization, and recommendations. It must never perform arithmetic, derive new metrics, or substitute judgment for deterministic engine output.

### Deterministic before Probabilistic

Every analytical result that can be computed deterministically **must** be computed deterministically. Probabilistic generation is applied only after facts are fixed, validated, and bounded.

### Facts before Language

No LLM invocation occurs until business engines have produced a **Facts Contract** — a structured, validated set of facts. Language is the last stage of the pipeline, not the first.

---

## 3. AI Responsibility

The LLM is **not** the analytical engine.

The **analytical engine** is the business layer — domain services and business engines that operate on validated data with deterministic rules.

The LLM is responsible for:

| Responsibility | Description |
|----------------|-------------|
| Interpreting results | Explaining what fixed facts mean in executive context |
| Connecting facts | Relating findings across domains without inventing links unsupported by data |
| Writing executive reports | Producing narrative summaries suitable for decision makers |
| Prioritizing findings | Ordering and emphasizing facts by severity, impact, or urgency |
| Generating recommendations | Suggesting actions grounded in provided facts |

The LLM must **never** perform business calculations. Any numeric output in an LLM response must trace to a value already present in the supplied facts.

---

## 4. Official AI Pipeline

The complete end-to-end pipeline from external data to user-facing intelligence:

```
ERP / Excel / CSV
        ↓
     Parser
        ↓
  Data Validation
        ↓
   Data Quality
        ↓
 Business Engines
        ↓
  Facts Contract
        ↓
 Context Builder
        ↓
  Prompt Engine
        ↓
       LLM
        ↓
  Number Guard
        ↓
Response Validation
        ↓
    Frontend
```

| Stage | Responsibility |
|-------|----------------|
| **ERP / Excel / CSV** | External source systems and uploaded files. Raw input only; no interpretation. |
| **Parser** | Converts external formats into internal structures. No calculations. |
| **Data Validation** | Enforces required fields, types, dates, currencies, and missing-value rules. Rejects or flags invalid records. |
| **Data Quality** | Assesses completeness, consistency, and confidence of validated data. Engines receive only data that passes quality gates. |
| **Business Engines** | Sole layer permitted to calculate, derive metrics, evaluate KPIs, and detect deterministic patterns. |
| **Facts Contract** | Structured output from engines — facts only, never narrative reports. |
| **Context Builder** | Selects relevant facts for the current AI task; optimizes tokens; prioritizes and reduces context. |
| **Prompt Engine** | Assembles system prompt, user prompt, output rules, language rules, and JSON rules. No business logic. |
| **LLM** | Generates language from bounded context. Compares, prioritizes, summarizes, explains — within allowed boundaries. |
| **Number Guard** | Verifies every number in the LLM output exists in the provided facts. Accepts, rejects, or requests regeneration — never corrects output. |
| **Response Validation** | Validates JSON structure, required fields, output schema, and formatting. |
| **Frontend** | Presents deterministic KPIs, charts, and dashboards; displays validated narrative when available. |

---

## 5. Data Parser

The Parser is the ingestion boundary between external systems and Khazina's internal data model.

**Responsibilities:**

- Read ERP exports, Excel workbooks, and CSV files
- Map external columns and records to internal structures
- Normalize identifiers, labels, and structural shapes for downstream validation
- Report parse errors with source location (file, sheet, row) where possible

**Constraints:**

- **No calculations.** The Parser does not compute totals, ratios, variances, or derived fields.
- **No business rules.** Classification, thresholds, and KPI logic belong to Business Engines.
- **No LLM involvement.** Parsing is fully deterministic.

---

## 6. Data Validation

Data Validation enforces structural and semantic correctness before any analytical processing.

**Validated dimensions:**

| Dimension | Validation scope |
|-----------|------------------|
| Required fields | Mandatory columns and attributes present per domain schema |
| Types | Numeric, textual, boolean, and enum values match expected types |
| Dates | Valid date formats, logical date ranges, period alignment |
| Currencies | Currency codes present and consistent where amounts are monetary |
| Missing values | Explicit handling of nulls, blanks, and incomplete records |

Invalid records are rejected, quarantined, or flagged according to domain rules. Business Engines must not receive records that fail validation.

---

## 7. Data Quality

Data Quality assesses whether validated data is **fit for analytical use**.

**Responsibilities:**

- Measure completeness (coverage of required dimensions)
- Detect inconsistencies (cross-field contradictions, orphan references)
- Assign **confidence** or **quality status** to datasets or record groups
- Gate engine input — engines receive only data that meets minimum quality thresholds

Quality assessment is deterministic. Engines operate on validated, quality-scored data — never on raw or unvalidated input.

---

## 8. Business Engines

Business Engines are the **only layer** permitted to:

- Calculate financial and operational metrics
- Derive KPIs and indicators
- Evaluate thresholds and targets
- Detect deterministic patterns (anomalies, trends, rule violations)

**Current and planned engines (extensible):**

| Engine | Domain focus |
|--------|--------------|
| Financial Engine | Statements, ratios, liquidity, profitability |
| Waste Engine | Cost leakage, redundant spend, inefficiency patterns |
| Supplier Engine | Vendor concentration, contract exposure, procurement risk |
| Asset Engine | Asset utilization, depreciation impact, capital efficiency |
| Scenario Engine | What-if inputs against fixed baseline facts |

Additional engines may be introduced in future sprints. Each engine outputs **facts** — never narrative reports or LLM-ready prose.

Business Engines do not call the LLM. They do not import `app.ai.client`.

---

## 9. Facts Contract

The Facts Contract is the **mandatory handoff** between Business Engines and the AI layer — and the **most important interface** between deterministic analysis and AI interpretation.

### Why it exists

Raw business data, database records, and engine internals are not suitable LLM input. They carry noise, excess volume, and unbounded structure that invite hallucination. The Facts Contract exists to provide a **fixed, auditable, bounded** set of analytical outputs that the AI layer may interpret — and nothing else.

### Who produces it

**Business Engines** produce the Facts Contract. After Parser → Validation → Quality → Engine processing, each engine emits structured facts representing its deterministic results. Engines never emit narrative, prose, or LLM-ready summaries.

### Who consumes it

The **Context Builder** consumes the Facts Contract as its sole input from the analytical layer. From there, selected facts flow through the Prompt Engine to the LLM. The LLM **never receives raw business data directly** — no ERP rows, no CSV content, no unfiltered database entities, and no engine-internal state.

### Why it is the critical boundary

Business Engines communicate with the AI layer **exclusively** through this structured contract. There is no alternate path. This boundary ensures:

- Every number the LLM may reference was computed deterministically upstream
- Traceability from narrative back to engine, metric, and source
- Clear separation of **truth production** (engines) from **truth interpretation** (LLM)

Business Engines never send reports, paragraphs, or executive summaries to the LLM. They send **structured facts** — atomic, typed, traceable statements of analytical output.

**Conceptual fields (not an implementation schema):**

| Field | Meaning |
|-------|---------|
| `domain` | Business domain (e.g., financial, waste, risk) |
| `metric` | Name or identifier of the measured attribute |
| `value` | Deterministic numeric or categorical result |
| `unit` | Unit of measure (currency, percentage, count, etc.) |
| `severity` | Impact or urgency classification assigned by the engine |
| `confidence` | Engine or data-quality confidence in the fact |
| `source` | Provenance — engine name, dataset, period, record reference |

The Facts Contract is immutable input to the Context Builder. The LLM may reference fact values; it may not alter them.

Implementation details (serialization format, storage, API shape) are defined in subsequent sprints and must remain compatible with this contract.

---

## 10. Context Builder

The Context Builder prepares a **minimal, task-relevant** fact set for the Prompt Engine.

**Responsibilities:**

- Select only facts relevant to the current AI task (report type, domain, user scope)
- **Prioritize** high-severity and high-confidence facts
- **Reduce context** by excluding redundant or low-value facts
- **Optimize tokens** — stay within model context limits without dropping critical facts

The Context Builder contains no business logic and performs no calculations. It filters and orders facts produced by Business Engines.

---

## 11. Prompt Engine

The Prompt Engine assembles the complete prompt package sent to the LLM.

**Owns:**

| Component | Purpose |
|-----------|---------|
| System Prompt | Role, boundaries, and global behavioral rules |
| User Prompt | Task-specific instruction and selected fact context |
| Output Rules | Structure, length, tone, and section requirements |
| Language Rules | Arabic/RTL requirements, terminology, executive register |
| JSON Rules | Required fields, schema constraints, serialization format |

**Constraints:**

- Contains **no business logic**
- Does not compute, derive, or transform fact values
- Does not bypass Number Guard or Response Validation rules

Prompt templates live in `app/ai/prompts/` when implemented. Template content is versioned and reviewed; changes follow sprint scope and this architecture.

### Prompt Metadata Policy

Every prompt composed by the Prompt Engine **must** include internal **Prompt Metadata**. Metadata is system observability data — it is **not** part of prompt instructions sent as task content.

**Purpose:** observability, debugging, traceability, prompt evolution tracking, and production diagnostics.

**Required fields (mandatory):**

| Field | Description |
|-------|-------------|
| `prompt_version` | Prompt Engine template/version identifier |
| `prompt_language` | Single language code for the composed prompt |
| `task` | `PromptTask` identifier |
| `created_at` | UTC timestamp at composition time |

**Architectural requirement:** `PromptComposer` is the **sole** creator of Prompt Metadata. No duplicated metadata generation elsewhere.

**Extensibility:** Optional future fields (e.g. `template_name`, `template_version`, `engine_version`, `facts_count`, `correlation_id`) may be added via metadata extensions without breaking compatibility.

Implementation: `app/ai/prompts/metadata.py` — `PromptMetadata`, `build_prompt_metadata()`.

### Prompt Language Policy

The Prompt Engine supports **configurable prompt languages** via `DEFAULT_PROMPT_LANGUAGE` (environment / `AiSettings.default_prompt_language`).

| Rule | Detail |
|------|--------|
| Configuration | Language selected from centralized config — not hardcoded in template modules |
| Current default | `ar` (Modern Standard Arabic) — deployment default only, not an architectural limit |
| One language per prompt | Mixed-language prompts are prohibited |
| Future languages | Additional language packs (e.g. `en`, `fr`, `ja`) require configuration + pack registration — no Prompt Engine redesign |
| Content location | Localized strings live in `app/ai/prompts/languages/` packs |

Changing the default language requires **configuration only** (`DEFAULT_PROMPT_LANGUAGE`), not source code changes, once the target language pack exists.

---

## 12. LLM Boundaries

### Allowed

| Action | Scope |
|--------|-------|
| Compare facts | Contrast values, periods, or domains **already present** in context |
| Prioritize | Order findings by severity, impact, or urgency using provided severity fields |
| Summarize | Condense fact sets into executive narrative |
| Explain | Clarify meaning and implications of fixed facts |
| Connect findings | Relate facts across domains when supported by supplied context |

Comparison between provided facts is explicitly allowed. The LLM may state that one fact is higher than another **only when both values were supplied**.

### Forbidden

| Action | Reason |
|--------|--------|
| Calculate | Arithmetic and derivation belong to Business Engines |
| Derive new numbers | Any numeric output must exist in the Facts Contract |
| Modify values | Fact values are read-only input |
| Invent data | No fabricated metrics, dates, entities, or sources |

**Creation of new numerical values is prohibited.** Restatement, comparison, and prioritization of existing values is permitted.

---

## 13. Number Guard

The Number Guard is a **verification layer** applied to every LLM response before it reaches the user or persistence layer.

**Rule:** Every number appearing in LLM output must **already exist** in the facts provided to that request.

**Responsibilities (exclusive):**

| Action | Permitted |
|--------|-----------|
| **Verify** | Check that each numeric value in the response traces to the supplied facts |
| **Accept** | Pass the response to Response Validation when all numbers are verified |
| **Reject** | Block the response when any number cannot be traced to input facts |
| **Request regeneration** | Trigger a new LLM attempt with stricter constraints (implementation choice per sprint) |

**Explicitly forbidden:**

The Number Guard is **not** allowed to **correct**, **replace**, or **modify** generated numbers. It must never "fix" an AI response. If verification fails, the only outcomes are rejection or regeneration — never silent correction.

The Number Guard is architectural — not optional. It operates independently of prompt wording and cannot be disabled without an ADR.

---

## 14. Response Validation

Response Validation ensures LLM output is structurally correct and safe to consume.

**Validated dimensions:**

| Dimension | Scope |
|-----------|-------|
| JSON | Valid syntax; parseable structure |
| Required fields | All mandatory output fields present |
| Output schema | Conformance to approved response schema for the task |
| Formatting | Language, encoding, and presentation rules |

Failed validation follows the same rejection or regeneration path as Number Guard failures. Invalid responses must never reach the Frontend or database.

---

## 15. Graceful Degradation

Khazina must remain operational when the LLM is unavailable, misconfigured, or failing validation.

| Component | Behavior when LLM fails |
|-----------|-------------------------|
| Dashboard | Continues — deterministic KPIs and charts from Business Engines |
| Business Engines | Continue — calculations and fact production unaffected |
| Charts | Continue — data-driven visualizations from engine output |
| KPIs | Continue — metrics from deterministic layer |
| Narrative generation | Unavailable — reports, summaries, and AI recommendations show degraded state |

Graceful degradation is a product requirement. The LLM enhances intelligence; it is not a single point of failure for core financial visibility.

---

## 16. AI Model Policy

The AI architecture is **model-agnostic**. No specific model is a permanent architectural dependency.

**Configuration:**

- Model selection is via `OLLAMA_MODEL` (operator/deployment environment)
- Switching models requires **configuration changes only** — no source code changes
- See [ARCHITECTURE.md](ARCHITECTURE.md) and [ADR 006](ADR/006-ollama.md)

**Current Development Baseline:**

| Setting | Value |
|---------|-------|
| Model | `Qwen3:8B` |

The Current Development Baseline reflects the **temporary model in use for Phase 5 development**. It is replaceable at any time and is **not** a recommended, default, or permanent model binding in application code.

**Model replacement has no architectural impact.** Changing the model requires updating `OLLAMA_MODEL` in the deployment environment only — no source code changes, no pipeline changes, and no ADR unless the replacement introduces a new class of integration (e.g., cloud provider). Future deployments may use any Ollama-compatible model that meets quality and latency requirements, subject to operator configuration and Tech Lead approval.

---

## 17. Hallucination Prevention

Hallucination prevention is achieved by **architecture**, not prompt engineering alone.

```
Facts Contract
      ↓
Context Builder
      ↓
 Prompt Rules
      ↓
Low Temperature
      ↓
 Number Guard
      ↓
Response Validation
```

| Layer | Prevention mechanism |
|-------|---------------------|
| Facts Contract | LLM receives only engine-produced facts — no open-ended data fetching |
| Context Builder | Bounded, prioritized context — no extraneous prompt surface |
| Prompt Rules | Explicit boundaries on allowed and forbidden actions |
| Low Temperature | Reduced sampling randomness for factual restatement tasks |
| Number Guard | Hard rejection of numerics not traceable to input facts; never corrects or replaces values |
| Response Validation | Structural enforcement before output is accepted |

No single layer is sufficient. The chain is mandatory for production AI features.

---

## 18. Privacy

**Company data never leaves the deployment environment.**

- Financial and operational data is processed locally via Ollama within the operator's infrastructure
- No company data is transmitted to external LLM APIs without a separate ADR and security review

**External market information** (benchmarks, indices, public market data) may be incorporated in future phases. Such data must be:

- Collected independently by Khazina or approved integrations
- Kept separate from company data transmission paths
- Never used as a channel to exfiltrate company data

Privacy constraints apply to Context Builder inputs, prompt content, logs, and error messages. Sensitive data redaction rules in [ARCHITECTURE.md](ARCHITECTURE.md) extend to AI logging.

---

## 19. Multi-Agent Policy

**Status: Deferred** — Multi-Agent is intentionally **outside the scope of Phase 5**.

Phase 5 implementation uses a **single LLM invocation path** per task, orchestrated by the pipeline defined in this document. Business Engines, Context Builder, Prompt Engine, Number Guard, and Response Validation already separate responsibilities without agent orchestration.

**Why deferred (not implemented in Phase 5):**

| Concern | Impact |
|---------|--------|
| Scope boundary | Phase 5 delivers the Facts-First pipeline; agent orchestration is a separate concern |
| Additional latency | Multiple agent rounds increase response time |
| Increased non-determinism | Agent coordination introduces unpredictable outputs |
| Existing separation | Current pipeline already divides deterministic and probabilistic work |

**Future extensibility:**

The architecture is **designed to support future agent-based extensions**. Multi-Agent is not rejected — it is deferred until business requirements justify the added complexity. A **future ADR may introduce Multi-Agent** if measurable benefit and acceptable risk are demonstrated.

No Phase 5 implementation should assume Multi-Agent is permanently excluded.

---

## 20. Final Principle

**English:**

> Business Engines produce trusted facts.  
> The LLM transforms trusted facts into executive intelligence.

**Arabic (design statement):**

> محركات الأعمال تُنتج حقائق موثوقة.  
> نموذج اللغة يحوّل الحقائق الموثوقة إلى ذكاء تنفيذي.

This principle is the governing statement for all AI work on Khazina. When design questions arise, resolve them in favor of deterministic fact production first and probabilistic language second.

---

## Related Documents

| Document | Relationship |
|----------|--------------|
| [ARCHITECTURE.md](ARCHITECTURE.md) | Platform layers, `app/ai/` infrastructure (Sprint 5.1) |
| [ADR 006](ADR/006-ollama.md) | Ollama service and model-agnostic configuration |
| [ADR 008](ADR/008-ai-architecture.md) | Adoption of this specification |
| [AI_GUIDELINES.md](AI_GUIDELINES.md) | AI-assisted development workflow |
| [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) | Phase 5 sprint plan |
