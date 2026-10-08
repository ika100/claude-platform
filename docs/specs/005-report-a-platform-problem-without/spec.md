---
spec_id: 005-report-a-platform-problem-without
title: Report a platform problem without leaking secrets
status: done
priority: P2
---

# 005 — Report a platform problem without leaking secrets

## Stories

As a contributor, I want `/shared:report-issue` to draft a GitHub issue with diagnostics, so that platform bugs reach the maintainer.

## Acceptance criteria

- **AC-005.1** Nothing is sent without explicit confirmation.
- **AC-005.2** Secrets are removed from the diagnostics.
- **AC-005.3** Every agent and command tells Claude to stop and offer this when a platform template, script or command misbehaves.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P2 · **Source:** CHANGELOG 2.2.0 · **Code:** `scripts/cplat/feedback.py`

## Changelog

- 2026-10-08 migrated from STORY-005 in docs/backlog.md
