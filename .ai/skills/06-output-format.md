# Skill 06 — Output Format

Standardize every AI response on Khazina.

Use these structures consistently. Adapt section depth to task complexity — keep simple tasks concise.

---

## Before Implementation

Use when scope has been determined but work has not started, or when waiting for approval.

```markdown
## Summary
[One to three sentences: what will be done and why]

## Files to Modify
| File | Action | Reason |
|------|--------|--------|
| path/to/file | Modify / Create / Delete | Brief reason |

## Files NOT Modified
- [List explicitly, especially docs/code outside scope]

## Validation
- [ ] Checks that will be run after implementation

## Risks
- [Architectural, scope, or dependency risks — or "None identified"]

## Waiting for Review
[State whether proceeding or waiting for approval]
```

---

## After Implementation (Task Complete)

Use when work is finished and ready for developer review.

```markdown
## Summary
[What was done and why]

## Files Modified
- `path/to/file` — brief description of change

## Files Created
- `path/to/file` — brief description (or "None")

## Validation
| Check | Result |
|-------|--------|
| [Check name] | Pass / Fail / N/A |

## Risks
- [Remaining risks or "None identified"]

## Next Steps
- [What the developer or Tech Lead should do next]

## Commit
Not created — awaiting explicit request. (or state commit hash if requested and created)
```

---

## Documentation-Only Tasks

Add when only docs were changed:

```markdown
## Documentation Validation
- Only documentation files changed: Yes / No
- UTF-8 without BOM verified: Yes / No
- No information duplicated across docs: Yes / No
- progress.md modified: Yes / No (and why)
```

---

## When Blocked

Use when the AI must stop before implementing.

```markdown
## Summary
[Why implementation cannot proceed]

## Blocker
[Specific issue: scope unclear, architecture change, phase gate, missing approval]

## Recommended Action
[What the developer or Tech Lead should decide]

## Waiting for Review
Stopped. Awaiting [approval / clarification / Tech Lead decision].
```

---

## Response Rules

1. Always include **Summary**
2. Always list **Files Modified** or **Files to Modify**
3. Always state **Validation** results or planned checks
4. Always note **Risks** (even if none)
5. End sprint work with **Waiting for Review** or **Next Steps**
6. **Never create a commit** unless explicitly requested — state this explicitly
7. Do not reproduce full documentation content — link to `docs/` files instead
8. Use code citations (`startLine:endLine:filepath`) when referencing existing code
9. Keep responses proportional to task complexity

---

## References

- Development workflow: [01-development-workflow.md](01-development-workflow.md)
- Documentation rules: [02-documentation-rules.md](02-documentation-rules.md)
