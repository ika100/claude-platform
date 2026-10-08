---
spec_id: 053-contracts-settle-cross-repo-details
spec_hash: 7efe795ad95e
summary: Contracts must state errors and timeouts
tasks:
- id: t1
  title: plan-check requires errors and timeouts in multi-repo contracts
  files: [templates/gitops-app/scripts/plan.py, tests/cplat/test_plan.py]
  covers: [AC-053.1]
  parallel_safe: true
  depends_on: []
- id: t2
  title: Planner instructions
  files: [plugins/app/agents/planner.md]
  covers: [AC-053.2]
  parallel_safe: true
  depends_on: []
---

## t1 — plan-check requires errors and timeouts in multi-repo contracts

**Files:** templates/gitops-app/scripts/plan.py, tests/cplat/test_plan.py
**Covers:** AC-053.1
**Goal:** For plans with ≥ 2 repos and `spec:`, the `## Contract` section (or design.md's) must have `### Errors` and `### Timeouts` subsections; missing ones are reported by name.

**Implementation notes:**
- —

**Done when:** Tests: missing Errors, missing Timeouts, both present, single-repo plan exempt.

## t2 — Planner instructions

**Files:** plugins/app/agents/planner.md
**Covers:** AC-053.2
**Goal:** The contract step asks for the error format, timeout and unavailable behaviour per call, and the handling of unlisted responses, under those two headings.

**Implementation notes:**
- —

**Done when:** Agent text contains the three items.
