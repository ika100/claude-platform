---
spec_id: 045-multi-repo-builds-handle-the-gitops-app
title: Multi-repo builds handle the gitops-app entry
status: draft
priority: P0
---

# 045 — Multi-repo builds handle the gitops-app entry

## Problem

The planner put the gitops-app repo itself into the todo plan (Postgres addon, exposure of todo-web, `TODO_API_URL`). `/app:build` routes every repo through `/svc:spec --from-plan`, which refuses gitops-app; the agent improvised with `/gitops:addon` and `/gitops:compose`, and a human opened the PR.

## Stories

As a founder, I want the gitops part of a product plan to be built like the other repos, so that one `/app:build` delivers the wiring, the addon and the services together.

## Acceptance criteria

- **AC-045.1** Given a product plan with a repo entry of shape `gitops-app`, when `/app:build` runs its wave, then that entry is built in the gitops-app repo with `/gitops:addon` and `/gitops:compose` (never `/svc:*`) and ends like the other repos at a pushed branch with a pull request or its exact `gh pr create` command.
- **AC-045.2** Given that entry, when the planner writes it, then it lists the operations as data (for example addon `postgres` for todo-api, expose `todo-web` at a host, env `TODO_API_URL` on todo-web) and `plan-check` rejects an unknown operation or service.
- **AC-045.3** Given service repos that depend on the gitops operations (a database), when `/app:build` reports the wave, then it says to merge the gitops pull request first.

## Non-goals

- Pinning images to staging or prod (that stays `/gitops:promote`).

## Open questions

- Structured operations in the plan (`gitops: [{addon: postgres, for: todo-api}, …]`) or prose instructions for the agent? (suggested: structured, so `plan-check` can validate them and spec 052 can copy them; affects AC-045.2)

## References

- [End-to-end run 2026-10-08, issue 3](../../e2e/2026-10-08-todo-spec-driven.md#issues-and-workarounds)

## Changelog

- 2026-10-08 created from issue 3 of the todo end-to-end run
