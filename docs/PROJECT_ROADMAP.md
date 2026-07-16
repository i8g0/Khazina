# Khazina Project Roadmap

This document is the master roadmap for the Khazina project. It defines the long-term vision, development methodology, phase plan, sprint rules, and quality gates that govern all project work.

For current sprint status, see [progress.md](progress.md).

**Roadmap alignment (2026-07-16):** Phases 1–7, Product Polish, and Phase 8 (Testing & QA) are complete. Phase 9 (Financial Risk Intelligence) is the active next phase. Phase 10 combines remaining Reports/Analytics scope with Production Deployment. Prior roadmap labels "Phase 8 — Reports and Analytics" and "Phase 9 — Testing" reflected pre-execution planning; execution history is preserved in sprint reports and completion documents.

---

## Project Vision

### Purpose

Khazina is an Enterprise Financial Decision Intelligence Platform. The platform is designed to help organizations analyze financial data, evaluate decisions, and support strategic planning through structured backend services, a modern web interface, and AI-assisted analysis capabilities.

### Long-Term Goals

- Deliver a reliable, scalable platform for financial decision support.
- Maintain a clean separation between frontend presentation, backend business logic, data persistence, and AI services.
- Support enterprise-grade security, auditability, and maintainability.
- Enable incremental delivery through phased development without compromising architectural integrity.

### Development Philosophy

**Foundation first, features second.**

Khazina is built in deliberate phases. Each phase establishes stable infrastructure before dependent features are introduced. No business feature is implemented until the supporting foundation is reviewed, validated, and committed.

This approach reduces rework, preserves architectural consistency, and ensures that every new capability builds on verified project standards.

---

## Development Methodology

Khazina development follows a structured lifecycle for every unit of work:

```
Phase
  ↓
Sprint
  ↓
Implementation
  ↓
Review
  ↓
Validation
  ↓
Commit
  ↓
Push
```

### Responsibilities

| Role | Responsibility |
|------|----------------|
| Developer | Implements the sprint scope, runs local validation, updates documentation, prepares the commit |
| AI Assistant | Generates or refactors code only within approved sprint scope and project standards |
| Tech Lead | Approves architecture, reviews sprint deliverables, authorizes merge to `main` |
| Project Tracker | Maintained in `docs/progress.md` after every completed sprint |

### Definition of Done (Summary)

A sprint is complete only when implementation, review, validation, documentation update, and commit are all finished. See the detailed checklist in the [Definition of Done](#definition-of-done) section below.

---

## Project Phases

### Phase 1 — Foundation

**Status:** Completed (Sprints 1.1 through 1.5)

**Purpose**

Establish the repository, development environment, backend infrastructure, Docker configuration, and project standards required for all future work.

**Objectives**

- Bootstrap frontend (Next.js, TypeScript, Tailwind, App Router, RTL support)
- Bootstrap backend (FastAPI, configuration, logging, API versioning, database connection structure)
- Initialize Alembic without business migrations
- Configure Docker Compose for postgres, backend, frontend, and ollama
- Standardize API responses and global exception handling
- Validate local development and stabilize Docker configuration

**Expected Deliverables**

- Monorepo structure: `frontend/`, `backend/`, `ai/`, `database/`, `docker/`, `docs/`, `scripts/`
- Health endpoint at `GET /api/v1/health`
- Environment templates (`.env.example` files)
- Docker Compose with service healthchecks and startup ordering
- Progress tracker and project documentation foundation

**Exit Criteria**

- All Phase 1 sprints reviewed and approved by Tech Lead
- Backend and frontend start successfully in local development
- No business logic, authentication, database models, or AI services implemented
- Foundation documented and frozen before Phase 2 begins

---

### Phase 2 — Frontend Foundation

**Purpose**

Build the shared frontend structure, layout system, routing conventions, and UI foundations required before feature pages are implemented.

**Objectives**

- Establish application layout and navigation patterns
- Define component organization and styling conventions
- Integrate API client infrastructure using `NEXT_PUBLIC_API_URL`
- Prepare RTL-ready UI patterns consistent with project standards

**Expected Deliverables**

- Shared layout components and routing structure
- Reusable UI primitives and frontend configuration patterns
- Documented frontend folder conventions
- Verified integration with the backend health endpoint

**Exit Criteria**

- Frontend foundation reviewed and approved
- No business feature pages beyond approved foundation scope
- Frontend build passes in local and Docker environments

---

### Phase 3 — Database

**Purpose**

Introduce the data layer: SQLAlchemy models, Alembic migrations, and database schema aligned with Khazina domain requirements.

**Objectives**

- Define database models and relationships
- Create initial Alembic migrations
- Wire `target_metadata` in Alembic configuration
- Validate database connectivity in local and Docker environments

**Expected Deliverables**

- SQLAlchemy models in the backend
- Version-controlled Alembic migration files
- Database initialization and migration workflow documented
- Connection validation integrated where approved

**Exit Criteria**

- Migrations apply cleanly against PostgreSQL
- No business logic beyond approved schema scope
- Database layer reviewed and approved by Tech Lead

---

### Phase 4 — Authentication and Authorization

**Purpose**

Secure the platform with authentication, session or token management, and role-based access control.

**Objectives**

- Implement user identity management
- Protect API endpoints with authorization middleware
- Define role and permission models
- Integrate authentication with frontend session handling

**Expected Deliverables**

- Authentication API endpoints
- Authorization enforcement on protected routes
- Frontend login and session management
- Security review of authentication flow

**Exit Criteria**

- Unauthorized access is blocked on protected endpoints
- Authentication flow validated end-to-end
- Security review approved by Tech Lead

---

### Phase 5 — AI Infrastructure

**Purpose**

Establish the AI service layer and integration patterns between the backend, Ollama, and future analysis features.

**Objectives**

- Define the `ai/` service structure and backend integration points
- Establish Ollama connectivity and operator-driven model configuration (`OLLAMA_MODEL`; no application default model)
- Create approved patterns for AI request and response handling
- Document AI usage boundaries and security constraints

**Expected Deliverables**

- AI service scaffolding in `ai/` and backend integration layer
- Ollama integration validated in Docker environment
- Model-agnostic configuration documented (`OLLAMA_MODEL` operator-supplied; no default model in code)
- AI guidelines enforced in development workflow
- **AI architecture specification frozen** — [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md) (Sprint 5.2)
- No unapproved model or dependency additions

**Exit Criteria**

- AI infrastructure operational in development environment
- Integration patterns documented and approved
- [AI_ARCHITECTURE.md](AI_ARCHITECTURE.md) adopted as normative AI specification (ADR 008)
- No production financial analysis logic without separate sprint approval

---

### Phase 6 — Financial Core

**Purpose**

Implement the core financial engines and domain services that power Khazina decision intelligence capabilities.

**Objectives**

- Implement approved financial calculation and analysis services
- Introduce rule engine, risk engine, and simulation engine components as scoped
- Enforce domain separation and API contracts
- Integrate financial services with the database layer

**Expected Deliverables**

- Backend financial domain modules
- API endpoints for approved financial operations
- Unit and integration tests for core calculations
- Documented financial domain boundaries

**Exit Criteria**

- Core financial services validated against approved requirements
- No scope creep into frontend reporting or AI features outside sprint plan
- Tech Lead approval on domain architecture compliance

---

### Phase 7 — Frontend Features

**Status:** Completed (Sprints 7.1 through 7.3)

**Purpose**

Deliver user-facing application pages that consume backend and financial services.

**Objectives**

- Implement dashboard, upload, analysis, and related UI workflows as approved per sprint
- Connect frontend pages to backend APIs using established client patterns
- Maintain RTL support and consistent UX standards

**Expected Deliverables**

- Approved application pages and user workflows
- Frontend state management and API integration
- Responsive, accessible UI aligned with design standards

**Exit Criteria**

- Feature pages function against live backend APIs
- Frontend review approved by Tech Lead
- No hardcoded or mock business data unless explicitly approved

---

### Transition Stage — Product Polish

**Status:** Completed (Sprints D1 through D5; pre-polish Sprint 8.x mock removal and verification)

**Purpose**

Bridge the gap between a functionally complete MVP (Phases 6–7) and a presentation- and production-ready executive product before formal quality assurance.

**Objectives**

- Audit and improve the executive user journey without redesigning core architecture
- Remove mock data from the demo path; wire live APIs and intentional empty states
- Optimize AI pipeline performance baseline; validate W-1 Excel ingestion
- Establish operational observability (structured logging, health surfaces, error handling)

**Expected Deliverables**

- Product Polish completion report and sprint reports D1–D5
- Verified executive pipeline: upload → waste → AI → simulation → report → PDF
- Guided demo UX, workflow indicator, and health/status surfaces

**Exit Criteria**

- All Product Polish sprints reviewed and documented
- Executive demo path verified with dynamic datasets
- Ready to enter Phase 8 — Testing & Quality Assurance

See [PRODUCT_POLISH_COMPLETION_REPORT.md](PRODUCT_POLISH_COMPLETION_REPORT.md).

---

### Phase 8 — Testing & Quality Assurance

**Status:** Completed (Sprints 8.1 through 8.5) — **ACCEPTED** 2026-07-16

**Purpose**

Establish comprehensive validation, quality gates, and release readiness across the platform before advancing to the next product phase.

**Objectives**

- Validate backend APIs, services, repositories, and migrations (Sprint 8.1)
- Validate frontend routes, components, and executive UX regression (Sprint 8.2)
- Prove end-to-end integration across the demo-critical path (Sprint 8.3)
- Characterize performance and AI reliability (Sprint 8.4)
- Execute QA freeze and release-readiness certification (Sprint 8.5)

**Expected Deliverables**

- Expanded backend test suite (219 pytest tests passing)
- Frontend TypeScript/lint validation; defect fixes documented
- Integration and performance verification harnesses with JSON artifacts
- Phase 8 completion report and sprint reports 8.1–8.5

**Exit Criteria**

- No critical defects blocking MVP / executive demo scope
- Integration harness exit 0; QA checklist passed
- Tech Lead sign-off on Phase 8 acceptance

**Note:** Report generation and PDF export were delivered in Phase 6 (Sprint 6.6) and re-verified during Phase 8 integration testing. Phase 8 did **not** add new business features.

See [PHASE_8_COMPLETION_REPORT.md](PHASE_8_COMPLETION_REPORT.md).

---

### Phase 9 — Financial Risk Intelligence

**Status:** Next active phase

**Purpose**

Integrate financial risk intelligence into the executive product path — connecting the existing backend risk engine and APIs to user-facing workflows.

**Objectives**

- Wire the Risk Management frontend to live backend risk capabilities
- Deliver executive risk workflows aligned with frozen Phase 6 domain boundaries
- Validate risk data accuracy and permissions on the executive demo path
- Document risk engine product boundaries and deferred admin surfaces

**Expected Deliverables**

- Risk page and related UI consuming production APIs (replacing intentional empty states from Product Polish)
- Executive risk views consistent with RTL and UX standards from Phase 7
- Validation evidence and sprint reports under Phase 9 charter

**Exit Criteria**

- Risk workflows function against live backend APIs on the certified executive path
- No regression to Phases 6–8 deliverables
- Tech Lead approval before Phase 10 begins

**Deferred context:** Risk engine backend exists; executive UI was intentionally deferred through Phase 7 freeze and Product Polish (see [FRONTEND_FREEZE.md](FRONTEND_FREEZE.md)).

---

### Phase 10 — Reports, Analytics & Production Deployment

**Status:** Planned

**Purpose**

Complete remaining reporting and analytics scope, then prepare Khazina for production deployment with hardened configuration, monitoring, and operational procedures.

#### Reports and Analytics (remaining scope)

**Note:** Core report generation and PDF export were delivered in Phase 6 and verified in Phase 8. Remaining analytics scope includes:

**Objectives**

- Executive dashboard KPI/chart aggregation API and UI
- Repository summary and advanced analytics queries as approved per sprint
- Additional export formats (Excel, PowerPoint) where in charter

**Expected Deliverables**

- Dashboard aggregation endpoints and frontend wiring
- Optimized analytics queries for production-scale data volumes
- Export workflows beyond PDF where approved

#### Production deployment

**Objectives**

- Define production Docker and deployment configuration
- Introduce CI pipelines, coverage gates, and automated quality enforcement (smoke QA completed in Phase 8; full CI gates remain here)
- Implement secrets management and environment separation
- Configure logging aggregation, monitoring, and backup procedures
- Document deployment runbooks and rollback procedures

**Expected Deliverables**

- Production-ready deployment configuration
- CI configuration and documented testing standards
- Environment-specific settings (development, staging, production)
- Operational documentation and incident response guidelines

**Exit Criteria**

- Remaining analytics scope validated against approved requirements
- Successful deployment to staging environment
- CI passes on `main` for all required checks
- Production checklist completed and approved
- Tech Lead and operations sign-off before production release

---

## Sprint Rules

Every sprint must follow these rules without exception:

1. **One logical sprint** — Each sprint has a single, clearly defined objective documented in `docs/progress.md`.
2. **One review** — Every sprint receives explicit review before it is marked complete.
3. **One logical commit per sprint** — Each approved sprint is committed as one cohesive changeset unless Tech Lead directs otherwise.
4. **Update progress tracker** — `docs/progress.md` must reflect sprint status, review outcome, commit hash, and validation results before the sprint is closed.
5. **No scope creep** — Deferred items from a sprint are recorded explicitly and are not implemented in the same sprint.
6. **Stop after completion** — Implementation stops after sprint delivery until Tech Lead review is complete.

---

## Git Workflow

### Daily Workflow

1. Pull latest changes from `main`.
2. Create a feature branch if the sprint spans multiple days or requires pull request review.
3. Implement sprint scope only.
4. Run local validation (backend start, frontend build, relevant endpoint checks).
5. Update `docs/progress.md`.
6. Stage only files related to the sprint.
7. Commit with a clear message describing the sprint purpose.
8. Push to remote when approved.

### Commit Message Convention

Commit messages should state the sprint and purpose:

```
Sprint 1.3: Core backend infrastructure

- Split configuration into domain settings
- Add standardized ApiResponse model
- Register global exception handlers
```

### File Encoding

All text files must be saved as UTF-8 without BOM. Binary diffs in Git indicate an encoding problem that must be resolved before commit.

---

## Pull Request Workflow

Pull requests are required when:

- A sprint is developed on a feature branch
- Multiple developers collaborate on the same phase
- Tech Lead review is requested before merge to `main`

### Pull Request Process

1. Developer opens a pull request against `main`.
2. Pull request description references the sprint number and objective.
3. Validation results are included in the description or linked from `docs/progress.md`.
4. Tech Lead reviews code, architecture compliance, and scope adherence.
5. Required changes are addressed before merge.
6. Pull request is merged only after Tech Lead approval.
7. `docs/progress.md` is updated with the merge commit hash.

Direct commits to `main` are permitted for approved solo sprint work when Tech Lead policy allows it.

---

## Branch Strategy

| Branch | Purpose |
|--------|---------|
| `main` | Production-ready code. Always stable. Protected by Tech Lead review. |
| `feature/<sprint-or-feature>` | Sprint implementation work. Example: `feature/2.1-layout-system` |
| `hotfix/<issue>` | Urgent fixes to `main`. Example: `hotfix/health-endpoint-regression` |

### Branch Rules

- `main` must never contain unreviewed or incomplete sprint work.
- Feature branches are deleted after merge unless ongoing work continues.
- Hotfix branches merge directly to `main` with expedited Tech Lead review.

---

## Definition of Done

A sprint is **Done** only when all of the following are satisfied:

### Implementation

- [ ] Sprint objective fully implemented as documented
- [ ] No out-of-scope features added
- [ ] No new dependencies added without Tech Lead approval
- [ ] No architecture changes without Tech Lead approval
- [ ] Files saved as UTF-8 without BOM

### Validation

- [ ] Backend starts without errors (when backend is in scope)
- [ ] Frontend builds successfully (when frontend is in scope)
- [ ] Relevant API endpoints return expected responses
- [ ] Docker configuration validated when Docker files are modified
- [ ] No secrets or credentials committed to the repository

### Documentation

- [ ] `docs/progress.md` updated with sprint summary and details
- [ ] Validation results recorded in progress tracker
- [ ] README updated if setup or usage instructions changed

### Review

- [ ] Developer self-review completed
- [ ] AI-generated code verified by developer
- [ ] Tech Lead review status recorded in `docs/progress.md`
- [ ] All review feedback addressed

### Git

- [ ] Changes committed with a descriptive message
- [ ] Commit hash recorded in `docs/progress.md`
- [ ] Changes pushed to remote repository
- [ ] No unrelated files included in the commit

---

## Hackathon Execution Strategy

The project roadmap defines the **complete long-term product**. Hackathons change **implementation scope only** — they never change the roadmap.

| Principle | Rule |
|-----------|------|
| Roadmap | Permanent. Phases, architecture, and quality standards remain unchanged. |
| MVP scope | Adjusts based on available time during a hackathon. |
| Architecture | Must never be sacrificed. Reduce feature scope instead. |
| Post-hackathon | Remaining roadmap work continues normally. |

For execution details, see [HACKATHON_PLAN.md](HACKATHON_PLAN.md).

| Phase | Hackathon Scope | Post Hackathon |
|-------|-----------------|----------------|
| Phase 2 | Full | Improvements |
| Phase 3 | Full | Improvements |
| Phase 4 | Core Only | Complete Later |
| Phase 5 | Core AI + Performance Validation | Optimization Later |
| Phase 6 | MVP Features | Remaining Features |
| Phase 7 | Basic Dashboard | Advanced Analytics |
| Product Polish | Executive demo UX | Full analytics |
| Phase 8 | Full QA (executed) | CI hardening in Phase 10 |
| Phase 9 | Risk MVP | Full risk workflows |
| Phase 10 | Dashboard analytics + demo deployment | Production |

---

## Related Documents

- [ARCHITECTURE.md](ARCHITECTURE.md) — Official system architecture
- [AI_GUIDELINES.md](AI_GUIDELINES.md) — AI-assisted development standards
- [progress.md](progress.md) — Live sprint and phase tracker
- [PRODUCT_POLISH_COMPLETION_REPORT.md](PRODUCT_POLISH_COMPLETION_REPORT.md) — Product Polish closure
- [PHASE_8_COMPLETION_REPORT.md](PHASE_8_COMPLETION_REPORT.md) — Phase 8 acceptance