# Claude Code Multi-Agent Setup

This document describes the orchestration model used by the `svc`, `gitops`, and `shared` plugins. Read this first when adding or modifying agents.

---

## Golden rule: everything goes through `devbox run`

Every agent — human, CI, or AI — runs shell commands via `devbox run <script>`. The canonical recipes (test, lint, typecheck, audit, secrets-scan, bandit, image-build, image-scan, migrate, deploy, …) are defined once in `devbox.json` and reused everywhere. The `service-python` Copier template ships the full canonical set; consumer repos start with that and add project-specific recipes as needed.

If a recipe is missing, **add it to `devbox.json` and commit** — never run an ad-hoc `pip install`, `uv add`, `pytest …`, `ruff …`, or similar. This keeps the dev shell, CI pipeline, and agents producing identical results.

---

## Permissions allowlist

Each consumer repo ships a `.claude/settings.json` (templated by Copier) with a committed allowlist that pre-approves the safe, frequent operations the pipeline needs — so `/svc:build-feature` and `/svc:quick-task` don't pause for permission prompts mid-flight.

**Auto-allowed (in service-python template):**
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
- Out-of-band installs: `pip install`, `uv add`, `uv remove`

**Pre-approved by the `shared` plugin specifically:**
- `gh repo create * --private *` and `gh repo edit * --add-topic *` so `/shared:new-service` can bootstrap a repo end-to-end.

---

## Parallel implementation via git worktrees

`/svc:build-feature` Phase 3 fans coder agents out in parallel using the Agent tool's `isolation: "worktree"` mode. Each parallel coder works in its own git worktree on its own branch; the orchestrator merges branches back onto the base branch sequentially with a quality gate between each merge.

The flow only works when the architect's plan is machine-readable. Plans must start with a YAML metadata block (see `plugins/svc/agents/architect.md` for the exact spec):

```yaml
---
plan_id: <slug>
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

/svc:build-feature ──►  [above] ──►  coders ║parallel║  ──►  merge+quality  ──►  tester  ──►  security  ──►  deployment
                                       │   (1 worktree per task)   │              │             │               │
                                       ▼                           ▼              ▼             ▼               ▼
                                  Python code               ruff+mypy/test    pytest+cov   CVE+secrets    Dockerfile+k8s

/svc:fix-bug       ──►  coder (diagnose) ──►  coder (fix) ──►  tester (verify)
                                  └──────────── loop (max 3) ──────────────┘

/shared:check-quality ──►  quality + security (parallel, read-only)

/svc:release       ──►  quality gate ──►  tester gate ──►  security gate ──►  release agent
                                                                                  │
                                                                                  ▼
                                                                          changelog + tag + PR

/gitops:promote <svc> <from> <to>   ──►  promote agent  ──►  PR (Argo reconciles on merge)
```

---

## Agents by plugin

### `svc` plugin

| Agent | Model | Job |
|---|---|---|
| `product-manager` | opus | User stories, acceptance criteria, issue triage |
| `architect` | opus | ADRs, implementation plans with parallel-safe metadata |
| `coder` | sonnet | Python implementation |
| `tester` | sonnet | pytest, coverage, bandit |
| `migrations` | sonnet | Alembic migrations |
| `observability` | sonnet | structlog + Prometheus + OTel scaffolding |
| `release` | sonnet | Semver, CHANGELOG, release branch + PR |
| `deployment` | sonnet | Dockerfile, base k8s, CI/CD |

### `gitops` plugin

| Agent | Model | Job |
|---|---|---|
| `deployment` | sonnet | ArgoCD ApplicationSet, cluster add-ons, overrides |
| `promote` | sonnet | Cross-environment version pinning |

### `shared` plugin

| Agent | Model | Job |
|---|---|---|
| `quality` | sonnet | ruff + mypy |
| `security` | sonnet | pip-audit + detect-secrets + bandit + trivy |

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
| `k8s/base/` | Base Kubernetes manifests |
| `k8s/overlays/<env>/` | Environment-specific Kustomize overlays |
| `k8s/monitoring/alerts.yaml` | Prometheus alerting rules |
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
