# ADR 008: AI Architecture — Facts-First Pipeline

**Status:** Accepted  
**Date:** Phase 5 — Sprint 5.2 (Pre-Implementation), 2026-07-13  
**Phase:** AI Integration (Architecture Freeze)

## Decision

Khazina adopts the **Facts-First AI Pipeline** defined in [AI_ARCHITECTURE.md](../AI_ARCHITECTURE.md) as the official specification for all AI-related implementation.

Key architectural commitments:

1. **Business Engines** are the sole analytical layer — all calculations, KPIs, and deterministic pattern detection occur there.
2. **Facts Contract** is the mandatory handoff from engines to the AI layer — structured facts only, never engine-generated narrative.
3. **LLM** interprets, prioritizes, summarizes, and recommends — it does not calculate or invent numerical values.
4. **Number Guard** and **Response Validation** are mandatory verification layers on every LLM output. Number Guard verifies, accepts, rejects, or requests regeneration — it never corrects or modifies numbers.
5. **Graceful degradation** — core dashboards, KPIs, and charts operate without the LLM; narrative generation is optional enhancement.
6. **Multi-Agent deferred** in Phase 5 — single bounded pipeline per task; architecture designed to support future agent-based extensions via ADR if justified by business requirements.
7. **Model-agnostic configuration** — `OLLAMA_MODEL` is operator-supplied; Current Development Baseline is `Qwen3:8B` (temporary, replaceable via configuration only; no architectural impact).
8. **Prompt Metadata Policy** — every composed prompt includes mandatory metadata (`prompt_version`, `prompt_language`, `task`, `created_at`); centralized in `PromptComposer` via `build_prompt_metadata()`.
9. **Prompt Language Policy** — configurable via `DEFAULT_PROMPT_LANGUAGE`; one language per prompt; localized content in language packs under `app/ai/prompts/languages/`; current default `ar`.

## Context

Phase 5 Sprint 5.1 established AI infrastructure (`app/ai/`, Ollama client, health check). Sprint 5.2 freezes the **logical architecture** before implementation sprints build parsers, engines, context builders, prompts, and guards.

Financial decision intelligence requires:

- Auditability of calculated metrics
- Protection against LLM hallucination of numbers
- Separation of deterministic analysis from probabilistic language
- Local privacy (company data stays in deployment environment)

Alternatives considered:

| Alternative | Reason Not Selected |
|-------------|---------------------|
| LLM-as-analytical-engine | Non-deterministic; unauditable calculations; hallucination risk on financial figures |
| Prompt-only guardrails | Insufficient alone; architecture must enforce facts-first boundary |
| Multi-agent orchestration (Phase 5) | **Deferred** — outside Phase 5 scope; architecture supports future introduction via ADR if business requirements justify |
| Cloud LLM default | Conflicts with local privacy requirement; Ollama local inference adopted in ADR 006 |

## Consequences

**Positive**

- Single normative specification (`AI_ARCHITECTURE.md`) for all Phase 5+ AI work
- Clear implementation boundaries — each pipeline stage maps to future sprint scope
- Hallucination prevention through layered architecture, not prompts alone
- Business layer (Phase 3 frozen core) remains authoritative for calculations

**Negative**

- More pipeline stages to implement before end-to-end AI features ship
- Number Guard adds latency (validation/regeneration cycle); never silently corrects output
- Facts Contract schema must be designed carefully in a future sprint

**Related Documents**

- [AI_ARCHITECTURE.md](../AI_ARCHITECTURE.md) — normative specification (frozen Sprint 5.2)
- [ARCHITECTURE.md](../ARCHITECTURE.md) — platform architecture and `app/ai/` infrastructure
- [ADR 006: Ollama for Local AI Inference](006-ollama.md)
- [AI_GUIDELINES.md](../AI_GUIDELINES.md)
