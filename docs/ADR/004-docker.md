# ADR 004: Docker and Docker Compose for Local Development

**Status:** Accepted  
**Date:** Phase 1 — Sprint 1.1 (stabilized Sprint 1.4)  
**Phase:** Foundation

## Decision

Khazina uses Docker for containerization and Docker Compose for orchestrating local development services.

## Why Docker

- Consistent runtime environments across developer machines
- Reproducible builds for backend and frontend through dedicated Dockerfiles
- Isolation of services (postgres, backend, frontend, ollama) with defined networking
- Non-root container users enforced for backend and frontend images
- Foundation for Phase 10 production deployment patterns

## Why Compose

- Single command to start the full local stack: `docker compose -f docker/docker-compose.yml up --build`
- Service healthchecks enforce startup ordering (postgres → backend → frontend)
- Environment defaults centralized in `docker/.env.example`
- Volume persistence for PostgreSQL and Ollama data across restarts
- Lower complexity than Kubernetes for local development

## Local Development Strategy

Khazina supports two development modes:

| Mode | When to Use |
|------|-------------|
| Docker Compose | Full-stack integration testing; validating service interactions |
| Native local | Fast iteration on backend (`uvicorn --reload`) or frontend (`npm run dev`) |

Rules established in Phase 1:

- Docker Compose configuration lives in `docker/docker-compose.yml`
- Compose owns orchestration healthchecks; Dockerfiles stay focused on build and runtime
- Frontend `NEXT_PUBLIC_API_URL` is injected at Docker build time via build args
- Backend `DATABASE_URL` uses hostname `postgres` inside Compose and `localhost` for native local development

## Consequences

**Positive**

- New developers can start the full stack with documented commands
- Service boundaries mirror production architecture

**Negative**

- Docker Desktop required for Compose runtime validation (pending on some development machines)
- Frontend rebuild required when changing public environment variables

**Related Documents**

- [ARCHITECTURE.md](../ARCHITECTURE.md)
- [PROJECT_ROADMAP.md](../PROJECT_ROADMAP.md)
