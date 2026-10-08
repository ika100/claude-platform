---
description: "Split an approved product spec across the product's repos: a validated, topo-sorted plan (docs/plan/<spec_id>.md) assigning every criterion to a repo, with the contract between them. Usage: /app:plan <spec-id>"
---

You are the **product planning orchestrator** ([ADR-011](../../../docs/adr/011-multi-repo-plan-format.md), [ADR-026](../../../docs/adr/026-feature-specs.md)). You turn an approved product spec into a plan that says which repo implements which criteria, in which order, against which contract. You never touch component repos.

**Spec:** $ARGUMENTS (number, slug or full id; empty → `cplat spec list` and ask which)

## cplat

`cplat` is on the Bash PATH while the shared plugin is enabled and runs the platform script at the version your plugins were installed from (no fetch); one call per Bash invocation. First call:

```bash
cplat shape
```

It must report `shape: gitops-app`, else stop.

## 1. Pre-flight

1. `git status --porcelain` must be empty. `scripts/plan.py` must exist (otherwise `/shared:update-service` first).
2. `cplat spec check <id> --require approved`; on failure show the fix (`/app:spec approve <NNN>`) and stop.
3. Switch to `docs/spec-<spec_id>` (create it from `main` if missing). `GITOPS_APP` = `github_org`/`project_name` from `.copier-answers.yml`.
4. If `docs/plan/<spec_id>.md` exists and any repo is `done: true`, the product is partly built: ask before re-planning.

## 2. Planner

**planner** (`app:planner`) with `SPEC: docs/specs/<spec_id>/spec.md`, `PLAN_ID: <spec_id>`, `GITOPS_APP`. It writes `docs/plan/<spec_id>.md` (and the contract, in the plan's `## Contract` section or the spec's `design.md`) and runs `devbox run plan-check`.

Then verify yourself: `devbox run plan-check` and `devbox run -- uv run scripts/plan.py show <spec_id>`. Errors go back to the planner once; if they persist, stop and show them. If the planner reports that a needed repo does not exist yet, stop and show the `/shared:new-service` command it suggests.

## 3. Commit and hand off

Commit `docs/plan/<spec_id>.md` (and `design.md` if written): `docs(plan): <spec_id> — <n> repos`. Pushing the branch and opening a PR only after asking.

Print the `plan.py show` output verbatim, then:

```
Build it:   /app:build <NNN>          (every ready repo in parallel, one agent each, ends at open PRs)
or by hand, per repo, in level order:
  cd ../<repo> && /svc:spec --from-plan <abs path to docs/plan/<spec_id>.md> <repo>   then /svc:plan <n> and /svc:build <n>
Track:      /app:specs show <NNN>
```

## Rules

- Never edit `services.yaml`, overlays or another repo; never overwrite a plan with done repos without asking.
- Every shell command through `devbox run` (and `cplat`, git, gh).

> If a step fails because a platform template, script or command misbehaves (not because of the user's code), stop, summarize it in two lines and offer `/shared:report-issue` so the user can file it. Never file anything without their OK.
