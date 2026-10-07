# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**{{ project_name }}** — {{ description }}

Owned by {{ owner_team }}. Python module: `{{ module_name }}`. Distributed as a wheel via internal index (no Docker image, no deployment).

## Development Environment

```bash
devbox shell        # enter the dev environment
devbox run quality  # ruff + mypy
devbox run test     # pytest with coverage
```

Canonical `devbox run` scripts:

| Script | Purpose |
|---|---|
| `test` | pytest with coverage (`--cov={{ module_name }}`) |
| `test-fast` | quick pytest |
| `lint` | `ruff check` + `ruff format --check` |
| `lint-fix` | `ruff check --fix` + `ruff format` |
| `quality` | lint + typecheck |
| `audit` | pip-audit |
| `secrets-scan` | detect-secrets |
| `bandit` | bandit |
| `security` | audit + secrets-scan + bandit |

**Rule for every agent: never call `ruff`, `mypy`, `pytest`, `pip`, or `uv add` directly. Always `devbox run <script>`.**

## Claude Code agents

Plugins enabled in `.claude/settings.json`:

- `svc@sdlc-foundry` — coder, architect, tester, quality gate
- `shared@sdlc-foundry` — quality + security agents

Library repos don't need the `deployment` agent (no Dockerfile, no k8s) — leave those plugin commands unused.

Common workflows:

| Task | Command |
|---|---|
| Small change | `/svc:quick-task <description>` |
| Plan a feature or refactor (first step) | `/svc:plan-feature <description>` |
| Build the approved plan | `/svc:build-feature --plan docs/plan/<slug>.md` |
| Release | `/svc:release` |
| Quality + security audit | `/shared:check-quality` |

### Spec first

A feature starts with a spec, not code: run `/svc:plan-feature <description>`, review the stories in `docs/backlog.md` and the plan in `docs/plan/<slug>.md`, then build it with `/svc:build-feature --plan docs/plan/<slug>.md`. The PR cites the story ids (`STORY-NNN`). Small changes (`/svc:quick-task`) and bug fixes (`/svc:fix-bug`) are exempt.

## Conventions

- Library, not a service — no HTTP entry point, no `/health` endpoint
- Public API in `src/{{ module_name }}/__init__.py`
- Tests in `tests/`, fixtures in `conftest.py`
- Branch naming: `feature/`, `fix/`, `chore/`, `docs/`, `refactor/`, `release/`
- Conventional commits in PR titles
