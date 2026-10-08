---
spec_id: 045-multi-repo-builds-handle-the-gitops-app
spec_hash: 2d81574a4e81
summary: The gitops entry of a product plan is built from structured operations
tasks:
- id: t1
  title: Add `cplat compose set` to change an existing service
  files: [scripts/cplat/compose.py, tests/cplat/test_gitops.py]
  covers: [AC-045.1]
  parallel_safe: true
  depends_on: []
- id: t2
  title: Validate `gitops:` operations in plan.py
  files: [templates/gitops-app/scripts/plan.py, tests/cplat/test_plan.py]
  covers: [AC-045.2]
  parallel_safe: true
  depends_on: []
- id: t3
  title: Planner writes the operations; /app:build runs them
  files: [plugins/app/agents/planner.md, plugins/app/commands/build.md, docs/adr/011-multi-repo-plan-format.md]
  covers: [AC-045.1, AC-045.3, AC-045.4]
  parallel_safe: false
  depends_on: [t1, t2]
- id: t4
  title: Contract tests for the gitops entry
  files: [tests/cplat/test_spec_agents.py]
  covers: [AC-045.1, AC-045.3, AC-045.4]
  parallel_safe: false
  depends_on: [t3]
---

## t1 — Add `cplat compose set` to change an existing service

**Files:** scripts/cplat/compose.py, tests/cplat/test_gitops.py
**Covers:** AC-045.1
**Goal:** Operations on services that already run (env, exposure, addon use) need an update path; `compose add` refuses existing services.

**Implementation notes:**
- New action `set <service>` taking the same `--env`, `--expose`, `--uses` options; merges into the existing entry and re-renders.
- Refuses an unknown service with the list of known ones; `--dry-run` shows the diff.

**Done when:** Tests: set adds env, exposure and uses to an existing entry; unknown service is refused; render output contains the new env.

## t2 — Validate `gitops:` operations in plan.py

**Files:** templates/gitops-app/scripts/plan.py, tests/cplat/test_plan.py
**Covers:** AC-045.2
**Goal:** `plan-check` accepts a `gitops:` list on the gitops-app repo entry and rejects unknown operations or services.

**Implementation notes:**
- Operations per design.md: `addon`, `uses`, `expose`, `env`; each names a service from services.yaml or another repo of the plan.
- A gitops-app entry needs `gitops:` (and may have `acs`).

**Done when:** New tests in `test_plan.py` for a valid list, an unknown operation and an unknown service.

## t3 — Planner writes the operations; /app:build runs them

**Files:** plugins/app/agents/planner.md, plugins/app/commands/build.md, docs/adr/011-multi-repo-plan-format.md
**Covers:** AC-045.1, AC-045.3, AC-045.4
**Goal:** The planner emits the gitops entry with operations; `/app:build` executes them in the gitops repo with `cplat addon add` and `cplat compose set`, ends at a branch + PR (or command), says to merge it first, and removes any worktree it created.

**Implementation notes:**
- `/app:build`: the gitops entry is not given to a repo agent; the orchestrator runs it in its own repo on `compose/<spec_id>`.
- Final table marks the gitops PR as `merge first`.
- ADR-011 amendment: the `gitops:` operations.

**Done when:** Command and agent text contain the rules; `test_spec_agents.py` assertions in t4.

## t4 — Contract tests for the gitops entry

**Files:** tests/cplat/test_spec_agents.py
**Covers:** AC-045.1, AC-045.3, AC-045.4
**Goal:** Guard the command contract.

**Implementation notes:**
- `/app:build` names `cplat compose set`, `merge first` and `git worktree remove`; the planner shows a `gitops:` example.

**Done when:** Tests pass.
