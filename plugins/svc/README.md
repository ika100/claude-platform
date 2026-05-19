# svc plugin

Multi-agent pipeline for Python service repos. Pair with the `shared` plugin for quality/security and the `service-python` Copier template for the canonical project skeleton.

## Agents

| Agent | Model | Purpose |
|---|---|---|
| `product-manager` | opus | User stories, acceptance criteria, backlog grooming, GitHub issue triage |
| `architect` | opus | ADRs, implementation plans with parallel-safe YAML metadata |
| `coder` | sonnet | Python implementation following the architect's plan |
| `tester` | sonnet | pytest suite, coverage gate (≥80%), bandit |
| `migrations` | sonnet | Alembic migrations and seed scripts |
| `observability` | sonnet | structlog + Prometheus + OTel scaffolding, alerting rules |
| `release` | sonnet | Semver bump, CHANGELOG, release branch + PR |
| `deployment` | sonnet | Dockerfile, base k8s manifests, GHCR CI pipeline |

## Commands

| Command | Purpose |
|---|---|
| `/svc:plan-feature <desc>` | product-manager → architect (no code) |
| `/svc:build-feature <desc>` | Full pipeline: PM → architect → parallel coders → quality → tester → security → deployment → PR |
| `/svc:quick-task <desc>` | Lightweight: coder → quality → tester → PR |
| `/svc:fix-bug <desc>` | Diagnose → fix → regression test → PR |
| `/svc:release` | Quality gate → test gate → security gate → version bump → tag → close issues |

## Hooks

- `SessionStart` runs `devbox run -- uv sync --all-extras` to keep the venv current.

## Dependencies

This plugin assumes:

1. **`shared` plugin is also enabled** (provides `quality` + `security` agents that several commands invoke).
2. **Project has a `devbox.json` with the canonical recipes** (`test`, `lint`, `quality`, `security`, `image-build`, `deploy-check`, …). Use the `service-python` Copier template to bootstrap a project with the right shape.
3. **Project is a Python repo** using `uv` and `pyproject.toml`.

Enable both plugins via `.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "svc@ika100-claude": true,
    "shared@ika100-claude": true
  }
}
```

## Bootstrap

```
/shared:new-service payments-api --description "Stripe webhooks → Postgres"
```
