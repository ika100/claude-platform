---
spec_id: 022-see-what-is-deployed-where
title: See what is deployed where
status: done
priority: P1
---

# 022 — See what is deployed where

## Stories

As a founder, I want `/shared:status` in a gitops-app repo to show one table per product.

## Acceptance criteria

- **AC-022.1** Per service and environment: the pinned tag; CI state of each service's `main`; ArgoCD sync and health (`--context` selects the cluster). Addon health is included.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P1 · **Source:** CHANGELOG 2.0.0 · **Code:** `scripts/cplat/status.py`

## Changelog

- 2026-10-08 migrated from STORY-022 in docs/backlog.md
