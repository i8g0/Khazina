# Prompt Template — Architecture Review

Reusable template for architecture review or proposed architecture change tasks. Replace placeholders before use.

---

## Task Description

```
[Describe what is being reviewed or proposed]
[Specific area: folder structure, framework, API standards, dependencies, infrastructure]
[Question to answer or decision required]
```

---

## Required Documentation

Read before starting:

- [.ai/AI_PROJECT_PROFILE.md](../AI_PROJECT_PROFILE.md)
- [docs/ARCHITECTURE.md](../../docs/ARCHITECTURE.md)
- All relevant [docs/ADR/](../../docs/ADR/) files for the area under review
- [docs/progress.md](../../docs/progress.md) — current phase and constraints

Do not read application source code unless needed to assess the specific proposal.

---

## Required Skills

- [Skill 03 — Architecture Rules](../skills/03-architecture-rules.md)
- [Skill 02 — Documentation Rules](../skills/02-documentation-rules.md) — if ADR or ARCHITECTURE update is proposed
- [Skill 05 — Token Optimization](../skills/05-token-optimization.md)
- [Skill 06 — Output Format](../skills/06-output-format.md)

---

## Scope Verification

Before reviewing or proposing changes, confirm:

- [ ] Review is analysis-only OR change requires Tech Lead approval
- [ ] Phase gates considered (DB Phase 3, auth Phase 4, AI Phase 5)
- [ ] Impact on existing ADRs identified
- [ ] No implementation until approval is granted
- [ ] If approved: ARCHITECTURE.md and ADR updates planned (not duplicated elsewhere)

---

## Validation Checklist

For review-only tasks:

- [ ] Proposal assessed against current ARCHITECTURE.md and ADRs
- [ ] Risks and alternatives documented
- [ ] Phase gate compliance verified
- [ ] Clear recommendation provided (approve / reject / defer)

For approved implementation:

- [ ] ARCHITECTURE.md updated if architecture changed
- [ ] New or updated ADR created if decision changed
- [ ] No information duplicated across documents
- [ ] UTF-8 without BOM

---

## Required Output Format

Follow [Skill 06 — Output Format](../skills/06-output-format.md).

For review tasks, use the **When Blocked** or **Before Implementation** format:

- Summary of proposal or review question
- Assessment against current architecture and ADRs
- Risks and alternatives
- Recommendation
- Waiting for Review — do not implement without Tech Lead approval

No commit unless explicitly requested.

Stop and wait for review.
