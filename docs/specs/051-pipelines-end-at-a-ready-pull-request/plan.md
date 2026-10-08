---
spec_id: 051-pipelines-end-at-a-ready-pull-request
spec_hash: 9177164d4ce3
summary: Every pipeline ends with a ready PR command when PRs cannot be opened
tasks:
- id: t1
  title: PR fallback in the svc pipelines
  files: [plugins/svc/commands/build.md, plugins/svc/commands/quick-task.md, plugins/svc/commands/fix-bug.md]
  covers: [AC-051.1, AC-051.2]
  parallel_safe: true
  depends_on: []
  done: true
- id: t2
  title: PR fallback in /app:build
  files: [plugins/app/commands/build.md]
  covers: [AC-051.1, AC-051.2]
  parallel_safe: true
  depends_on: []
  done: true
- id: t3
  title: Contract tests
  files: [tests/cplat/test_spec_agents.py]
  covers: [AC-051.1, AC-051.2]
  parallel_safe: false
  depends_on: [t1, t2]
  done: true
---

## t1 — PR fallback in the svc pipelines

**Files:** plugins/svc/commands/build.md, plugins/svc/commands/quick-task.md, plugins/svc/commands/fix-bug.md
**Covers:** AC-051.1, AC-051.2
**Goal:** When `gh pr create` is denied, push the branch, write `.git/PR_BODY.md`, print `gh pr create … --body-file .git/PR_BODY.md` as the last line.

**Implementation notes:**
- One shared paragraph per command; the Final Report ends with the command.

**Done when:** Commands contain the fallback.

## t2 — PR fallback in /app:build

**Files:** plugins/app/commands/build.md
**Covers:** AC-051.1, AC-051.2
**Goal:** Repo agents use the same fallback; the wave table ends with one command per repo.

**Implementation notes:**
- —

**Done when:** Command contains it.

## t3 — Contract tests

**Files:** tests/cplat/test_spec_agents.py
**Covers:** AC-051.1, AC-051.2
**Goal:** Guard the fallback in all four commands.

**Implementation notes:**
- —

**Done when:** Tests pass.
