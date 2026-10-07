# ADR-023: Parallel execution of multi-repo plans

**Status:** Accepted
**Date:** 2026-10-07

## Context

[ADR-007](007-cross-repo-orchestration-scope.md) made `/app:build-feature` plan-only and left execution to a "v2". Building the project-management sample showed the cost: backend and UI were built one after the other although an agreed API makes them independent. A client reported the same (issue #56, idea 1). ADR-007's worry was partial failure: one repo merged, another failed, gitops half-pinned.

## Decision

Add `/app:run-plan <slug>` (app plugin). It executes the plan of ADR-011 **wave by wave**:

- `scripts/plan.py ready <slug>` (deterministic, tested) returns the repos that are not done and whose `depends_on` are all done: one wave.
- The executor starts **one subagent per ready repo in a single message** (concurrent), each working only in its own clone and stopping at an **open pull request**.
- Merging stays human: nothing is merged without an explicit "merge" from the user, and `plan.py done` is called only after GitHub reports the PR as `MERGED`. A failed or blocked repo stops the loop; re-running the command resumes from the plan file, which is the only state.
- Image pins in gitops are never applied by the executor: it prints the `/gitops:promote` commands at the end.
- The planner is told to **make repos independent through a contract**: a `## Contract` section in the plan body (endpoints, fields, status codes, errors) that is given to every agent, so a backend and its UI can start together. `depends_on` stays for real code dependencies.

## Consequences

- Plan format unchanged (ADR-011); `ready` only reads it.
- Partial failure is bounded: PRs are open or merged one by one under human control, state is explicit, pins are not applied.
- Wall-clock time of a multi-repo feature becomes the longest wave instead of the sum of all repos.
- Parallel agents cost proportionally more tokens; `--max` limits concurrency (default 3).
