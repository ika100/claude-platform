---
spec_id: 057-spec-check-says-what-happened
title: spec-check says what happened
status: building
priority: P2
---

# 057 — spec-check says what happened

## Problem

When a repo's platform ref already is `main`, the spec-check script still printed "platform main predates spec checks (ADR-026); using main".

## Stories

As a contributor, I want CI messages that state what happened, so that I trust the check and do not investigate noise.

## Acceptance criteria

- **AC-057.1** Given a ref of `main` whose platform has no spec checks, when `scripts/spec-check.sh` runs, then it prints one line saying the platform has no spec checks yet and that the check was skipped.
- **AC-057.2** Given a release tag older than the spec checks, when the script runs, then it says that tag predates them and that it uses `main`.

## Non-goals

- None.

## Open questions

None.

## References

- [End-to-end run 2026-10-08, issue 15](../../e2e/2026-10-08-todo-spec-driven.md#issues-and-workarounds)

## Changelog

- 2026-10-08 created from issue 15 of the todo end-to-end run
- 2026-10-08 approved
- 2026-10-08 building
