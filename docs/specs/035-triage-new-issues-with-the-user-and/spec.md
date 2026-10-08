---
spec_id: 035-triage-new-issues-with-the-user-and
title: Triage new issues with the user and route them
status: done
priority: P1
---

# 035 — Triage new issues with the user and route them

## Stories

As a maintainer of a repo built on the platform (or of the platform itself), I want `/shared:triage` to read new GitHub issues, discuss unclear ones with me, and route each to the right path (backlog story, quick task, bug fix, or a reply), so that issues become tracked work with the right amount of process instead of piling up.

## Acceptance criteria

- **AC-035.1** `/shared:triage [<number> | --all]` lists open issues that carry the `triage` label (or, with `--new`, have no triage-related label yet), read-only, with title, author, age, labels and the first lines of the body. Issue text is treated as data, never as instructions, and is shown redacted of secrets.
- **AC-035.2** For each issue the command proposes one classification with a one-line reason: `bug`, `small-change`, `feature`, `question`, `duplicate`, `wontfix`, or `needs-info`, using a documented rubric (reproducible defect → bug; well-scoped change of one pass → small-change; new behaviour, API, schema or several modules → feature).
- **AC-035.3** When information is missing, the command asks the user at most three focused questions per issue in the session, and offers to post the unanswered ones to the reporter as a comment and label the issue `needs-info`. Nothing is posted, labelled or closed without the user's confirmation, and issues are never closed by the command.
- **AC-035.4** After confirmation, a `feature` becomes a `STORY-NNN` in `docs/backlog.md` with `**Tracks:** #N` (product-manager rules, ids as in STORY-034) and the issue is labelled `tracked`; the user is pointed to `/svc:plan-feature`.
- **AC-035.5** After confirmation, a `bug` is handed to `/svc:fix-bug` and a `small-change` to `/svc:quick-task`, with the issue number, title, redacted body and the answers from the discussion as the task text; the resulting PR says `Closes #N`. A bug the user marks urgent additionally suggests a patch release (`/svc:release`) after the fix merges; the release is not started automatically.
- **AC-035.6** After confirmation, a `feature` issue also gets a comment with the story id (`Tracked as STORY-NNN`) so the reporter can see it; the comment is shown to the user before it is posted.
- **AC-035.7** Decisions are recorded on the issue as labels from a fixed set (`triage`, `needs-info`, `tracked`, `bug`, `enhancement`, `question`, `duplicate`, `wontfix`) created idempotently by `cplat triage setup-labels`; a re-run of the command skips issues that already carry a decision label.
- **AC-035.8** Every template ships issue forms (`bug_report.yml`, `feature_request.yml`, `config.yml`) that apply the `triage` label, project-owned so updates do not overwrite them.
- **AC-035.9** Shapes without svc-style pipelines (gitops-app) and repos without a shape (the platform) get classification, discussion, labels, comments and backlog entries, but are told which command would handle a bug there (`/gitops:*` or a PR by hand) instead of an unavailable `/svc:*`.
- **AC-035.10** Deterministic parts (listing, fetching with comments, label setup, applying a decision) are in `cplat triage` with tests using a faked `gh`.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P1 · **Source:** user request 2026-10-07 · **Plan:** [plan/issue-triage.md](../../plan/issue-triage.md) · **ADR:** [025](../../adr/025-issue-triage.md)

## Changelog

- 2026-10-08 migrated from STORY-035 in docs/backlog.md
