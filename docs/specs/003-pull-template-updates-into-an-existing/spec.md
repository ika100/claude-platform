---
spec_id: 003-pull-template-updates-into-an-existing
title: Pull template updates into an existing repo safely
status: done
priority: P0
---

# 003 — Pull template updates into an existing repo safely

## Stories

As a founder, I want `/shared:update-service` to bring the latest skeleton (CI, Dockerfile, devbox recipes, CLAUDE.md) into my repo, so that fixes propagate without losing my work.

## Acceptance criteria

- **AC-003.1** Changes land on a review branch (unique name if today's already exists), never on `main`.
- **AC-003.2** Files in a template's `_skip_if_exists` (dependency manifests, app code, tests, project docs) are never overwritten, and new files copier would add inside those paths are removed and reported.
- **AC-003.3** The report lists overwritten skeleton files and the changelog range since the repo's `.platform-version`.
- **AC-003.4** `--ref <tag>` pins a platform version; `--data k=v` changes template options; `--migrate` converts a v1 repo (removes `k8s/`).
- **AC-003.5** A test asserts that every template protects its dependency manifest.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Source:** PRD D2, CHANGELOG 0.5.0, 3.0.1, 3.0.2 · **Code:** `scripts/cplat/update.py`

## Changelog

- 2026-10-08 migrated from STORY-003 in docs/backlog.md
