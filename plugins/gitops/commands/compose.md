---
description: Adds or removes component services in a gitops-app repo (services.yaml + generated ApplicationSets/overlays) and opens one PR. Usage: /gitops:compose add|remove <service> [<service>...]
---

You are the **compose orchestrator** for a `gitops-app` repository. Drive an add/remove operation through pre-flight, the compose agent, and PR creation.

**Arguments:** $ARGUMENTS

Expected format: `add|remove <service> [<service>...]`. If malformed, print usage and stop.

---

## Phase 1 — Pre-flight

1. Detect the shape per `plugins/shared/fragments/shape-detection.md`. It must be `gitops-app`; otherwise stop: "`/gitops:compose` only works inside a gitops-app repo (created with `/shared:new-service <name> --gitops`)."
2. `git status --porcelain` must be empty; otherwise stop.
3. Back on a clean main: `git checkout main && git fetch origin && git merge --ff-only origin/main` (skip `fetch`/`merge` if there is no `origin` yet).
4. Resolve the application: `applications/*/services.yaml`. If exactly one, use it. If several, ask the user which app (free-form text, once).

Print `## Phase 1 complete — app: <app>, op: <add|remove>, services: <list>`.

---

## Phase 2 — Compose

Spawn the **compose** agent (`gitops:compose`) with `OP`, `SERVICES`, `APP_FILE`. Wait for it. If it stops (missing topic, missing repo, validate failure), relay its message verbatim and stop — do not retry with workarounds.

---

## Phase 3 — Report

```
## Compose PR opened

| Field | Value |
|---|---|
| Operation | add|remove |
| Services | <list> |
| PR | <URL> |

Next: review and merge. For `add`: dev tracks `main`; run `/gitops:promote <services> dev staging` to pin staging.
For `remove`: Argo prunes the Applications after merge.
```

---

## Rules

- One PR per invocation, regardless of how many services are listed (batch operations, ADR-014).
- Never auto-merge. Never `kubectl apply`.
- Never add GitHub topics — report the missing topic and let the user fix it.
