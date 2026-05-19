# Phase prelude (canonical workflow)

Every `svc` orchestration command (`build-feature`, `quick-task`, `fix-bug`) runs the same checks before any agent is spawned. This file is the **canonical source of truth** for that workflow — keep each command's inline Phase 0 in sync with the steps below.

## The five checks

1. **Working tree clean.** Run `git status --porcelain`. If non-empty, stop and tell the user to commit or stash first. Never auto-stash.
2. **Identify the branch.** Run `git symbolic-ref --short HEAD`. Record it as `$WORK_BRANCH` (build-feature uses `$FEATURE_BRANCH`).
3. **Branch off `main` when needed.** If currently on `main`, derive a slug from the user's request (lowercase, hyphens for spaces, ≤40 chars) and create the branch with the command-specific prefix:
   - `/svc:build-feature` → `feature/<slug>`
   - `/svc:quick-task` → `feature/<slug>` (or `fix/`, `chore/`, `docs/` based on task type)
   - `/svc:fix-bug` → `fix/<slug>`
   Then `git checkout -b <prefix>/<slug>` and update `$WORK_BRANCH`.
4. **Capture base ref.** `BASE_REF=$(git rev-parse HEAD)` — used later for diff scope and for the touched-files context.
5. **Pre-compute subagent context.** Build a short context block to prepend to every subagent prompt:
   ```
   <project-map>
   {{ output of: ls -d */ 2>/dev/null | grep -vE '^(\.devbox|\.venv|\.git|node_modules)/$' }}
   </project-map>
   ```
   For phases after coder work, also emit:
   ```
   <touched-files>
   {{ git diff --name-only $BASE_REF..HEAD }}
   </touched-files>
   ```
   This saves every downstream agent 2–5 Glob/Grep exploration calls.

## Outputs

After the prelude, the orchestrator should hold:

| Variable | Source | Purpose |
|---|---|---|
| `$WORK_BRANCH` | step 2 or 3 | Branch the orchestration stays on; never leave it except for parallel-coder worktrees |
| `$BASE_REF` | step 4 | Diff baseline for touched-files context and "files changed in this run" reports |
| `<project-map>` | step 5 | Inline context block included in every subagent prompt |
| `<touched-files>` | step 5 (post-coder) | Same; lets tester/quality/security/deployment skip exploration |

## Why this exists

Three commands used to carry slightly-different copies of this workflow (~14 lines each). Drift was the recurring failure mode — quick-task gained a slug rule that build-feature never adopted, fix-bug forgot the `BASE_REF` capture, etc. Keeping the prose here lets each command stay short and lets maintainers audit one place.
