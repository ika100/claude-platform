# ADR-011: Multi-repo plan format for `/app:build-feature`

**Status:** Accepted
**Date:** 2026-05-22

## Context

[ADR-007](007-cross-repo-orchestration-scope.md) made `/app:build-feature` v1 plan-only. The plan it writes wasn't given a concrete schema, leaving its producers (the architect agent extended for multi-repo planning) and consumers (`compose`, `promote`, and humans running `/svc:build-feature` per repo) without a contract.

## Decision

`/app:build-feature` writes `docs/plan/<slug>.md` in the gitops-app repo. The file is a **YAML metadata block followed by a Markdown body**, mirroring the existing per-service architect plan format.

### YAML schema

```yaml
---
plan_id: <slug>
feature: <one-line description>
gitops_app: <org>/<repo>          # the gitops-app this plan targets
status: draft                     # draft | in_progress | completed | abandoned
repos:
  - id: <repo-name>               # GitHub repo name (and key in the topo sort)
    shape: <shape-id>             # must be a key in shapes.yml (ADR-015)
    summary: <one-line>           # what this repo's PR does
    arguments: |                  # paste-ready prompt for /svc:build-feature
      <multi-line prompt text>
    depends_on: []                # list of repo ids this one waits on; empty for roots
    done: false                   # flipped to true after the per-repo PR merges
gitops_pin:
  - service: <repo-name>          # which service to pin
    overlay: dev|staging|prod
    apply_after: <repo-id> | merge_of_all
    note: <human-readable rationale>
---
```

### Lifecycle state machine

The `status` field tracks the plan's overall lifecycle. Transitions:

| From | Trigger | To |
|---|---|---|
| `draft` | `/app:build-feature` writes the plan | (initial state) |
| `draft` | first `/svc:build-feature --from-plan` invocation against any repo in the plan | `in_progress` |
| `in_progress` | per-repo PR merges → `done: true` for that repo; all `repos[].done: true` | `completed` |
| `draft` or `in_progress` | `/app:plans abandon <slug>` | `abandoned` |

The `/app:plans` command exposes these states — `list` shows `draft` + `in_progress` by default, `--all` includes terminal states.

### `--from-plan` consumption pattern

`/svc:build-feature --from-plan <path-to-plan> [<repo-id>]` reads the per-repo block keyed by `<repo-id>` (defaulting to the current repo resolved via `.platform-app.yml` from [ADR-014](014-gitops-app-composition-spec.md)), then runs as if the `arguments` field had been passed positionally. Side-effect: flips `repos[<id>].done: true` after the PR merges and advances the plan's `status` per the table above.

### Markdown body

Per-repo sections (one per `repos[]` entry, ordered by topo-sort):

```markdown
## <repo-id> — <summary>

**Shape:** `<shape-id>` · **Depends on:** [<repo-id>, ...] · **Run:** `/svc:build-feature` with the `arguments` block above.

<rationale: why this repo needs changes, expected file touches, test concerns>
```

A final section describes the gitops-app PR that pins the resulting image tags.

### Topo-sort and execution order

- The orchestrator sorts `repos[]` by `depends_on` so that library bumps land before their consumers, frontends land after the APIs they call, etc.
- Each level of the topo sort can contain multiple repos that can be worked in parallel (different repos, no shared files by definition).
- v1 plan-only stops here — the user reads the ordered plan and runs `/svc:build-feature` in each repo manually, in topo order.
- v2 (future ADR) uses the same schema to drive auto-dispatch and PR creation.

## Rationale

- Same shape as the architect's per-service plan ([AGENTS.md](../AGENTS.md) §"Parallel implementation via git worktrees") — agents and humans already know the format.
- `depends_on` is the only structural way to capture "library bumps before consumers"; phase numbers drift, prose narrative gets misread.
- Topo-sorted output is paste-ready: `/svc:build-feature` invocations in the printed order produce a working integration.

## Consequences

- The architect agent (or a thin wrapper specifically for app-level planning) emits this format when invoked from a `gitops-app` repo with `/app:build-feature`.
- The `compose` and `promote` agents read the `gitops_pin[]` section to know which overlays to update and when (per the `apply_after` field).
- Plan-format validation belongs in a small platform script (`scripts/validate-plan.py` or similar) that CI runs against `docs/plan/*.md` files in gitops-app repos.
- v2 execution mode can land without re-designing the format — it just adds an "execute" flag that the orchestrator honors.

## References

- [platform-vision.md §6 C2](../requirements/platform-vision.md)
- [ADR-007](007-cross-repo-orchestration-scope.md) — the plan-only v1 decision this ADR operationalises
- [end-to-end-scenario.md Q8/Q9](../requirements/end-to-end-scenario.md) — the gap this resolves

## Amendment (implementation, phase 5)

- `/app:build-feature` and `/app:plans` ship in their own marketplace plugin, **`app`** (a plugin's name is the slash-command namespace), enabled by the `gitops-app` template next to `gitops`, `svc` and `shared`.
- Validation and lifecycle edits are implemented by `scripts/plan.py` **in the `gitops-app` template** (not the platform repo), so every application repo has it: `devbox run plan-check` (also part of `devbox run validate`, hence CI), and `plan.py list|show|start|done|abandon`. The platform repo tests it in `scripts/test-plan.sh` against `tests/fixtures/plans/`.
- `/svc:build-feature --from-plan` runs in a *component* repo, so it never edits the plan file. The user (or `/app:plans`) records progress in the gitops-app repo with `/app:plans start <slug>` and `/app:plans done <slug> <repo-id>`.
