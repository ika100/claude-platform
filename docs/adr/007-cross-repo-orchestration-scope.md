# ADR-007: Cross-repo orchestration — plan-only in v1, execution in v2

**Status:** Accepted
**Date:** 2026-05-22

## Context

Building a SaaS feature can touch multiple repos at once: backend service(s), web frontend, plus the `gitops-app` repo that pins image tags. Should `/app:build-feature` orchestrate all of this end-to-end, or only plan it?

## Decision

**v1 is plan-only.** `/app:build-feature <description>` invoked from a `gitops-app` repo produces a multi-repo plan in `docs/plan/<slug>.md`:
- which component repos are affected and why
- per-repo task summary (becomes the `$ARGUMENTS` for `/svc:build-feature` in that repo)
- post-merge gitops-app PR that pins the new image tags

The user then runs `/svc:build-feature` per repo manually. v2 of `/app:build-feature` (a future ADR) will fan execution out automatically once the planner is trusted.

## Rationale

- The hard problem in multi-repo orchestration is partial-failure recovery: one repo's PR fails CI, another already merged, gitops-app is half-pinned. That state is brittle and surprising.
- A good plan delivers ~80% of the leverage (the user no longer has to figure out *which* repos need changes) at ~10% of the risk.
- A trusted planner is a prerequisite to safe execution anyway — building it standalone lets us measure planner quality before betting execution on it.

## Consequences

- `/app:build-feature` is P1 in the PRD, not P0 — it lands after the per-shape commands work.
- The plan format includes a YAML metadata block similar to the architect's per-service plan, but with `repos:` instead of `tasks:`, and a `gitops_pin` section listing image-tag bumps.
- The PRD's acceptance signal (§7) assumes manual per-repo invocation; the one-day onboarding goal is met without v2.

## References

- [platform-vision.md §11.6, §10 risks](../requirements/platform-vision.md)
