---
title: "Environments and promotion"
description: "dev, staging and production, opt-in per service, moved by pull request."
sidebar:
  order: 3
---

Each application has three environments, each in its own namespace `<app>-<env>`. A service is rendered only for the environments in its `environments` list (default `[dev]`), so a new service never reaches production by accident.

| Environment | Pinned image tag | Moves when |
|---|---|---|
| `dev` | `latest` (tracks the service's `main`) | the service's CI publishes |
| `staging` | `sha-<first 7 of the commit>` | `/gitops:promote <svc> dev staging` |
| `prod` | `X.Y.Z` (the service's release tag without `v`) | `/gitops:promote <svc> staging prod` |

`/gitops:promote` verifies in GHCR that the tag exists, edits `environments`, renders the overlay, pins the tag and opens one pull request. It only moves forward; rollback is reverting the merged pull request. Details and a walk-through: [Promote to production safely](/sdlc-foundry/scenarios/promote-safely/).
