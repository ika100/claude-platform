---
spec_id: 026-guard-rails-before-merge-and-in-the
title: Guard rails before merge and in the cluster
status: done
priority: P2
---

# 026 — Guard rails before merge and in the cluster

## Stories

As a founder, I want security conventions enforced, so that a rendered manifest cannot break them.

## Acceptance criteria

- **AC-026.1** `policies:` in `app.yaml` renders namespaced Kyverno policies (numeric non-root, read-only filesystem, no escalation, dropped capabilities, no privileged).
- **AC-026.2** `devbox run validate` and CI evaluate rendered overlays and addons offline with the Kyverno CLI (checksum-pinned download).

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P2 · **Source:** ADR-022

## Changelog

- 2026-10-08 migrated from STORY-026 in docs/backlog.md
