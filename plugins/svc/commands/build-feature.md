---
description: Full-pipeline feature build. Orchestrates product-manager → architect → parallel coders → quality → tester → security → deployment for the given feature request. Usage: /svc:build-feature <feature description>
---

You are the **orchestrator**. Your job is to drive a feature from idea to deployment by delegating to specialized subagents — and to fan coders out in parallel git worktrees wherever the architect's plan permits.

**Feature request:** $ARGUMENTS

Work through the phases in order. Complete each phase fully before starting the next. After each phase, print `## Phase N complete` with a one-line summary.

---

## Phase 0 — Branch check

Before Phase 1:

1. Check `git status --porcelain`. If dirty, stop: "Working tree has uncommitted changes — commit or stash before running /svc:build-feature."
2. Get current branch: `git symbolic-ref --short HEAD`. Record it as `$FEATURE_BRANCH`.
3. **If on `main`:** derive a slug from the feature description (lowercase, hyphens, ≤40 chars, always `feature/` prefix). Create and switch:
   ```bash
   git checkout -b feature/<slug>
   ```
   Update `$FEATURE_BRANCH` to this new branch. Print: `## Phase 0 — on feature branch: feature/<slug>`
4. **If already on a non-main branch:** print: `## Phase 0 — already on branch: <branch>`

Note: Phase 3.0 captures `BASE_BRANCH=$(git symbolic-ref --short HEAD)`. After Phase 0, `BASE_BRANCH` will be the feature branch — correct, as worktrees merge back into it.

---

## Phase 1 — Product Definition

Use the **product-manager** agent to:
- Clarify the feature request (make reasonable assumptions if the request is clear enough — do not block on questions)
- Produce user stories with acceptance criteria
- Save output to `docs/backlog.md` (append or create)

Wait for the product-manager agent to finish. Extract the acceptance criteria checklist — you will use it in Phase 4.

---

## Phase 2 — Architecture

Use the **architect** agent, passing it:
- The user stories and acceptance criteria from Phase 1
- The instruction to read the existing codebase before designing
- The instruction to **emit the structured plan format documented in the architect agent's system prompt** — a YAML metadata block listing every task with `id`, `files`, `parallel_safe`, `depends_on`, followed by per-task prose.

The architect must produce:
1. An implementation plan at `docs/plan/<feature-slug>.md` with the mandatory YAML metadata
2. Any ADR if a significant technology decision was made (save to `docs/adr/`)
3. Module/API specs sufficient for the coder to start without follow-up questions

Wait for the architect to finish. Read `docs/plan/<feature-slug>.md` and parse the YAML metadata block. If the metadata is absent or malformed, **send the plan back to the architect** with the format spec and require a re-emission — do not proceed to Phase 3 without it.

---

## Phase 3 — Implementation (parallel via git worktrees)

### 3.0 Pre-flight

Confirm `git status --porcelain` is empty and capture the base branch (the feature branch from Phase 0):
```bash
BASE_BRANCH=$(git symbolic-ref --short HEAD)
BASE_REF=$(git rev-parse HEAD)
```

### 3.0a Worktree-isolation probe

Before fanning coders out, probe the harness for worktree support. If the Claude Code session started before `git init`, the harness may have cached "not a git repository" state — the Agent tool's `isolation: "worktree"` will return an error and parallel fan-out becomes impossible mid-flight.

Run the probe as a tiny throwaway `Agent` call with `isolation: "worktree"` (e.g. a one-line "print pwd and exit" coder task). If it returns:
- ✅ a valid worktree branch+path → fan-out is available. Continue with the normal parallel flow described below.
- ❌ an error containing "Cannot create agent worktree" or "not in a git repository" → **fall back to sequential execution.** Run every task on `$BASE_BRANCH` one after another (skip the merge phase entirely; each task lands as its own commit on the base branch). Note "worktree isolation unavailable this session — fell back to sequential" in the Final Report's *Next steps* so the user knows to restart their session for true parallelism next time.

Do not attempt fan-out without a passing probe — silently degrading mid-batch produces confusing error returns from real coder agents.

### 3.1 Build the execution schedule

From the parsed plan metadata, compute the schedule:

1. **Topologically sort** tasks by `depends_on`. Tasks with no incoming edges go first.
2. **Group into levels** — at level N, place every task whose dependencies are all in levels < N.
3. **Within each level, build parallel batches** by greedy file-disjoint grouping:
   - A task is added to the current batch only if `parallel_safe: true` AND its `files` set is disjoint from every file set already in the batch.
   - Tasks with `parallel_safe: false` or that would conflict are placed in their own singleton batches.

Print the schedule as a markdown table before executing:

```
| Level | Batch | Tasks | Mode |
|---|---|---|---|
| 1 | 1 | t1, t2 | parallel |
| 1 | 2 | t3     | sequential |
| 2 | 1 | t4     | sequential |
```

### 3.2 Execute each batch

For each batch in order:

**Parallel batch (≥2 tasks, all `parallel_safe`):**

Spawn one **coder** subagent per task **in a single message** (multiple Agent tool calls in one assistant turn), each with `isolation: "worktree"`. The subagent prompt must include:
- Path to `docs/plan/<slug>.md` and the task's `id`
- The task's prose section verbatim
- The task's `files` list (you may not touch any file outside this list)
- The instruction: "You are working in an isolated git worktree. Commit your changes locally (`git add` + `git commit -m '<task-id>: <title>'`) before returning. Do not push. Do not switch branches."

Wait for all coder calls to complete. Collect the `(branch_name, worktree_path)` returned by each that made changes; ignore agents that made no changes (worktree auto-cleans).

**Sequential batch (single task, or `parallel_safe: false`):**

Spawn one coder subagent **without** `isolation: "worktree"` — it works directly on the base branch. After it finishes, commit on the orchestrator's behalf if the coder didn't:
```bash
git add -A && git commit -m "<task-id>: <title>"
```

### 3.3 Merge phase (after a parallel batch)

For each returned `(branch, worktree_path)` from the batch:

```bash
git merge --no-ff --no-edit <branch>
```

After each merge:
1. **Lint-fix pre-pass:** run `devbox run lint-fix` directly to auto-resolve ruff-fixable issues before invoking the quality gate. Stage the result so it lands in the next commit.
2. Run `devbox run quality`. If it still fails, hand the violation report back to that task's coder (it can re-enter its worktree if still present, or work on main) to fix only the lint/type issues. Re-run quality.
3. Run `devbox run test-fast` as a sanity check. Failures here are usually integration issues between parallel branches — route to the coder agent with the failing test output.
3. Clean up:
   ```bash
   git worktree remove <worktree_path>
   git branch -d <branch>
   ```

**Merge conflicts:** if `git merge` reports a conflict, abort with `git merge --abort`, stop the pipeline, and escalate to the user with:
- The two conflicting tasks (ids and titles)
- The conflicting files
- The branch names so the user can inspect manually

Do not auto-resolve conflicts. The architect's `files` declaration was supposed to prevent this — a conflict means the plan metadata was wrong.

### 3.4 Phase 3 wrap-up

Print:
```
## Phase 3 complete
- Tasks executed: N (P in parallel, S sequential)
- Merges: M successful, C conflicts
- Files changed: <git diff --name-only $BASE_REF..HEAD | count>
```

---

## Phase 3a — Quality gate (final)

After all task merges, run one consolidated quality check on the integrated tree.

**Pre-pass:** run `devbox run lint-fix` directly from the orchestrator first — this auto-resolves ruff-fixable issues without spinning up an agent.

Then use the **quality agent** with instruction:
> Run `devbox run quality` and report all violations.

If violations remain, hand back to the **coder** agent for lint/type fixes only (no logic changes), then re-run. Do not advance until clean.

Print `## Phase 3a complete — quality gate passed`.

---

## Phase 4 — Testing

Use the **tester** agent, passing it:
- The acceptance criteria checklist from Phase 1
- The full list of files changed since `$BASE_REF`
- The instruction to write tests covering the acceptance criteria and then run them via `devbox run test`

The tester must report: tests written, pass/fail count, coverage %, and any open bugs.

If the tester reports bugs:
- Use the **coder** agent to fix them (pass the exact bug report). No worktree — these are integration fixes on the merged tree.
- Then re-run the **tester** agent to confirm the fix
- Repeat until all acceptance criteria pass (max 2 fix cycles; escalate to the user if not resolved)

---

## Phase 4a — Security scan

Use the **security** agent with instruction:
> Run `devbox run security`. If a Dockerfile was created or modified during this feature, also run `devbox run image-build && devbox run image-scan`. Document findings in `docs/security/scan-<today>.md`.

**Escalation rules:**
- **CRITICAL findings:** stop and escalate to the user immediately with full details. Do not proceed to deployment.
- **HIGH findings:** document and continue; note them in the Final Report.

Print `## Phase 4a complete — security scan done`.

---

## Phase 5 — Deployment

Use the **deployment** agent (from the svc plugin), passing it:
- The list of changed/new modules
- The instruction to update or create: Dockerfile, k8s manifests in `k8s/`, and any needed `devbox run` script
- The instruction to verify manifests with `devbox run deploy-check`

---

## Phase 6 — Backlog finalization

If `docs/backlog.md` lists user stories for this feature with a status field (e.g. "Not started" / "In progress" / "Done"), update each story implemented by this build to **Done**. Edit `docs/backlog.md` directly — small, atomic, leave the rest of the file untouched. Commit as a single `docs(backlog): mark <story-ids> done` commit on `$BASE_BRANCH`.

If the backlog uses checkboxes instead of status fields, tick each acceptance-criterion checkbox covered by the tests that passed in Phase 4.

If the file has no status field and no checkboxes for these stories, skip this phase silently.

Print `## Phase 6 complete — backlog updated` (or `## Phase 6 skipped — no status fields in backlog`).

---

## Phase 7 — Open PR

After Phase 6 completes:

1. Extract GitHub issue references so the PR can close them on merge.

   Scan `$ARGUMENTS`, `docs/backlog.md` (look for `#NNN` in the stories for this feature), and the git log since `$BASE_REF` for `#NNN` patterns:
   ```bash
   git log "$BASE_REF"..HEAD --format='%B'
   ```
   Verify each candidate is a real, open issue:
   ```bash
   gh issue view <NNN> --json state,number -q '"\(.number) \(.state)"'
   ```
   Keep only `OPEN` issues. Build a `CLOSES` list (e.g. `Closes #42\nCloses #7`). If none, set `CLOSES` to `N/A`.

2. Push the feature branch (requires user confirmation — `git push` is in the `ask` list):
   ```bash
   git push -u origin $FEATURE_BRANCH
   ```

3. Create the PR (requires user confirmation — `gh pr create` is in the `ask` list). Build the body explicitly so `Closes #NNN` appears as live text (not an HTML comment) and GitHub auto-closes the linked issues on merge:
   ```bash
   gh pr create \
     --title "feat(<feature-slug>): <one-line summary from Phase 1 user stories>" \
     --body "$(cat <<'EOF'
   ## Summary

   <3–5 sentence description of the feature: what problem it solves, what was built, and how a user or operator interacts with it. Include concrete details — endpoint paths, CLI flags, config variables, response schemas, or observable behaviour — so a reviewer understands what the feature does without reading the code. Draw from the Phase 1 user stories and Phase 4 acceptance criteria.>

   ## Type of change

   - [x] feat — new user-visible feature

   ## Related issues / stories

   <CLOSES — e.g. "Closes #42" or "N/A">

   ## Testing done

   <tester summary: N tests written, X% coverage, acceptance criteria status>

   ## Checklist

   - [x] `devbox run quality` passes (ruff + mypy)
   - [x] `devbox run test` passes with coverage ≥ 80%
   - [x] `devbox run security` passes (no CRITICAL findings)
   - [x] No secrets, credentials, or API keys committed
   - [x] Documentation updated if public-facing behaviour changed
   EOF
   )"
   ```
   The title must satisfy Conventional Commits format (≤72 chars after `type: `) to pass the `pr-title` CI check. Replace `<CLOSES>` with the actual closing keywords determined in step 1.

4. Print the PR URL.

**If `$FEATURE_BRANCH` is `main`** (Phase 0 skipped branch creation): warn "Skipping PR creation — working directly on main." and skip Phase 7.

Print `## Phase 7 complete — PR opened: <URL>`

---

## Final Report

```
## Build complete: <feature name>

| Phase | Output |
|---|---|
| Product | docs/backlog.md updated, N user stories |
| Architecture | docs/plan/<slug>.md, N tasks (P parallel, S sequential) |
| Implementation | N files changed across M commits |
| Quality gate | PASS — devbox run quality clean |
| Testing | N tests, N passed, X% coverage |
| Security scan | PASS / WARN — docs/security/scan-<date>.md |
| Deployment | Dockerfile, k8s/<manifest>.yaml — deploy-check clean |
| PR | <URL> — CI running |

### Acceptance criteria
- [x] criteria 1
- [x] criteria 2
...

### Next steps
<any open items, known limitations, or follow-up recommendations>
```

---

## Rules

- **Push only at Phase 7** — all work through Phase 6 is local. Phase 7 is the single push point (`git push -u origin $FEATURE_BRANCH`, then `gh pr create`). Both require user confirmation.
- **Never resolve merge conflicts automatically** — escalate. Conflicts indicate the plan metadata was inaccurate; the architect must update it.
- **Every shell command goes through `devbox run <script>`** — see `CLAUDE.md` for the canonical list.
- **Stay on `$BASE_BRANCH`** for orchestration. Only the parallel coder subagents leave it, and only into isolated worktrees.
- **No `--no-verify`, no `--no-gpg-sign`** — let the user's hooks run.
