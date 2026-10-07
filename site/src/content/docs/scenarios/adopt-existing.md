---
title: "Adopt an existing repository"
description: "Bring existing services or a v1 setup onto the platform without starting over."
---

**Situation.** You have working repositories and want the platform's flow (agents, CI, GitOps) without rebuilding them.

## Steps

1. **Install the plugins** in the repository and run `/shared:doctor`.
2. **Add the platform reference** and adopt the template for skeleton updates so CI, Dockerfile, `devbox` recipes and `CLAUDE.md` can be pulled in later with `/shared:update-service` ([Adopting](/sdlc-foundry/guides/adopting/) has the exact steps per shape).
3. **Review the update branch.** `/shared:update-service` writes to a review branch and lists which skeleton files it overwrote; keep your customisations in the files that are project-owned (application code, tests, documentation).
4. **Compose the service into a GitOps repository**: `/gitops:compose add <service>` writes a complete, reviewable `services.yaml` entry using the shape's runtime defaults.

## Migrating from platform v1 (services shipped Kubernetes manifests)

```text
/gitops:compose add <svc...> --from-k8s    # seeds port, probes, env, replicas, resources from the old k8s/base
/shared:update-service --migrate           # in each service repo: removes k8s/ and obsolete recipes on a review branch
```

Existing image pins are kept, so ArgoCD updates the running Deployments in place instead of recreating them. If some services are still in the old format the command refuses and prints the single command that migrates them together.

## What you get

A service repository that contains code and an image build, a GitOps repository that owns every manifest, and an update path for the skeleton that never touches your code.

## If something looks wrong

`/shared:doctor` first; then see [Troubleshooting](/sdlc-foundry/guides/adopting/#troubleshooting); then `/shared:report-issue`.
