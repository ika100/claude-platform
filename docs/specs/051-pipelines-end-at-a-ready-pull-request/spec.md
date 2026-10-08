---
spec_id: 051-pipelines-end-at-a-ready-pull-request
title: Pipelines end at a ready pull request
status: building
priority: P1
---

# 051 — Pipelines end at a ready pull request

## Problem

In headless and untrusted workspaces the template allowlist is ignored, but the `ask` list still applies, so agents cannot run `gh pr create`. In the todo run the operator opened five pull requests by hand from branches and body files the agents prepared when told to.

## Stories

As a founder, I want every pipeline to end with something I can open in one step, so that the human gate on pull requests costs seconds even when I was not watching.

## Acceptance criteria

- **AC-051.1** Given `/svc:build`, `/svc:quick-task`, `/svc:fix-bug` or `/app:build` where `gh pr create` is not allowed, when the pipeline reaches its PR step, then it pushes the branch, writes the PR body to a file and prints the exact `gh pr create` command, instead of stopping with an error.
- **AC-051.2** Given that fallback, when the final report is printed, then the command is its last line, and `/app:build` lists one command per repo.

## Non-goals

- Allowing agents to open pull requests without confirmation.

## Open questions

None.

## References

- [End-to-end run 2026-10-08, issue 9](../../e2e/2026-10-08-todo-spec-driven.md#issues-and-workarounds)

## Changelog

- 2026-10-08 created from issue 9 of the todo end-to-end run
- 2026-10-08 approved
- 2026-10-08 building
