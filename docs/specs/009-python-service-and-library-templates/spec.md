---
spec_id: 009-python-service-and-library-templates
title: Python service and library templates
status: done
priority: P0
---

# 009 — Python service and library templates

## Stories

As a founder, I want Python 3.12 / uv / FastAPI services and uv-distributed libraries.

## Acceptance criteria

- **AC-009.1** `service-python` serves `/health`, `/ready` and `/metrics` on port 8080, runs as numeric user 10001, and includes Alembic migrations scaffolding.
- **AC-009.2** `library-python` has no Dockerfile and no deployable topic; consumers install it via `git+https` with `uv` (ADR-016).

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Source:** PRD §4, ADR-016

## Changelog

- 2026-10-08 migrated from STORY-009 in docs/backlog.md
