---
spec_id: 053-contracts-settle-cross-repo-details
title: Contracts settle cross-repo details
status: done
priority: P2
---

# 053 — Contracts settle cross-repo details

## Problem

Each todo repo spec raised one more question that belonged to the contract between repos (how fast todo-api answers when its database is down; how the web app treats a response the contract does not list), costing one round-trip per repo.

## Stories

As a founder, I want the plan's contract to answer the questions every repo would otherwise ask, so that the per-repo specs need no extra round of answers.

## Acceptance criteria

- **AC-053.1** Given a plan with two or more repos, when `plan-check` runs, then it requires a `## Contract` section with error responses and timeouts, and reports which are missing.
- **AC-053.2** Given the planner's instructions, when it writes the contract, then they ask for the error format, the timeout and unavailable behaviour of every call, and how a caller treats responses the contract does not list.

## Non-goals

- None.

## Open questions

None.

## References

- [End-to-end run 2026-10-08, issue 11](../../e2e/2026-10-08-todo-spec-driven.md#issues-and-workarounds)

## Changelog

- 2026-10-08 created from issue 11 of the todo end-to-end run
- 2026-10-08 approved
- 2026-10-08 building
- 2026-10-08 done
