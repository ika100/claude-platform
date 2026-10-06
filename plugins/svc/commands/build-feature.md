---
description: Full-pipeline feature build. Orchestrates product-manager → architect → parallel coders → quality+test+security (fan-out) → deployment for the given feature request. Usage: /svc:build-feature <feature description>
---

You are the **orchestrator**. Drive a feature from idea to deployment by delegating to specialized subagents — and fan coders out in parallel git worktrees wherever the architect's plan permits.

**Feature request:** $ARGUMENTS

**`--from-plan <path> [<repo-id>]`** (optional, [ADR-011](../../../docs/adr/011-multi-repo-plan-format.md)): if `$ARGUMENTS` starts with this flag, read the multi-repo plan at `<path>`, pick the `repos[]` entry whose `id` is `<repo-id>` (default: the current repo's name, or the `repo` in `.platform-app.yml`), and use that entry's `arguments` block as the feature request from here on. The plan file lives in the gitops-app repo, so do **not** edit it from here; instead tell the user to run `/app:plans start <slug>` before and `/app:plans done <slug> <repo-id>` (in the gitops-app repo) after the Phase 7 PR merges, and include those two commands in the Final Report.

Work through the phases in order. Complete each phase fully before starting the next. After each phase, print `## Phase N complete` with a one-line summary.

---

## Phase 0a — Scope classifier

Before running the full pipeline, decide whether the request actually needs it. Read `$ARGUMENTS` and classify:

- **Typo / docs / one-file tweak** (e.g. "fix typo in README", "rename CONST_X to CONST_Y") → stop and recommend `/svc:quick-task "$ARGUMENTS"`. Do not proceed.
- **Bug report with a stack trace, error message, or "X is broken"** → stop and recommend `/svc:fix-bug "$ARGUMENTS"`. Do not proceed.
- **Standard feature** (1–3 modules, no new public API surface, no schema changes) → recommend `/svc:quick-task` but ask the user "this looks light enough for quick-task — confirm full pipeline?". Stop unless the user explicitly confirms.
- **Real feature** (cross-cutting, new endpoints, new modules, schema changes, or the user says "build feature") → proceed to Phase 0b.

Print exactly one of `## Phase 0a — proceeding to full pipeline` or `## Phase 0a — routing to /svc:<other-command>`.

---

## Phase 0b — Prelude

Run the canonical prelude — see `plugins/svc/fragments/phase-prelude.md`. Specifically:

1. `git status --porcelain` — stop if dirty.
2. `git symbolic-ref --short HEAD` → record `$FEATURE_BRANCH`.
3. If on `main`: derive a `feature/<slug>` slug (lowercase, hyphens, ≤40 chars) and `git checkout -b feature/<slug>`. Update `$FEATURE_BRANCH`.
4. `BASE_REF=$(git rev-parse HEAD)`.
5. Build `<project-map>` from `ls -d */` (excluding `.devbox`, `.venv`, `.git`, `node_modules`). Hold it as `$PROJECT_MAP`. Every subagent prompt below must prepend it.

Print `## Phase 0b complete — on $FEATURE_BRANCH, BASE_REF=<short-sha>`.

**Shape dispatch.** After the prelude, resolve the shape and route agents per `plugins/svc/fragments/shape-dispatch.md`: detect `$SHAPE`, look up `$SHAPE_PLUGIN` / `$DEPLOYABLE` in `shapes.yml`, and spawn coder/tester, deployment, observability (deployment/observability only when `$DEPLOYABLE` is true; skip Phase 5 for libraries) as `$SHAPE_PLUGIN:<role>` (`svc:<role>` for Python shapes). Quality and security stay `shared:<role>`. On a `gitops-app` repo stop and recommend `/gitops:compose` or `/app:build-feature`. Print `Shape: $SHAPE (plugin: $SHAPE_PLUGIN)`.

---

## Phase 1 — Product Definition

Use the **product-manager** agent. Prompt prelude:

```
<project-map>
$PROJECT_MAP
</project-map>
```

Then:
- Clarify the feature request (make reasonable assumptions; do not block on questions)
- Produce user stories with acceptance criteria
- Save output to `docs/backlog.md` (append or create)

Extract the acceptance criteria checklist when the agent finishes — reused in Phase 4.

---

## Phase 2 — Architecture

Use the **architect** agent. Prompt prelude: same `<project-map>` block. Then:
- Pass the user stories and acceptance criteria from Phase 1
- Instruction to read the existing codebase before designing
- Instruction to record `shape: $SHAPE` in the plan metadata and to **emit the structured plan format documented in the architect agent's system prompt** — a YAML metadata block listing every task with `id`, `files`, `parallel_safe`, `depends_on`, followed by per-task prose

The architect produces:
1. An implementation plan at `docs/plan/<feature-slug>.md` with the mandatory YAML metadata
2. Any ADR if a significant technology decision was made (save to `docs/adr/`)
3. Module/API specs sufficient for the coder to start without follow-up questions

Read `docs/plan/<feature-slug>.md` and parse the YAML metadata. If absent or malformed, send the plan back to the architect — do not proceed without it.

---

## Phase 3 — Implementation (parallel via git worktrees)

### 3.0 Pre-flight

Working tree should already be clean. Capture the base branch (the feature branch from Phase 0b):
```bash
BASE_BRANCH=$(git symbolic-ref --short HEAD)
```

### 3.0a Worktree-isolation probe

Before fanning out, probe the harness for worktree support. If the Claude Code session started before `git init`, the harness may have cached "not a git repository" — `isolation: "worktree"` will error out mid-flight.

Run a throwaway `Agent` with `isolation: "worktree"` and a one-line task. If it returns:
- ✅ a worktree branch+path → continue normally.
- ❌ "Cannot create agent worktree" or "not in a git repository" → fall back to sequential execution on `$BASE_BRANCH`, skipping the merge phase. Note in the Final Report so the user knows to restart for true parallelism.

### 3.1 Build the execution schedule

From the parsed plan metadata:
1. **Topologically sort** tasks by `depends_on`.
2. **Group into levels** — level N holds tasks whose deps are all in levels < N.
3. **Within each level, build parallel batches** by greedy file-disjoint grouping: a task joins the current batch only if `parallel_safe: true` AND its `files` set is disjoint from every other file set in the batch. Otherwise it becomes a singleton.

Print the schedule as a markdown table before executing.

### 3.2 Execute each batch

For each batch:

**Parallel batch (≥2 tasks, all `parallel_safe`):**

Spawn one **coder** subagent per task **in a single message**, each with `isolation: "worktree"`. Each prompt must include:
- `<project-map>` block
- Path to `docs/plan/<slug>.md` and the task's `id`
- The task's prose section verbatim
- The task's `files` list (you may not touch files outside it)
- Instruction: "You are in an isolated worktree. Commit locally (`git add` + `git commit -m '<task-id>: <title>'`) before returning. Do not push. Do not switch branches."

Wait for all calls. Collect `(branch_name, worktree_path)` from each that made changes; ignore agents with no changes (worktree auto-cleans).

**Sequential batch (single task or `parallel_safe: false`):**

Spawn one coder **without** `isolation: "worktree"` — works directly on the base branch. Commit on its behalf if it didn't:
```bash
git add -A && git commit -m "<task-id>: <title>"
```

### 3.3 Merge phase (after a parallel batch)

For each returned `(branch, worktree_path)`:

```bash
git merge --no-ff --no-edit <branch>
```

After each merge:
1. **Lint-fix pre-pass:** `devbox run lint-fix` from the orchestrator — auto-resolves ruff-fixable issues without spawning anything. Stage the result.
2. `devbox run quality`. If it still fails, route the report to that task's coder (lint/type fixes only). Re-run.
3. `devbox run test-fast` sanity check. Failures here are usually parallel-integration issues — route to the coder with the failing output.
4. Clean up:
   ```bash
   git worktree remove <worktree_path>
   git branch -d <branch>
   ```

**Merge conflicts:** abort with `git merge --abort`, stop, escalate to the user. Do not auto-resolve. A conflict means the architect's `files` declaration was wrong.

### 3.4 Phase 3 wrap-up

Compute and hold the touched-files context for downstream phases:
```bash
TOUCHED_FILES=$(git diff --name-only $BASE_REF..HEAD)
```

Print:
```
## Phase 3 complete
- Tasks executed: N (P in parallel, S sequential)
- Merges: M successful, C conflicts
- Files changed: <count>
```

---

## Phase 4 — Parallel QA fan-out (quality + tester + security)

**This phase fans out three subagents in a single message — mirroring `/shared:check-quality`.** Total wall-clock is the longest leg, not the sum.

Each subagent prompt includes the same context prelude:
```
<project-map>
$PROJECT_MAP
</project-map>
<touched-files>
$TOUCHED_FILES
</touched-files>
```

Spawn all three in one assistant turn:

1. **Quality agent** — instruction: "Run `devbox run lint-fix` then `devbox run quality`. Report all remaining violations."
2. **Tester agent** — instruction: "Acceptance criteria: <list from Phase 1>. Touched files above. Write tests covering the criteria, then run `devbox run test`. Report pass/fail count, coverage %, and any open bugs."
3. **Security agent** — instruction: "Run `devbox run security`. If a Dockerfile was created or modified during this feature, also run `devbox run image-build && devbox run image-scan`. Document findings in `docs/security/scan-<today>.md`."

Wait for all three. Reconcile:

- **Quality failures** → route to the **coder** for lint/type fixes only (no logic changes). Re-run quality. Max 2 cycles.
- **Tester bugs** → route to the **coder** with the exact bug report. Re-run tester. Max 2 cycles.
- **CRITICAL security findings** → stop, escalate to the user, do not proceed to deployment.
- **HIGH security findings** → document and continue; note in Final Report.

If quality or tester cycles modified files, refresh `$TOUCHED_FILES` before continuing.

Print `## Phase 4 complete — QA fan-out passed (tests: N, coverage X%, sec: PASS/WARN)`.

---

## Phase 5 — Deployment

Skip with `## Phase 5 skipped — $SHAPE is not deployable` when `$DEPLOYABLE` is false. Otherwise use the **deployment** agent (`$SHAPE_PLUGIN:deployment`). Prompt prelude: `<project-map>` + `<touched-files>` (refreshed). Then:
- The list of changed/new modules (from `$TOUCHED_FILES`)
- Instruction to update or create: Dockerfile, k8s manifests in `k8s/`, and any needed `devbox run` script
- Instruction to verify manifests with `devbox run deploy-check`

---

## Phase 6 — Backlog finalization

If `docs/backlog.md` lists user stories for this feature with a status field, mark each story implemented by this build as **Done**. Single commit: `docs(backlog): mark <story-ids> done`.

If the backlog uses checkboxes instead of status, tick each acceptance-criterion checkbox covered by tests that passed in Phase 4.

If neither, skip silently.

Print `## Phase 6 complete — backlog updated` (or `## Phase 6 skipped — no status fields`).

---

## Phase 7 — Open PR

After Phase 6:

1. **Collect linked issues.** Scan `$ARGUMENTS`, `docs/backlog.md`, and `git log "$BASE_REF"..HEAD --format='%B'` for `#NNN` patterns. Verify each is `OPEN` via `gh issue view <NNN> --json state -q .state`. Build a `CLOSES` list (e.g. `Closes #42\nCloses #7`) or `N/A`.

2. **Push the feature branch** (requires user confirmation):
   ```bash
   git push -u origin $FEATURE_BRANCH
   ```

3. **Create the PR** (requires user confirmation):
   ```bash
   gh pr create \
     --title "feat(<feature-slug>): <one-line summary from Phase 1 user stories>" \
     --body "$(cat <<'EOF'
   ## Summary

   <3–5 sentence description: what problem it solves, what was built, how a user or operator interacts with it. Include concrete details — endpoint paths, CLI flags, config variables, response schemas — so a reviewer understands the feature without reading code.>

   ## Type of change

   - [x] feat — new user-visible feature

   ## Related issues / stories

   <CLOSES — e.g. "Closes #42" or "N/A">

   ## Testing done

   <tester summary: N tests written, X% coverage, acceptance criteria status>

   ## Checklist

   - [x] `devbox run quality` passes
   - [x] `devbox run test` passes with coverage ≥ 80%
   - [x] `devbox run security` passes (no CRITICAL findings)
   - [x] No secrets, credentials, or API keys committed
   - [x] Documentation updated if public-facing behaviour changed
   EOF
   )"
   ```
   Title must satisfy Conventional Commits (`type(scope): description ≤72 chars`).

4. Print the PR URL.

**If `$FEATURE_BRANCH` is `main`** (Phase 0b skipped branch creation): warn "Skipping PR creation — working directly on main." and skip Phase 7.

Print `## Phase 7 complete — PR opened: <URL>`.

---

## Final Report

```
## Build complete: <feature name>

| Phase | Output |
|---|---|
| Product | docs/backlog.md, N user stories |
| Architecture | docs/plan/<slug>.md, N tasks (P parallel, S sequential) |
| Implementation | N files changed across M commits |
| QA fan-out | quality PASS, tests N (X% cov), security PASS/WARN |
| Deployment | Dockerfile, k8s/<manifest>.yaml — deploy-check clean |
| PR | <URL> — CI running |

### Acceptance criteria
- [x] criteria 1
- [x] criteria 2

### Next steps
<any open items, known limitations, or follow-up recommendations>
```

---

## Rules

- **Push only at Phase 7** — all work through Phase 6 is local. Phase 7 is the single push point; both `git push` and `gh pr create` require user confirmation.
- **Never resolve merge conflicts automatically** — escalate. Conflicts indicate the plan metadata was inaccurate.
- **Every shell command goes through `devbox run <script>`** — see `CLAUDE.md`.
- **Stay on `$FEATURE_BRANCH`** for orchestration. Only the parallel coder subagents leave it, and only into isolated worktrees.
- **Phase 4 fan-out is the default.** Do not serialize quality → tester → security unless one of them needs to gate on another's output — in which case, document the dependency in the orchestrator output.
- **No `--no-verify`, no `--no-gpg-sign`** — let the user's hooks run.
