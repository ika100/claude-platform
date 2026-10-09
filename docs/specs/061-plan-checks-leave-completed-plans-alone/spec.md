---
spec_id: 061-plan-checks-leave-completed-plans-alone
title: Plan checks leave completed plans alone
status: draft
priority: P1
---

# 061 — Plan checks leave completed plans alone

## Problem

Updating ika100/todo to platform 4.0.0 (end-to-end run 2, 2026-10-08) made `devbox run test-fast` fail right after `/shared:update-service`: v4's `scripts/plan.py` applies the rules of specs 045 and 053 (a `gitops:` list per repo, `### Errors` and `### Timeouts` in the contract) to the **completed** plan 001, written under 3.x. Its contract already had an error format and a 5 s timeout, just under other headings. Every gitops-app repo with finished plans breaks the same way on upgrade, and the only fix is editing history: a plan that will never run again.

## Stories

As a product owner upgrading the platform, I want finished plans to stay valid, so that an upgrade does not ask me to rewrite records of work that is done.

## Acceptance criteria

- **AC-061.1** Given a plan with status `completed` or `abandoned` that lacks `gitops:` lists or the `### Errors` / `### Timeouts` headings, when `plan.py validate` runs, then it passes (the structural checks that every plan needs, such as frontmatter keys and repo ids, still apply).
- **AC-061.2** Given a plan with status `draft` or `in_progress` that lacks them, when `plan.py validate` runs, then it fails as today.
- **AC-061.3** Given an active plan whose contract misses `### Errors` or `### Timeouts`, when `plan.py validate` fails, then the message names the missing heading and shows the exact heading line to add.
- **AC-061.4** Given ika100/todo's completed plan 001 as it was before the run-2 workaround, when the gitops-app template's `test-fast` runs after an update to the fixed version, then it passes (fixture test).

## Non-goals

- Migrating old plans to the new format automatically.
- Recognising error or timeout content under arbitrary headings.

## Open questions

- Should a completed plan that misses the new sections get a warning (printed, exit 0) so the gap stays visible, or be skipped silently? (suggested: one warning line per plan; affects AC-061.1)

## References

- [run 2 log](../../e2e/2026-10-09-todo-second-feature.md), finding 1.

## Changelog

- 2026-10-09 created from end-to-end run 2
