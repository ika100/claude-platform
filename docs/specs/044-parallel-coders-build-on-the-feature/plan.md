---
spec_id: 044-parallel-coders-build-on-the-feature
spec_hash: c2bd9c148148
summary: Parallel coders start from the feature branch
tasks:
- id: t1
  title: Set worktree.baseRef to head in every template
  files: [templates/service-python/.claude/settings.json, templates/library-python/.claude/settings.json, templates/web-nextjs/.claude/settings.json.jinja,
    templates/service-java/.claude/settings.json.jinja, templates/service-go/.claude/settings.json.jinja, templates/gitops-app/.claude/settings.json.jinja,
    scripts/shapes.py]
  covers: [AC-044.1, AC-044.2]
  parallel_safe: true
  depends_on: []
  done: true
- id: t2
  title: Assert the worktree base in the build's probe
  files: [plugins/svc/commands/build.md]
  covers: [AC-044.3, AC-044.4]
  parallel_safe: true
  depends_on: []
  done: true
- id: t3
  title: Tests for the template setting and the probe rule
  files: [tests/cplat/test_spec_driven.py, tests/cplat/test_spec_agents.py]
  covers: [AC-044.1, AC-044.2, AC-044.3]
  parallel_safe: false
  depends_on: [t1, t2]
  done: true
---

## t1 — Set worktree.baseRef to head in every template

**Files:** templates/service-python/.claude/settings.json, templates/library-python/.claude/settings.json, templates/web-nextjs/.claude/settings.json.jinja, templates/service-java/.claude/settings.json.jinja, templates/service-go/.claude/settings.json.jinja, templates/gitops-app/.claude/settings.json.jinja, scripts/shapes.py
**Covers:** AC-044.1, AC-044.2
**Goal:** Subagent worktrees in generated repos branch from the orchestrator's HEAD (the feature branch).

**Implementation notes:**
- Add `"worktree": {"baseRef": "head"}` to each template's `.claude/settings.json(.jinja)`.
- `shapes.py check_contract` fails a template whose settings lack it.

**Done when:** `uv run scripts/shapes.py check` passes and fails when the key is removed from one template.

## t2 — Assert the worktree base in the build's probe

**Files:** plugins/svc/commands/build.md
**Covers:** AC-044.3, AC-044.4
**Goal:** Phase 2.2 of `/svc:build` verifies that the probe worktree starts at `$FEATURE_HEAD`; otherwise it runs sequentially and says why.

**Implementation notes:**
- The probe agent reports `git rev-parse HEAD` of its worktree; the orchestrator compares it with `git rev-parse HEAD` before the batch.
- Mismatch → sequential fallback with the reason `worktree base is <sha>, not the feature head; set worktree.baseRef: "head" (/shared:update-service)`.
- Merging a task branch: document that it contains only the task's commits because it started at the feature head.

**Done when:** The build command text contains the base assertion and the fallback reason.

## t3 — Tests for the template setting and the probe rule

**Files:** tests/cplat/test_spec_driven.py, tests/cplat/test_spec_agents.py
**Covers:** AC-044.1, AC-044.2, AC-044.3
**Goal:** Regression tests for the contract.

**Implementation notes:**
- `test_spec_driven.py`: every template's settings set `worktree.baseRef` to `head`.
- `test_spec_agents.py`: `build.md` asserts the worktree base and names the fallback.

**Done when:** Both tests pass.
