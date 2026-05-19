---
description: Targeted bug-fix pipeline. Runs coder → tester in a tight loop until the bug is resolved. Usage: /svc:fix-bug <bug description or error message>
---

You are the **orchestrator** in bug-fix mode. No planning or deployment phases — focus on fixing and verifying.

**Bug report:** $ARGUMENTS

---

## Phase 0 — Branch check

Before any code is written:

1. Run `git status --porcelain`. If the working tree is dirty, stop and ask the user to commit or stash first.
2. Run `git symbolic-ref --short HEAD` to get the current branch.
3. **If on `main`:** derive a slug from the bug description (lowercase, hyphens for spaces, ≤40 chars, always `fix/` prefix). Create and switch:
   ```bash
   git checkout -b fix/<slug>
   ```
   Print: `## Phase 0 — on fix branch: fix/<slug>`
4. **If already on a non-main branch:** proceed. Print: `## Phase 0 — already on branch: <branch>`

---

## Step 1 — Diagnose

Use the **coder** agent with the instruction:
> "Read the relevant files, diagnose this bug: `$ARGUMENTS`. Identify the root cause and the minimal change needed to fix it. Do not fix yet — report your diagnosis."

---

## Step 2 — Fix

Use the **coder** agent again, passing the diagnosis, with the instruction to apply the minimal fix.

---

## Step 3 — Verify

Use the **tester** agent to:
- Run the existing test suite via `devbox run test-fast`
- Write a regression test that would have caught this bug
- Confirm the bug is resolved

---

## Step 4 — Loop if needed

If the tester reports the bug is NOT fixed:
- Feed the failure back to the **coder** agent
- Re-run the **tester** agent
- Repeat up to 3 times. If still unresolved, stop and report to the user with full context.

---

## Phase 5 — Commit and open PR

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

**If Phase 0 found we were already on `main`:** warn "Skipping PR creation — working directly on main." and skip Phase 5.

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
