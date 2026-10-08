---
spec_id: 052-repo-specs-know-the-gitops-wiring
title: Repo specs know the gitops wiring
status: done
priority: P1
---

# 052 — Repo specs know the gitops wiring

## Problem

Both todo repo builds asked the user to add `TODO_API_URL` or `DATABASE_URL` to `services.yaml`, which the gitops part of the same plan had already done. A repo agent cannot see the gitops repo, so its advice was wrong.

## Stories

As a contributor, I want a repo's spec to say which wiring the product provides, so that the build relies on it and stops asking for changes that already exist.

## Acceptance criteria

- **AC-052.1** Given a product plan whose gitops entry wires a service (env names, addon), when `cplat spec new --from-plan` writes that service's spec, then its Product context lists the env variables and addons the product provides to it.
- **AC-052.2** Given that context, when the repo's build ends, then the Final Report asks for gitops changes only for wiring that is not listed there.

## Non-goals

- None.

## Open questions

None.

## References

- Depends on spec 045 (structured gitops operations in the plan).
- [End-to-end run 2026-10-08, issue 10](../../e2e/2026-10-08-todo-spec-driven.md#issues-and-workarounds)

## Changelog

- 2026-10-08 created from issue 10 of the todo end-to-end run
- 2026-10-08 approved
- 2026-10-08 building
- 2026-10-08 done
