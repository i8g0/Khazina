# ADR 009: Business Engine Architecture

**Status:** Accepted  
**Date:** Phase 5 — Sprint 5.3A, 2026-07-13  
**Last refined:** Sprint 5.3A Architecture Refinement, 2026-07-13  
**Phase:** AI Integration (Business Engine Architecture Freeze)

## Decision

Khazina adopts the **Business Engine Architecture** defined in [BUSINESS_ENGINE_ARCHITECTURE.md](../BUSINESS_ENGINE_ARCHITECTURE.md) as the foundation for all deterministic analysis engines.

Key commitments:

1. **Business Engines** are deterministic Python components in `app/business/` — not AI, not LLM callers, not report generators.
2. **Layered pipeline** within each engine: Business Engine → Calculator → Detector → **Fact Assembler** → Facts Contract.
3. **Facts Contract** is the sole interface to the AI layer — designed in 5.3A, implemented in 5.3B.
4. **Common engine interface** — `run()`, `analyze()`, `assemble_facts()` on abstract `BusinessEngine`; **`manifest`** property returns static `EngineManifest`.
5. **Business Engine Manifest (mandatory)** — every engine exposes `EngineManifest` (`engine_id`, `engine_name`, `engine_version`, `engine_description`, `supported_facts`); Registry consumes manifest as single source of truth for engine identity.
6. **Immutable Engine Registry** — lifecycle: Initialization → Registration → Freeze → Read Only; `register_engine()` only before `freeze_registry()`; post-freeze mutations raise `RegistryFrozenError`.
7. **Fact Assembler naming** — the component that assembles calculator/detector outputs into Facts is named **Fact Assembler** (not Fact Builder); package folder `assemblers/`.
8. **Registry-based extensibility** — new engines add a folder + manifest + registration without architectural redesign.
9. **Strict AI isolation** — `app/business/` must not import `app.ai`.

## Context

Phase 5 established AI infrastructure (Sprint 5.1), AI logical architecture (Sprint 5.2), and Prompt Engine (Sprint 5.2 implementation). Before implementing domain engines (Waste, Revenue, Liquidity, etc.), the project requires a frozen, generic engine pattern.

The Phase 3 service layer is frozen. Business Engines are a **new layer** separate from CRUD services — they produce analytical facts, not persistence operations.

Sprint 5.3A Architecture Refinement strengthened the pattern before implementation: mandatory manifests eliminate duplicated metadata, immutable registry guarantees deterministic discovery in production, and Fact Assembler naming reflects assembly of deterministic outputs rather than a classic Builder pattern.

Alternatives considered:

| Alternative | Reason Not Selected |
|-------------|---------------------|
| Calculations inside services | Violates separation; couples CRUD to analysis; harder to test deterministically |
| LLM-as-calculator | Non-deterministic; violates AI_ARCHITECTURE.md |
| One monolithic engine module | Not extensible; domain engines need independent evolution |
| Facts embedded in service responses | No clean AI boundary; hallucination risk |
| Mutable runtime registry | Accidental registration in production; non-deterministic discovery |
| Duplicated engine metadata outside manifest | Drift between registry keys and engine identity |

## Consequences

**Positive**

- Single pattern for unlimited future engines
- Clear Facts Contract boundary before AI consumption
- Testable deterministic layer independent of LLM
- Aligns with Facts-First AI Pipeline (ADR 008)
- Manifest as SSOT simplifies discovery and documentation
- Immutable registry improves production safety

**Negative**

- Additional layer to implement before end-to-end analysis
- Orchestration between services and engines deferred to later sprints
- Facts Contract implementation still required (Sprint 5.3B)
- Startup must explicitly call `freeze_registry()` once engines are registered

**Related Documents**

- [BUSINESS_ENGINE_ARCHITECTURE.md](../BUSINESS_ENGINE_ARCHITECTURE.md) — normative specification (frozen Sprint 5.3A)
- [AI_ARCHITECTURE.md](../AI_ARCHITECTURE.md) — AI pipeline and Facts Contract consumer role
- [ADR 008: AI Architecture](008-ai-architecture.md)
