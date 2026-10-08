---
spec_id: 050-product-spec-and-plan-reach-main
title: Product spec and plan reach main
status: approved
priority: P1
---

# 050 — Product spec and plan reach main

## Problem

`/app:spec` and `/app:plan` commit on a local `docs/spec-<id>` branch and never push it; `/app:build` read the local plan file. In the todo run the spec and plan reached GitHub only because the operator pushed them and opened the PR.

## Stories

As a founder, I want the approved product spec and its plan on `main`, so that everyone (and every agent in a fresh clone) builds from the same reviewed plan.

## Acceptance criteria

- **AC-050.1** Given `/app:plan` has written a valid plan, when it finishes, then it pushes `docs/spec-<id>` and opens a pull request (or prints its exact `gh pr create` command when that is not allowed), after asking.
- **AC-050.2** Given `/app:build <id>`, when the plan file differs from `origin/main` or is missing there, then it says so before starting and asks whether to continue from the local file.

## Non-goals

- None.

## Open questions

None.

## References

- [End-to-end run 2026-10-08, issue 8](../../e2e/2026-10-08-todo-spec-driven.md#issues-and-workarounds)

## Changelog

- 2026-10-08 created from issue 8 of the todo end-to-end run
- 2026-10-08 approved
