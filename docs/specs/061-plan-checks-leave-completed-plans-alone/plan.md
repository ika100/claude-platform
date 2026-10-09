---
spec_id: 061-plan-checks-leave-completed-plans-alone
spec_hash: d69bbc4d86bc
summary: plan.py applies the 045/053 rules to active plans only and says which heading to add
tasks:
- id: t1
  title: Status-dependent rules and precise messages in plan.py
  files: [templates/gitops-app/scripts/plan.py, tests/cplat/test_plan.py, tests/cplat/fixtures/plans/001-todo-list.md, tests/cplat/fixtures/specs/001-todo-list/spec.md]
  covers: [AC-061.1, AC-061.2, AC-061.3, AC-061.4]
  parallel_safe: true
  depends_on: []
  done: true
- id: t2
  title: Changelog
  files: [docs/CHANGELOG.md]
  covers: [AC-061.1]
  parallel_safe: false
  depends_on: [t1]
  done: true
---

## t1 — Status-dependent rules and precise messages in plan.py

**Files:** templates/gitops-app/scripts/plan.py, tests/cplat/test_plan.py, tests/cplat/fixtures/plans/001-todo-list.md, tests/cplat/fixtures/specs/001-todo-list/spec.md
**Covers:** AC-061.1, AC-061.2, AC-061.3, AC-061.4
**Goal:** Finished plans pass with one warning; active plans fail as today, with messages that say what to add.

**Implementation notes:**
- `check()` returns `(errors, warnings)`; `check_gitops` and `check_contract` feed warnings for `completed`/`abandoned`.
- `validate`: print warnings (one line per plan), exit on errors only.
- Fixture from ika100/todo `b7feaf8` (plan 001 before the run-2 hand edit), named `001-todo-list.md`.

**Done when:** Tests: completed plan without gitops list or headings → exit 0 with one warning; the same plan as `in_progress` → exit 1; the message for a missing `### Timeouts` contains the line to add; the fixture passes in a rendered gitops-app.

## t2 — Changelog

**Files:** docs/CHANGELOG.md
**Covers:** AC-061.1
**Goal:** Upgraders know old plans pass now.

**Implementation notes:**
- `[Unreleased]` entry, linking the run-2 log.

**Done when:** Entry present; links resolve.
