---
spec_id: 036-plans-are-approved-before-they-are-built
title: Plans are approved before they are built
status: superseded
priority: P2
---

# 036 — Plans are approved before they are built

## Stories

As a founder, I want a plan to be explicitly approved before `build-feature` consumes it, so that the review step between planning and building is real and recorded.

## Acceptance criteria

- **AC-036.1** `/svc:plan-feature` writes `status: draft` into the plan metadata and its closing message says how to approve (review the files, then confirm).
- **AC-036.2** Approving sets `status: approved` (a one-line edit by the user or by `/svc:plan-feature --approve <slug>`), recorded in git history.
- **AC-036.3** `/svc:build-feature --plan <path>` refuses a plan that is not `approved` and says how to approve it; without `--plan` the command is unchanged.
- **AC-036.4** The multi-repo plan lifecycle of ADR-011 (`draft` → `in_progress` → `completed`) is unchanged; this status belongs to single-repo plans only, and the docs say how the two differ.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done (superseded by STORY-037/039: specs are approved, plans are checked against them) · **Priority:** P2 · **Depends on:** STORY-034 · **Source:** decision 2026-10-07

## Changelog

- 2026-10-08 migrated from STORY-036 in docs/backlog.md
