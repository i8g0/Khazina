# Khazina AI Development Guidelines

This document defines how AI-assisted development tools are used within the Khazina project. These guidelines apply to all AI tools regardless of vendor or product name.

For architecture constraints, see [ARCHITECTURE.md](ARCHITECTURE.md). For sprint process, see [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md). For developer workflow, see [CONTRIBUTING.md](CONTRIBUTING.md).

---

## Purpose

AI tools accelerate implementation, documentation, and debugging within Khazina. They do not replace human judgment, architectural oversight, or accountability.

The purpose of these guidelines is to:

- Define what AI tools may and may not do
- Ensure all AI-generated output is reviewed before it enters the codebase
- Protect architectural integrity and project standards
- Establish a consistent workflow for AI-assisted development
- Require documentation review before every implementation task

---

## Mandatory Pre-Implementation Checklist

Before implementing any task, every AI assistant must complete the following steps.

### Step 1 — Read Project Documentation

Always read the latest versions of these files before making any changes:

1. [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md)
2. [ARCHITECTURE.md](ARCHITECTURE.md)
3. [AI_GUIDELINES.md](AI_GUIDELINES.md)
4. [progress.md](progress.md)

Additionally:

- Read [CONTRIBUTING.md](CONTRIBUTING.md) if repository workflow may be affected.
- Read [API_CONTRACTS.md](API_CONTRACTS.md) if API work is involved.
- Read [GLOSSARY.md](GLOSSARY.md) if project terminology is relevant.
- Read [DEVELOPMENT_JOURNAL.md](DEVELOPMENT_JOURNAL.md) when historical decisions may affect the implementation.
- Read any relevant ADR files under [docs/ADR/](ADR/) before changing architecture or infrastructure.

Never assume previous context is still valid.

Always treat the documentation as the single source of truth.

### AI Model Configuration (Phase 5+)

The backend AI infrastructure is **model-agnostic**. When working on AI-related sprints:

- Do **not** hardcode, default, or document a specific model name (e.g. in code, `.env.example`, or docs) unless explicitly approved for a one-off test fixture.
- **`OLLAMA_MODEL`** is set by the deployment operator; the application does not recommend or prefer a model.
- Switching models must require **configuration changes only** (`OLLAMA_MODEL`), not source code changes.
- See [ARCHITECTURE.md](ARCHITECTURE.md) (AI Infrastructure) and [ADR 006: Ollama](ADR/006-ollama.md) (Model Selection Policy).

### Step 2 — Determine Current Project Status

Identify:

- Current Phase
- Current Sprint
- Previous Sprint Deliverables
- Deferred Items
- Current Architecture Constraints

Never implement work outside the current sprint scope.

### Step 3 — Verify Scope

Before writing code, explain:

- What files will be modified.
- Why each file must change.
- Which files will NOT change.
- Any architectural risks.

Wait for approval if the requested scope is unclear.

### Step 4 — After Implementation

Before finishing:

- Update [progress.md](progress.md) if the sprint status changed.
- Update README only if setup or usage changed.
- Update [DEVELOPMENT_JOURNAL.md](DEVELOPMENT_JOURNAL.md) only if an important architectural decision, lesson learned, or significant obstacle occurred.
- Update ADR documents only when an architectural decision changes.
- Verify UTF-8 encoding.
- Verify only intended files were modified.
- Summarize all changes.
- Do not create a commit unless explicitly requested.

---

## Allowed AI Tools

The following categories of AI tools are permitted for Khazina development:

| Category | Examples | Use Case |
|----------|----------|----------|
| Code assistants | IDE-integrated AI coding tools | Sprint implementation, refactoring, debugging |
| Documentation assistants | AI writing tools | Documentation drafts, progress updates |
| Review assistants | AI code review tools | Pre-review analysis, suggestion generation |

Specific tool selection is at the developer's discretion. These guidelines apply uniformly regardless of which tool is used.

---

## General Principles

### Human Responsibility

The developer who submits AI-generated code is fully responsible for its correctness, security, and compliance with project standards. AI output is a draft, not a deliverable.

### No Automatic Acceptance

AI suggestions are never automatically accepted. Every generated change must be reviewed, validated, and explicitly approved by the developer before commit.

### Architecture Requires Approval

Architecture decisions require Tech Lead approval regardless of whether they originate from a developer or an AI tool. AI tools must not change architecture autonomously.

### Sprint Scope Only

AI tools implement only what the current sprint specifies. They must not add features, dependencies, or infrastructure beyond approved sprint scope.

### Foundation First

AI tools follow the same "foundation first, features second" philosophy as human developers. Infrastructure must be stable before features are built on top of it.

---

## Allowed Tasks

AI tools may be used for the following tasks when they fall within approved sprint scope:

| Task | Conditions |
|------|------------|
| Generating code | Must follow architecture and coding standards; must not add unapproved dependencies |
| Refactoring | Must not change behavior; must not alter architecture |
| Documentation | Must reflect actual project state; no fictional features |
| Tests | Must test real behavior; no trivial assertions |
| Debugging | Must diagnose from evidence; must not introduce workarounds that bypass standards |
| Boilerplate | Must match existing project conventions and file structure |
| Comments | Must explain non-obvious logic only; must not restate self-evident code |

---

## Forbidden Tasks

AI tools must not perform the following without explicit Tech Lead approval:

| Task | Reason |
|------|--------|
| Changing architecture | Architecture is governed by `docs/ARCHITECTURE.md` and Tech Lead |
| Changing folder structure | Directory layout is fixed per architecture document |
| Adding dependencies | New packages require Tech Lead approval |
| Changing Docker configuration | Docker setup is governed by approved sprints |
| Changing CI configuration | CI is not yet established; changes require Phase 9 approval |
| Changing Git workflow | Git workflow is defined in `docs/PROJECT_ROADMAP.md` |
| Changing API contracts | Response envelope and versioning are fixed standards |
| Deleting shared code | Shared infrastructure must not be removed without approval |
| Implementing business logic outside sprint scope | Scope creep is prohibited |
| Creating database models or migrations outside Phase 3 | Database layer is phase-gated |
| Implementing authentication outside Phase 4 | Security layer is phase-gated |
| Adding AI services outside Phase 5 | AI infrastructure is phase-gated |

If an AI tool identifies a need for any forbidden task, it must stop and request Tech Lead approval before proceeding.

---

## Code Review Rules

Every piece of AI-generated code must pass through human review before merge or commit.

### Developer Review Checklist

Before committing AI-generated code, the developer must verify:

1. Code matches the sprint objective exactly.
2. No architecture changes were introduced.
3. No new dependencies were added.
4. No secrets or credentials are present.
5. Files are UTF-8 without BOM.
6. Existing conventions (naming, structure, patterns) are followed.
7. Validation was run locally (backend start, frontend build, endpoint checks).
8. `docs/progress.md` is updated.

### Tech Lead Review

Tech Lead review is required for every sprint before it is marked complete. Tech Lead verifies:

1. Scope adherence
2. Architecture compliance
3. Code quality and maintainability
4. Validation results
5. Documentation completeness

---

## Prompt Writing Guidelines

Effective prompts produce better AI output and reduce review overhead. Follow these guidelines when writing prompts for AI tools.

### Structure

A well-formed prompt includes:

1. **Role context** — State the developer role and project constraints.
2. **Sprint reference** — Specify the sprint number and objective.
3. **Scope** — List exactly what must be implemented.
4. **Constraints** — List what must not be changed or added.
5. **Deliverables** — Define expected output (files changed, validation, documentation).
6. **Stop condition** — Instruct the AI to stop after sprint completion and wait for review.

### Example: Good Prompt

```
You are implementing Sprint 2.1 of the Khazina project.

Objective: Create the shared application layout component.

Tasks:
1. Create frontend/components/layout/AppShell.tsx
2. Update frontend/app/layout.tsx to use AppShell
3. Update docs/progress.md

Rules:
- Do NOT implement business logic
- Do NOT add dependencies
- Do NOT change architecture
- Follow existing Tailwind and RTL conventions
- Stop after completion and wait for review
```

### Example: Bad Prompt

```
Build the full Khazina dashboard with authentication, database models,
and AI analysis. Use whatever libraries you think are best.
```

This prompt fails because it:

- Spans multiple phases without approval
- Delegates architectural and dependency decisions to AI
- Has no sprint boundary or stop condition

### Prompt Rules

- One sprint per prompt session.
- Reference `docs/ARCHITECTURE.md` when architectural context is needed.
- Explicitly list forbidden actions.
- Request validation results in the deliverables.
- Never ask AI to "improve" or "optimize" architecture without Tech Lead approval.

---

## Quality Checklist

Before accepting AI-generated code, evaluate it against these criteria:

### Correctness

- Does the code perform what the sprint requires?
- Does it handle edge cases appropriately?
- Do validation steps pass locally?

### Readability

- Are names clear and consistent with project conventions?
- Are files small and focused?
- Is the code self-explanatory without excessive comments?

### Consistency

- Does the code match existing patterns in the codebase?
- Are imports, formatting, and structure aligned with neighboring files?
- Does it use the standard `ApiResponse` envelope for API endpoints?

### Performance

- Are there obvious performance anti-patterns (N+1 queries, unnecessary re-renders)?
- Is database access efficient for the current scope?

### Security

- Are secrets excluded from code and commits?
- Is user input validated through Pydantic models?
- Are error responses safe for production (no internal details leaked)?

### Maintainability

- Can another developer understand and extend this code?
- Is there unnecessary abstraction or over-engineering?
- Does the change follow SOLID, DRY, and KISS principles?

---

## Review Workflow

AI-assisted development follows this workflow for every sprint:

```
Developer defines sprint scope
        ↓
AI implements within scope
        ↓
Developer verifies output
        ↓
Developer runs local validation
        ↓
Developer updates docs/progress.md
        ↓
Tech Lead Review
        ↓
Merge / Commit to main
```

### Workflow Rules

- AI must not proceed to the next sprint without Tech Lead approval of the current sprint.
- AI must not commit code autonomously unless the developer explicitly requests it.
- AI must report files changed, validation results, and known issues at sprint completion.
- If AI detects a blocker or architectural concern, it must stop and escalate to the developer.

---

## Best Practices

### Common Mistakes

| Mistake | Impact | Prevention |
|---------|--------|------------|
| Accepting AI output without reading it | Bugs, security issues, architecture violations | Always review every changed line |
| Prompting for multiple phases at once | Scope creep, untested infrastructure | One sprint per session |
| Letting AI choose dependencies | Unapproved packages, version conflicts | Explicitly forbid new dependencies |
| Skipping local validation | Broken builds committed to repository | Run validation before every commit |
| UTF-16 file encoding on Windows | Git binary diffs, broken tooling | Save all files as UTF-8 without BOM |
| AI making architectural decisions | Inconsistent system design | Reference ARCHITECTURE.md; escalate to Tech Lead |

### Good AI Usage Examples

- "Implement the health endpoint using the standard ApiResponse model as defined in Sprint 1.3."
- "Refactor the logging module to extract constants without changing behavior."
- "Update docs/progress.md with Sprint 1.5 validation results."
- "Fix the Alembic env.py engine configuration to use settings.database_url."

### Bad AI Usage Examples

- "Redesign the backend to use Django instead of FastAPI."
- "Add Redis caching to improve performance."
- "Create the full authentication system with JWT and OAuth."
- "Restructure the project folders for better organization."
- "Implement the financial analysis engine with mock data for now."

---

## Escalation

When an AI tool encounters any of the following, it must stop and notify the developer:

- A requirement that changes architecture
- A need for a new dependency
- A conflict between sprint scope and architecture document
- An ambiguous requirement with multiple valid approaches
- A discovered bug outside current sprint scope
- A security concern in existing or proposed code

The developer escalates to Tech Lead when architectural approval is required.

---

## Minimal Changes Policy

When AI tools modify existing files, they must follow these rules:

- Prefer the smallest possible diff.
- Never regenerate entire files unless explicitly requested.
- Preserve formatting.
- Preserve architecture.
- Preserve existing comments unless obsolete.
- Avoid unnecessary refactoring.

---

## Time-Constrained Development

When development occurs under strict deadlines (for example, hackathons), AI must:

- Prioritize MVP — deliver the minimum working scope defined for the current phase.
- Preserve architecture — never sacrifice structure, standards, or quality gates for speed.
- Reduce implementation scope — defer non-essential features to post-hackathon work on the roadmap.
- Never skip validation — run relevant checks before marking work complete.
- Never skip documentation — update only the owning document when required.
- Never rewrite unrelated code — apply [Minimal Changes Policy](#minimal-changes-policy) strictly.

Execution details: [HACKATHON_PLAN.md](HACKATHON_PLAN.md)

---

## Documentation Ownership

Each document has a single responsibility. Never duplicate information across documents. Update only the document responsible for that information.

| Document | Responsibility |
|----------|----------------|
| [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) | Long-term roadmap |
| [ARCHITECTURE.md](ARCHITECTURE.md) | System architecture |
| [AI_GUIDELINES.md](AI_GUIDELINES.md) | AI behavior |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Developer workflow |
| [API_CONTRACTS.md](API_CONTRACTS.md) | API standards |
| [GLOSSARY.md](GLOSSARY.md) | Project terminology |
| [DEVELOPMENT_JOURNAL.md](DEVELOPMENT_JOURNAL.md) | Historical decisions and lessons learned |
| [progress.md](progress.md) | Current project status |
| [docs/ADR/](ADR/) | Architectural decisions |

---

## Automatic Documentation Maintenance

Whenever a task is completed, the AI must determine whether any project documentation requires updating.

At minimum, evaluate:

- [progress.md](progress.md)
- [DEVELOPMENT_JOURNAL.md](DEVELOPMENT_JOURNAL.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [API_CONTRACTS.md](API_CONTRACTS.md)
- [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md)

If updates are required:

- Explain why.
- Apply only the necessary documentation changes.
- Do not modify unrelated sections.

Documentation is considered part of the implementation. A sprint is not complete until required documentation has been updated.

---

## Related Documents

- [ARCHITECTURE.md](ARCHITECTURE.md) — Official system architecture and change control
- [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) — Phase plan, sprint rules, and Definition of Done
- [CONTRIBUTING.md](CONTRIBUTING.md) — Developer workflow and validation
- [API_CONTRACTS.md](API_CONTRACTS.md) — API response and naming standards
- [GLOSSARY.md](GLOSSARY.md) — Project terminology
- [DEVELOPMENT_JOURNAL.md](DEVELOPMENT_JOURNAL.md) — Historical decisions and lessons learned
- [progress.md](progress.md) — Current sprint and phase status
- [docs/ADR/](ADR/) — Architecture Decision Records
