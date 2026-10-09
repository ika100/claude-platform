---
spec_id: 063-acceptance-test-diff-looks-only-at-test
title: Acceptance-test diff looks only at test files
status: building
priority: P1
---

# 063 — Acceptance-test diff looks only at test files

## Problem

`cplat spec test-diff` (spec 048) protects acceptance tests: during a build it fails when a test that names a criterion changed beyond formatting. Without explicit files it selects every changed file that names a criterion of a `building` spec, and that includes `docs/specs/<id>/plan.md`, which names criteria in each task's `covers:`. After `cplat spec task-done` writes `done: true` the check fails. In end-to-end run 2 it failed this way in both todo-api and todo-web; the agents judged it a false alarm and continued. A safety check that cries wolf teaches agents to ignore it.

## Stories

As a reviewer, I want the acceptance-test check to fire only when an acceptance test changed, so that its failures are worth stopping for.

## Acceptance criteria

- **AC-063.1** Given a build where only `plan.md`, `spec.md`, `design.md` or `verification.md` changed since the base, when `cplat spec test-diff` runs without files, then it reports "no acceptance test changed" and exits 0.
- **AC-063.2** Given a changed file under the repo shape's `test_globs` that names a criterion and changed beyond formatting, when `cplat spec test-diff` runs, then it fails as today.
- **AC-063.3** Given a repo without a recorded shape, when `cplat spec test-diff` runs without files, then it never selects files under `docs/`.
- **AC-063.4** Given the build commands and agents, when `test-diff` fails, then they stop and report instead of judging it themselves (unchanged rule, now tested against `/svc:build`'s text).

## Non-goals

- Changing what counts as formatting (spec 048).

## Open questions

- None.

## References

- [run 2 log](../../e2e/2026-10-09-todo-second-feature.md), finding 4. Spec 048.

## Changelog

- 2026-10-09 created from end-to-end run 2
- 2026-10-09 approved
- 2026-10-09 building
