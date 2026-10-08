---
spec_id: 054-new-repos-protect-main
title: New repos protect main
status: approved
priority: P2
---

# 054 — New repos protect main

## Problem

The generated `CLAUDE.md` says `main` is protected, but `/shared:new-service` and `/shared:new-app` do not set branch protection; in the todo run a pull request was merged before its checks finished.

## Stories

As a founder, I want `main` of every new repo protected by its required checks, so that nothing reaches the images and the cluster without passing CI.

## Acceptance criteria

- **AC-054.1** Given `/shared:new-service` or `/shared:new-app` with GitHub available, when it creates a repo, then `main` requires the shape's CI checks before merging (no review requirement), and the preview lists this as an outward step.
- **AC-054.2** Given an account or plan where protection cannot be set, when the repo is created, then the command warns, prints the manual step, and still succeeds.

## Non-goals

- None.

## Open questions

- ~~Require pull request reviews too, or only status checks? (suggested: status checks only; solo founders cannot approve their own PRs; affects AC-054.1)~~ Answered: status checks only; no review requirement (solo founders cannot approve their own PRs).

## References

- [End-to-end run 2026-10-08, issue 12](../../e2e/2026-10-08-todo-spec-driven.md#issues-and-workarounds)

## Changelog

- 2026-10-08 created from issue 12 of the todo end-to-end run
- 2026-10-08 open question answered: status checks only; no review requirement (solo founders cannot approve their own PRs).
- 2026-10-08 approved
