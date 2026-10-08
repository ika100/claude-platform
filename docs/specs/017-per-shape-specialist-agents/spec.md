---
spec_id: 017-per-shape-specialist-agents
title: Per-shape specialist agents
status: done
priority: P0
---

# 017 — Per-shape specialist agents

## Stories

As an agent, I want idiomatic coder, tester, deployment, observability and release roles for each shape.

## Acceptance criteria

- **AC-017.1** `svc`, `web`, `svc-java` and `svc-go` each ship `coder`, `tester`, `deployment`, `observability` and `release`; `svc` also ships `product-manager`, `architect` and `migrations`.
- **AC-017.2** Deployment agents own the Dockerfile and CI image job only; they do not write Kubernetes manifests (ADR-017).
- **AC-017.3** The product-manager tags stories per repo for multi-repo features and folds client issues labelled `triage` into the backlog.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Source:** PRD B1..B3, E2

## Changelog

- 2026-10-08 migrated from STORY-017 in docs/backlog.md
