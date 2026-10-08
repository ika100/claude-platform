---
spec_id: 052-repo-specs-know-the-gitops-wiring
spec_hash: ad43c3277f43
summary: Repo spec slices carry the gitops wiring
tasks:
- id: t1
  title: slice_from_plan lists the wiring for the repo
  files: [scripts/cplat/spec.py, tests/cplat/test_spec.py]
  covers: [AC-052.1]
  parallel_safe: true
  depends_on: []
  done: true
- id: t2
  title: Build reports only missing wiring
  files: [plugins/svc/commands/build.md, tests/cplat/test_spec_agents.py]
  covers: [AC-052.2]
  parallel_safe: false
  depends_on: [t1]
  done: true
---

## t1 — slice_from_plan lists the wiring for the repo

**Files:** scripts/cplat/spec.py, tests/cplat/test_spec.py
**Covers:** AC-052.1
**Goal:** The Product context gets a 'Provided by the product' list: env vars, addons (with their env contract, e.g. postgres → DATABASE_URL, PG*), exposure, from the gitops entry's operations (spec 045).

**Implementation notes:**
- Read `gitops:` operations of the plan; keep those whose service is the repo id; addon env names from the addon contract (ADR-020).

**Done when:** Tests: the slice for todo-api lists DATABASE_URL and PG*; todo-web lists TODO_API_URL and its host; a plan without gitops ops adds nothing.

## t2 — Build reports only missing wiring

**Files:** plugins/svc/commands/build.md, tests/cplat/test_spec_agents.py
**Covers:** AC-052.2
**Goal:** Phase 5 / Final Report: ask for gitops changes only for env, ports or addons not listed under 'Provided by the product'.

**Implementation notes:**
- —

**Done when:** Command text and a contract test.
