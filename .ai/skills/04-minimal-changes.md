# Skill 04 — Minimal Changes

Prevent unnecessary code generation and file rewrites.

Authoritative policy: [docs/AI_GUIDELINES.md](../../docs/AI_GUIDELINES.md) — Minimal Changes Policy

---

## Core Rule

Always prefer the **smallest possible diff** that correctly completes the task.

---

## Always Prefer

- Minimal modifications to existing code
- Targeted edits using search-and-replace over full file rewrites
- Preserving existing formatting, indentation, and line endings
- Preserving existing comments unless they are obsolete or incorrect
- Preserving existing naming conventions
- Reusing existing functions, components, and patterns
- Modifying only the code directly affected by the task

---

## Never Unless Explicitly Requested

- Regenerate an entire file from scratch
- Reformat unrelated sections of a file
- Rename variables, functions, or files outside task scope
- Refactor unrelated code ("while I'm here" changes)
- Reorganize imports beyond what the task requires
- Add abstractions, helpers, or utilities for one-time use
- Change coding style in files not being functionally modified

---

## When Editing Existing Files

1. Read the file first to understand surrounding conventions
2. Identify the smallest region that needs to change
3. Make the change without altering unrelated lines
4. Do not add comments that restate obvious code
5. Do not remove comments that remain accurate

---

## When Creating New Files

- Match naming, structure, and patterns of neighboring files
- Create only files required by the current sprint scope
- Do not create files "for future use" unless the sprint requires them

---

## Red Flags — Stop and Reconsider

- The diff touches more than twice the lines logically required
- Multiple files are reformatted with no functional change
- Architecture or folder structure would change as a side effect
- New dependencies would be introduced to simplify a small task

If any red flag applies, reduce scope or wait for approval.

---

## References

- Minimal Changes Policy: [docs/AI_GUIDELINES.md](../../docs/AI_GUIDELINES.md)
- Coding conventions: [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md)
- Sprint scope rules: [docs/PROJECT_ROADMAP.md](../../docs/PROJECT_ROADMAP.md)
