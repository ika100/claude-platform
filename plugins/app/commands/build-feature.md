---
description: "Plan a feature across several repos from a gitops-app repo (plan-only): stories → validated topo-sorted plan → per-repo hand-off commands. Usage: /app:build-feature <description>"
---

You are the **application planning orchestrator**. Turn one feature request into a validated multi-repo plan. **v1 is plan-only**: you do not touch component repos, open their PRs, or change overlay pins — the user runs `/svc:spec --from-plan …` → `/svc:plan` → `/svc:build` in each repo, or `/app:run-plan` does it ([ADR-007](../../../docs/adr/007-cross-repo-orchestration-scope.md)).

**Feature request:** $ARGUMENTS

If `$ARGUMENTS` is empty, print usage and stop.

---

## Phase 1 — Pre-flight

1. Resolve the shape: run this in one Bash call: `P="${XDG_CACHE_HOME:-$HOME/.cache}/sdlc-foundry"; { [ -d "$P/.git" ] && git -C "$P" fetch -q --depth 1 origin main && git -C "$P" checkout -q FETCH_HEAD; } || { rm -rf "$P"; git clone -q --depth 1 https://github.com/ika100/sdlc-foundry.git "$P"; }; uv run "$P/scripts/cplat/cplat.py" shape` It must report `shape: gitops-app`; otherwise stop: "`/app:build-feature` runs inside a gitops-app repo (`/shared:new-service <name> --gitops`)."
2. `git status --porcelain` must be empty; otherwise stop.
3. Read `applications/*/services.yaml`. If it lists no services, stop and recommend `/gitops:compose add <service>` first (a plan needs components to plan against). Exception: if the feature is "create the first service", say so and stop with the bootstrap commands instead.
4. Derive `SLUG` from the request (lowercase, hyphens, ≤40 chars). If `docs/plan/<SLUG>.md` exists, append `-2`, `-3`, … Resolve `GITOPS_APP` = `github_org`/`project_name` from `.copier-answers.yml`.
5. Create a branch: `git checkout -b docs/plan-<SLUG>` (if on `main`; otherwise stay).

Print `## Phase 1 complete — app repo <GITOPS_APP>, slug <SLUG>, <N> services registered`.

---

## Phase 2 — Product spec ([ADR-026](../../../docs/adr/026-feature-specs.md))

`CPLAT spec new "<short title>"` creates `docs/specs/<spec_id>/spec.md` (`CPLAT <args>` = `uv run "${XDG_CACHE_HOME:-$HOME/.cache}/sdlc-foundry/scripts/cplat/cplat.py" <args>` (the checkout the shape call above brought up to date)).

Use the **product-manager** agent (`svc:product-manager`), prompt: `MODE: new`, `SPEC_DIR: docs/specs/<spec_id>/`, the feature verbatim, and the product's component repos (`<name (shape)>` from services.yaml, plus shared libraries if relevant). Then `CPLAT spec check <spec_id>`.

Ask the user every question in its `OPEN QUESTIONS` with AskUserQuestion (suggested answer first, marked "(Recommended)"), send the answers back (`MODE: amend`), and repeat at most 3 rounds, exactly like `/svc:spec`. The spec must have no open questions before planning; ask the user to approve it, then `CPLAT spec approve <spec_id>`.

Print `## Phase 2 complete — spec <spec_id>, <N> criteria, approved`.

---

## Phase 3 — Plan

Use the **planner** agent (`app:planner`) with `FEATURE`, `SLUG`, `GITOPS_APP`, and `SPEC: docs/specs/<spec_id>/spec.md` from Phase 2. It writes `docs/plan/<SLUG>.md` and runs `devbox run plan-check`.

Then verify yourself:
```bash
devbox run plan-check
devbox run -- uv run scripts/plan.py show <SLUG>
```
If validation fails, send the exact errors back to the planner once; if it still fails, stop and show the errors.

Print `## Phase 3 complete — plan valid, <N> repos in <L> levels`.

---

## Phase 4 — Commit and hand off

Commit the spec and the plan on the planning branch:
```bash
git add docs/plan/<SLUG>.md docs/specs/<spec_id>/
git commit -m "docs(plan): <SLUG> — multi-repo plan for <short feature>"
```
Push and open a PR only after asking the user (`git push -u origin docs/plan-<SLUG>`, `gh pr create` both require confirmation). The plan is useful even unmerged — the next step can run from the local file.

Print the hand-off, in topological order, one block per level (repos in a level can run in parallel):

```
## Plan ready: <feature>   (docs/plan/<SLUG>.md)

Level 1:
  cd ../<repo-a> && /svc:spec --from-plan <abs-path-to-plan> <repo-a>   then /svc:plan <NNN> and /svc:build <NNN>
Level 2 (after Level 1 PRs merge):
  cd ../<repo-b> && /svc:spec --from-plan <abs-path-to-plan> <repo-b>   then /svc:plan <NNN> and /svc:build <NNN>
...
Finally, in this repo, pin the released images:
  /gitops:promote <service> dev staging      (per gitops_pin in the plan)

Track progress with /app:plans show <SLUG>; mark repos done with /app:plans done <SLUG> <repo-id>.
```

---

## Rules

- **Plan-only.** Never run `/svc:*` in another repo, never open PRs in component repos, never edit `services.yaml` or overlays.
- Every shell command goes through `devbox run`. Never `kubectl apply`.
- Never push or open a PR without the user's confirmation.
- Never overwrite an existing plan; use a new slug.

> If a step fails because a platform template, script or command misbehaves (not because of the user's code), stop, summarize it in two lines and offer `/shared:report-issue` so the user can file it. Never file anything without their OK.
