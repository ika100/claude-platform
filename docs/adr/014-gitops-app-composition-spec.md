# ADR-014: gitops-app composition spec

**Status:** Accepted
**Date:** 2026-05-22

## Context

PRD §6 B5 ("`compose` agent") and B6 ("cross-repo promote") describe what the agents do but not the concrete manifest layout they read and write. Without that schema, agents can't be implemented and the `gitops-app` Copier template can't be scaffolded.

This ADR resolves three coupled gaps surfaced in [end-to-end-scenario.md](../requirements/end-to-end-scenario.md) Q13, Q14, Q15.

## Decision

A `gitops-app` repo has this layout:

```
<gitops-app-repo>/
├── applications/<app-name>/
│   ├── applicationset.yaml         # one ApplicationSet per environment, List generator
│   ├── services.yaml               # human-edited registry of component services
│   └── overlays/
│       ├── dev/
│       │   ├── kustomization.yaml  # bases + image tag pins
│       │   └── images.yaml         # per-service image: latest
│       ├── staging/
│       │   └── … (sha-<short> or semver pins, edited by /gitops:promote)
│       └── prod/
│           └── … (semver pins, edited by /gitops:promote)
├── docs/plan/                       # multi-repo plans written by /app:build-feature
└── .copier-answers.yml
```

### `services.yaml` schema

```yaml
services:
  - name: taskboard-api
    repo: ika100/taskboard-api
    shape: service-python
    path: k8s/base                  # path in service repo to use as Kustomize base
  - name: taskboard-web
    repo: ika100/taskboard-web
    shape: web-nextjs
    path: k8s/base
```

The `compose` agent edits this file; the ApplicationSet's List generator reads it (via a small in-repo script or a yq-rendered template).

### ApplicationSet generator — List generator from `services.yaml`

One ApplicationSet per environment, parameterised by `services.yaml`:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: <app-name>-dev
spec:
  generators:
    - list:
        elements: |  # rendered from services.yaml at PR time
          - name: taskboard-api
            repoURL: https://github.com/ika100/taskboard-api
            …
  template:
    metadata:
      name: '{{name}}-dev'
    spec:
      source:
        repoURL: https://github.com/ika100/<gitops-app-repo>
        path: applications/<app-name>/overlays/dev
      …
```

List generator chosen (over Git directory or SCM Provider generators) because it makes the service set explicit and reviewable in `services.yaml` — every add/remove is a visible diff. Implicit discovery patterns are more magical but harder to audit.

### `dev` overlay pin policy — `latest` (track-main mode)

The `dev` overlay's `images.yaml` pins every service's image to `latest`. ArgoCD's image-updater (or Argo's normal reconcile loop with `imagePullPolicy: Always`) picks up new images as they're pushed on every merge to `main` — dev tracks `main` automatically.

`staging` and `prod` overlays pin to specific `sha-<short>` (staging) and semver (`v1.2.3`, prod) tags, edited only by `/gitops:promote` PRs.

### `.platform-app.yml` in service repos (for B6)

Service repos that belong to a gitops-app drop a `.platform-app.yml` at repo root:

```yaml
# .platform-app.yml
gitops_apps:
  - ika100/taskboard-app
```

`gitops_apps` is a list — a service can belong to multiple apps (e.g., a shared identity service used by two products). `/gitops:promote` invoked from a service repo reads this file to resolve the target gitops-app. If multiple are listed, the agent prompts the user to pick.

The Copier template adds an optional `--app <org>/<repo>` flag to `/shared:new-service` that pre-populates `.platform-app.yml`. Users can add or edit it later by hand.

### `compose remove`

Symmetric to `compose add`: removes the service from `services.yaml`, opens a PR. After merge, ArgoCD prunes the Application (if `syncPolicy.automated.prune: true` is set on the ApplicationSet — which the template defaults to `true`).

### Batch operations

`compose` and `promote` accept multiple services in one invocation and open **one PR per logical operation**, not one per service:

- `/gitops:compose add <svc1> <svc2> ...` — single PR adding all listed services to `services.yaml` and the ApplicationSet.
- `/gitops:compose remove <svc1> <svc2> ...` — single PR removing all listed services.
- `/gitops:promote <svc1> <svc2> ... <from> <to>` — single PR pinning the given services in the target overlay.
- `/gitops:promote --all <from> <to>` — single PR promoting every service currently in `services.yaml` one env step.

Batch mode is the default ergonomic for multi-service products; single-service invocations are just `n=1` of the batch path.

## Rationale

- **Explicit beats implicit.** `services.yaml` is human-readable; reviewers can see the set of components at a glance. Git directory and SCM Provider generators are less reviewable.
- **`latest` in dev matches developer expectation.** "Merge to main, see it in dev" is the velocity contract; pinning sha in dev breaks that loop.
- **`.platform-app.yml` is grep-able and supports multi-app membership.** Reusing `.copier-answers.yml` for this would conflate shape-detection with operational config and hide the membership behind a key most users don't read.

## Consequences

- The `gitops-app` Copier template ships all of the above scaffolding: `applicationset.yaml` templates, `services.yaml` skeleton, three overlay directories with starter `kustomization.yaml`, and the README that explains the layout.
- The `compose` agent has a tight, parseable schema to edit (`services.yaml` is YAML, not freeform Markdown).
- The `promote` agent reads `services.yaml` to validate that the service being promoted is actually a member of the app, then edits the relevant overlay's `images.yaml`.
- `/shared:new-service` gains an optional `--app <org>/<repo>` flag; un-flagged service repos work fine, they just need a manual `.platform-app.yml` edit later if they ever join an app.

## References

- [platform-vision.md §6 B5, B6](../requirements/platform-vision.md)
- [ADR-006](006-gitops-app-overlay-structure.md) — env-only overlay decision this ADR concretises
- [end-to-end-scenario.md Q13, Q14, Q15](../requirements/end-to-end-scenario.md)
