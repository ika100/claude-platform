---
description: Lightweight pipeline for small, well-scoped changes. Runs coder → quality → tester with a tight fix loop. No PM, no architect, no security, no deployment. Usage: /svc:quick-task <description>
---

You are the **orchestrator** in quick-task mode. Use this for changes that don't need product or architectural review: small features, refactors, doc tweaks, config changes, or anything a single coder can finish in one pass.

**Task:** $ARGUMENTS

If the task is large or cross-cutting (multiple modules, new public APIs, schema changes, anything that would benefit from user stories or an ADR), **stop and recommend `/svc:build-feature` instead** rather than continuing.

---

## Phase 0 — Prelude

Run the canonical prelude — see `plugins/svc/fragments/phase-prelude.md`. Specifically:

1. `git status --porcelain` — stop if dirty.
2. `git symbolic-ref --short HEAD` → record `$WORK_BRANCH`.
3. If on `main`: derive a slug (lowercase, hyphens, ≤40 chars). Pick a prefix from task type: `feature/` (default), `fix/`, `chore/`, `docs/`. Then `git checkout -b <prefix>/<slug>` and update `$WORK_BRANCH`.
4. `BASE_REF=$(git rev-parse HEAD)`.
5. Build `<project-map>` (output of `ls -d */` excluding `.devbox`, `.venv`, `.git`, `node_modules`). Hold as `$PROJECT_MAP`. Prepend to each subagent prompt below.

Print `## Phase 0 — on $WORK_BRANCH, BASE_REF=<short-sha>`.

**Shape dispatch.** After the prelude, resolve the shape and route agents per `plugins/svc/fragments/shape-dispatch.md`: detect `$SHAPE`, look up `$SHAPE_PLUGIN` / `$DEPLOYABLE` in `shapes.yml`, and spawn coder/tester as `$SHAPE_PLUGIN:<role>` (`svc:<role>` for Python shapes). Quality and security stay `shared:<role>`. On a `gitops-app` repo stop and recommend `/gitops:compose` or `/app:build-feature`. Print `Shape: $SHAPE (plugin: $SHAPE_PLUGIN)`.

---

## Step 1 — Implement

Use the **coder** agent. Prompt prelude: the `<project-map>` block. Then:
- The task description verbatim
- Instruction to read relevant files first, make the minimal change, and report touched files
- Instruction to use `devbox run lint-fix` and `devbox run test-fast` as needed during implementation

One coder, one pass — no worktrees, no fan-out.

After the coder finishes, capture:
```bash
TOUCHED_FILES=$(git diff --name-only $BASE_REF -- .)
```

---

## Step 2 — Parallel QA fan-out (quality + tester)

Fan out **quality** and **tester** in a single message. Wall-clock is the longer leg, not the sum. Each prompt prelude:
```
<project-map>
$PROJECT_MAP
</project-map>
<touched-files>
$TOUCHED_FILES
</touched-files>
```

Then:

1. **Quality agent** — instruction: "Run `devbox run lint-fix` then `devbox run quality`. Report remaining violations."
2. **Tester agent** — instruction: "Touched files listed above. Run `devbox run test` and write any missing tests for the changed code paths. Report pass/fail count and coverage."

Reconcile:
- **Quality failures** → route to **coder** for lint/type fixes only. Re-run quality. Max 2 cycles.
- **Tester failures or coverage drop** → route to **coder** with the exact pytest output. Re-run tester. Max 2 cycles.
- If either cycle modified files, refresh `$TOUCHED_FILES`.

If still failing after 2 cycles, escalate to the user.

---

## Phase 3 — Commit and open PR

After the tester passes:

1. Check for uncommitted changes:
   ```bash
   git status --porcelain
   ```
   If non-empty, commit everything with a conventional commit message:
   ```bash
   git add -A
   git commit -m "feat(<scope>): <imperative description of the task>"
   ```
   Use `fix:` for bug fixes, `chore:` for tooling, `docs:` for documentation, etc.

2. Extract GitHub issue references so the PR can close them on merge.

   First, scan `$ARGUMENTS` and the last 10 commit messages for `#NNN` patterns:
   ```bash
   git log --format='%B' -10
   ```
   Collect every distinct `#NNN` found (e.g. `#42`, `#7`). Then verify each one is a real, open issue:
   ```bash
   gh issue view <NNN> --json state,number -q '"\(.number) \(.state)"'
   ```
   Keep only issues whose state is `OPEN`. Build a `CLOSES` list (e.g. `Closes #42\nCloses #7`). If no open issues are found, set `CLOSES` to `N/A`.

3. Push the branch (requires user confirmation — `git push` is in the `ask` list):
   ```bash
   git push -u origin <current-branch>
   ```

4. Create the PR (requires user confirmation — `gh pr create` is in the `ask` list). Build the body explicitly so `Closes #NNN` appears as live text (not an HTML comment) and GitHub auto-closes the linked issues on merge:
   ```bash
   gh pr create \
     --title "<type>(<scope>): <same description as the commit>" \
     --body "$(cat <<'EOF'
   ## Summary

   <2–4 sentence description of the change: what it does, how it works, and why it was needed. For a new feature, describe what the feature is and how a user or operator would interact with it (e.g. which endpoint, flag, or behaviour was added). For a fix, describe what was broken and how it was resolved.>

   ## Type of change

   - [x] <tick the matching type from: feat / fix / refactor / perf / test / docs / chore / ci / revert>

   ## Related issues / stories

   <CLOSES — e.g. "Closes #42" or "N/A">

   ## Testing done

   <tester output summary: N tests, X% coverage>

   ## Checklist

   - [x] `devbox run quality` passes (ruff + mypy)
   - [x] `devbox run test` passes with coverage ≥ 80%
   - [ ] `devbox run security` passes (no CRITICAL findings)
   - [x] No secrets, credentials, or API keys committed
   - [ ] Documentation updated if public-facing behaviour changed
   EOF
   )"
   ```
   The `--title` must match Conventional Commits format to pass the `pr-title` CI check. Replace `<CLOSES>` with the actual closing keywords determined in step 2.

5. Print the PR URL.

**If Phase 0 found we were already on `main` and did not create a branch:** warn "Skipping PR creation — working directly on main." and skip Phase 3.

---

## Final Report

```
## Quick-task complete

**Task:** $ARGUMENTS
**Branch:** <branch-name>
**Files changed:** <list>
**Tests:** N passed, X% coverage
**Quality:** PASS
**PR:** <URL> (CI running)

### What's next
- Review the PR diff at the URL above
- Merge when CI is green
```

---

## Rules

- **One coder, one pass.** If the task balloons mid-implementation (coder reports it needs more than ~3 files outside the original scope, or asks design questions), **stop and recommend `/svc:build-feature`** — don't keep stretching quick-task.
- **Commit at Phase 3, not before.** The coder leaves the working tree dirty; Phase 3 does the single commit before pushing.
- **No deployment, no security scan, no PRD.** Those are `/svc:build-feature` territory.
- **Every shell command goes through `devbox run`.**
