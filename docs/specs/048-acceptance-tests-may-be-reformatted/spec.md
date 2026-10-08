---
spec_id: 048-acceptance-tests-may-be-reformatted
title: Acceptance tests may be reformatted, never weakened
status: approved
priority: P1
---

# 048 — Acceptance tests may be reformatted, never weakened

## Problem

The tester's acceptance test file in todo-api failed ruff (import order, long lines). Because acceptance tests are fixed, the build stopped instead of running `lint-fix`; a human allowed the change and the agent compared the code before and after by hand.

## Stories

As a contributor, I want formatting fixes to acceptance tests to happen automatically and anything more to stop the build, so that lint never blocks a build and tests are never quietly weakened.

## Acceptance criteria

- **AC-048.1** Given acceptance tests that fail lint, when the build runs `devbox run lint-fix`, then it applies the formatting to them and continues.
- **AC-048.2** Given a change to an acceptance test file after Phase 1, when the build checks it, then a change that only alters formatting passes and any other change (assertion, value, removed test, criterion id) stops the build and asks the user.
- **AC-048.3** Given the check in AC-048.2, when it runs, then it is deterministic: `cplat spec test-diff` compares Python by token stream (ignoring import order) and other languages with all whitespace removed.

## Non-goals

- Formatting for languages without a tokenizer in cplat beyond whitespace comparison.

## Open questions

- ~~Compare Python by its token stream and other languages by whitespace-insensitive text, or require a per-shape formatter check? (suggested: Python tokens, others whitespace-insensitive; affects AC-048.3)~~ Answered: Python by token stream (import order ignored), other languages whitespace-insensitive.

## References

- [End-to-end run 2026-10-08, issue 6](../../e2e/2026-10-08-todo-spec-driven.md#issues-and-workarounds)

## Changelog

- 2026-10-08 created from issue 6 of the todo end-to-end run
- 2026-10-08 open question answered: Python by token stream (import order ignored), other languages whitespace-insensitive.
- 2026-10-08 approved
