---
spec_id: 050-product-spec-and-plan-reach-main
spec_hash: 4f9817d7f54c
summary: The product spec and plan are pushed and checked before building
tasks:
- id: t1
  title: /app:plan pushes the spec branch and opens the PR
  files: [plugins/app/commands/plan.md]
  covers: [AC-050.1]
  parallel_safe: true
  depends_on: []
  done: true
- id: t2
  title: /app:build checks the plan is on origin/main
  files: [plugins/app/commands/build.md]
  covers: [AC-050.2]
  parallel_safe: true
  depends_on: []
  done: true
- id: t3
  title: Contract tests
  files: [tests/cplat/test_spec_agents.py]
  covers: [AC-050.1, AC-050.2]
  parallel_safe: false
  depends_on: [t1, t2]
  done: true
---

## t1 — /app:plan pushes the spec branch and opens the PR

**Files:** plugins/app/commands/plan.md
**Covers:** AC-050.1
**Goal:** After a valid plan, ask, push `docs/spec-<id>`, open the PR (or print the command, spec 051).

**Implementation notes:**
- Replace 'only after asking' prose with the concrete push + PR step.

**Done when:** Command contains the step.

## t2 — /app:build checks the plan is on origin/main

**Files:** plugins/app/commands/build.md
**Covers:** AC-050.2
**Goal:** Pre-flight: `git fetch`; compare `docs/plan/<id>.md` with `origin/main`; differ or missing → say so and ask before using the local file.

**Implementation notes:**
- —

**Done when:** Command contains the check.

## t3 — Contract tests

**Files:** tests/cplat/test_spec_agents.py
**Covers:** AC-050.1, AC-050.2
**Goal:** Guard both steps.

**Implementation notes:**
- —

**Done when:** Tests pass.
