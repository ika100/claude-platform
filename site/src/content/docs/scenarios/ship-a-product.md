---
title: "Ship a product from zero"
description: "From an idea to a running, promoted application: GitOps repo, services, first environment."
---

**Situation.** You are starting "Shop": a Java API and a Next.js web app. You have no repositories.

## Steps

```text
/shared:new-service shop Product GitOps repo --gitops
/shared:new-service shop-api Catalog and orders API --type service-java
/shared:new-service shop-web Storefront --web
```

Each command shows a preview first, then creates the repository from its template (CI, Dockerfile, `devbox` recipes, agent instructions), makes the first commit and creates a private GitHub repository. Service repositories get the `deployable-service` topic so tooling can find them.

In `shop-api` and `shop-web`, build features with the agents (see [Build a feature](/sdlc-foundry/scenarios/build-a-feature/)). When CI has published the first images, compose the product in the GitOps repository:

```text
/gitops:compose add shop-api
/gitops:compose add shop-web --expose --env API_URL=http://shop-api
```

Each call shows a preview, edits `applications/shop/services.yaml`, regenerates every manifest and opens one pull request (`--expose` publishes only the web app, `--env` wires it to the API inside the cluster). Merge them, then run the application locally:

```bash
devbox run cluster-up      # k3d, ArgoCD, Gateway API, your GitHub credentials, the root Application
```

## What you get

- Two repositories that build, test, scan and publish `linux/amd64` and `linux/arm64` images on every merge to `main`.
- A GitOps repository containing the generated Deployments, Services and routes for the `dev` environment, synced by ArgoCD.
- `http://shop-web.shop-dev.localhost:8088/` once the pods are ready (hostnames come from the `hosts` template in `app.yaml`; `*.localhost` needs no DNS setup); `/shared:status` shows the pinned image per environment.

## Check it

`/shared:doctor` reports missing tools or `gh` scopes with a fix for each. If something fails because a template or script misbehaves, `/shared:report-issue` drafts an issue for you.

Next: [Promote to production safely](/sdlc-foundry/scenarios/promote-safely/).
