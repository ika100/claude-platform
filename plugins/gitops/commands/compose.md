---
description: "Add/remove services in a gitops-app repo: writes a complete services.yaml entry, regenerates manifests, opens one PR. Usage: /gitops:compose add|remove <service...> [--expose] [--env K=V] [--generate S=K,K] [--secret S=K,K] [--from-k8s]"
---

Run the platform script inside the gitops-app repo. **Request:** $ARGUMENTS

Prefix for every call (one Bash call each; run it from the repo root):

```bash
P="${XDG_CACHE_HOME:-$HOME/.cache}/claude-platform"; { [ -d "$P/.git" ] && git -C "$P" fetch -q --depth 1 origin "${REF:-main}" && git -C "$P" checkout -q FETCH_HEAD; } || { rm -rf "$P"; git clone -q --depth 1 --branch "${REF:-main}" https://github.com/ika100/claude-platform.git "$P"; }; uv run "$P/scripts/cplat/cplat.py" compose <ARGS>
```

1. **Preview** with `--dry-run`; show it verbatim. Errors carry a `fix:` line (typical: repo missing the `deployable-service` topic, service not found, dirty tree) — show them and stop.
2. **Run** with `--pr` (one PR per invocation, however many services). Creating the branch and PR is what the user asked for; do not ask again.
3. **Report** the script's output. Remind the user of the two follow-ups in it: adapt the new entry if the service needs wiring (`env`, `replicas`, `--expose`), and that new services start in `dev` only — `/gitops:promote` moves them on.

Migrating a service that still has `k8s/base` (platform v1)? Add `--from-k8s` to seed port, probes, env, replicas and resources from it; afterwards `/shared:update-service --migrate` removes the service's `k8s/` directory.

Secrets: `--generate NAME=KEY,KEY` makes External Secrets Operator create random values in the cluster (DB passwords, signing keys); `--secret NAME=KEY` declares values read from the secret store (set locally with `/gitops:secret`). Values never go to git.

Rules: only `applications/` and `bootstrap/` change; never `kubectl apply`; never add GitHub topics (report the missing one instead).
