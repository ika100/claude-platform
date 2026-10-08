---
spec_id: 047-builds-resume-after-an-interruption
title: Builds resume after an interruption
status: approved
priority: P1
---

# 047 — Builds resume after an interruption

## Problem

When the todo-api build was interrupted, its coder left uncommitted files and a stale index (five bootstrap files staged at old versions). The resumed `/svc:build` refused the dirty tree; the operator had to tell it to commit the work as WIP, and the agent had to notice the stale index by itself.

## Stories

As a contributor, I want `/svc:build <id>` to pick up an interrupted build without manual git surgery, so that a crash or timeout costs minutes, not a restart.

## Acceptance criteria

- **AC-047.1** Given a spec with status `building` and a dirty working tree, when `/svc:build <id>` starts, then it commits the changes as `wip(<task-id>): interrupted` for the first task not `done` (after confirmation, or directly when the run is unattended) and resumes that task with the WIP diff as context.
- **AC-047.2** Given staged index entries that differ from both HEAD and the working tree, when the build resumes, then it unstages them before committing and says which files were affected.
- **AC-047.3** Given a dirty tree on a spec that is not `building`, when `/svc:build` starts, then it still stops with the clean-tree message.
- **AC-047.4** Given WIP commits on the feature branch, when the pull request is opened, then its body says to squash-merge.

## Non-goals

- Resuming a task in the middle of a coder's reasoning.

## Open questions

None.

## References

- [End-to-end run 2026-10-08, issue 5](../../e2e/2026-10-08-todo-spec-driven.md#issues-and-workarounds)

## Changelog

- 2026-10-08 created from issue 5 of the todo end-to-end run
- 2026-10-08 approved
