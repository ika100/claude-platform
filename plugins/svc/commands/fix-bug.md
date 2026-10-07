---
description: "Targeted bug-fix pipeline. Runs coder → tester in a tight loop until the bug is resolved. Usage: /svc:fix-bug <bug description or error message>"
---

You are the **orchestrator** in bug-fix mode. No planning or deployment phases — focus on fixing and verifying.

**Bug report:** $ARGUMENTS

---

## Phase 0 — Prelude

Run the prelude:

1. `git status --porcelain` — stop if dirty.
2. `git symbolic-ref --short HEAD` → record `$WORK_BRANCH`.
3. If on `main`: derive a `fix/<slug>` slug (lowercase, hyphens, ≤40 chars). Then `git checkout -b fix/<slug>` and update `$WORK_BRANCH`.
4. `BASE_REF=$(git rev-parse HEAD)`.
5. Build `<project-map>` (output of `ls -d */` excluding `.devbox`, `.venv`, `.git`, `node_modules`). Hold as `$PROJECT_MAP`. Prepend to each subagent prompt below.

Print `## Phase 0 — on $WORK_BRANCH, BASE_REF=<short-sha>`.

**Shape dispatch.** After the prelude, run this in one Bash call: `P="${XDG_CACHE_HOME:-$HOME/.cache}/claude-platform"; { [ -d "$P/.git" ] && git -C "$P" fetch -q --depth 1 origin main && git -C "$P" checkout -q FETCH_HEAD; } || { rm -rf "$P"; git clone -q --depth 1 https://github.com/ika100/claude-platform.git "$P"; }; uv run "$P/scripts/cplat/cplat.py" shape` It prints JSON: `shape`, `plugin`, `deployable`, `library` and `agents` (the subagent type for every role — spawn each role with exactly that type, e.g. `agents.coder`). If `unsupported` is present, stop and show it. Roles missing from `agents` (e.g. deployment for a library) are skipped. Print `Shape: <shape>`.

---

## Step 1 — Diagnose and fix

Use the **coder** agent. Prompt prelude: the `<project-map>` block. Then:
> "Bug report: `$ARGUMENTS`.
>
> Step 1: read the relevant files and identify the root cause. State the root cause and the minimal change you intend to make in 2-3 lines before editing.
>
> Step 2: apply the minimal fix. Do not refactor surrounding code or add unrelated changes.
>
> Step 3: report what you changed (files + 1-line summary per file) and the root cause you found."

After the coder finishes, capture:
```bash
TOUCHED_FILES=$(git diff --name-only $BASE_REF -- .)
```

---

## Step 2 — Verify

Use the **tester** agent. Prompt prelude:
```
<project-map>
$PROJECT_MAP
</project-map>
<touched-files>
$TOUCHED_FILES
</touched-files>
```

Then:
- Run the existing test suite via `devbox run test-fast`
- Write a regression test that would have caught this bug (anchor it on the files in `<touched-files>`)
- Confirm the bug is resolved

---

## Step 3 — Loop if needed

If the tester reports the bug is NOT fixed:
- Feed the failure back to the **coder** (with `<project-map>` + refreshed `<touched-files>`)
- Re-run the **tester**
- Repeat up to 3 times. If still unresolved, stop and report with full context.

---

## Phase 4 — Commit and open PR

After the tester confirms the bug is resolved:

1. Check for uncommitted changes (`git status --porcelain`). If non-empty, commit with a conventional commit message:
   ```bash
   git add -A
   git commit -m "fix(<scope>): <imperative description of the fix>"
   ```

2. Push the branch (pre-approved for `fix/*` branches):
   ```bash
   git push -u origin <current-branch>
   ```

3. Create the PR (requires user confirmation — `gh pr create` is in the `ask` list):
   ```bash
   gh pr create \
     --title "fix(<scope>): <same description as the commit>" \
     --fill-verbose
   ```

4. Print the PR URL.

**If Phase 0 found we were already on `main`:** warn "Skipping PR creation — working directly on main." and skip Phase 4.

---

## Final Report

```
## Bug fix complete (or: escalating to user)

**Bug:** $ARGUMENTS
**Branch:** <branch-name>
**Root cause:** <one line>
**Fix:** <files changed, what changed>
**Regression test:** <test file and test name>
**Test result:** N passed
**PR:** <URL> (CI running)
```
