---
description: "Declare addons for the application (postgres, observability). Usage: /gitops:addon add|remove|list <postgres|observability> [--version N] [--ui lgtm] [--export-to URL]"
---

Run the platform script inside the gitops-app repo. **Request:** $ARGUMENTS

```bash
P="${XDG_CACHE_HOME:-$HOME/.cache}/sdlc-foundry"; { [ -d "$P/.git" ] && git -C "$P" fetch -q --depth 1 origin "${REF:-main}" && git -C "$P" checkout -q FETCH_HEAD; } || { rm -rf "$P"; git clone -q --depth 1 --branch "${REF:-main}" https://github.com/ika100/sdlc-foundry.git "$P"; }; uv run "$P/scripts/cplat/cplat.py" addon <ARGS>
```

1. **Preview** with `--dry-run` and show it verbatim; errors carry a `fix:` line.
2. **Run** with `--pr` (one PR; the user asked for it, do not ask again).
3. **Next**: services opt in with `/gitops:compose add <service> --uses postgres` (or `uses: [postgres]`), which injects `DATABASE_URL` and `PG*`. The operator (CloudNativePG) must exist in the cluster; `devbox run cluster-up` installs it locally.

`observability` needs no `uses:`: every service gets `OTEL_*` variables and a collector per environment (`--ui lgtm` = local Grafana dev stack, `--export-to` = your OTLP/HTTP backend). Removing an addon never deletes the database; say so. No backups/PITR/pooling are provided (ADR-020).

> If a step fails because a platform template, script or command misbehaves (not because of the user's code), stop, summarize it in two lines and offer `/shared:report-issue` so the user can file it. Never file anything without their OK.
