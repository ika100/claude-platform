---
title: "Run it on your laptop"
description: "devbox run cluster-up creates a local k3d cluster with ArgoCD, the Gateway API and your application."
---

In the GitOps repository:

```bash
devbox run cluster-up      # about 2 minutes the first time
devbox run cluster-down    # removes the cluster and its registry
```

## What `cluster-up` does

1. Creates (or reuses) a k3d cluster named `<app>-local` on a pinned k3s image, mapping port `8088` to the Gateway.
2. Enables the Gateway API on k3s' built-in Traefik, so `HTTPRoute`s work and `*.localhost` host names resolve without any DNS setup.
3. Installs ArgoCD, hands it read access to your private GitOps repository, pre-creates the `<app>-dev`, `-staging` and `-prod` namespaces with an image pull secret for GHCR, and applies the root Application.
4. Installs only what your declarations need: External Secrets Operator, CloudNativePG (if `addons.postgres`), Kyverno (if `policies:`), a Grafana dev stack (if `observability: {ui: lgtm}`).
5. Prints the URLs of exposed services and of Grafana.

Then watch it converge:

```bash
kubectl --context k3d-<app>-local -n argocd get applications
kubectl --context k3d-<app>-local -n <app>-dev get pods
```

or use `/shared:status` for one table.

## Credentials

By default `cluster-up` uses your `gh` login for ArgoCD and for the image pull secret and says so. For least privilege set `REPO_TOKEN` (a fine-grained token with contents:read on the GitOps repo) and `PULL_TOKEN` (read:packages only).

## Options

All environment variables (versions, `WITH_*` switches, ports, registry) are listed in the [configuration reference](/claude-platform/reference/configuration/#devbox-run-cluster-up-local-clustersh). Examples:

```bash
LOCAL_HTTP_PORT=9090 devbox run cluster-up   # different host port
WITH_KYVERNO=0 devbox run cluster-up         # skip an operator
```

## Real clusters

The platform never applies manifests to a real cluster by itself. A human bootstraps it once with `KUBE_CONTEXT=<context> devbox run bootstrap`; from then on every change arrives through merged pull requests and ArgoCD. Operators for the features you use (External Secrets, CloudNativePG, Kyverno) must be installed there by the cluster's owner.
