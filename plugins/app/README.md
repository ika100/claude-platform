# app plugin

Multi-repo planning for **`gitops-app`** repos (one per SaaS product). `/app:build-feature` plans ([ADR-007](../../docs/adr/007-cross-repo-orchestration-scope.md)): which component repos a feature touches and in what order, with paste-ready `/svc:spec --from-plan` commands (each repo then runs `/svc:plan` and `/svc:build`); `/app:run-plan` executes the plan with independent repos in parallel ([ADR-023](../../docs/adr/023-parallel-plan-execution.md)).

## Agents

| Agent | Model | Purpose |
|---|---|---|
| `planner` | opus | Writes `docs/plan/<slug>.md` (ADR-011 format) across the product's repos |

## Commands

| Command | Purpose |
|---|---|
| `/app:build-feature <desc>` | product spec (`docs/specs/`, your answers, approval) → planner → validated, topo-sorted plan → hand-off commands |
| `/app:plans [list\|show\|start\|done\|abandon]` | Plan lifecycle: `draft → in_progress → completed \| abandoned` |
| `/app:run-plan <slug> [--max N]` | Executes a plan wave by wave: one agent per ready repo **in parallel**, PRs opened, merges only on your word ([ADR-023](../../docs/adr/023-parallel-plan-execution.md)) |

## Dependencies

- `svc` (product-manager agent, `/svc:spec --from-plan`, `/svc:plan`, `/svc:build`), `shared`, `gitops` — all enabled in the `gitops-app` template's `.claude/settings.json`.
- The repo's `scripts/plan.py` and `devbox run plan-check` (shipped by the `gitops-app` template) do validation and lifecycle edits.

## Not yet

Automatic merging and image pinning (always a human step); `/app:release` (PRD C4, P2).
