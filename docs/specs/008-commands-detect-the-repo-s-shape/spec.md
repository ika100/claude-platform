---
spec_id: 008-commands-detect-the-repo-s-shape
title: Commands detect the repo's shape
status: done
priority: P0
---

# 008 — Commands detect the repo's shape

## Stories

As an agent, I want `cplat shape` to tell me the shape and which subagent type to use for each role, so that I route work correctly.

## Acceptance criteria

- **AC-008.1** The shape comes from `_src_path` in `.copier-answers.yml`; if absent, from sniffing (`next.config.*` → web; `pyproject.toml` + `Dockerfile` → service-python; `pyproject.toml` without `Dockerfile` → library-python; `applications/*/applicationset.yaml` → gitops-app; and so on).
- **AC-008.2** Output is JSON with `shape`, `plugin`, `deployable`, `library` and `agents` (role → subagent type). Roles a shape lacks (for example deployment for a library) are absent.
- **AC-008.3** An unknown repo returns `unsupported` and the commands stop with that message.
- **AC-008.4** `scripts/test-detect-shape.sh` covers the fixtures.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Source:** ADR-008 · **Code:** `scripts/detect-shape.sh`, `scripts/cplat/shapecmd.py`

## Changelog

- 2026-10-08 migrated from STORY-008 in docs/backlog.md
