---
spec_id: 044-parallel-coders-build-on-the-feature
title: Parallel coders build on the feature branch
status: approved
priority: P0
---

# 044 — Parallel coders build on the feature branch

## Problem

`/svc:build` Phase 2 runs parallel coders with `isolation: "worktree"`. In the todo run the worktrees started from `main`, so the coders saw neither the spec, the plan nor the acceptance tests; correcting it with `git reset --hard` is in the `ask` list and was refused. The build silently fell back to running every task sequentially.

## Stories

As a contributor, I want parallel coders to start from the feature branch, so that parallel batches work on the spec and its acceptance tests and the build is as fast as the plan allows.

## Acceptance criteria

- **AC-044.1** Given a parallel batch in `/svc:build`, when a coder starts in its worktree, then its HEAD is the feature branch head at the start of the batch (spec, plan and acceptance tests present).
- **AC-044.2** Given every template's \`.claude/settings.json\`, when it is rendered, then it sets \`worktree.baseRef: "head"\`, so subagent worktrees branch from the orchestrator's HEAD (the feature branch); \`shapes.py check\` fails a template without it.
- **AC-044.3** Given the worktree probe before the first batch, when its worktree does not start at the feature head (setting missing, older Claude Code), then the build runs sequentially and the Final Report says why.
- **AC-044.4** Given a merged parallel task, when its branch is merged into the feature branch, then the merge brings only that task's commits.

## Non-goals

- Changing how the Claude Code harness creates worktrees.

## Open questions

- ~~Can the base of `isolation: "worktree"` be configured in Claude Code, which would make the in-worktree switch unnecessary? (suggested: check the Agent tool docs first, otherwise switch inside the worktree; affects AC-044.2)~~ Answered: yes: worktree.baseRef "head" in settings (Claude Code docs, "Choose the base branch"); the templates set it.

## References

- [End-to-end run 2026-10-08, issue 2](../../e2e/2026-10-08-todo-spec-driven.md#issues-and-workarounds)

## Changelog

- 2026-10-08 created from issue 2 of the todo end-to-end run
- 2026-10-08 open question answered: yes: worktree.baseRef "head" in settings (Claude Code docs, "Choose the base branch"); the templates set it.
- 2026-10-08 approved
