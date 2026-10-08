---
spec_id: 021-promote-images-through-environments
title: Promote images through environments
status: done
priority: P0
---

# 021 — Promote images through environments

## Stories

As a founder, I want `/gitops:promote <service...|--all> <from> <to>` to move a version up one environment.

## Acceptance criteria

- **AC-021.1** Pins an image tag only: staging `sha-<7>`, prod `X.Y.Z`. The tag is verified to exist in GHCR before the PR opens.
- **AC-021.2** One PR per invocation, including batches and `--all`. `--version vX.Y.Z` and `--sha <full-sha>` override the default.
- **AC-021.3** Works from inside the gitops-app repo or from a service repo via `.platform-app.yml`.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Source:** PRD B6, CHANGELOG 1.1.1, 2.0.0 · **Code:** `scripts/cplat/promote.py`

## Changelog

- 2026-10-08 migrated from STORY-021 in docs/backlog.md
