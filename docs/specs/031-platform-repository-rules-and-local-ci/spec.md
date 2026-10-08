---
spec_id: 031-platform-repository-rules-and-local-ci
title: Platform repository rules and local CI
status: done
priority: P1
---

# 031 — Platform repository rules and local CI

## Stories

As a maintainer, I want changes to the shared source of truth to be checked before they reach every downstream repo.

## Acceptance criteria

- **AC-031.1** `main` requires a pull request and the single status `ci-success`; commits are DCO signed-off (`git commit -s`, `scripts/check-dco.py`).
- **AC-031.2** `devbox run validate` checks `marketplace.json`, every `plugin.json` and `hooks.json`; plugin versions match between the marketplace and each manifest.
- **AC-031.3** The CI runs only the jobs a change needs (docs-only changes run the validation jobs only); `scripts/ci-local.sh` runs the cheap checks locally; Markdown links are checked.
- **AC-031.4** A weekly job bumps template dependency pins, verifies by re-rendering, and opens a PR; it never bumps `packageManager`.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P1 · **Source:** CONTRIBUTING.md, CHANGELOG 2.2.0, 3.0.0, 3.2.0 · **Code:** `scripts/ci-local.sh`, `scripts/check-*.py`, `scripts/bump_template_pins.py`

## Changelog

- 2026-10-08 migrated from STORY-031 in docs/backlog.md
