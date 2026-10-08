---
spec_id: 047-builds-resume-after-an-interruption
spec_hash: af8247a36b24
summary: /svc:build resumes cleanly after an interruption
tasks:
- id: t1
  title: Resume pre-flight in /svc:build
  files: [plugins/svc/commands/build.md]
  covers: [AC-047.1, AC-047.2, AC-047.3, AC-047.4]
  parallel_safe: true
  depends_on: []
  done: true
- id: t2
  title: Contract tests for resume
  files: [tests/cplat/test_spec_agents.py]
  covers: [AC-047.1, AC-047.2, AC-047.3, AC-047.4]
  parallel_safe: false
  depends_on: [t1]
  done: true
---

## t1 — Resume pre-flight in /svc:build

**Files:** plugins/svc/commands/build.md
**Covers:** AC-047.1, AC-047.2, AC-047.3, AC-047.4
**Goal:** Phase 0 distinguishes a dirty tree on a `building` spec (resume) from any other dirty tree (stop).

**Implementation notes:**
- Resume: list `git status --porcelain`; unstage index entries that differ from both HEAD and the working tree (`git restore --staged <files>`), naming them; commit the rest as `wip(<task-id>): interrupted` for the first task not `done` (ask; directly when unattended); pass `git show --stat HEAD` and the diff to that task's coder.
- Not building: unchanged clean-tree stop.
- Phase 7: when the branch has `wip(` commits, the PR body says to squash-merge.

**Done when:** Command text contains the four rules.

## t2 — Contract tests for resume

**Files:** tests/cplat/test_spec_agents.py
**Covers:** AC-047.1, AC-047.2, AC-047.3, AC-047.4
**Goal:** Guard the rules.

**Implementation notes:**
- Assert `wip(<task-id>): interrupted`, `git restore --staged`, the not-building stop and the squash note.

**Done when:** Tests pass.
