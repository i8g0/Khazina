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
│   │   └── v1/
│   │       ├── router.py        Version 1 route aggregator
│   │       └── health.py        Health check endpoint
│   ├── core/
│   │   ├── config/              Domain-specific settings
│   │   │   ├── base.py          Shared settings config
│   │   │   ├── app.py           AppSettings
│   │   │   ├── database.py      DatabaseSettings
│   │   │   └── logging_config.py LoggingSettings
│   │   ├── logging.py           Logging setup
│   │   ├── exceptions.py        AppError exception class
│   │   └── exception_handlers.py Global exception handlers
│   ├── db/
│   │   └── session.py           Engine, session factory, connection check
│   └── schemas/
│       └── response.py          ApiResponse models and helpers
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
| Database | `app/db/` | SQLAlchemy engine and session management |
| Migrations | `alembic/` | Database schema versioning |

Business logic modules (services, repositories, domain models) will be introduced in later phases following the same layered pattern.

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
- No SQLAlchemy models or migration files exist yet.

### Connection Management

| Environment | Host | Configuration Source |
|-------------|------|---------------------|
| Local development | `localhost` | `backend/.env` |
| Docker Compose | `postgres` | Injected via `docker-compose.yml` |

Connection pool settings are defined in `DatabaseSettings`:

- `database_pool_size` (default: 5)
- `database_max_overflow` (default: 10)
- `database_pool_pre_ping` (default: true)

### Future State (Phase 3)

- Business domain boundaries and ownership are documented in [BUSINESS_DOMAIN_DISCOVERY.md](BUSINESS_DOMAIN_DISCOVERY.md) (approved pending Technical Lead sign-off on review revisions).
- SQLAlchemy models will define the schema.
- Alembic migrations will version all schema changes.
- `target_metadata` in `alembic/env.py` will reference the model registry.

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
| Current endpoints | `GET /api/v1/health` |

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
api/  →  schemas/, core/, db/ (via dependencies)
schemas/  →  (no upward dependencies)
core/  →  (no upward dependencies)
db/  →  core/config/
```

- API routes must not contain business logic.
- Schemas define data shapes only.
- Database access goes through session/dependency injection patterns.
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
- Authentication and authorization will be enforced in Phase 4.
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
