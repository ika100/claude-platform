---
description: "Declare backing services for the application (Postgres). Usage: /gitops:addon add|remove|list [postgres] [--version N]"
---

Run the platform script inside the gitops-app repo. **Request:** $ARGUMENTS

```bash
P="${XDG_CACHE_HOME:-$HOME/.cache}/claude-platform"; { [ -d "$P/.git" ] && git -C "$P" fetch -q --depth 1 origin "${REF:-main}" && git -C "$P" checkout -q FETCH_HEAD; } || { rm -rf "$P"; git clone -q --depth 1 --branch "${REF:-main}" https://github.com/ika100/claude-platform.git "$P"; }; uv run "$P/scripts/cplat/cplat.py" addon <ARGS>
```

1. **Preview** with `--dry-run` and show it verbatim; errors carry a `fix:` line.
2. **Run** with `--pr` (one PR; the user asked for it, do not ask again).
3. **Next**: services opt in with `/gitops:compose add <service> --uses postgres` (or `uses: [postgres]`), which injects `DATABASE_URL` and `PG*`. The operator (CloudNativePG) must exist in the cluster; `devbox run cluster-up` installs it locally.

Removing an addon never deletes the database; say so. No backups/PITR/pooling are provided (ADR-020).
