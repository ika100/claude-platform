# ADR-017: The GitOps repo owns every Kubernetes manifest; services ship an image

**Status:** Accepted
**Date:** 2026-10-07
**Supersedes (in part):** ADR-014 (remote Kustomize bases, per-service `k8s/base`), ADR-006 overlays-per-service-repo assumption, ADR-012 `deploy-check`

## Context

The end-to-end todo-app test (platform v1.1.1) found that the Kubernetes files inside each *service* repo were the main source of defects: an invalid `team: "@owner"` label that made every Deployment unappliable, `API_URL` wiring hard-coded in the web repo (a product concern, not a service concern), replicas wrong for an in-memory app, `k8s/base/deployment.yaml` overwritten by skeleton updates, non-numeric container users, kustomize `?ref=` versus image-tag confusion (`sha-<short>` is not a git ref; semver images have no `v`), and private-repo credentials needed by Argo **and** by CI just to `kustomize build` another repo. Service-level `overlays/{local,staging,prod}`, `k3d`, `kubectl`, `k9s` and `deploy`/`deploy-check` were unused once a gitops-app repo existed.

## Decision

1. **Services ship only a container image.** The four service templates (`service-python`, `service-java`, `service-go`, `web-nextjs`) contain no `k8s/` directory and no Kubernetes tooling; `shapes.py check` fails if one reappears.
2. **The gitops-app repo generates all manifests** from `applications/<app>/services.yaml` (+ `app.yaml`) with `scripts/render.py`: `deployment.yaml`, `service.yaml`, optional `httproute.yaml`, and a `kustomization.yaml` that pins the image tag. No remote bases, no `?ref=`; Argo reads only the gitops repo.
3. **`shapes.yml` carries `runtime:` defaults** per deployable shape (port, probe paths, numeric user, writable volumes, env, resources). `/gitops:compose add` copies them into a **complete, explicit** `services.yaml` entry (the service's own `.copier-answers.yml` `port` wins), so every value is reviewable and the generator stays shape-agnostic.
4. **Wiring is product configuration**: `env` (e.g. `API_URL: http://todo-api`), `replicas` and `resources` per environment, `secretRefs` (names only), `expose`.
5. **Environments are opt-in**: a service is rendered only for the environments in `environments` (default `[dev]`); `/gitops:promote` adds `staging`, then `prod`. A new service no longer reaches prod on day one.
6. **Promotion pins an image tag only**: staging `sha-<first 7 of the commit>` of a main build, prod `X.Y.Z` (the `vX.Y.Z` git tag without `v`, exactly what CI publishes); both verified to exist in GHCR before the PR is opened.
7. **Exposure uses the Gateway API**: `expose:` renders an `HTTPRoute` attached to the gateway named in `app.yaml`; the hostname comes from a per-environment template (dev default `{service}.{app}-dev.localhost`; `*.localhost` resolves to loopback everywhere, unlike `localtest.me`/nip.io which a rebind-protecting DNS blocks). `cluster-up` enables Traefik's Gateway provider on k3s (the Gateway API CRDs already ship with k3s' `traefik-crd` chart — installing them ourselves races with that Helm install and breaks a fresh cluster, found by the e2e test; `HelmChartConfig`: `providers.kubernetesGateway.enabled`, `gateway.listeners.web.namespacePolicy: All`) — verified on k3s v1.32.5 / Traefik 3.3.6. Real clusters point `gateway:` at their own controller.
8. The Deployment selector stays `app: <name>` (what v1 used), so migrating a running v1 Deployment is an in-place update, not a recreate.

## Consequences

- **Breaking → platform v2.** Migration: for each service `/gitops:compose add <svc> --from-k8s` (seeds the entry from the service's `k8s/base`), then `/shared:update-service --migrate` in the service repo (removes `k8s/`), then `devbox run render` / PR in the gitops repo. Existing v1 `services.yaml` entries (with `path:`) fail `render.py` with an actionable error.
- Gone: `SERVICE_REPOS_TOKEN`, Argo credentials for service repos, `deploy`/`deploy-check` recipes, `owner_label`, per-service PrometheusRule files (alerting moves to a gitops-side add-on, tracked as a follow-up). The platform-wide "ApplicationSet discovers service repos by topic" mode and its `promote` variant only apply to v1 services.
- Trade-off: changing a probe path or port is now a two-repo change (Dockerfile/app + `services.yaml`); the deployment agents say so explicitly. A service-side descriptor can be added later if this hurts.
- Generated manifests are validated offline in CI (`check-k8s-labels.py`, `kubectl kustomize`, kubeconform with Argo/Gateway CRD schemas) and server-side on a real cluster in the e2e job.
