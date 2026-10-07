# shared plugin

Common agents and commands used by every shape's plugin. Pre-approves `gh repo create` / `gh repo edit --add-topic` so `/shared:new-service` can scaffold a repo end-to-end without permission prompts mid-flight.

## Agents

| Agent | Model | Purpose |
|---|---|---|
| `quality` | sonnet | `devbox run quality` for the repo's shape (ruff + mypy, ESLint + tsc, Spotless + Checkstyle, golangci-lint, kustomize/kubeconform, …). |
| `security` | sonnet | `devbox run security` (pip-audit / pnpm audit / OWASP DC / govulncheck + detect-secrets) and trivy when a Dockerfile is present. |

## Commands

| Command | Purpose |
|---|---|
| `/shared:check-quality` | Runs `quality` + `security` agents in parallel (read-only). |
| `/shared:new-service <name> [description words…] [--type <shape>] [--library\|--web\|--gitops] [--app <org>/<repo>]` | Bootstraps a new repo of any shape from its Copier template, creates the GitHub repo, tags deployable shapes for GitOps discovery. |
| `/shared:new-app <app.yml> [--resume] [--public] [--no-github]` | Creates a whole product: the gitops-app repo plus every component repo from a manifest, then opens one pull request that composes the deployable ones. A failure midway reports what exists; `--resume` continues. |
| `/shared:update-service [--ref <tag>] [--data k=v]` | Re-applies the template skeleton to an existing repo on a review branch (project-owned files untouched). |

## Pre-approved operations (settings.json)

To make `/shared:new-service` flow without prompts:

- `gh repo create * --private *`
- `gh repo edit * --add-topic *`
- `gh api user`
- `copier copy *`, `copier update *`

Removal of topics, deletion of repos, and `--public` repo creation **prompt** the user.

## Usage notes

- Enable this plugin on every repo that uses any shape plugin — they depend on it for the canonical `quality` and `security` definitions.
- The `/shared:new-service` command requires `copier` to be installed on the host. If absent, install once: `uv tool install copier`.
