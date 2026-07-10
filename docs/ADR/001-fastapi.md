# ADR 001: FastAPI as the Backend Framework

**Status:** Accepted  
**Date:** Phase 1 — Sprint 1.1  
**Phase:** Foundation

## Decision

Khazina uses FastAPI as the sole backend web framework for all REST API services.

## Context

The backend must expose a versioned REST API, support structured configuration, integrate with SQLAlchemy and Alembic, and provide automatic OpenAPI documentation. Phase 1 required a framework that enables rapid infrastructure setup without imposing unnecessary complexity.

## Alternatives Considered

| Alternative | Reason Not Selected |
|-------------|---------------------|
| Django + Django REST Framework | Heavier framework; includes ORM and admin patterns not required at bootstrap |
| Flask | Minimal core requires more manual structure for API versioning, validation, and documentation |
| Node.js (Express/NestJS) | Would split the backend language from Python-based data and AI tooling planned for later phases |

## Why FastAPI

- Native async support and high performance for I/O-bound API workloads
- Pydantic integration for request/response validation aligned with the `ApiResponse` standard
- Automatic OpenAPI and Swagger documentation generation
- Clean dependency injection model suitable for layered architecture
- Strong Python ecosystem compatibility with SQLAlchemy, Alembic, and future AI libraries
- Minimal boilerplate for the health endpoint and infrastructure sprints completed in Phase 1

## Consequences

**Positive**

- Fast bootstrap of API versioning under `/api/v1`
- Consistent validation and serialization through Pydantic
- Developer-friendly local development with uvicorn hot reload

**Negative**

- Team must enforce architectural discipline manually; FastAPI does not impose project structure
- Async patterns require careful use with synchronous SQLAlchemy sessions until async patterns are adopted in later phases

**Related Documents**

- [ARCHITECTURE.md](../ARCHITECTURE.md)
- [ADR 005: ApiResponse Standard](005-api-response.md)
