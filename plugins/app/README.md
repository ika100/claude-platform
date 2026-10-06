# app plugin

Multi-repo planning for **`gitops-app`** repos (one per SaaS product). v1 is **plan-only** ([ADR-007](../../docs/adr/007-cross-repo-orchestration-scope.md)): it decides which component repos a feature touches and in what order, then hands you paste-ready `/svc:build-feature --from-plan` commands.

## Agents

| Agent | Model | Purpose |
|---|---|---|
| `planner` | opus | Writes `docs/plan/<slug>.md` (ADR-011 format) across the product's repos |

## Commands

| Command | Purpose |
|---|---|
| `/app:build-feature <desc>` | PM stories (per repo) → planner → validated, topo-sorted plan → hand-off commands |
| `/app:plans [list\|show\|start\|done\|abandon]` | Plan lifecycle: `draft → in_progress → completed \| abandoned` |

## Dependencies

- `svc` (product-manager agent, `/svc:build-feature --from-plan`), `shared`, `gitops` — all enabled in the `gitops-app` template's `.claude/settings.json`.
- The repo's `scripts/plan.py` and `devbox run plan-check` (shipped by the `gitops-app` template) do validation and lifecycle edits.

## Not in v1

Automatic fan-out into component repos and cross-repo PR creation (v2, future ADR); `/app:release` (PRD C4, P2).
