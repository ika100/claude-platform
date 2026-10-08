---
spec_id: 046-unattended-builds-survive-long-runs
spec_hash: 74d61dc76b59
summary: Repo agents run as parallel foreground calls; unattended runs are documented
tasks:
- id: t1
  title: Foreground repo agents in /app:build
  files: [plugins/app/commands/build.md]
  covers: [AC-046.1]
  parallel_safe: true
  depends_on: []
  done: true
- id: t2
  title: Document unattended runs
  files: [docs/ADOPTING.md, tests/cplat/test_spec_agents.py]
  covers: [AC-046.2, AC-046.1]
  parallel_safe: false
  depends_on: [t1]
  done: true
---

## t1 — Foreground repo agents in /app:build

**Files:** plugins/app/commands/build.md
**Covers:** AC-046.1
**Goal:** The wave's repo agents start in one message without `run_in_background`, so the orchestrator waits for all and print mode's background ceiling does not apply.

**Implementation notes:**
- Replace 'start one subagent per ready repo' wording with explicit foreground parallel Agent calls; forbid background agents.

**Done when:** The command states foreground parallel calls.

## t2 — Document unattended runs

**Files:** docs/ADOPTING.md, tests/cplat/test_spec_agents.py
**Covers:** AC-046.2, AC-046.1
**Goal:** A section 'Unattended runs' names `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS`, `--permission-mode`, workspace trust and the PR fallback (spec 051).

**Implementation notes:**
- Test asserts the command forbids background agents and the doc names the variable.

**Done when:** Tests pass.
