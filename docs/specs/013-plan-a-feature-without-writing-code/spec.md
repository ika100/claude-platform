---
spec_id: 013-plan-a-feature-without-writing-code
title: Plan a feature without writing code
status: done
priority: P0
---

# 013 — Plan a feature without writing code

## Stories

As a founder, I want `/svc:plan-feature <description>` to produce stories and a plan, so that I can review before anything is built.

## Acceptance criteria

- **AC-013.1** Refuses to run on a dirty working tree; prints the current branch and the resolved shape.
- **AC-013.2** Product-manager writes `docs/backlog.md`; architect writes `docs/plan/<slug>.md` (and ADRs when a decision is significant). No production code is written.
- **AC-013.3** Ends with a summary of tasks and acceptance criteria and points to `/svc:build-feature`.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Source:** `plugins/svc/commands/plan-feature.md`

## Changelog

- 2026-10-08 migrated from STORY-013 in docs/backlog.md
