---
spec_id: 029-run-a-plan-in-parallel
title: Run a plan in parallel
status: done
priority: P1
---

# 029 — Run a plan in parallel

## Stories

As a founder, I want `/app:run-plan <slug>` to build every repo whose dependencies are done at the same time.

## Acceptance criteria

- **AC-029.1** `plan.py ready` computes the wave; one agent runs `/svc:build-feature --from-plan` per ready repo (`--max N` limits concurrency).
- **AC-029.2** Each repo ends at an open PR. The command merges only when told to and never pins images.
- **AC-029.3** A failure in one repo pauses its dependents and reports the state; the plan stays recoverable.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P1 · **Source:** ADR-023, CHANGELOG 3.2.0

## Changelog

- 2026-10-08 migrated from STORY-029 in docs/backlog.md
