---
spec_id: 043-python-templates-pass-their-own-quality
title: Python templates pass their own quality gate
status: approved
priority: P0
---

# 043 — Python templates pass their own quality gate

## Problem

A freshly generated service-python repo was red on `main` in the todo run: `tracing.py` and `test_tracing.py` from the template break ruff E501/I001, so the bootstrap CI published no image until the first feature PR fixed the formatting. Platform CI renders the Python templates but never lints or tests them; only the local `devbox run smoke` does, while Go, web and Java are linted in CI.

## Stories

As a founder, I want every generated Python repo to start green, so that my first image is published by the bootstrap commit and the first feature PR only contains the feature.

## Acceptance criteria

- **AC-043.1** Given service-python rendered with `project_name=todo-api` (and with the defaults), when `devbox run quality` runs, then ruff and mypy report no error.
- **AC-043.2** Given library-python rendered the same way, when `devbox run quality` runs, then it reports no error.
- **AC-043.3** Given a pull request to the platform repo, when CI runs, then the rendered service-python and library-python are linted, type-checked and tested with uv (no devbox on the runner), and a lint error in either template fails the pull request; `devbox run smoke` remains the full local check.
- **AC-043.4** Given a repo created with `/shared:new-service <name> --type service-python`, when its first CI run on `main` finishes, then `quality` passes and the multi-arch image is published.

## Non-goals

- Changing the ruff rule set or line length of generated repos.

## Open questions

- ~~Should platform CI run the Python templates through devbox (identical to generated repos, slower) or through uv only? (suggested: uv only in CI; `devbox run smoke` stays the local full check; affects AC-043.3)~~ Answered: uv only in CI; devbox run smoke stays the full local check.

## References

- [End-to-end run 2026-10-08, issue 1](../../e2e/2026-10-08-todo-spec-driven.md#issues-and-workarounds)

## Changelog

- 2026-10-08 created from issue 1 of the todo end-to-end run
- 2026-10-08 open question answered: uv only in CI; devbox run smoke stays the full local check.
- 2026-10-08 approved
