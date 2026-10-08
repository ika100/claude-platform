---
spec_id: 049-spec-documents-do-not-break-the-python
title: Spec documents do not break the Python lint
status: draft
priority: P1
---

# 049 — Spec documents do not break the Python lint

## Problem

ruff also formats Python code blocks in Markdown, so the architect's `design.md` in todo-api failed `devbox run quality` and needed its own formatting commit.

## Stories

As a contributor, I want specs and designs to be free-form documentation, so that writing an example in `design.md` never breaks CI.

## Acceptance criteria

- **AC-049.1** Given a generated Python repo with a `docs/specs/<id>/design.md` containing unformatted Python code blocks, when `devbox run quality` runs, then it passes.
- **AC-049.2** Given the Python templates, when their ruff configuration is read, then `docs/` is excluded from lint and format.

## Non-goals

- Linting code examples in documentation.

## Open questions

None.

## References

- [End-to-end run 2026-10-08, issue 7](../../e2e/2026-10-08-todo-spec-driven.md#issues-and-workarounds)

## Changelog

- 2026-10-08 created from issue 7 of the todo end-to-end run
