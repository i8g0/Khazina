# Prompt Template — Frontend Feature

Reusable template for frontend implementation tasks. Replace placeholders before use.

---

## Task Description

```
[Sprint number and objective]
[Specific frontend deliverables: components, pages, layout, styling, etc.]
[Explicit constraints: what must NOT change]
```

---

## Required Documentation

Read before starting:

- [.ai/AI_PROJECT_PROFILE.md](../AI_PROJECT_PROFILE.md)
- [docs/progress.md](../../docs/progress.md)
- [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) — frontend sections

Read only if relevant. Do not load backend or unrelated docs.

---

## Required Skills

- [Skill 01 — Development Workflow](../skills/01-development-workflow.md)
- [Skill 04 — Minimal Changes](../skills/04-minimal-changes.md)
- [Skill 05 — Token Optimization](../skills/05-token-optimization.md)
- [Skill 06 — Output Format](../skills/06-output-format.md)

---

## Scope Verification

Before writing code, confirm:

- [ ] Current sprint and phase from progress.md
- [ ] Files to modify or create
- [ ] Files that must NOT change (backend, Docker, unrelated frontend modules)
- [ ] No new dependencies without approval
- [ ] No architecture or folder structure changes
- [ ] Existing Tailwind, RTL, and App Router conventions preserved

---

## Validation Checklist

After completion:

- [ ] Frontend builds successfully (`npm run build`)
- [ ] No console errors on affected pages (when applicable)
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
