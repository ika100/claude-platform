# User journey: from empty folder to a running SaaS product

A guided walk-through of the whole platform, told through one made-up product, **Taskboard** (a Python API + a Next.js frontend, deployed by ArgoCD). Use it to explain the setup to someone new; every command below exists, and the reference docs are linked at the end.

**You type slash commands in Claude Code. Claude does the engineering; you review pull requests.**

---

## The mental model (2 minutes)

```
                          ┌────────────────────────────┐
                          │  ika100/claude-platform    │   one marketplace repo
                          │  plugins  +  templates     │
                          └──────────┬─────────────────┘
        /plugin install              │ /shared:new-service            /shared:update-service
        (agents & commands)          ▼ (skeleton, once)               (skeleton, later)
  ┌───────────────┐   ┌────────────────────────────────────────────────────────────┐
  │ Claude Code   │   │  Your repos                                                  │
  │ + devbox      │   │  taskboard           (gitops-app: which services, which     │
  └───────────────┘   │                       version runs in dev/staging/prod)     │
                      │  taskboard-api       (service-python)                        │
                      │  taskboard-web       (web-nextjs)                            │
                      └────────────────────────────────────────────────────────────┘
                                                     │  ArgoCD reconciles
                                                     ▼
                                                Kubernetes
```

Three ideas carry everything:

1. **Shapes.** Every repo has a *shape* (`service-python`, `web-nextjs`, `gitops-app`, `service-java`, `service-go`, `library-python`). The shape decides which template creates it and which agents work on it. You never pick agents; commands detect the shape.
2. **`devbox run <recipe>` is the only way anything runs** (`test`, `quality`, `security`, `image-build`, …). Same recipes in every shape, so humans, CI and agents behave identically.
3. **Two update channels.** Agents and commands update with `/plugin marketplace update`; the project skeleton (CI, Dockerfile, devbox, CLAUDE.md) updates with `/shared:update-service`. Your own code is never touched by either.

---

## Chapter 0 — One-time setup (10 minutes)

| Need | How |
|---|---|
| Claude Code | already installed |
| devbox | `curl -fsSL https://get.jetify.com/devbox/install.sh \| bash` |
| GitHub CLI, logged in | `gh auth login` (without it, `/shared:new-service` prints the GitHub commands instead of running them) |
| copier | installed for you via `uv` on first use |
| A Kubernetes cluster with ArgoCD | out of scope here; Argo needs read access to your GitHub repos |

Make the platform's commands available (once per machine/user, or pre-wired in each repo — step 1 of every new repo does that for you):

```
/plugin marketplace add ika100/claude-platform
/plugin install shared@ika100-claude
```

You can already create repos with just `shared`. Every generated repo enables the plugins it needs.

---

## Chapter 1 — Create the product's GitOps repo

```
/shared:new-service taskboard GitOps repo for the Taskboard product --gitops
```

What happens (no questions asked beyond the name and a description):

1. The `gitops-app` template is rendered, committed, and pushed to a new **private** repo `<you>/taskboard`.
2. You get `applications/taskboard/` with an empty `services.yaml`, generated ApplicationSets (dev/staging/prod) and `overlays/`, plus CI that validates everything (`kustomize build`, `kubeconform`, secret scan).
3. It is *not* tagged `deployable-service` (it is the GitOps source, not a service).

Open it: `cd taskboard && claude`. Its `CLAUDE.md` already explains the layout and pin policy to Claude.

> **One-time cluster step (manual).** Give Argo the ApplicationSets once, e.g. `kubectl apply -n argocd -f applications/taskboard/applicationset.yaml`, and make sure Argo can read the repos. After that everything is driven by pull requests — no more `kubectl apply`.

---

## Chapter 2 — Create the services

```
/shared:new-service taskboard-api Task CRUD API --app <you>/taskboard
/shared:new-service taskboard-web Taskboard frontend --web --app <you>/taskboard
```

Each command: renders the template → commits → creates a private repo → adds the `deployable-service` topic → writes `.platform-app.yml` (so `/gitops:promote` can later find `taskboard` from inside this repo).

| Repo | Shape | What you get on day one |
|---|---|---|
| `taskboard-api` | `service-python` | FastAPI app with `/health` + `/ready`, pytest + coverage gate, ruff/mypy, Dockerfile, k8s manifests, CI incl. image push |
| `taskboard-web` | `web-nextjs` | Next.js App Router, Vitest, `/api/health` `/api/ready` `/api/metrics`, Dockerfile, k8s manifests, CI |

Want Java or Go instead? `--type service-java` / `--type service-go`. A shared library? `--library`.

```bash
cd taskboard-api && devbox shell
devbox run quality && devbox run test      # sanity check — should be green out of the box
```

---

## Chapter 3 — Build a feature with the agent pipeline

In `taskboard-api`, inside Claude Code:

```
/svc:plan-feature "ping endpoint"           # optional: stories + plan only, no code
/svc:build-feature "ping endpoint"          # the full pipeline
```

What `/svc:build-feature` does (you watch phase headers, you are only asked before pushing):

| Phase | Who | Output |
|---|---|---|
| 0 | orchestrator | detects shape, creates `feature/<slug>`, refuses a dirty tree; tiny change? suggests `/svc:quick-task` instead |
| 1 | product-manager | user stories + acceptance criteria → `docs/backlog.md` |
| 2 | architect | `docs/plan/<slug>.md` with tasks, files, dependencies (and `shape:`) |
| 3 | shape's **coder** agents, in parallel git worktrees | implementation, merged with a quality gate between merges |
| 4 | quality ‖ tester ‖ security, in parallel | lint/types, tests + coverage, CVE + secrets scan |
| 5 | deployment | Dockerfile/k8s verified (`devbox run deploy-check`) |
| 7 | orchestrator | asks to push, opens a PR with a summary, linked issues, checklist |

You review and merge the PR. CI re-runs the same recipes and **pushes the image** on merge to `main` (`latest`, `sha-<short>`).

Smaller jobs: `/svc:quick-task "…"` (coder → quality → tester) and `/svc:fix-bug "stack trace or description"`. Any time: `/shared:check-quality` (read-only audit).

Same commands in `taskboard-web`: the orchestrator detects `web-nextjs` and uses the web coder/tester (Vitest, App Router idioms) instead.

---

## Chapter 4 — Put the services into the product

Both services have merged to `main` and their images exist. In `taskboard`:

```
/gitops:compose add taskboard-api taskboard-web
```

The compose agent verifies each repo exists, has the `deployable-service` topic and a `k8s/base`, detects its shape, edits `services.yaml`, regenerates ApplicationSets and overlays (`devbox run render`), validates (`devbox run validate`) and opens **one PR**. Merge it; Argo creates the Applications. **dev** now tracks each service's `main` automatically.

---

## Chapter 5 — Promote through the environments

```
/gitops:promote taskboard-api taskboard-web dev staging
```

One PR pinning both services in **staging** to the `sha-<short>` of the image currently built from their `main`. Merge → Argo rolls staging.

For **prod** you pin a release: in each service repo run `/svc:release` (quality gate → test gate → security gate → version bump → changelog PR → tag `vX.Y.Z` → CI pushes semver images). Then:

```
/gitops:promote taskboard-api staging prod            # newest released semver
/gitops:promote taskboard-web staging prod v1.2.0     # or an explicit version
```

The agent prints **ABOUT TO PROMOTE TO PRODUCTION** before opening the PR. Nothing auto-merges; rolling back is reverting the promote PR.

Run it from inside a service repo and it finds the GitOps repo through `.platform-app.yml`.

---

## Chapter 6 — A feature that spans repos

"Add billing" touches the API, the web app, maybe a shared models library. In `taskboard`:

```
/app:build-feature "add billing with Stripe checkout"
```

`/app:build-feature` is **plan-only**: it reads every registered service, asks the product-manager for stories tagged per repo, and the planner writes `docs/plan/add-billing….md` — repos in dependency order (library → API → web) with a paste-ready prompt for each and when to pin versions. It validates the plan and prints the hand-off:

```
Level 1:  cd ../taskboard-api && /svc:build-feature --from-plan <plan> taskboard-api
Level 2:  cd ../taskboard-web && /svc:build-feature --from-plan <plan> taskboard-web
Then:     /gitops:promote taskboard-api taskboard-web dev staging
```

Track it with `/app:plans` (`list`, `show <slug>`, `start`, `done <slug> <repo>`, `abandon`). Each repo still goes through the normal PR flow of Chapter 3.

---

## Chapter 7 — Living with it

| Situation | What to do |
|---|---|
| Agents or commands improved | `/plugin marketplace update` |
| CI / Dockerfile / devbox recipes improved in the template | `/shared:update-service` in each repo → review branch → PR |
| Need a feature flag in the template (e.g. migrations, observability) | `/shared:update-service --data needs_migrations=true` |
| New backend language/framework | `docs/templates.md` — add a shape; CI enforces the checklist |
| Repo existed before the platform | `docs/ADOPTING.md` (migration guides per shape) |
| Something broke in a recipe | fix `devbox.json` — never bypass it with raw `pnpm`/`mvn`/`go`/`uv` |

---

## The whole journey in one screen

```
/shared:new-service taskboard   GitOps repo for Taskboard --gitops
/shared:new-service taskboard-api  Task API --app me/taskboard
/shared:new-service taskboard-web  Frontend --web --app me/taskboard

(in each service)   /svc:build-feature "first feature"      → PR → merge → image pushed
(in taskboard)      /gitops:compose add taskboard-api taskboard-web
                    /gitops:promote taskboard-api taskboard-web dev staging
(in each service)   /svc:release                              → vX.Y.Z → semver image
(in taskboard)      /gitops:promote taskboard-api taskboard-web staging prod
(any time)          /app:build-feature "add billing"          → plan → /svc:build-feature --from-plan …
                    /shared:check-quality     /shared:update-service     /svc:fix-bug "…"
```

## Honest limits to mention when presenting

- Plugin commands are Claude prompts, not scripts: they follow the documented flow but ask you before pushing or opening PRs.
- Cross-repo work is **plan-only** in v1: you run `/svc:build-feature --from-plan` in each repo yourself.
- ArgoCD/cluster setup and registry credentials are outside the platform (see the one-time step in Chapter 1).
- Skeleton updates overwrite customised skeleton files by design; the review branch is where you keep or restore your changes.

## Where to read more

[README](../README.md) · [ADOPTING](ADOPTING.md) (new repos, migrations) · [AGENTS](AGENTS.md) (orchestration model) · [ARCHITECTURE](ARCHITECTURE.md) · [templates](templates.md) (add a shape) · [vision & ADRs](requirements/platform-vision.md)
