# Khazina Architecture

This document describes the official architecture of the Khazina Enterprise Financial Decision Intelligence Platform. All developers and AI tools must comply with the structures, conventions, and constraints defined here.

For development process and phase planning, see [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md).

---

## High-Level Architecture

```
Browser
    │
    ▼
Next.js Frontend
    │
REST API
    ▼
FastAPI Backend
    │
SQLAlchemy
    ▼
PostgreSQL
    │
AI Requests
    ▼
Ollama
```

---

## Overview

Khazina is a monorepo composed of a Next.js frontend, a FastAPI backend, PostgreSQL database infrastructure, Docker-based local development services, and a reserved AI service area. The platform follows a layered architecture with clear separation of concerns.

```
Khazina/
├── frontend/     Next.js web application
├── backend/      FastAPI REST API
├── ai/           AI services (future phases)
├── database/     Database assets (future phases)
├── docker/       Docker Compose configuration
├── docs/         Project documentation
└── scripts/      Utility scripts
```

---

## Project Structure

| Directory | Responsibility |
|-----------|----------------|
| `frontend/` | User interface, client-side logic, API consumption |
| `backend/` | REST API, business logic, data access, configuration |
| `ai/` | AI model integration and inference services (Phase 5+) |
| `database/` | Database scripts, seeds, and migration assets (Phase 3+) |
| `docker/` | Docker Compose and container orchestration |
| `docs/` | Architecture, roadmap, progress tracker, guidelines |
| `scripts/` | Development and operational utility scripts |

No application code belongs in the repository root except `README.md` and `.gitignore`.

---

## Frontend Architecture

### Stack

| Component | Technology |
|-----------|------------|
| Framework | Next.js 15 (App Router) |
| Language | TypeScript |
| Styling | Tailwind CSS v4 |
| Runtime | Node.js 22 |
| Direction | RTL (`dir="rtl"`, `lang="ar"`) |

### Structure

```
frontend/
├── app/
│   ├── layout.tsx       Root layout and metadata
│   ├── page.tsx         Home page
│   ├── globals.css      Tailwind entry
│   └── site.ts          Shared site constants
├── public/              Static assets
├── Dockerfile           Production container build
├── .env.example         Local environment template
└── package.json         Dependencies and scripts
```

### Principles

- App Router is the only routing mechanism. Pages Router is not used.
- Shared constants (site name, descriptions) live in dedicated modules such as `app/site.ts`.
- Public environment variables (`NEXT_PUBLIC_*`) are injected at build time in Docker via build args.
- Components will be organized by feature as the frontend foundation phase progresses.
- Production builds use Next.js standalone output for Docker deployment.

### Current State (Phase 1 Complete)

- Placeholder home page only
- No dashboard, upload, or analysis pages
- No API client implementation yet

---

## Backend Architecture

### Stack

| Component | Technology |
|-----------|------------|
| Framework | FastAPI |
| Language | Python 3.12 |
| ORM | SQLAlchemy 2.x |
| Migrations | Alembic |
| Database Driver | psycopg2-binary |
| Configuration | pydantic-settings |

### Structure

```
backend/
├── app/
│   ├── main.py                  Application factory and lifespan
│   ├── api/
│   │   ├── deps.py              FastAPI DI: Session → Repositories → Services
│   │   ├── permissions.py       Role and organization authorization (Sprint 4.3)
│   │   └── v1/
│   │       ├── router.py        Version 1 route aggregator
│   │       ├── health.py        Health check endpoint
│   │       └── *.py             One router per business domain (Sprint 3.6)
│   ├── core/
│   │   ├── config/              Domain-specific settings
│   │   │   ├── base.py          Shared settings config
│   │   │   ├── app.py           AppSettings
│   │   │   ├── database.py      DatabaseSettings
│   │   │   ├── auth.py          AuthSettings (JWT)
│   │   │   └── logging_config.py LoggingSettings
│   │   ├── logging.py           Logging setup
│   │   ├── exceptions.py        AppError exception class
│   │   ├── exception_handlers.py Global exception handlers
│   │   ├── jwt.py               JWT access-token utilities (Sprint 4.2)
│   │   ├── logging_filters.py   Sensitive log redaction (Sprint 4.4)
│   │   ├── middleware/          HTTP middleware (Sprint 4.4 security headers)
│   │   └── security.py          Password hashing utilities (Sprint 4.1)
│   ├── db/
│   │   ├── base.py              Shared Base, UUID and timestamp mixins
│   │   ├── session.py           Engine, session factory, connection check
│   │   └── models/              SQLAlchemy ORM models by domain (Sprint 3.3)
│   ├── repositories/            Domain repositories over ORM models (Sprint 3.5)
│   │   ├── base.py              Session holder and generic persistence helpers
│   │   ├── exceptions.py        RepositoryError, EntityNotFoundError (HTTP-agnostic)
│   │   └── *.py                 One module per business domain
│   ├── services/                Business logic orchestration
│   │   ├── base.py              BaseService: transaction boundary and validation helpers
│   │   ├── exceptions.py        Business-level exceptions (HTTP-agnostic)
│   │   └── *.py                 One service per business domain
│   └── schemas/
│       ├── response.py          ApiResponse envelope and helpers
│       ├── common.py            Shared schema utilities and pagination
│       └── *.py                 Create / Update / Response schemas per domain (Sprint 3.6)
├── alembic/
│   ├── env.py                   Migration environment
│   └── versions/                Migration files (empty until Phase 3)
├── alembic.ini
├── requirements.txt
├── Dockerfile
└── .env.example
```

### Layer Responsibilities

| Layer | Path | Responsibility |
|-------|------|----------------|
| API | `app/api/v1/` | HTTP route definitions, request/response binding |
| Core | `app/core/` | Configuration, logging, exception handling |
| Schemas | `app/schemas/` | Pydantic models for API request and response shapes |
| Database | `app/db/` | SQLAlchemy engine, session management, and ORM models |
| Repositories | `app/repositories/` | All SQLAlchemy data access, organized by business domain (Sprint 3.5) |
| Services | `app/services/` | Business logic, workflow validation, and transaction management |
| Migrations | `alembic/` | Database schema versioning |

Repository conventions (Sprint 3.5):

- Repositories receive a `Session` via constructor injection (compatible with `get_db`); they never create sessions or use globals.
- Repositories flush (never commit); transaction orchestration belongs to the Service Layer.
- Repositories contain no business logic — no KPI calculation, business validation, report generation, or AI triggers.
- `EntityNotFoundError` (extends `RepositoryError`, a pure `Exception`) is raised by `require_*` lookups; it carries only domain data (entity name and id) with no HTTP semantics. Mapping to HTTP status codes is done by upper layers. Database errors propagate unswallowed.

Service conventions:

- Services receive the `Session` and their repositories via constructor injection; dependencies are explicit and no globals are used.
- Services own transaction boundaries: every mutating use case runs inside a unit-of-work that commits on success and rolls back on any error. Repositories continue to flush only.
- All business rules live in services: workflow sequencing (file processing, analysis run, and report lifecycles), duplicate prevention, organization ownership checks, active-reporting-period rules, and state-transition validation.
- Services raise business-level exceptions (`ServiceError` hierarchy in `app/services/exceptions.py`): validation, not-found, duplicate, ownership, invalid-state/transition, and integrity-rule violations. These carry no HTTP semantics; translation to status codes is performed by the API layer (Sprint 3.6).
- Services contain no HTTP concepts (no routers, request/response objects, or FastAPI imports) and execute no raw SQL — all data access goes through repositories.

API conventions (Sprint 3.6):

- Routers live in `app/api/v1/`, one module per business domain; they are thin and delegate all business logic to services.
- Dependency chain: `get_db` → repository factories → service factories (`app/api/deps.py`); routers receive services via `Depends()`.
- Pydantic schemas in `app/schemas/` separate Create, Update, and Response shapes; ORM models are never returned directly.
- All successful responses use the `ApiResponse[T]` envelope from `app/schemas/response.py`.
- Business exceptions are mapped to HTTP status codes in `app/core/exception_handlers.py`: `ResourceNotFoundError` → 404, `BusinessValidationError` → 400, `DuplicateResourceError` → 409, `OwnershipViolationError` → 403, `InvalidStateError` / `BusinessRuleViolationError` → 409.
- Organization-scoped resources are nested under `/api/v1/organizations/{organization_id}/…`.
- List endpoints support `limit` / `offset` pagination and domain-specific query filters exposed by the service layer.

### Application Lifecycle

1. `create_app()` constructs the FastAPI instance.
2. `lifespan` context manager initializes logging on startup.
3. Exception handlers are registered before routes.
4. API v1 router is mounted at `/api/v1`.

---

## Database Architecture

### Current State

- PostgreSQL 16 is the designated database engine.
- SQLAlchemy engine and session factory are configured in `app/db/session.py`.
- Alembic is initialized with `env.py` reading `settings.database_url`.
- SQLAlchemy ORM models are implemented in `app/db/models/` per [DATABASE_SCHEMA_DESIGN.md](DATABASE_SCHEMA_DESIGN.md) (Sprint 3.3).
- `target_metadata` in `alembic/env.py` references `Base.metadata` with all models registered via `app.db.models` (Sprint 3.4).
- Initial Alembic migration `f58d9c1c4a02_initial_schema.py` creates the complete approved schema — 25 tables with primary keys, foreign keys, unique/check constraints, indexes (including partial indexes), and server defaults. Upgrade and downgrade paths validated against PostgreSQL 16 (Sprint 3.4).

### Migration Workflow

- Apply schema on a fresh database: `alembic upgrade head` (run from `backend/` with `DATABASE_URL` set).
- Roll back: `alembic downgrade base`.
- New schema changes require a new autogenerated revision reviewed manually before commit; autogeneration is configured with `compare_type` and `compare_server_default` enabled.

### Connection Management

| Environment | Host | Configuration Source |
|-------------|------|---------------------|
| Local development | `localhost` | `backend/.env` |
| Docker Compose | `postgres` | Injected via `docker-compose.yml` |

Connection pool settings are defined in `DatabaseSettings`:

- `database_pool_size` (default: 5)
- `database_max_overflow` (default: 10)
- `database_pool_pre_ping` (default: true)

### Backend Core (Phase 3 — Frozen, Sprint 3.7)

The backend core is feature-complete and frozen. All layers are implemented and validated:

- Business domain boundaries documented in [BUSINESS_DOMAIN_DISCOVERY.md](BUSINESS_DOMAIN_DISCOVERY.md)
- MVP relational schema in [DATABASE_SCHEMA_DESIGN.md](DATABASE_SCHEMA_DESIGN.md)
- SQLAlchemy ORM models in `app/db/models/` (Sprint 3.3)
- Alembic initial migration `f58d9c1c4a02_initial_schema.py` — 25 tables (Sprint 3.4)
- Repository layer in `app/repositories/` — flush-only data access (Sprint 3.5)
- Service layer in `app/services/` — business logic and transaction ownership
- CRUD API layer in `app/api/v1/` with Pydantic schemas (Sprint 3.6)

No further backend core changes unless a defect is discovered. Phase 4 (Authentication & Security) builds on this foundation and is frozen as of Sprint 4.5.

### Authentication & Security (Phase 4 — Frozen, Sprint 4.5)

Phase 4 is feature-complete and frozen. Sprints 4.1–4.4 delivered and were validated end-to-end in Sprint 4.5:

| Sprint | Scope | Status |
|--------|-------|--------|
| 4.1 | User System (`users` table, bcrypt storage, user CRUD) | ✅ Frozen |
| 4.2 | JWT Authentication (`POST /auth/login`, `get_current_user`) | ✅ Frozen |
| 4.3 | Roles & Permissions (`app/api/permissions.py`, protected endpoints) | ✅ Frozen |
| 4.4 | Security Hardening (secrets, headers, log redaction, error sanitization) | ✅ Frozen |

No further authentication or authorization changes unless a defect is discovered. Phase 5 builds on this foundation.

### User System (Phase 4 — Sprint 4.1)

The User domain extends the frozen backend core without modifying existing business workflows:

| Layer | Location | Notes |
|-------|----------|-------|
| ORM | `app/db/models/user.py` | `users` table; FK to `organizations`; globally unique `email` |
| Migration | `alembic/versions/b7e4a2f91c03_add_users_table.py` | Append-only; does not modify prior migrations |
| Repository | `app/repositories/user.py` | Flush-only; `create`, `get_by_id`, `get_by_email`, `list`, `update`, `deactivate` |
| Service | `app/services/user.py` | Duplicate-email prevention, organization ownership, active/inactive rules |
| Schemas | `app/schemas/user.py` | `UserCreate`, `UserUpdate`, `UserResponse` — plain passwords accepted on input only |
| Router | `app/api/v1/user.py` | Organization-scoped under `/organizations/{organization_id}/users` |
| Password storage | `app/core/security.py` | `bcrypt` via `hash_password()` and `verify_password()` |

### JWT Authentication (Phase 4 — Sprint 4.2)

Authentication is implemented on top of the User domain.

| Layer | Location | Notes |
|-------|----------|-------|
| Configuration | `app/core/config/auth.py` | `JWT_SECRET_KEY` (required from environment), `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` |
| JWT utilities | `app/core/jwt.py` | `create_access_token()`, `decode_access_token()` via PyJWT |
| Service | `app/services/auth.py` | Login, password verification, token issuance |
| Schemas | `app/schemas/auth.py` | `LoginRequest`, `TokenResponse` |
| Router | `app/api/v1/auth.py` | `POST /auth/login` |
| Dependency | `app/api/deps.py` | `get_current_user()` — Bearer token → validated JWT → active `User` |

No refresh tokens or OAuth.

### Roles & Permissions (Phase 4 — Sprint 4.3)

Authorization uses the existing `UserRole` enum (`admin`, `executive`, `analyst`) with hierarchical role checks and organization scoping at the API layer.

| Layer | Location | Notes |
|-------|----------|-------|
| Dependencies | `app/api/permissions.py` | `RequireAdmin`, `RequireExecutive`, `RequireAnalyst`, plus org-scoped variants |
| Enforcement | `app/api/v1/*.py` | Routers compose auth dependencies; services unchanged |
| Status codes | — | `401` unauthenticated; `403` authenticated but forbidden or cross-org |

Role hierarchy: `admin` ≥ `executive` ≥ `analyst`. Organization-scoped routes require membership (`user.organization_id == path organization_id`). User management routes require org admin. Mutations generally require executive; deletes require admin.

### Security Hardening (Phase 4 — Sprint 4.4)

Defensive improvements over the approved auth stack without changing business behavior or API contracts.

| Area | Location | Notes |
|------|----------|-------|
| Required secrets | `app/core/config/auth.py`, `database.py` | `JWT_SECRET_KEY` (≥32 chars) and `DATABASE_URL` required from environment; no insecure code defaults |
| JWT safety | `app/core/config/auth.py` | `JWT_ALGORITHM` restricted to `HS256` |
| Security headers | `app/core/middleware/security_headers.py` | `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Content-Security-Policy`, `X-Permitted-Cross-Domain-Policies` |
| Error sanitization | `app/core/exception_handlers.py` | Production hides internal/DB/auth details; dedicated SQLAlchemy handler |
| Log redaction | `app/core/logging_filters.py` | Filters passwords, tokens, Authorization headers, database URLs |

---

## Phase 4 Freeze Confirmation (Sprint 4.5)

The Authentication & Security layer is **officially frozen**. Layer boundaries verified:

- **Repositories** — persistence only; no auth logic
- **Services** — business rules and transactions; no HTTP/JWT concepts
- **API** — thin routers; auth via `get_current_user()` and `app/api/permissions.py`
- **Core** — JWT, bcrypt, security headers, sanitized errors, log redaction

Required runtime configuration: `DATABASE_URL`, `JWT_SECRET_KEY` (≥32 characters), optional `JWT_ALGORITHM=HS256`.

---

## Docker Architecture

### Services

| Service | Image / Build | Port | Purpose |
|---------|---------------|------|---------|
| postgres | postgres:16-alpine | 5432 | Primary database |
| backend | Built from `backend/Dockerfile` | 8000 | FastAPI API |
| frontend | Built from `frontend/Dockerfile` | 3000 | Next.js application |
| ollama | ollama/ollama:latest | 11434 | Local AI model runtime |

### Startup Order

```
postgres (healthy) → backend (healthy) → frontend
ollama (independent)
```

Healthchecks in `docker/docker-compose.yml` enforce startup ordering. Dockerfiles do not define healthchecks; orchestration healthchecks are owned by Compose.

### Configuration

- Project name: `khazina`
- Environment defaults: `docker/.env.example`
- Build contexts are relative to `docker/`: `../backend`, `../frontend`
- Frontend `NEXT_PUBLIC_API_URL` is passed as a Docker build argument

---

## Configuration System

### Backend

Configuration uses `pydantic-settings` with domain-specific settings classes:

| Class | Module | Variables |
|-------|--------|-----------|
| `AppSettings` | `app/core/config/app.py` | `app_name`, `app_version`, `debug` |
| `DatabaseSettings` | `app/core/config/database.py` | `database_url`, pool settings |
| `LoggingSettings` | `app/core/config/logging_config.py` | `log_level` |

A facade `Settings` class in `app/core/config/__init__.py` composes all domain settings and exposes backward-compatible property accessors.

All settings classes share `SETTINGS_CONFIG` from `app/core/config/base.py`:

- Reads from `.env` file
- Case-insensitive environment variable matching
- UTF-8 encoding

### Frontend

| Variable | Purpose |
|----------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API base URL for client requests |

Local development uses `frontend/.env.local`. Docker injects the variable at build time.

---

## Logging System

Backend logging is configured in `app/core/logging.py`:

| Setting | Value |
|---------|-------|
| Format | `%(asctime)s \| %(levelname)-8s \| %(name)s \| %(message)s` |
| Date format | `%Y-%m-%d %H:%M:%S` |
| Output | stdout |
| Level | Controlled by `LOG_LEVEL` setting |

Logging is initialized once during application startup via the FastAPI lifespan handler. The `get_logger(name)` function provides module-level loggers.

---

## API Versioning

All API endpoints are versioned under `/api/v1/`.

| Rule | Detail |
|------|--------|
| Prefix | `/api/v1` |
| Router | `app/api/v1/router.py` aggregates version-specific routes |
| Breaking changes | Require a new version (e.g., `/api/v2/`) |
| Current endpoints | Health check plus 93 domain CRUD/workflow/auth operations across 12 routers (organizations, departments, financial, analysis, waste, risk, simulation, reports, recommendations, timeline, users, auth) |

New endpoints must be added to the appropriate version router, never directly to the application root.

---

## Environment Management

| File | Scope |
|------|-------|
| `backend/.env.example` | Backend local development template |
| `frontend/.env.example` | Frontend local development template |
| `docker/.env.example` | Docker Compose overrides template |
| `backend/.env` | Local backend secrets (gitignored) |
| `frontend/.env.local` | Local frontend secrets (gitignored) |
| `docker/.env` | Local Docker overrides (gitignored) |

Rules:

- Never commit `.env` files containing secrets.
- `.env.example` files document available variables with safe development defaults.
- Docker Compose uses `${VAR:-default}` syntax for safe fallbacks.

---

## Error Handling

Global exception handlers are registered in `app/core/exception_handlers.py`:

| Exception Type | HTTP Status | Response Format |
|----------------|-------------|-----------------|
| `AppError` | Custom (default 400) | `ApiResponse` error envelope |
| `HTTPException` | As raised | `ApiResponse` error envelope |
| `RequestValidationError` | 422 | `ApiResponse` with field errors |
| Unhandled `Exception` | 500 | Generic message (details only in debug mode) |

All error responses use the standard `ApiResponse` envelope. Internal exception details are suppressed in production (`debug=false`).

---

## Response Standard

All API responses use the `ApiResponse` generic model:

```json
{
  "success": true,
  "message": "Service is healthy",
  "data": { "status": "ok" },
  "errors": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether the operation succeeded |
| `message` | string | Human-readable summary |
| `data` | T or null | Response payload |
| `errors` | list of strings or null | Error details when `success` is false |

Helpers:

- `success_response(data, message)` — success envelope
- `error_response(message, errors)` — error envelope

All new endpoints must return `ApiResponse` unless Tech Lead approves an exception.

---

## Folder Responsibilities

### Backend Dependency Rules

```
api/  →  services/ (via deps), schemas/, core/
services/  →  repositories/, db/ (session holder only)
repositories/  →  db/ (no services/, no HTTP concerns)
schemas/  →  (no upward dependencies)
core/  →  (no upward dependencies)
db/  →  core/config/
```

- API routes must not contain business logic; they delegate to services.
- Services must not contain HTTP concepts or execute raw SQL.
- Repositories must not contain business logic or manage transactions.
- Schemas define data shapes only.
- Cross-layer imports must follow the dependency direction above.

### Frontend Dependency Rules

```
app/pages and layouts  →  components/, lib/ (future)
components/  →  lib/ (future)
lib/  →  external packages only
```

Circular dependencies between frontend modules are not permitted.

---

## Single Source of Truth

Each piece of configuration or shared data has exactly one authoritative location:

| Concern | Single Source |
|---------|---------------|
| Backend settings defaults | Pydantic settings classes in `app/core/config/` |
| Site name and description | `frontend/app/site.ts` |
| Docker service configuration | `docker/docker-compose.yml` |
| API response shape | `app/schemas/response.py` |
| Sprint and phase status | `docs/progress.md` |
| Architecture decisions | `docs/ARCHITECTURE.md` |

Duplicated defaults across `.env.example` and settings classes are acceptable for documentation purposes, but runtime behavior is governed by the Pydantic settings classes.

---

## Modularity

- Each backend module has a single responsibility.
- Configuration is split by domain (app, database, logging).
- API versions are isolated in separate router modules.
- Frontend constants are extracted from components into shared modules.
- New features are added as new modules, not by expanding unrelated files.

Files should remain small and focused. If a file exceeds approximately 200 lines, consider splitting it.

---

## Scalability Principles

- Stateless API design: session state belongs in the database or token store, not server memory.
- Database connection pooling is configured from the start.
- API versioning allows backward-compatible evolution.
- Docker Compose supports horizontal scaling patterns in production (Phase 10).
- AI services are isolated in the `ai/` directory to scale independently.
- Configuration is externalized through environment variables for environment-specific deployment.

---

## Naming Conventions

### Backend (Python)

| Element | Convention | Example |
|---------|------------|---------|
| Modules | snake_case | `exception_handlers.py` |
| Classes | PascalCase | `AppSettings`, `ApiResponse` |
| Functions | snake_case | `success_response`, `get_db` |
| Constants | UPPER_SNAKE_CASE | `LOG_FORMAT`, `SETTINGS_CONFIG` |
| Environment variables | UPPER_SNAKE_CASE | `DATABASE_URL`, `LOG_LEVEL` |

### Frontend (TypeScript)

| Element | Convention | Example |
|---------|------------|---------|
| Components | PascalCase | `RootLayout`, `Home` |
| Files (components) | PascalCase or kebab-case | `layout.tsx`, `site.ts` |
| Constants | UPPER_SNAKE_CASE | `SITE_NAME`, `SITE_DESCRIPTION` |
| Environment variables | UPPER_SNAKE_CASE | `NEXT_PUBLIC_API_URL` |

### Git

| Element | Convention | Example |
|---------|------------|---------|
| Branches | kebab-case with prefix | `feature/2.1-layout-system` |
| Commits | Sprint prefix + description | `Sprint 1.3: Core backend infrastructure` |

---

## Coding Standards

### General

- Follow Clean Architecture, SOLID, DRY, and KISS principles.
- Write self-documenting code. Comments explain non-obvious business logic only.
- No hardcoded secrets, credentials, or environment-specific values in source code.
- No mock or hardcoded business data unless explicitly approved for a sprint.
- All text files must be UTF-8 without BOM.

### Backend

- Type hints on all function signatures.
- Pydantic models for all API input and output.
- Dependencies injected via FastAPI `Depends()`.
- Logging via `get_logger(__name__)`, not print statements.

### Frontend

- Strict TypeScript mode enabled.
- Tailwind CSS for styling. No inline style objects unless justified.
- Server Components by default. Client Components only when interactivity requires it.

---

## Documentation Standards

- Sprint progress is tracked in `docs/progress.md`.
- Architecture changes are documented in `docs/ARCHITECTURE.md`.
- Development process is documented in `docs/PROJECT_ROADMAP.md`.
- AI usage rules are documented in `docs/AI_GUIDELINES.md`.
- README.md covers setup and quick start only.
- Every completed sprint updates the progress tracker before commit.

---

## Security Principles

- Secrets never committed to the repository.
- Backend runs as a non-root user in Docker.
- Frontend runs as a non-root user in Docker.
- Debug mode exposes exception details; production must run with `debug=false`.
- JWT access-token authentication is available via `POST /api/v1/auth/login` and the `get_current_user()` dependency (Sprint 4.2).
- Role-based authorization is enforced via `app/api/permissions.py` dependencies on protected endpoints (Sprint 4.3).
- Required secrets (`JWT_SECRET_KEY`, `DATABASE_URL`) must be supplied via environment variables; startup fails fast if missing (Sprint 4.4).
- Production error responses and logs are sanitized; security headers are applied via middleware (Sprint 4.4).
- **Phase 4 (Authentication & Security) is frozen** as of Sprint 4.5 — no further auth changes unless a defect is discovered.
- User passwords are hashed with `bcrypt` before persistence (`app/core/security.py`); plain passwords are never stored or returned in API responses.
- All user input is validated through Pydantic models.
- SQL queries use SQLAlchemy ORM; raw SQL only with Tech Lead approval.
- CORS, rate limiting, and security headers will be configured in appropriate phases.

---

## Change Control

### Requires Tech Lead Approval

- Project directory structure (`frontend/`, `backend/`, `ai/`, etc.)
- Technology stack (Next.js, FastAPI, PostgreSQL, Docker, Ollama)
- API versioning strategy and response envelope format
- Configuration system architecture
- Database engine and ORM choice
- Docker service composition
- Authentication and authorization approach
- Adding or removing dependencies
- CI/CD pipeline configuration
- Git workflow and branch strategy

### Developers May Change (Within Sprint Scope)

- Implementing approved endpoints in existing API version routers
- Adding Pydantic schemas for approved features
- Adding frontend components and pages per sprint plan
- Updating `.env.example` files to document new variables
- Updating `docs/progress.md` after sprint completion
- Fixing bugs within existing modules without architectural impact
- Refactoring within a module for readability (no behavior change)

### Architecture Decision Process

1. Developer or AI identifies a need for an architectural change.
2. A written proposal is submitted to the Tech Lead with rationale and alternatives.
3. Tech Lead approves, rejects, or requests modification.
4. If approved, `docs/ARCHITECTURE.md` is updated before implementation begins.
5. Implementation proceeds only within the approved sprint scope.

AI tools must never make architectural decisions autonomously.

---

## Related Documents

- [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) — Phase and sprint planning
- [AI_GUIDELINES.md](AI_GUIDELINES.md) — AI-assisted development rules
- [progress.md](progress.md) — Current sprint status
