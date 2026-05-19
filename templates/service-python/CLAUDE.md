# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

**{{ project_name }}** — {{ description }}

Owned by {{ owner_team }}. Python module: `{{ module_name }}`. Container image: `{{ docker_registry }}/{{ project_name }}`.

## Development Environment

This project uses [devbox](https://www.jetify.com/devbox) to manage the dev environment.

```bash
devbox shell       # enter the dev environment
devbox run test    # full pytest run with coverage
devbox run quality # ruff + mypy gate
```

Canonical `devbox run` scripts (configured in `devbox.json`):

| Script | Purpose |
|---|---|
| `test` | Full pytest run with coverage (`--cov={{ module_name }} --cov-report=term-missing`) |
| `test-fast` | Quick pytest run without coverage |
| `lint` | `ruff check` + `ruff format --check` |
| `lint-fix` | `ruff check --fix` + `ruff format` |
| `typecheck` | `mypy .` |
| `quality` | `lint` then `typecheck` — the gate CI runs |
| `audit` | `pip-audit --strict` |
| `secrets-scan` | `detect-secrets-hook` against `.secrets.baseline.json` |
| `bandit` | `bandit -r src/ -q` |
| `security` | `audit` + `secrets-scan` + `bandit` |
| `image-build` | Build local container image `{{ project_name }}:scan` |
| `image-scan` | `trivy image --severity CRITICAL,HIGH` against `{{ project_name }}:scan` |
{%- if needs_migrations %}
| `migrate` | `alembic upgrade head` |
| `migrate-new` | `alembic revision --autogenerate -m <msg>` |
| `migrate-down` | `alembic downgrade -1` |
| `migrate-status` | `alembic current` + `alembic history --verbose` |
{%- endif %}
| `deploy` | `kubectl apply -k k8s/overlays/local/` |
| `deploy-check` | `kubectl apply --dry-run=client -k k8s/overlays/local/` |

**Rule for every agent (human, CI, and AI): never call `ruff`, `mypy`, `pytest`, `pip-audit`, `detect-secrets`, `trivy`,{% if needs_migrations %} `alembic`,{% endif %} `bandit`, `pip`, or `uv add` directly. Always go through `devbox run <script>`.**

## Claude Code agents

Agents and slash commands come from the [`ika100/claude-platform`](https://github.com/ika100/claude-platform) marketplace. The plugins are enabled in `.claude/settings.json`:

- `svc@ika100-claude` — multi-agent pipeline (product-manager, architect, coder, tester, migrations, observability, release, deployment)
- `shared@ika100-claude` — quality, security, and the `/shared:new-service` bootstrap command

Read the platform's `docs/AGENTS.md` for the full orchestration model.

### Common workflows

| Task | Command |
|---|---|
| Plan a feature, no code | `/svc:plan-feature <description>` |
| Build a feature end-to-end | `/svc:build-feature <description>` |
| Small change | `/svc:quick-task <description>` |
| Fix a bug | `/svc:fix-bug <description or error>` |
| Read-only quality + security audit | `/shared:check-quality` |
| Release | `/svc:release` |

## Feature Branch Workflow

Branch prefixes: `feature/`, `fix/`, `chore/`, `docs/`, `refactor/`, `release/`. Slugs: lowercase, hyphens, ≤40 chars.

Main is protected. All changes via PR. Required CI checks: `quality`, `test`, `security`, `pr-title`, `docker`.

PR title format: `<type>(<optional-scope>): <description ≤72 chars>`. Valid types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `ci`, `build`, `revert`.

## Conventions

- **Config:** read exclusively from environment variables
- **HTTP services:** expose `/health` and `/ready` endpoints
- **Logging:** structured JSON{% if needs_observability %} via structlog{% endif %}
- **Tests:** pytest, in `tests/`, fixtures in `conftest.py`
- **Manifests:** Kubernetes YAML in `k8s/`
- **Docs:** plans in `docs/plan/`, ADRs in `docs/adr/`, backlog in `docs/backlog.md`

## Docker image pipeline

Whenever a `Dockerfile` exists, the CI workflow includes a `docker (build + push)` job that:

| Trigger | Tags pushed |
|---|---|
| PR | Build only — no push |
| Merge to `main` | `latest`, `sha-<short>` |
| Version tag `v1.2.3` | `1.2.3`, `1.2`, `1`, `latest`, `sha-<short>` |

Registry: `{{ docker_registry }}/{{ project_name }}`. Authentication via `GITHUB_TOKEN`.

## GitOps deployment

This service is registered for ArgoCD auto-discovery via the GitHub topic `deployable-service`. Manifests in `k8s/overlays/prod/` are picked up by the platform GitOps repo's ApplicationSet.

Local Kubernetes (k3d): `devbox run deploy`. Cross-environment promotion happens via the platform gitops repo using `/gitops:promote {{ project_name }} <from> <to>`.
