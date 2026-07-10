# Prompt Template — Bug Fix

Reusable template for bug fix tasks. Replace placeholders before use.

---

## Task Description

```
[Describe the bug: expected behavior vs actual behavior]
[Affected files or modules]
[Steps to reproduce, if known]
[Scope limit: fix only this bug, no unrelated changes]
```

---

## Required Documentation

Read before starting:

- [.ai/AI_PROJECT_PROFILE.md](../AI_PROJECT_PROFILE.md)
- [docs/progress.md](../../docs/progress.md)
- Relevant sections of [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) for affected module

Read only docs directly related to the bug. Do not load full project documentation.

---

## Required Skills

- [Skill 04 — Minimal Changes](../skills/04-minimal-changes.md)
- [Skill 05 — Token Optimization](../skills/05-token-optimization.md)
- [Skill 06 — Output Format](../skills/06-output-format.md)

Load [Skill 03 — Architecture Rules](../skills/03-architecture-rules.md) if the fix touches infrastructure or shared modules.

---

## Scope Verification

Before fixing, confirm:

- [ ] Root cause identified from evidence (not assumptions)
- [ ] Files to modify — minimum set required for the fix
- [ ] Files that must NOT change
- [ ] Fix does not introduce architecture changes or new dependencies
- [ ] Fix does not expand into refactoring unrelated code
- [ ] Bug is within current sprint scope or explicitly approved as hotfix

---

## Validation Checklist

After completion:

- [ ] Bug is resolved — expected behavior confirmed
- [ ] No regressions in related functionality
- [ ] Relevant service starts / builds successfully
- [ ] UTF-8 without BOM
- [ ] Only intended files modified
- [ ] progress.md updated if sprint status changed

---

## Required Output Format

Follow [Skill 06 — Output Format](../skills/06-output-format.md):

- Summary (root cause + fix)
- Files Modified
- Validation table
- Risks
- Next Steps
- No commit unless explicitly requested

Stop and wait for review.
