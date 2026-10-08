---
spec_id: 058-reference-skills-stay-out-of-the-command
spec_hash: d7080aeb2fa9
summary: Hide the spec-format skill from the command list
tasks:
- id: t1
  title: 'user-invocable: false'
  files: [plugins/svc/skills/spec-format/SKILL.md, tests/cplat/test_spec_agents.py]
  covers: [AC-058.1, AC-058.2]
  parallel_safe: true
  depends_on: []
  done: true
---

## t1 — user-invocable: false

**Files:** plugins/svc/skills/spec-format/SKILL.md, tests/cplat/test_spec_agents.py
**Covers:** AC-058.1, AC-058.2
**Goal:** Frontmatter `user-invocable: false`; agents keep reading the references (the existing path test).

**Implementation notes:**
- —

**Done when:** Test asserts the frontmatter; `claude plugin validate plugins/svc` passes.
