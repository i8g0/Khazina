# Skill 01 — Development Workflow

Required workflow before implementing anything on Khazina.

---

## Step 1 — Read Profile

Read [.ai/AI_PROJECT_PROFILE.md](../AI_PROJECT_PROFILE.md) first.

Do not assume prior conversation context is still valid.

---

## Step 2 — Determine Task Type

Classify the request using [05-token-optimization.md](05-token-optimization.md).

Examples: documentation, frontend, backend, database, infrastructure, architecture, testing, bug fix, refactor.

---

## Step 3 — Read Only Required Documentation

Read the minimum docs for the task type. Always include:

- [docs/progress.md](../../docs/progress.md) — current phase and sprint

Add others only when relevant. Do not read every document on every task.

---

## Step 4 — Explain Implementation Scope

Before writing code or modifying files, state:

- What files will be modified or created
- Why each file must change
- Which files will NOT change
- Any architectural risks

Use the format in [06-output-format.md](06-output-format.md).

---

## Step 5 — Wait for Approval If Unclear

Stop and wait when:

- Sprint scope is ambiguous
- The request spans multiple phases
- Architecture, dependencies, or folder structure would change
- The task conflicts with [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md) or current sprint scope

---

## Step 6 — Implement

- Follow current sprint scope only
- Apply [04-minimal-changes.md](04-minimal-changes.md)
- Apply [03-architecture-rules.md](03-architecture-rules.md)
- One sprint per session unless explicitly directed otherwise

---

## Step 7 — Validate After Implementation

Run relevant checks:

- Backend starts (when backend in scope)
- Frontend builds (when frontend in scope)
- Endpoints return expected responses (when API in scope)
- Docker starts (when Docker files modified)
- UTF-8 without BOM on all modified text files
- Only intended files were changed

---

## Step 8 — Update Documentation If Necessary

Follow [02-documentation-rules.md](02-documentation-rules.md).

Update only the owning document. Do not duplicate information across docs.

---

## Step 9 — Report and Stop

Deliver response using [06-output-format.md](06-output-format.md).

**Never create commits automatically.** Commit only when the developer explicitly requests it.

Stop and wait for Tech Lead review after sprint delivery.

---

## References

- Pre-implementation checklist: [docs/AI_GUIDELINES.md](../../docs/AI_GUIDELINES.md)
- Developer workflow: [docs/CONTRIBUTING.md](../../docs/CONTRIBUTING.md)
- Sprint rules: [docs/PROJECT_ROADMAP.md](../../docs/PROJECT_ROADMAP.md)
