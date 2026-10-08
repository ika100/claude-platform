---
spec_id: 046-unattended-builds-survive-long-runs
title: Unattended builds survive long runs
status: done
priority: P1
---

# 046 — Unattended builds survive long runs

## Problem

Headless Claude Code (`claude -p`) stops background subagents after 600 seconds. `/app:build` started its repo agents in the background, so the unattended todo build was cut off mid-task after 10 minutes; it continued only with `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS=0`.

## Stories

As a founder, I want `/app:build` to finish when nobody watches it, so that scheduled and headless runs end at open PRs instead of half-done branches.

## Acceptance criteria

- **AC-046.1** Given a headless `/app:build` whose repo builds take longer than 10 minutes, when it runs without extra environment variables, then no repo agent is terminated before it reports (the repo agents run as parallel foreground calls in one message and the orchestrator waits for all of them).
- **AC-046.2** Given the documentation for unattended runs (`/loop`, `/schedule`, CI), when a user reads it, then it names `CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS` and when it is needed.

## Non-goals

- Changing Claude Code's print-mode defaults.

## Open questions

- ~~Run the repo agents as parallel foreground Agent calls in one message (waits for all, still parallel) instead of background agents? (suggested: yes; affects AC-046.1)~~ Answered: yes: parallel foreground Agent calls in one message; the env var is documented for other unattended uses.

## References

- [End-to-end run 2026-10-08, issue 4](../../e2e/2026-10-08-todo-spec-driven.md#issues-and-workarounds)

## Changelog

- 2026-10-08 created from issue 4 of the todo end-to-end run
- 2026-10-08 open question answered: yes: parallel foreground Agent calls in one message; the env var is documented for other unattended uses.
- 2026-10-08 approved
- 2026-10-08 building
- 2026-10-08 done
