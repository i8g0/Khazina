# Skill 02 — Documentation Rules

Teaches AI how documentation ownership works. Documentation in `docs/` is the single source of truth.

Skills define AI behavior. Documentation defines project knowledge.

**Never duplicate information across documents.**

---

## Ownership Map

| Document | Owns | Do NOT put here |
|----------|------|-----------------|
| [docs/progress.md](../../docs/progress.md) | Current phase, sprint status, deliverables, validation, review, commit hashes | Architecture details, roadmap phases, API specs |
| [docs/PROJECT_ROADMAP.md](../../docs/PROJECT_ROADMAP.md) | Long-term phases, sprint rules, Definition of Done, Git/PR workflow | Current sprint details, commit hashes |
| [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) | System architecture, stack, folder structure, conventions | Sprint status, historical narrative |
| [docs/API_CONTRACTS.md](../../docs/API_CONTRACTS.md) | API standards, response format, naming, pagination rules | Endpoint implementations, architecture overview |
| [docs/AI_GUIDELINES.md](../../docs/AI_GUIDELINES.md) | AI behavior, pre-implementation checklist, documentation maintenance | Developer Git workflow (see CONTRIBUTING) |
| [docs/CONTRIBUTING.md](../../docs/CONTRIBUTING.md) | Developer workflow, branches, commits, PRs, validation checklist | AI-specific behavior (see AI_GUIDELINES) |
| [docs/GLOSSARY.md](../../docs/GLOSSARY.md) | Project terminology definitions | Process rules, architecture details |
| [docs/DEVELOPMENT_JOURNAL.md](../../docs/DEVELOPMENT_JOURNAL.md) | Historical decisions, lessons learned, obstacles | Current status (see progress.md) |
| [docs/ADR/](../../docs/ADR/) | Specific architectural decisions with context and consequences | General architecture (see ARCHITECTURE.md) |

---

## When to Update Each Document

### progress.md

Update when sprint status changes: started, in progress, completed, blocked.

Include: objective summary, deliverables, validation results, review status, commit hash.

Do not alter completed sprint history unless Tech Lead directs a correction.

### DEVELOPMENT_JOURNAL.md

Update only when an important architectural decision, lesson learned, or significant obstacle occurred during implementation.

Do not use for routine sprint status — that belongs in progress.md.

### PROJECT_ROADMAP.md

Update only when phase plans, sprint rules, or methodology change.

Do not update for current sprint progress.

### ARCHITECTURE.md

Update only when system architecture, stack, folder structure, or conventions change.

Requires Tech Lead approval before modifying.

### API_CONTRACTS.md

Update only when API standards, response format, or naming conventions change.

Do not add endpoint implementations here.

### ADR (docs/ADR/)

Create or update only when a specific architectural decision is made or changed.

One decision per ADR file. Do not modify existing ADRs to reflect new decisions — create a new ADR.

### CONTRIBUTING.md

Update only when developer workflow, branch strategy, or contribution process changes.

### AI_GUIDELINES.md

Update only when AI behavior rules or the pre-implementation checklist change.

---

## Rules

1. Update only the document that owns the information
2. Never copy content from one doc into another — link instead
3. Do not rewrite existing documentation unless explicitly requested
4. Evaluate doc updates at task completion (see [docs/AI_GUIDELINES.md](../../docs/AI_GUIDELINES.md) — Automatic Documentation Maintenance)
5. A sprint is not complete until required documentation is updated

---

## References

- Documentation ownership (authoritative): [docs/AI_GUIDELINES.md](../../docs/AI_GUIDELINES.md)
- Terminology: [docs/GLOSSARY.md](../../docs/GLOSSARY.md)
