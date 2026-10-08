---
spec_id: 028-manage-plan-lifecycle
title: Manage plan lifecycle
status: done
priority: P1
---

# 028 — Manage plan lifecycle

## Stories

As a founder, I want `/app:plans` to track a plan's progress.

## Acceptance criteria

- **AC-028.1** `list` shows `draft` and `in_progress` (`--all` includes terminal states); `show <slug>` shows a checklist; `start`, `done <slug> <repo-id>` and `abandon <slug>` apply the state machine `draft → in_progress → completed | abandoned`.
- **AC-028.2** The plan becomes `completed` when every repo is `done`.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P1 · **Source:** ADR-011

## Changelog

- 2026-10-08 migrated from STORY-028 in docs/backlog.md
