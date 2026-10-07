---
description: "One-table overview of a product (run in its gitops-app repo) — which image each environment pins, whether each service's CI on main is green, and ArgoCD sync/health. Usage: /shared:status [--context <kube-context>]"
---

Show the product status. One Bash call from the gitops-app repo root:

```bash
P="${XDG_CACHE_HOME:-$HOME/.cache}/claude-platform"; { [ -d "$P/.git" ] && git -C "$P" fetch -q --depth 1 origin main && git -C "$P" checkout -q FETCH_HEAD; } || { rm -rf "$P"; git clone -q --depth 1 https://github.com/ika100/claude-platform.git "$P"; }; uv run "$P/scripts/cplat/cplat.py" status <ARGS>
```

Pass `--context k3d-<app>-local` (or the user's cluster context) when they want the Argo column. Show the table verbatim, then add at most three lines: anything not `ok`/`Synced/Healthy`, whether staging/prod lag behind dev, and the one command that would fix the most obvious problem. Read-only: never change anything.
