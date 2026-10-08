---
description: "Product specs and their multi-repo plans in a gitops-app repo: status, next step, per-repo progress. Usage: /app:specs [--all | show <id> | done <id> <repo> | abandon <id>]"
---

Show and track the product's specs and plans ([ADR-011](../../../docs/adr/011-multi-repo-plan-format.md), [ADR-026](../../../docs/adr/026-feature-specs.md)). **Arguments:** $ARGUMENTS (default: list)

`cplat` is on the Bash PATH while the shared plugin is enabled and runs the platform script at the version your plugins were installed from (no fetch); one call per Bash invocation:

```bash
cplat <ARGS>
```

Run `shape` first: it must report `gitops-app`. `scripts/plan.py` must exist (otherwise `/shared:update-service`).

| Arguments | Run |
|---|---|
| *(none)* / `--all` | `spec list [--all]` (prefix), then `devbox run -- uv run scripts/plan.py list [--all]` |
| `show <id>` | `devbox run -- uv run scripts/plan.py show <spec_id>` |
| `done <id> <repo-id>` | `devbox run -- uv run scripts/plan.py done <spec_id> <repo-id>`; when the plan reports `completed`, also `spec set-status <spec_id> done` and `spec index` |
| `abandon <id>` | ask for confirmation, then `devbox run -- uv run scripts/plan.py abandon <spec_id>` and `spec set-status <spec_id> superseded --reason "abandoned"` |

Anything else: print the table and stop. Print every output verbatim. After a state change run `devbox run plan-check` and offer to commit the plan and spec (`docs(plan): <spec_id> <new status>`); never push without confirmation. Plans written before ADR-026 (no `spec:`) are shown and tracked the same way by their `plan_id`.

> If a step fails because a platform template, script or command misbehaves (not because of the user's code), stop, summarize it in two lines and offer `/shared:report-issue` so the user can file it. Never file anything without their OK.
