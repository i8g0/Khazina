# Prompt Template — Refactor

Reusable template for refactoring tasks. Replace placeholders before use.

---

## Task Description

```
[Describe the refactor: what code, what change, what stays the same]
[Explicit requirement: no behavior change unless stated]
[Files or modules in scope]
[Explicit constraints: what must NOT change]
```

---

## Required Documentation

Read before starting:

- [.ai/AI_PROJECT_PROFILE.md](../AI_PROJECT_PROFILE.md)
- [docs/progress.md](../../docs/progress.md)
- Relevant sections of [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) for conventions

Read only docs for affected modules. Do not load unrelated documentation.

---

## Required Skills

- [Skill 04 — Minimal Changes](../skills/04-minimal-changes.md)
- [Skill 05 — Token Optimization](../skills/05-token-optimization.md)
- [Skill 06 — Output Format](../skills/06-output-format.md)

Load [Skill 03 — Architecture Rules](../skills/03-architecture-rules.md) if refactor touches folder structure or shared modules.

---

## Scope Verification

Before refactoring, confirm:

- [ ] Refactor is within current sprint scope or explicitly approved
- [ ] Behavior remains unchanged (unless behavior change is explicitly requested)
- [ ] Files to modify — no scope creep into unrelated modules
- [ ] No architecture, folder structure, or API standard changes
- [ ] No new dependencies
- [ ] No "while I'm here" improvements outside stated scope

---

## Validation Checklist

After completion:

- [ ] Behavior unchanged (or changes match explicit request)
- [ ] Relevant service starts / builds successfully
- [ ] Existing tests pass (when tests exist)
- [ ] UTF-8 without BOM
- [ ] Only intended files modified
- [ ] progress.md updated if sprint status changed

---

## Required Output Format

Follow [Skill 06 — Output Format](../skills/06-output-format.md):

- Summary
- Files Modified
- Validation table
- Risks
- Next Steps
- No commit unless explicitly requested

Stop and wait for review.
