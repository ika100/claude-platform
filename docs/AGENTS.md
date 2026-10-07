# Claude Code Multi-Agent Setup

This document describes the orchestration model used by the `svc`, `web`, `svc-java`, `svc-go`, `gitops`, `app` and `shared` plugins. Read this first when adding or modifying agents.

---

## Golden rule: everything goes through `devbox run`

Every agent — human, CI, or AI — runs shell commands via `devbox run <script>`. The canonical recipes (`test`, `test-fast`, `lint`, `lint-fix`, `typecheck`, `quality`, `security`, `image-build`, `image-scan`, `deploy-check`, … — the same names in every shape, wrapping that shape's tools) are defined once in `devbox.json` and reused everywhere. Each shape's Copier template ships the full canonical set; consumer repos start with that and add project-specific recipes as needed.

If a recipe is missing, **add it to `devbox.json` and commit** — never run an ad-hoc `pip install`, `uv add`, `pnpm add`, `go get`, `mvn …`, `pytest …`, `ruff …`, or similar (one-off tool calls go through `devbox run -- <tool> …`). This keeps the dev shell, CI pipeline, and agents producing identical results.

### SessionStart hooks

The `svc`, `web`, `svc-java`, `svc-go`, `gitops` and `shared` plugins ship a `hooks/hooks.json` with a `SessionStart` hook that:

- **Warns if `devbox` is missing from `PATH`** and prints the install command: `curl -fsSL https://get.jetify.com/devbox/install.sh | bash`. The hook exits 0 — it never blocks the session.
- **Runs `devbox install` (idempotent)** if a `devbox.json` is present in the working directory, so the dev environment is ready before any agent touches it. The `svc` hook additionally runs `uv sync --all-extras` for Python repos (when `pyproject.toml` exists); `web` runs `devbox run install` when `node_modules/` is missing.

A consumer repo that installs any of these plugins is therefore devbox-aware out of the box; a repo with no `devbox.json` sees the hook as a silent no-op.

---

## Permissions allowlist

Each consumer repo ships a `.claude/settings.json` (templated by Copier) with a committed allowlist that pre-approves the safe, frequent operations the pipeline needs — so `/svc:build-feature` and `/svc:quick-task` don't pause for permission prompts mid-flight.

**Auto-allowed (in every template; the Python-only `uv`/`python` entries exist only in the Python templates, `pnpm add`/`pnpm remove` prompt in the web template):**
- Every `devbox run <recipe>` (the canonical entry point)
- Read-only git (`status`, `diff`, `log`, `show`, …)
- Local-only git writes (`add`, `commit -m`, `merge --no-ff`, `worktree add/remove`, `branch -d`, `stash`, `tag -a`)
- Read-only inspection (`ls`, `find`, `grep`, `rg`, `jq`, `cat`, `head`, `tail`, `kubectl get/describe/logs/diff`, `kubectl apply --dry-run=*`)
- Pushing to non-main feature/fix/chore/docs/refactor/release branches and version tags
- Read-only `gh` (`pr view`, `issue list`, `run view`, …) and pre-approved `gh pr merge --merge release/*`

**Always prompts (explicitly listed in `ask`):**
- Anything that touches a remote: `git push origin main`, `git pull`, `gh pr create`, `gh release *`, `docker push`
- Anything destructive: `git reset`, `git clean`, `git rebase`, `git branch -D`, `git checkout --`, `git commit --amend`
- Cluster writes: `kubectl delete`, `kubectl rollout restart/undo` (live `kubectl apply` also prompts — it's covered by default since only `--dry-run=*` is allowlisted)
- Out-of-band installs: `pip install`, `uv add`, `uv remove` (Python) / `pnpm add`, `pnpm remove` (web)

**Pre-approved by the `shared` plugin specifically:**
- `gh repo create * --private *`, `gh repo edit * --add-topic *`, `git clone --depth 1 *`, `uv run * shapes.py *` and `copier copy *` so `/shared:new-service` and `/shared:update-service` can run without mid-flight prompts.

---

## Shapes and agent dispatch

Every `/svc:*` command starts by detecting the repo's **shape** (`.copier-answers.yml`, falling back to file sniffing) and looks it up in `shapes.yml`. Coder, tester, deployment, observability and release agents are then spawned from the plugin that owns the shape (`web:coder`, `svc-java:tester`, `svc-go:release`, …; `svc:*` for Python); product-manager and architect (`svc`) and quality and security (`shared`) are shared by all shapes. `gitops-app` repos do not use `/svc:build-feature`; they use `/gitops:compose`, `/gitops:promote` and `/app:build-feature` (`cplat shape` prints the routing). The multi-repo flow: `/app:build-feature` writes a plan → run `/svc:build-feature --from-plan <plan> <repo-id>` in each repo → `/app:plans done` → `/gitops:promote`.

---

## Parallel implementation via git worktrees

`/svc:build-feature` Phase 3 fans coder agents out in parallel using the Agent tool's `isolation: "worktree"` mode. Each parallel coder works in its own git worktree on its own branch; the orchestrator merges branches back onto the base branch sequentially with a quality gate between each merge.

The flow only works when the architect's plan is machine-readable. Plans must start with a YAML metadata block (see `plugins/svc/agents/architect.md` for the exact spec):

```yaml
---
plan_id: <slug>
shape: <shape-id>      # service-python | web-nextjs | service-java | service-go | …
tasks:
  - id: t1
    title: ...
    files: [<paths the task will touch>]
    parallel_safe: true
    depends_on: []
---
```

The orchestrator:

1. **Topologically sorts** tasks by `depends_on`.
2. At each dependency level, **greedily groups `parallel_safe: true` tasks into batches** whose `files` sets are disjoint.
3. For each batch ≥ 2: spawns one coder per task **in one assistant turn** (multiple Agent tool calls in parallel), each in its own worktree. Each coder commits inside its worktree before returning.
4. **Merges sequentially** back onto the base branch with `git merge --no-ff`. After each merge: `devbox run quality` and `devbox run test-fast`. On failure, hand back to that task's coder for lint/type fixes only.
5. Cleans up worktrees and branches as it merges.

**Merge conflicts are escalated, never auto-resolved.** A conflict means the architect's `files` declarations were inaccurate — the fix is to update the plan, not to paper over it.

---

## Feature branch and PR lifecycle

Both `/svc:quick-task` and `/svc:build-feature` include:

- **Phase 0** (pre-flight): if on `main`, create `feature/<slug>` branch before any work starts.
- **Final PR phase**: after all quality/test/security gates pass, push the branch and open a PR. Both push and PR creation are in the `ask` permission list — user must confirm.

### Automatic issue linking and closing

The PR phase explicitly scans for GitHub issue references — `#NNN` patterns — in:
- The task/feature description (`$ARGUMENTS`)
- The last 10–20 commit messages on the branch
- `docs/backlog.md` user stories (`build-feature` only)

Each candidate issue is verified via `gh issue view` to confirm it is `OPEN`. Live `Closes #NNN` lines (not HTML comments) are injected into the PR body. When the PR merges into `main`, GitHub automatically closes each linked issue.

The `/svc:release` pipeline adds a second safety net: **Phase 7** scans all commits included in the release (since the previous tag) for `#NNN` references and calls `gh issue close` on any that are still open, with a comment linking to the release version.

---

## Overview

```
/svc:plan-feature  ──►  product-manager  ──►  architect
                          │                    │
                          ▼                    ▼
                     user stories        implementation plan
                     (docs/backlog.md)   (docs/plan/<slug>.md, YAML metadata)

/svc:build-feature --plan <plan> ──► skips the two phases above and builds the reviewed plan (ADR-024)
/svc:build-feature ──►  [above] ──►  coders ║parallel║  ──►  merge+quality  ──►  tester  ──►  security  ──►  deployment
                                       │   (1 worktree per task)   │              │             │               │
                                       ▼                           ▼              ▼             ▼               ▼
                                  Python code               ruff+mypy/test    pytest+cov   CVE+secrets    Dockerfile image

/svc:fix-bug       ──►  coder (diagnose) ──►  coder (fix) ──►  tester (verify)
                                  └──────────── loop (max 3) ──────────────┘

/shared:check-quality ──►  quality + security (parallel, read-only)

/svc:release       ──►  quality gate ──►  tester gate ──►  security gate ──►  release agent
                                                                                  │
                                                                                  ▼
                                                                          changelog + tag + PR

/gitops:promote <svc...> <from> <to>   ──►  promote agent  ──►  PR (Argo reconciles on merge)
/gitops:compose add|remove <svc...>    ──►  compose agent  ──►  PR (services.yaml + generated ApplicationSets)
/app:build-feature <desc>              ──►  product-manager ──► planner ──►  docs/plan/<slug>.md  (then /svc:build-feature --from-plan per repo)
```

---

## Agents by plugin

### `svc` plugin

| Agent | Model | Job |
|---|---|---|
| `product-manager` | sonnet | User stories, acceptance criteria, backlog folding for issues handed over by `/shared:triage` |
| `architect` | opus | ADRs, implementation plans with parallel-safe metadata |
| `coder` | sonnet | Python implementation |
| `tester` | sonnet | pytest, coverage, bandit |
| `migrations` | sonnet | Alembic migrations |
| `observability` | sonnet | structlog + Prometheus + OTel scaffolding |
| `release` | sonnet | Semver, CHANGELOG, release branch + PR |
| `deployment` | sonnet | Dockerfile and GHCR CI (image only — manifests live in the gitops-app repo, ADR-017) |

Orchestrators dispatch `coder`, `tester`, `deployment`, `observability` and `release` to the plugin that owns the repo's shape (`<plugin>:<role>`; `cplat shape` prints the routing); for `service-python` / `library-python` that is `svc`. `product-manager`, `architect`, `quality` and `security` are shape-agnostic.

### `web` plugin (`web-nextjs`)

| Agent | Model | Job |
|---|---|---|
| `coder` | sonnet | App Router + strict TypeScript; sonnet is enough for pattern-driven UI/route work |
| `tester` | sonnet | Vitest + Testing Library, Playwright when enabled |
| `deployment` | sonnet | Standalone-output Dockerfile and CI (image only) |
| `observability` | sonnet | `/api/metrics`, OpenTelemetry instrumentation, alerts |
| `release` | sonnet | `package.json` version, CHANGELOG, release PR |

### `svc-java` plugin (`service-java`)

| Agent | Model | Job |
|---|---|---|
| `coder` | sonnet | Spring Boot 3 / Java 21 implementation |
| `tester` | sonnet | JUnit 5 + Spring Boot Test, JaCoCo gate |
| `deployment` | sonnet | Distroless Java image, JVM-aware probes |
| `observability` | sonnet | Actuator + Micrometer + OTel agent |
| `release` | sonnet | `pom.xml` version via `versions:set` |

### `svc-go` plugin (`service-go`)

| Agent | Model | Job |
|---|---|---|
| `coder` | sonnet | Idiomatic Go (chi, slog) |
| `tester` | sonnet | stdlib `testing` + httptest, race detector |
| `deployment` | sonnet | distroless/static image, ldflags version |
| `observability` | sonnet | slog + Prometheus client_golang |
| `release` | sonnet | CHANGELOG + PR; version is the git tag |

### `gitops` plugin

| Agent | Model | Job |
|---|---|---|
| `deployment` | sonnet | ArgoCD ApplicationSet, cluster add-ons, overrides (platform GitOps repo) |
| `promote` | sonnet | Cross-environment version pinning (platform repo and gitops-app repos, batch) |
| `compose` | sonnet | Add/remove services in a gitops-app repo (`services.yaml` → generated ApplicationSets/overlays); validates the `deployable-service` topic |

### `app` plugin

| Agent | Model | Job |
|---|---|---|
| `planner` | opus | Multi-repo plan (`docs/plan/<slug>.md`, ADR-011): which repos change, in what order, with paste-ready prompts. opus because decomposition across repos is the hard judgement call |

### `shared` plugin

| Agent | Model | Job |
|---|---|---|
| `quality` | sonnet | Runs `devbox run quality` for the repo's shape (ruff + mypy, ESLint + tsc, Spotless + Checkstyle, golangci-lint, kustomize/kubeconform, …) |
| `security` | sonnet | Runs `devbox run security` (pip-audit/pnpm audit/OWASP DC/govulncheck + detect-secrets) and trivy on images |

---

## File conventions in consumer repos

| Path | Purpose |
|---|---|
| `docs/backlog.md` | Prioritized product backlog (P0/P1/P2 stories) |
| `docs/prd/<feature>.md` | Product requirements documents |
| `docs/plan/<feature-slug>.md` | Architect's numbered implementation plans |
| `docs/adr/<nnn>-<title>.md` | Architecture decision records |
| `docs/env-vars.md` | Required environment variables |
| `docs/security/scan-<date>.md` | Security scan reports |
| `docs/migrations/runbook.md` | Migration runbook |
| `applications/<app>/services.yaml` (gitops-app repo) | How each service runs; the manifests under `overlays/` are generated from it |
| `migrations/` | Alembic migration scripts |
| `tests/` | pytest test suite |
| `.github/workflows/` | CI/CD pipelines |
| `pyproject.toml` | Python project config |
| `.pre-commit-config.yaml` | Pre-commit hooks |
| `CHANGELOG.md` | Release changelog |

---

## Model selection convention

- `model: opus` — agents whose primary output is *decisions* downstream agents consume (`product-manager`, `architect`). One bad plan poisons the whole run, so the reasoning headroom pays for itself.
- `model: sonnet` — execution agents (everything else).

When adding a new agent that needs to run shell commands, copy the **devbox rule** from `coder.md` or `quality.md` into the system prompt so the new agent inherits the same convention: shell only via `devbox run <script>`, recipes pinned in `devbox.json`.
