---
description: "Add, change or remove services in a gitops-app repo (services.yaml, rendered manifests, one PR). Usage: /gitops:compose add|set|remove <service...> [--env K=V] [--expose [HOST]] [--uses ADDON] [--replicas N] [secrets…] [--from-k8s]"
---

Run the platform script inside the gitops-app repo. **Request:** $ARGUMENTS

`cplat` is on the Bash PATH while the shared plugin is enabled and runs the platform script at the version your plugins were installed from; one call per Bash invocation, from the repo root:

```bash
cplat compose <ARGS>
```

1. **Preview** with `--dry-run`; show it verbatim. Errors carry a `fix:` line (typical: repo missing the `deployable-service` topic, service not found, dirty tree) — show them and stop.
2. **Run** with `--pr` (one PR per invocation, however many services). Creating the branch and PR is what the user asked for; do not ask again.
3. **Report** the script's output. Remind the user of the two follow-ups in it: wire the new entry if the service needs it (`/gitops:compose set <service> --env … --expose …`), and that new services start in `dev` only — `/gitops:promote` moves them on.

**Changing a service that is already composed** (spec 045): `set <service>` with `--env K=V`, `--expose [HOST]`, `--uses ADDON` or `--replicas N` merges into its existing entry (other env variables stay) and re-renders; `add` refuses a service that is already there. One service per `set`. Typical wiring: `set todo-web --env TODO_API_URL=http://todo-api --expose todo-web`, `set todo-api --uses postgres` (after `/gitops:addon add postgres`).

Migrating a service that still has `k8s/base` (platform v1)? Add `--from-k8s` to seed port, probes, env, replicas and resources from it; afterwards `/shared:update-service --migrate` removes the service's `k8s/` directory.

Secrets: `--generate NAME=KEY,KEY` makes External Secrets Operator create random values in the cluster (DB passwords, signing keys); `--secret NAME=KEY` declares values read from the secret store (set locally with `/gitops:secret`). Values never go to git.

Rules: only `applications/` and `bootstrap/` change; never `kubectl apply`; never add GitHub topics (report the missing one instead).

> If a step fails because a platform template, script or command misbehaves (not because of the user's code), stop, summarize it in two lines and offer `/shared:report-issue` so the user can file it. Never file anything without their OK.
