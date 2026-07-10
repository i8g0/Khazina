# Prompt Template — Backend Feature

Reusable template for backend implementation tasks. Replace placeholders before use.

---

## Task Description

```
[Sprint number and objective]
[Specific backend deliverables: routes, schemas, services, config, etc.]
[Explicit constraints: what must NOT change]
```

---

## Required Documentation

Read before starting:

- [.ai/AI_PROJECT_PROFILE.md](../AI_PROJECT_PROFILE.md)
- [docs/progress.md](../../docs/progress.md)
- [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) — backend sections
- [docs/API_CONTRACTS.md](../../docs/API_CONTRACTS.md)
- Relevant [docs/ADR/](../../docs/ADR/) files

Read only if relevant. Do not load frontend or unrelated docs.

---

## Required Skills

- [Skill 01 — Development Workflow](../skills/01-development-workflow.md)
- [Skill 03 — Architecture Rules](../skills/03-architecture-rules.md)
- [Skill 04 — Minimal Changes](../skills/04-minimal-changes.md)
- [Skill 05 — Token Optimization](../skills/05-token-optimization.md)
- [Skill 06 — Output Format](../skills/06-output-format.md)

---

## Scope Verification

Before writing code, confirm:

- [ ] Current sprint and phase from progress.md
- [ ] Files to modify or create
- [ ] Files that must NOT change (frontend, Docker, unrelated backend modules)
- [ ] No new dependencies without approval
- [ ] No architecture, folder structure, or API standard changes
- [ ] Phase gates respected (no DB models before Phase 3, no auth before Phase 4)

---

## Validation Checklist

After completion:

- [ ] Backend starts without errors
- [ ] Relevant endpoints return expected `ApiResponse` format
- [ ] No secrets committed
- [ ] UTF-8 without BOM
- [ ] Only intended files modified
- [ ] progress.md updated if sprint status changed
- [ ] Documentation updated if necessary (owning doc only)

---

## Required Output Format

Follow [Skill 06 — Output Format](../skills/06-output-format.md):

- Summary
- Files Modified / Files Created
- Validation table
- Risks
- Next Steps
- No commit unless explicitly requested

Stop and wait for review.
