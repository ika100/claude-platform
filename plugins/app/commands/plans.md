---
description: Lists and manages multi-repo plans in docs/plan/ of a gitops-app repo (ADR-011 lifecycle: draft → in_progress → completed | abandoned). Usage: /app:plans [list [--all] | show <slug> | start <slug> | done <slug> <repo-id> | abandon <slug>]
---

You manage the lifecycle of multi-repo plans written by `/app:build-feature`. This is a thin wrapper over `scripts/plan.py` in the gitops-app repo.

**Arguments:** $ARGUMENTS (default: `list`)

---

## Pre-flight

Resolve the shape: run this in one Bash call: `P="${XDG_CACHE_HOME:-$HOME/.cache}/claude-platform"; { [ -d "$P/.git" ] && git -C "$P" fetch -q --depth 1 origin main && git -C "$P" checkout -q FETCH_HEAD; } || { rm -rf "$P"; git clone -q --depth 1 https://github.com/ika100/claude-platform.git "$P"; }; uv run "$P/scripts/cplat/cplat.py" shape` It must report `shape: gitops-app`, else stop. Confirm `scripts/plan.py` exists; if not, tell the user to run `/shared:update-service` (older skeleton) and stop.

## Dispatch

Run exactly one of (all through devbox):

| Arguments | Command |
|---|---|
| *(none)* or `list [--all]` | `devbox run -- uv run scripts/plan.py list [--all]` — draft + in_progress by default |
| `show <slug>` | `devbox run -- uv run scripts/plan.py show <slug>` — topo-ordered checklist |
| `start <slug>` | `devbox run -- uv run scripts/plan.py start <slug>` — draft → in_progress |
| `done <slug> <repo-id>` | `devbox run -- uv run scripts/plan.py done <slug> <repo-id>` — marks the repo done; completes the plan when all are done |
| `abandon <slug>` | `devbox run -- uv run scripts/plan.py abandon <slug>` — asks the user to confirm first |

Anything else: print the table above and stop.

After a state-changing command (`start`, `done`, `abandon`) run `devbox run plan-check`, then offer to commit the plan file (`git add docs/plan/<slug>.md && git commit -m "docs(plan): <slug> <new status>"`). Never push without confirmation.

## Rules

- Only `docs/plan/*.md` changes. Never touch `services.yaml`, overlays or other repos.
- Print the script's output verbatim; do not paraphrase the checklist.
