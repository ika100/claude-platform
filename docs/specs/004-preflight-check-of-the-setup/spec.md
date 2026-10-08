---
spec_id: 004-preflight-check-of-the-setup
title: Preflight check of the setup
status: done
priority: P1
---

# 004 — Preflight check of the setup

## Stories

As a founder, I want `/shared:doctor` to check my machine and repo, so that I find problems before a command fails midway.

## Acceptance criteria

- **AC-004.1** Checks tools, `gh` scopes, Docker, kube context (warns on a non-local context), installed plugin versions, and the repo's platform version.
- **AC-004.2** Every problem comes with a concrete fix. A plugin installed under the old marketplace id gets the migration steps. Missing cluster operators (ESO, CloudNativePG, Kyverno) are warned about only when the app uses them.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P1 · **Source:** CHANGELOG 2.0.0 · **Code:** `scripts/cplat/doctor.py`

## Changelog

- 2026-10-08 migrated from STORY-004 in docs/backlog.md
