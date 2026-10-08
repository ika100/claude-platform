---
spec_id: 014-build-a-feature-end-to-end
title: Build a feature end to end
status: done
priority: P0
---

# 014 — Build a feature end to end

## Stories

As a founder, I want `/svc:build-feature <description>` to take a request to an open PR.

## Acceptance criteria

- **AC-014.1** Phases: pre-flight → product-manager → architect → parallel coders → quality, tests and security in parallel → deployment/observability where the shape needs them.
- **AC-014.2** Every role is spawned with the subagent type from `cplat shape`, so a Go repo uses `svc-go:coder` and a web repo `web:tester`.
- **AC-014.3** The plan starts with a YAML block (`plan_id`, `shape`, `tasks[]` with `files`, `parallel_safe`, `depends_on`); tasks that are `parallel_safe` run in separate git worktrees and are merged back one by one with a quality gate between merges.
- **AC-014.4** Work happens on a `feature/*` branch; nothing is committed to `main`.
- **AC-014.5** `--no-pm` skips the product-manager phase; `--from-plan <plan> [<repo-id>]` takes the repo's `arguments` from a multi-repo plan.
- **AC-014.6** Agents run commands only through `devbox run <recipe>`.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Source:** PRD C1, ADR-008, ADR-023 · **Code:** `plugins/svc/commands/build-feature.md`

## Changelog

- 2026-10-08 migrated from STORY-014 in docs/backlog.md
