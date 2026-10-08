---
spec_id: 039-svc-commands-follow-spec-plan-build
title: svc commands follow spec, plan, build, verify
status: done
priority: P0
---

# 039 — svc commands follow spec, plan, build, verify

## Stories

As a contributor, I want `/svc:spec`, `/svc:plan`, `/svc:build`, `/svc:verify` and `/svc:specs`, so that each step of a feature has one obvious command and the build is driven by approved criteria.

## Acceptance criteria

- **AC-039.1** `/svc:spec` asks me the open questions in the session before it ends; `/svc:spec approve <id>` approves and commits.
- **AC-039.2** `/svc:plan <id>` refuses a spec that is not approved.
- **AC-039.3** `/svc:build <id>` commits failing acceptance tests first, then implements until they pass, marks tasks done as it goes (a re-run resumes), verifies, and opens a PR that lists the spec and its criteria.
- **AC-039.4** `/svc:quick-task` and `/svc:fix-bug` update the spec whose criteria their change alters.
- **AC-039.5** `/svc:build-feature` and `/svc:plan-feature` are removed (svc 3.0.0) and the CHANGELOG maps old to new.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Depends on:** STORY-038 · **Code:** `plugins/svc/commands/{spec,plan,build,verify,specs}.md`

## Changelog

- 2026-10-08 migrated from STORY-039 in docs/backlog.md
