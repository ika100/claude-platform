---
description: "One-table overview of a product (run in its gitops-app repo) — which image each environment pins, whether each service's CI on main is green, and ArgoCD sync/health. Usage: /shared:status [--context <kube-context>]"
---

Show the product status. One Bash call from the gitops-app repo root:

```bash
cplat status <ARGS>
```

Pass `--context k3d-<app>-local` (or the user's cluster context) when they want the Argo column. Show the table verbatim, then add at most three lines: anything not `ok`/`Synced/Healthy`, whether staging/prod lag behind dev, and the one command that would fix the most obvious problem. Read-only: never change anything.

> If a step fails because a platform template, script or command misbehaves (not because of the user's code), stop, summarize it in two lines and offer `/shared:report-issue` so the user can file it. Never file anything without their OK.
