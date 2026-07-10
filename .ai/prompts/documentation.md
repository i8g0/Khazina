# Prompt Template — Documentation Task

Reusable template for documentation create/update tasks. Replace placeholders before use.

---

## Task Description

```
[Describe the documentation change: which file, what section, what information to add or update]
```

---

## Required Documentation

Read before starting:

- [.ai/AI_PROJECT_PROFILE.md](../AI_PROJECT_PROFILE.md)
- [docs/progress.md](../../docs/progress.md)
- The specific target document being modified
- [docs/AI_GUIDELINES.md](../../docs/AI_GUIDELINES.md) — documentation ownership rules

Read only if relevant to the task. Do not load unrelated docs.

---

## Required Skills

- [Skill 01 — Development Workflow](../skills/01-development-workflow.md)
- [Skill 02 — Documentation Rules](../skills/02-documentation-rules.md)
- [Skill 05 — Token Optimization](../skills/05-token-optimization.md)
- [Skill 06 — Output Format](../skills/06-output-format.md)

---

## Scope Verification

Before writing, confirm:

- [ ] Which document owns this information
- [ ] Files to modify or create
- [ ] Files that must NOT be modified (especially docs outside scope)
- [ ] No information will be duplicated across documents
- [ ] No existing documentation rewritten unless explicitly requested

---

## Validation Checklist

After completion:

- [ ] Only the owning document was updated
- [ ] No information duplicated across docs
- [ ] UTF-8 without BOM on all modified files
- [ ] Only intended files were changed
- [ ] Links and references are correct
- [ ] progress.md updated only if sprint status changed

---

## Required Output Format

Follow [Skill 06 — Output Format](../skills/06-output-format.md):

- Summary
- Files Modified / Files Created
- Documentation Validation section
- Validation results
- Risks
- Next Steps
- No commit unless explicitly requested

Stop and wait for review.
