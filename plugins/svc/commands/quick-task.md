---
description: Lightweight pipeline for small, well-scoped changes. Runs coder → quality → tester with a tight fix loop. No PM, no architect, no security, no deployment. Usage: /svc:quick-task <description>
---

You are the **orchestrator** in quick-task mode. Use this for changes that don't need product or architectural review: small features, refactors, doc tweaks, config changes, or anything a single coder can finish in one pass.

**Task:** $ARGUMENTS

If the task is large or cross-cutting (multiple modules, new public APIs, schema changes, anything that would benefit from user stories or an ADR), **stop and recommend `/svc:build-feature` instead** rather than continuing.

---

## Phase 0 — Branch check

Before any code is written:

1. Run `git status --porcelain`. If the working tree is dirty, stop and ask the user to commit or stash first.
2. Run `git symbolic-ref --short HEAD` to get the current branch.
3. **If on `main`:** derive a slug from the task description (lowercase, hyphens for spaces, ≤40 chars). Choose the prefix by task type: `feature/` for new functionality, `fix/` for bugs, `chore/` for tooling, `docs/` for documentation. Create and switch:
   ```bash
   git checkout -b feature/<slug>
   ```
   Print: `## Phase 0 — on feature branch: feature/<slug>`
4. **If already on a non-main branch:** proceed. Print: `## Phase 0 — already on branch: <branch>`

---

## Step 1 — Implement

Use the **coder** agent with:
- The task description verbatim
- The instruction to read relevant files first, make the minimal change, and report which files were touched
- The instruction to use `devbox run lint-fix` and `devbox run test-fast` as needed during implementation

Coder works on the current branch — no worktrees, no fan-out. This is a one-task path.

---

## Step 2 — Quality gate

**Pre-pass (cheap):** before calling the quality agent, run `devbox run lint-fix` directly from the orchestrator. This auto-resolves ruff-fixable formatting/import issues without spawning the coder. If `lint-fix` leaves the tree dirty, stage the resulting changes so the eventual commit captures them.

Then use the **quality** agent with:
> Run `devbox run quality`. Report all violations.

**Fix loop:** if violations remain, pass the report back to the **coder** with "fix only the lint/type issues, no logic changes." Re-run quality. Max 2 cycles — if still failing, escalate to the user.

---

## Step 3 — Test

Use the **tester** agent with:
- The list of files touched in Step 1
- The instruction to run `devbox run test` and write any missing tests for the changed code paths

**Fix loop:** if tests fail or coverage drops below the project target, pass the failure to the **coder** with the exact pytest output. Re-run tester. Max 2 cycles — if still failing, escalate.

---

## Phase 4 — Commit and open PR

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

**If Phase 0 found we were already on `main` and did not create a branch:** warn "Skipping PR creation — working directly on main." and skip Phase 4.

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
- **Commit at Phase 4, not before.** The coder leaves the working tree dirty; Phase 4 does the single commit before pushing.
- **No deployment, no security scan, no PRD.** Those are `/svc:build-feature` territory.
- **Every shell command goes through `devbox run`.**
