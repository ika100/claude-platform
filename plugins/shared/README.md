# shared plugin

Common agents and commands used by both `svc` and `gitops` plugins. Pre-approves `gh repo create` / `gh repo edit --add-topic` so `/shared:new-service` can scaffold a repo end-to-end without permission prompts mid-flight.

## Agents

| Agent | Model | Purpose |
|---|---|---|
| `quality` | sonnet | `devbox run quality` — ruff + mypy. Configures pyproject.toml + pre-commit hooks. |
| `security` | sonnet | `devbox run security` — pip-audit + detect-secrets + bandit + trivy (when Dockerfile present). |

## Commands

| Command | Purpose |
|---|---|
| `/shared:check-quality` | Runs `quality` + `security` agents in parallel (read-only). |
| `/shared:new-service <name> [--description "<text>"] [--library]` | Bootstraps a new repo from the appropriate Copier template, creates the GitHub repo, tags it for GitOps discovery. |

## Pre-approved operations (settings.json)

To make `/shared:new-service` flow without prompts:

- `gh repo create * --private *`
- `gh repo edit * --add-topic *`
- `gh api user`
- `copier copy *`, `copier update *`

Removal of topics, deletion of repos, and `--public` repo creation **prompt** the user.

## Usage notes

- Enable this plugin on every repo that uses `svc` or `gitops` — they depend on it for the canonical `quality` and `security` definitions.
- The `/shared:new-service` command requires `copier` to be installed on the host. If absent, install once: `uv tool install copier`.
