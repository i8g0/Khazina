# Khazina Contributing Guide

This document describes the repository workflow, quality standards, and conventions for all contributors to the Khazina project.

For phase planning and sprint rules, see [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md). For architecture constraints, see [ARCHITECTURE.md](ARCHITECTURE.md). For AI usage rules, see [AI_GUIDELINES.md](AI_GUIDELINES.md).

---

## Repository Workflow

Khazina development follows a structured lifecycle for every unit of work:

```
Phase → Sprint → Implementation → Review → Validation → Commit → Push
```

Each sprint has a single objective, receives explicit review, and is tracked in `docs/progress.md`. Work stops after sprint delivery until Tech Lead review is complete.

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
- Pull latest changes from `main` before starting new sprint work.

---

## Commit Naming

Commit messages should state the sprint number and purpose:

```
Sprint 1.3: Core backend infrastructure

- Split configuration into domain settings
- Add standardized ApiResponse model
- Register global exception handlers
```

Rules:

- One logical commit per sprint unless Tech Lead directs otherwise.
- Stage only files related to the sprint.
- Do not include unrelated files in the commit.
- Record the commit hash in `docs/progress.md` after approval.

---

## PR Process

Pull requests are required when:

- A sprint is developed on a feature branch
- Multiple developers collaborate on the same phase
- Tech Lead review is requested before merge to `main`

### Steps

1. Developer opens a pull request against `main`.
2. Pull request description references the sprint number and objective.
3. Validation results are included in the description or linked from `docs/progress.md`.
4. Tech Lead reviews code, architecture compliance, and scope adherence.
5. Required changes are addressed before merge.
6. Pull request is merged only after Tech Lead approval.
7. `docs/progress.md` is updated with the merge commit hash.

Direct commits to `main` are permitted for approved solo sprint work when Tech Lead policy allows it.

---

## Review Process

| Reviewer | Responsibility |
|----------|----------------|
| Developer | Self-review before submission; verify AI-generated code |
| Tech Lead | Approve architecture compliance, scope adherence, and merge authorization |

Review checklist:

- Sprint objective fully implemented with no scope creep
- No unauthorized dependencies or architecture changes
- Validation results recorded
- Documentation updated where required
- All review feedback addressed before merge

---

## Sprint Workflow

1. Confirm sprint objective from `docs/progress.md` and Tech Lead assignment.
2. Implement sprint scope only — no deferred items, no unrequested features.
3. Run local validation (backend start, frontend build, relevant endpoint checks).
4. Update `docs/progress.md` with implementation summary and validation results.
5. Self-review and prepare commit.
6. Stop and wait for Tech Lead review before marking sprint complete.
7. Commit, push, and record commit hash after approval.

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

## How to Update progress.md

`docs/progress.md` is the live sprint and phase tracker. Update it at the end of every sprint.

Include:

- Current phase and sprint status (in progress, completed, blocked)
- Sprint objective and scope summary
- Implementation details (files changed, key decisions within scope)
- Validation results (commands run, outcomes)
- Review status (pending, approved, changes requested)
- Commit hash after approval

Do not alter completed sprint history unless Tech Lead directs a correction.

---

## How AI Is Used

AI-assisted development tools are permitted for sprint implementation, documentation drafts, and pre-review analysis. See [AI_GUIDELINES.md](AI_GUIDELINES.md) for full rules, including the mandatory pre-implementation checklist and documentation maintenance requirements.

Key principles:

- AI implements only within approved sprint scope
- All AI-generated output is reviewed by the developer before commit
- AI must not change architecture, add dependencies, or expand scope without Tech Lead approval
- AI must stop and escalate when requirements are ambiguous or conflict with architecture

---

## Coding Conventions

Follow conventions defined in [ARCHITECTURE.md](ARCHITECTURE.md):

| Area | Convention |
|------|------------|
| Python | snake_case for functions and variables; PascalCase for classes |
| TypeScript | camelCase for variables and functions; PascalCase for components and types |
| API routes | Versioned under `/api/v1/`; kebab-case path segments |
| Responses | All endpoints return `ApiResponse` envelope |
| Configuration | Domain-specific settings in `backend/app/core/config/` |
| Dependencies | No new packages without Tech Lead approval |

All text files must be saved as UTF-8 without BOM.

---

## Documentation Rules

- Documentation lives in `docs/` unless README updates are required for setup instructions.
- Architecture changes require Tech Lead approval and updates to [ARCHITECTURE.md](ARCHITECTURE.md).
- Significant technology decisions are recorded as ADRs in [docs/ADR/](ADR/).
- Terminology is defined in [GLOSSARY.md](GLOSSARY.md).
- API standards are documented in [API_CONTRACTS.md](API_CONTRACTS.md).
- Development history is recorded in [DEVELOPMENT_JOURNAL.md](DEVELOPMENT_JOURNAL.md).

Use Markdown only. English only. UTF-8 without BOM.

---

## Validation Checklist

Before submitting a sprint for review:

- [ ] Backend starts: `uvicorn app.main:app --reload` (when backend in scope)
- [ ] Frontend builds: `pnpm build` (when frontend in scope)
- [ ] Health endpoint returns expected `ApiResponse` format: `GET /api/v1/health`
- [ ] Docker Compose starts when Docker files were modified
- [ ] No secrets in staged files
- [ ] No encoding issues (Git should not show binary diffs for text files)
- [ ] `docs/progress.md` updated

---

## Hackathon Workflow

During hackathons, the standard workflow above still applies. Additional priorities:

- Prefer MVP implementations — complete core scope before polish.
- Keep code quality — no shortcuts that violate architecture or standards.
- Keep documentation updated — progress and owning documents remain current.
- Keep reviews mandatory — Tech Lead review is still required before merge.
- Keep architecture unchanged — reduce feature scope, not structural quality.
- Deliver a working demo first — polish and remaining features follow post-hackathon.

See [HACKATHON_PLAN.md](HACKATHON_PLAN.md) for the four-day execution plan.

---

## Related Documents

- [PROJECT_ROADMAP.md](PROJECT_ROADMAP.md) — Phase plan and sprint rules
- [ARCHITECTURE.md](ARCHITECTURE.md) — Official system architecture
- [AI_GUIDELINES.md](AI_GUIDELINES.md) — AI-assisted development standards
- [API_CONTRACTS.md](API_CONTRACTS.md) — API response and naming standards
- [GLOSSARY.md](GLOSSARY.md) — Project terminology
- [progress.md](progress.md) — Live sprint and phase tracker
