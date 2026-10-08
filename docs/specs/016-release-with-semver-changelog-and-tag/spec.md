---
spec_id: 016-release-with-semver-changelog-and-tag
title: Release with semver, changelog and tag
status: done
priority: P0
---

# 016 — Release with semver, changelog and tag

## Stories

As a founder, I want `/svc:release` to cut a release for any shape.

## Acceptance criteria

- **AC-016.1** Runs quality, tests and security first, then a per-plugin `release` agent bumps the version (Python `pyproject.toml`, Java `pom.xml` via `versions:set`, Go has no version file, web `package.json`), writes the changelog and opens a PR from `release/vX.Y.Z`.
- **AC-016.2** The release agent never commits to `main` and never creates the tag; the orchestrator tags after the PR merges.
- **AC-016.3** The tag triggers a semver-tagged image publish (`X.Y.Z`).

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Source:** ADR-012, PRD C3

## Changelog

- 2026-10-08 migrated from STORY-016 in docs/backlog.md
