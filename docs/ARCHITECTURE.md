# Architecture

Why the platform looks the way it does.

## The problem

The ika100 fleet has many Python service repos (FastAPI-style, devbox-driven, k8s-deployed) plus one GitOps repo that wires them together via ArgoCD. The agentic Claude Code setup we built for the first service (money-maker) is ~99% generic — the 10 agents, 7 slash commands, and orchestration model would work for any repo with the same shape. But hand-copying them into each new repo doesn't scale:

- **Drift.** Each copy diverges from the others as agents get tweaked.
- **No central updates.** Improving the architect's plan format requires editing N repos.
- **Project-specific hardcoding.** `devbox.json`'s `--cov=<module>` and `<project>:scan` Docker tag have to be sed-replaced every time.

## The shape we chose

Two channels of distribution:

1. **Claude Code marketplace** — three plugins (`svc`, `gitops`, `shared`) published from this repo. Consumers reference the marketplace in their `.claude/settings.json`; updates flow via `/plugin marketplace update`.

2. **Copier templates** — two templates (`service-python`, `library-python`) that ship the project skeleton: `devbox.json`, CI workflow, `CLAUDE.md`, Dockerfile, k8s manifests, `pyproject.toml`. Updates flow via `copier update`.

These two channels run at different speeds — agents evolve frequently, project skeletons evolve rarely — and `copier update` does the conflict resolution Copier is good at. Maintaining two artifacts is cheaper than maintaining one big one that conflates both.

## Why not GitHub Templates

GitHub Templates fork once and then drift forever. Copier's `copier update` reconciles a generated repo with template changes, including conflict resolution for files the consumer customised. That's the killer feature: improvements to the CI workflow or devbox recipes can flow into existing repos without re-cloning.

## Why three plugins, not one

Different repo roles need different agents:

- A Python service needs `coder` / `tester` / `migrations` / `deployment`.
- The GitOps repo needs `deployment` (a different one — focused on ApplicationSets) and `promote`; no Python `coder`.
- A library needs `coder` / `tester` but no `deployment`.

Single-plugin would force every consumer to load every agent. The three-plugin split lets each repo enable only what it uses.

`shared` exists because `quality` and `security` are needed by every repo. Pulling them into a shared plugin avoids three definitions of the same agent drifting apart.

## Why ArgoCD ApplicationSet

The standard alternative — manually registering each new service in the GitOps repo by editing a list of Applications — is friction that scales linearly with services. `ApplicationSet` with the GitHub `scmProvider` generator auto-discovers any repo with the `deployable-service` topic. New service repo + topic → Argo Application appears within ~3 minutes. Zero edits to the gitops repo.

The contract enforced by this convention:

- Service repos opt in via the GitHub topic `deployable-service` (the Copier template's post-task adds it automatically).
- Every service has `k8s/overlays/prod/kustomization.yaml`.
- Argo `Application` name == GitHub repo name.

Promotion across environments (staging → prod) is the one explicit, human-approved step — `/gitops:promote` pins an image tag in the target overlay and opens a PR. Argo reconciles after merge.

## What this is NOT

- It is **not** a service catalog or developer portal (Backstage territory). We don't need an internal UI yet — at the current scale, slash commands and a marketplace cover developer experience well enough.
- It is **not** opinionated about cloud or k8s flavor — manifests are pure Kustomize, the ApplicationSet uses ArgoCD's GitHub scmProvider, Flux is supported with minor changes (replace the ApplicationSet with `GitRepository` + a generator action).
- It is **not** a vendor of agents. Agents and templates are deliberately thin wrappers around devbox, gh, kubectl, and copier. We add intelligence (when to fan coders out, how to gate quality) but not new tooling.

## When this stops being the right shape

If the fleet grows past ~15–20 services with a dedicated platform team, the next step is Backstage-style scaffolder + service catalog. Until then, the marketplace + Copier combo is the sweet spot.
