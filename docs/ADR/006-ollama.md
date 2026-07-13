# ADR 006: Ollama for Local AI Inference

**Status:** Accepted  
**Date:** Phase 1 — Sprint 1.1  
**Phase:** Foundation (infrastructure only; AI services deferred to Phase 5)

## Decision

Khazina includes Ollama as a Docker Compose service for local AI model inference. No models are downloaded and no AI business logic is implemented until Phase 5.

## Why Ollama

- Open-source local inference server with a simple HTTP API
- Runs entirely on developer infrastructure without external API dependencies during development
- Official Docker image available (`ollama/ollama:latest`)
- Supports multiple open models when Phase 5 AI infrastructure begins
- Aligns with data privacy requirements for financial analysis workloads

## Why Local Inference

- Financial data must not be sent to third-party AI APIs without explicit approval and security review
- Local inference enables offline development and testing of AI features
- Predictable cost model during development (no per-token cloud billing)
- Full control over model selection and versioning

## Future AI Architecture

Phase 5 will introduce:

- Backend integration layer between FastAPI and Ollama
- AI service modules in the `ai/` directory
- Approved request/response patterns for financial analysis prompts
- Model management conventions (which models, when to load, resource limits)

Ollama runs independently in Compose and does not block startup of postgres, backend, or frontend services.

Cloud-hosted AI providers may be evaluated in later phases through a separate ADR if requirements change.

## Model Selection Policy (Phase 5 — Sprint 5.1+)

The backend AI layer is **model-agnostic**:

- No default, preferred, or recommended model is defined in application code or repository configuration examples.
- The deployment operator selects the model by setting `OLLAMA_MODEL` in the environment (`backend/.env` or `docker/.env`).
- Switching models requires a configuration change only (`OLLAMA_MODEL`); no source code changes.
- Ollama model pull/load remains an operator responsibility outside the application.

**Related Documents**

- [ARCHITECTURE.md](../ARCHITECTURE.md)
- [AI_GUIDELINES.md](../AI_GUIDELINES.md)
- [PROJECT_ROADMAP.md](../PROJECT_ROADMAP.md) — Phase 5
