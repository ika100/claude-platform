---
spec_id: 055-template-action-pins-match-the-platform
title: Template action pins match the platform
status: approved
priority: P2
---

# 055 — Template action pins match the platform

## Problem

The templates pin `actions/checkout` v5 while the platform uses v7, so Dependabot opened an update PR in every new todo repo within a minute of its creation.

## Stories

As a founder, I want new repos to start without dependency PRs, so that the first thing I review is my own feature.

## Acceptance criteria

- **AC-055.1** Given the platform's workflows and every template's workflows, when the platform checks run, then each action is pinned to the same commit everywhere, and a mismatch fails the check.
- **AC-055.2** Given an action update in the platform, when the pin update runs, then it updates the templates in the same pull request.

## Non-goals

- None.

## Open questions

None.

## References

- [End-to-end run 2026-10-08, issue 13](../../e2e/2026-10-08-todo-spec-driven.md#issues-and-workarounds)

## Changelog

- 2026-10-08 created from issue 13 of the todo end-to-end run
- 2026-10-08 approved
