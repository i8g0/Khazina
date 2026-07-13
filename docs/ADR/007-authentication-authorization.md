# ADR 007: Authentication & Authorization Architecture

**Status:** Accepted  
**Date:** Phase 4 — Sprint 4.5 (documented in Maintenance sprint, 2026-07-13)  
**Phase:** Authentication & Security (Frozen)

## Decision

Khazina authenticates users with **JWT access tokens** (HS256) issued after **bcrypt** password verification. **Authorization** is enforced at the **API dependency layer** via hierarchical role checks and **organization ownership** validation. **Repositories and services** remain free of HTTP and auth concerns.

## Context

Phase 3 delivered a frozen backend core (CRUD APIs, services, repositories) without user identity. Phase 4 had to secure the platform without violating layer boundaries established in Phases 1–3. The frontend Phase 2 shells were built as presentation-only; the backend now requires authenticated, authorized access to business endpoints.

Constraints:

- No OAuth, MFA, sessions, or refresh tokens in Phase 4 scope
- No modification to frozen service/repository business logic for authorization
- Multi-tenant data isolation via `organization_id` on users and org-scoped routes
- Fail-fast secret management (`JWT_SECRET_KEY`, `DATABASE_URL` required from environment)

## Why JWT

| Factor | Rationale |
|--------|-----------|
| Stateless API | Access tokens carry identity claims; no server-side session store required for MVP |
| FastAPI alignment | Bearer token extraction maps cleanly to FastAPI dependency injection (`get_current_user`) |
| Frontend integration | Standard `Authorization: Bearer <token>` header works with Next.js API clients |
| Scope control | Access tokens with expiration (`JWT_ACCESS_TOKEN_EXPIRE_MINUTES`) limit exposure window |
| Phase boundary | Refresh tokens and OAuth deferred intentionally; JWT satisfies Phase 4 exit criteria |

Alternatives considered: server-side sessions (rejected — adds session store and complicates horizontal scaling for MVP); opaque API keys (rejected — no embedded expiration or standard claims without additional infrastructure).

## Why bcrypt

| Factor | Rationale |
|--------|-----------|
| Industry standard | Widely audited adaptive hashing for password storage |
| Python ecosystem | `bcrypt` library integrated in `app/core/security.py` |
| Cost factor | Work factor increases brute-force resistance without custom crypto |
| Separation | Hashing at persistence boundary; plain passwords never stored or returned in API responses |

Alternatives considered: Argon2 (stronger but adds dependency and operational tuning); PBKDF2 (acceptable but less common default in Python FastAPI stacks for greenfield projects).

## Why Repository/Service Layering Was Preserved

Authorization is an **HTTP/API concern** in this architecture. Business services already own duplicate-email rules, organization ownership on user mutations, and transaction boundaries. Duplicating role checks inside every service would:

- Couple domain logic to `UserRole` and JWT concepts
- Complicate testing of business rules in isolation
- Risk divergence between API and service enforcement

Repositories remain **flush-only persistence**. Services remain **business logic and transactions**. Phase 4 added auth without refactoring Phase 3 domains.

## Why Authorization Lives in API Dependencies

Implementation: `app/api/permissions.py` — `RequireAdmin`, `RequireExecutive`, `RequireAnalyst`, and org-scoped variants (`RequireOrg*`).

| Factor | Rationale |
|--------|-----------|
| FastAPI native pattern | `Depends()` composes cleanly on routers; OpenAPI documents protected routes |
| Single enforcement point | Role hierarchy (`admin` ≥ `executive` ≥ `analyst`) defined once in `ROLE_RANK` |
| Thin routers | Routers declare required permission; no inline role logic |
| Frozen services | Phase 3 services unchanged; Phase 4.3 scope met without service-layer churn |
| Clear HTTP semantics | `401` from `get_current_user()` (missing/invalid token, inactive user); `403` from permission deps (wrong role or organization) |

Organization ownership: `require_org_role()` compares `current_user.organization_id` to the path `organization_id` before role checks. Cross-organization access returns `403 Forbidden`.

## Why HS256

| Factor | Rationale |
|--------|-----------|
| Symmetric signing | Single `JWT_SECRET_KEY` (≥32 characters, required from environment) suitable for monolithic backend MVP |
| Simplicity | No public/private key rotation infrastructure required in Phase 4 |
| Library support | PyJWT handles HS256 encode/decode with minimal configuration |
| Restricted configuration | `JWT_ALGORITHM` validated to allow only `HS256` in `app/core/config/auth.py` — prevents misconfiguration to weak or unexpected algorithms |
| Operational fit | Docker Compose and local dev use one shared secret; asymmetric keys (RS256) deferred until multi-service token verification is required |

Alternatives considered: RS256 (rejected for MVP — key management overhead without multiple verifying services); ES256 (same rationale as RS256).

## Consequences

**Positive**

- End-to-end auth flow validated: login → JWT → protected endpoint → role and org checks
- Layer boundaries preserved; Phase 3 backend core remains frozen
- Security hardening (headers, log redaction, sanitized errors) layered without auth redesign
- Frontend can integrate against a stable, documented contract

**Negative**

- No refresh tokens — clients must re-authenticate when access tokens expire
- HS256 requires strict secret protection; compromise of `JWT_SECRET_KEY` affects all tokens
- Authorization at API layer means service-layer GET-by-ID paths rely on router-level deps for org isolation on reads

**Related Documents**

- [ARCHITECTURE.md](../ARCHITECTURE.md) — Phase 4 sections (User System, JWT, Roles, Security Hardening, Freeze)
- [API_CONTRACTS.md](../API_CONTRACTS.md) — Bearer token convention and HTTP status codes
- [FRONTEND_SPECIFICATION.md](../FRONTEND_SPECIFICATION.md) — frontend integration contract for Phase 5
