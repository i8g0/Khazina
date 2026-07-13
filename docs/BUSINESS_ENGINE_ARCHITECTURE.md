git push origin main# Khazina Business Engine Architecture

Official specification for the **deterministic Business Engine layer**. All future analysis engines (Waste, Revenue, Budget, Cost, Supplier, Risk, Liquidity, Scenario, and others) must conform to this document.

For the AI pipeline and Facts Contract role in AI interpretation, see [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md). For platform layers, see [ARCHITECTURE.md](ARCHITECTURE.md). For adoption rationale, see [ADR 009: Business Engine Architecture](ADR/009-business-engine-architecture.md).

Cross-references: [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) · [progress.md](progress.md) · [AI_GUIDELINES.md](AI_GUIDELINES.md)

---

## 1. Purpose

Business Engines transform validated business data into **trusted business facts** through deterministic Python logic.

This document freezes the architecture that every engine shares. **Sprint 5.3A defines structure only** — no engine implementations, no calculations, no APIs.

**Change control:** Modifications to layer responsibilities, lifecycle, or Facts Contract design require an ADR and Tech Lead approval.

**Status:** Frozen as of Sprint 5.3A (refined Sprint 5.3A-R) — implementation begins in Sprint 5.3B after approval.

---

## 2. Core Philosophy

Business Engines are **deterministic Python components**. They are **not AI**.

| Rule | Detail |
|------|--------|
| No LLM calls | Engines never import `app.ai` or call Ollama |
| No reports | Engines never produce narrative, summaries, or prose |
| No recommendations | Recommendation text is an AI-layer responsibility |
| No natural language | Engines never generate Arabic, English, or any human-readable output |
| Facts only | Output is structured facts via the Facts Contract |

**Single responsibility:** Transform business data into trusted business facts.

---

## 3. Layer Architecture

```
Business Engine
      ↓
  Calculator
      ↓
   Detector
      ↓
 Fact Assembler
      ↓
Facts Contract
```

| Layer | Responsibility |
|-------|----------------|
| **Business Engine** | Coordinates execution; orchestrates validation, calculation, detection, and fact assembly; exposes the engine lifecycle entry point |
| **Calculator** | Performs **deterministic calculations only** — metrics, ratios, aggregates, derived values |
| **Detector** | Detects business events, threshold crossings, anomalies, classifications, and rule violations from calculated outputs |
| **Fact Assembler** | Assembles calculator and detector outputs into standardized **Fact** records |
| **Facts Contract** | The packaged, versioned set of facts — the **only** interface exposed to the AI layer |

The architecture is **generic**. No engine-specific logic belongs in shared base layers.

---

## 4. Package Structure

```
backend/app/business/
├── __init__.py           # Public exports; engine registry access
├── base.py               # Abstract BusinessEngine interface
├── manifest.py           # EngineManifest — engine identity (SSOT)
├── exceptions.py         # Engine error hierarchy
├── registry.py           # Immutable engine registry
├── calculators/          # Shared calculator utilities (future)
│   └── __init__.py
├── detectors/            # Shared detector utilities (future)
│   └── __init__.py
├── assemblers/           # Fact Assembler implementations (future)
│   └── __init__.py
├── facts/                # Facts Contract types (Sprint 5.3B+)
│   └── __init__.py
└── engines/              # Domain engines (one subfolder per engine, future)
    └── __init__.py
```

**Adding a new engine (future):**

1. Create `app/business/engines/<engine_name>/`
2. Define static `EngineManifest` on the engine class
3. Implement `BusinessEngine` subclass
4. Register via `register_engine()` during application initialization
5. Call `freeze_registry()` before serving requests
6. No changes to shared architecture or AI layer

---

## 5. Engine Lifecycle

Complete execution flow — **the LLM is not part of this lifecycle**.

```
Input Data
    ↓
Validation          (engine input / preconditions)
    ↓
Calculation         (Calculator)
    ↓
Detection           (Detector)
    ↓
Fact Assembly       (Fact Assembler)
    ↓
Facts Contract      (versioned package returned to caller)
    ↓
Returned to caller  (orchestrator / service — not LLM)
```

| Stage | Owner | Output |
|-------|-------|--------|
| Input Data | Caller | Domain-specific input DTO or validated dataset reference |
| Validation | Business Engine | Rejects invalid input before calculation |
| Calculation | Calculator | Deterministic numeric/categorical results |
| Detection | Detector | Events, flags, severity assignments |
| Fact Assembly | Fact Assembler | List of `Fact` records |
| Facts Contract | Business Engine | Immutable, versioned fact collection |

Engines are **synchronous and deterministic**. Same input → same facts.

---

## 6. Business Engine Manifest (Mandatory)

Every Business Engine **must** expose a static **Engine Manifest** — the official identity of the engine.

Implementation: `app/business/manifest.py` — `EngineManifest` (frozen dataclass).

| Field | Constant | Required | Description |
|-------|----------|----------|-------------|
| `engine_id` | ENGINE_ID | Yes | Unique engine identifier |
| `engine_name` | ENGINE_NAME | Yes | Human-readable name |
| `engine_version` | ENGINE_VERSION | Yes | Current implementation version |
| `engine_description` | ENGINE_DESCRIPTION | Yes | Short description |
| `supported_facts` | SUPPORTED_FACTS | Yes | Fact types produced by this engine |

**Rules:**

- Manifest contains **descriptive metadata only** — no runtime state, no calculations, no mutable values
- The **Registry consumes the Manifest** — no duplicated engine metadata elsewhere
- Manifest is the **single source of truth** for engine identity and discovery

**Future extensibility** (optional `extensions` dict): `author`, `owner`, `category`, `deprecated`, `tags`, and others — no redesign required.

Each concrete engine exposes `manifest: EngineManifest` on the `BusinessEngine` interface.

---

## 7. Immutable Engine Registry

The Engine Registry (`app/business/registry.py`) becomes **immutable after application startup**.

### Registry Lifecycle

```
Initialization
      ↓
Registration        (register_engine — reads EngineManifest)
      ↓
Freeze              (freeze_registry)
      ↓
Read Only           (get_engine, get_engine_manifest, registered_manifests)
```

| Phase | Allowed operations |
|-------|-------------------|
| Initialization | Registry empty; not frozen |
| Registration | `register_engine(engine)` — key is `engine.manifest.engine_id` |
| Freeze | `freeze_registry()` — idempotent; called once at startup |
| Read Only | Lookup only; no registration, replacement, or removal |

**Immutable Registry Policy:** After freeze, any registration attempt raises `RegistryFrozenError`.

---

## 8. Engine Interface

Every Business Engine implements a common interface (defined in `app/business/base.py`):

| Method | Purpose |
|--------|---------|
| `run(input_data)` | Primary entry point — executes full lifecycle, returns Facts Contract |
| `analyze(input_data)` | Optional alias for orchestrators; delegates to `run()` unless overridden for staged analysis |
| `assemble_facts(calculation_result, detection_result)` | Invokes Fact Assembler logic; assembles facts from calculator/detector outputs during `run()` |

**Engine identity (required):**

| Property | Purpose |
|----------|---------|
| `manifest` | Static `EngineManifest` — single source of truth consumed by Registry |

Concrete engines implement these methods in Sprint 5.3B and later. Sprint 5.3A defines the interface only.

---

## 9. Facts Contract — Design Specification

The Facts Contract is **designed** in this sprint and **implemented** in Sprint 5.3B. It is the official interface between Business Engines and the AI layer (see [AI_ARCHITECTURE.md §9](AI_ARCHITECTURE.md#9-facts-contract)).

### Purpose

Provide a fixed, auditable, bounded set of analytical outputs. Raw business data never crosses into the AI layer.

### Ownership

| Aspect | Owner |
|--------|-------|
| Contract schema | Business Engine layer (`app/business/facts/`) |
| Fact production | Business Engines via Fact Assembler |
| Fact consumption | Context Builder (future sprint) → Prompt Engine |
| AI interpretation | LLM (downstream; never upstream) |

### Producer

Each Business Engine produces a **FactsContract** instance containing one or more **Fact** records after completing its lifecycle.

### Consumer

The **Context Builder** is the first consumer. It selects and prioritizes facts for the Prompt Engine. The LLM never receives the contract directly without Context Builder filtering (future).

### Lifecycle

```
Engine.run() → FactsContract (immutable) → persisted or passed to orchestrator
                                         → Context Builder (future)
                                         → PromptFact mapping (future)
```

Contracts are **immutable** once built. Corrections require a new engine run.

### Versioning Strategy

| Component | Version field |
|-----------|---------------|
| Facts Contract schema | `contract_version` (e.g. `"1.0"`) |
| Producing engine | `engine_id` + `engine_version` on each contract |
| Individual facts | Optional `fact_schema_version` for field extensions |

Breaking schema changes increment `contract_version` and require an ADR. Additive fields are backward-compatible.

### Allowed Fields (Fact record — conceptual)

| Field | Required | Description |
|-------|----------|-------------|
| `domain` | Yes | Business domain (`waste`, `liquidity`, `risk`, etc.) |
| `metric` | Yes | Metric identifier |
| `value` | Yes | Deterministic result (numeric string or categorical) |
| `unit` | No | Unit of measure |
| `severity` | No | Engine-assigned impact/urgency |
| `confidence` | No | Data quality or engine confidence |
| `source` | Yes | Provenance (engine id, dataset, period, record ref) |
| `organization_id` | No | Tenant scope (when applicable) |
| `period` | No | Reporting period reference |
| `metadata` | No | Extensible key-value bag (non-narrative) |

### Contract envelope (conceptual)

| Field | Required | Description |
|-------|----------|-------------|
| `contract_version` | Yes | Schema version |
| `engine_id` | Yes | Producing engine |
| `engine_version` | Yes | Engine release version |
| `generated_at` | Yes | UTC timestamp |
| `facts` | Yes | Ordered list of Fact records |
| `extensions` | No | Future metadata (correlation_id, run_id) |

### Future Compatibility

- New optional Fact fields may be added without breaking consumers
- Context Builder ignores unknown fields
- Prompt Engine maps Fact → `PromptFact` in a dedicated adapter (future)
- Narrative fields are **prohibited** on Fact records

---

## 10. Layer Responsibilities (Detail)

### Business Engine

- Validates preconditions and input shape
- Invokes Calculator and Detector in order
- Invokes Fact Assembler to assemble output
- Returns Facts Contract to caller
- Handles engine-level error translation
- **Must not** import `app.ai`, HTTP clients, or FastAPI

### Calculator

- Pure deterministic functions or stateless calculator classes
- Inputs: validated data structures only
- Outputs: typed calculation results (DTOs)
- **Must not** detect business events or build facts

### Detector

- Inputs: calculation results
- Outputs: detection results (events, classifications, severity flags)
- Rule-based and threshold-based logic only in Phase 5
- **Must not** perform LLM classification

### Fact Assembler

- Assembles deterministic calculator and detector outputs into Fact records
- Assigns `source`, `domain`, `severity` per engine rules
- **Must not** add narrative text or recommendations
- **Not** a classic Builder pattern — reflects assembly of pre-computed deterministic outputs

---

## 11. Error Handling

Engines report failures through a dedicated exception hierarchy (`app/business/exceptions.py`). **No AI interpretation of errors.**

| Exception | When |
|-----------|------|
| `EngineError` | Base class for all engine failures |
| `InvalidInputError` | Input fails structural or precondition validation |
| `MissingDataError` | Required data absent for calculation/detection |
| `ValidationError` | Business validation rule failed on input |
| `CalculationError` | Deterministic calculation failed |
| `DetectionError` | Detector rule execution failed |
| `BusinessRuleViolationError` | Domain rule violated (deterministic) |
| `RegistryFrozenError` | Registry modification attempted after freeze |

Errors carry **domain context** (engine id from manifest, field names, codes) — not HTTP status codes. Mapping to API responses is the responsibility of upper layers (services/API), not engines.

---

## 12. Extensibility

| Requirement | How |
|-------------|-----|
| Unlimited future engines | One folder per engine under `engines/` |
| No redesign per engine | Shared lifecycle, interface, and Facts Contract |
| Registration | `register_engine()` during init → `freeze_registry()` → read-only lookups |
| Engine identity | `EngineManifest` on each engine; Registry consumes manifest |
| Shared calculators/detectors | Optional reuse via `calculators/`, `detectors/` |
| AI isolation | Engines never import AI; AI never imports engine internals |

**Planned engines (not implemented):** Revenue, Budget, Cost, Supplier, Risk, Liquidity, Scenario, and others. **Waste Engine** implemented in Sprint 5.3B.

---

## 13. Dependency Rules

| Layer | May import | Must not import |
|-------|------------|-----------------|
| `app/business/` | Standard library, typed utilities, other `app.business` modules | `app.ai`, `app.api`, FastAPI, httpx, Ollama |
| `app/services/` (future orchestration) | `app.business`, repositories | Direct LLM calls for analysis |
| `app/ai/` | `PromptFact`, future Facts Contract **adapter** | Business Engine implementations |

Business Engines remain **independent** of the frozen Phase 3 service/repository layers until orchestration sprints wire them explicitly.

---

## 14. Relationship to AI Architecture

```
[Business Engine Layer]  ──Facts Contract──▶  [Context Builder]  ──▶  [Prompt Engine]  ──▶  LLM
     (this document)                              (future)              (Sprint 5.2)
```

Do not duplicate [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md). That document governs everything downstream of the Facts Contract.

---

## Related Documents

| Document | Relationship |
|----------|--------------|
| [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md) | AI pipeline, LLM boundaries, Facts Contract consumer role |
| [ADR 008](ADR/008-ai-architecture.md) | Facts-First AI Pipeline |
| [ADR 009](ADR/009-business-engine-architecture.md) | Adoption of this specification |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Platform architecture |
