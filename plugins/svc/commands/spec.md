---
description: "Write, amend or approve a feature spec (docs/specs/<NNN>-<slug>/spec.md); asks you the open questions. Usage: /svc:spec <description> | --amend <id> <change> | approve <id> | --from-plan <plan> [<repo-id>]"
---

You are the **spec orchestrator** ([ADR-026](../../../docs/adr/026-feature-specs.md)). A feature is built from an approved spec; your job is to get one, with every open question answered **by the user**, not guessed. You write no code and no plan.

**Request:** $ARGUMENTS

## cplat

Run the first platform call with this prefix (it brings the cached platform checkout up to date, one Bash call):

```bash
P="${XDG_CACHE_HOME:-$HOME/.cache}/sdlc-foundry"; { [ -d "$P/.git" ] && git -C "$P" fetch -q --depth 1 origin "${REF:-main}" && git -C "$P" checkout -q FETCH_HEAD; } || { rm -rf "$P"; git clone -q --depth 1 --branch "${REF:-main}" https://github.com/ika100/sdlc-foundry.git "$P"; }; uv run "$P/scripts/cplat/cplat.py" shape
```

Every later call in this command is `CPLAT <args>`, meaning: `uv run "${XDG_CACHE_HOME:-$HOME/.cache}/sdlc-foundry/scripts/cplat/cplat.py" <args>`. Print cplat output verbatim; never validate a spec yourself.

## 0. Pre-flight

1. **Mode** from `$ARGUMENTS`: `approve <id>` → section A. `--amend <id> <change>` → section C. `--from-plan <plan> [<repo-id>]` → section D. Empty → print usage and stop. Otherwise → new spec (section B).
2. **Route small work away** (new spec only): a typo, rename or one-file tweak → recommend `/svc:quick-task`; an error message or "X is broken" → recommend `/svc:fix-bug`. Stop unless the user insists on a spec.
3. `git status --porcelain` must be empty; otherwise stop: commit or stash first.
4. **Shape:** the prefix call above prints the routing JSON. If it reports `unsupported` (a gitops-app repo), stop and point to `/app:build-feature`. If it fails with "cannot determine the repo's shape", continue without a shape (`--no-shape` on `spec new`): specs work in any repo, only `/svc:build` needs a shape.
5. **Branch:** all steps of one spec happen on `feature/<spec_id>`, so its single PR carries spec, plan, tests, code and verification. Create or switch to it as the sections say. On a branch other than `main` and not `feature/<spec_id>`, ask before switching.

## A. approve <id>

1. `CPLAT spec approve <id>`. If it refuses, show the reasons and the fix (usually `/svc:spec --amend <id> …` for open questions).
2. Switch to `feature/<spec_id>` if it exists. Commit `docs/specs/<spec_id>/spec.md`: `docs(spec): approve <spec_id>`.
3. Print the next step: `/svc:plan <NNN>`.

## B. New spec

1. Derive a short title (≤ 60 chars, the feature's name, not the whole request) and any `#N` issue numbers in the request. Run `CPLAT spec new "<title>" [--tracks N …] [--no-shape]`; it prints `docs/specs/<spec_id>/spec.md`.
2. `git checkout -b feature/<spec_id>` (from `main`).
3. **product-manager** agent (`agents.product-manager` from the routing; `svc:product-manager` in a repo without a shape), prompt: `MODE: new`, `SPEC_DIR: docs/specs/<spec_id>/`, the request verbatim, the `<project-map>` (`ls -d */` without `.devbox`, `.venv`, `.git`, `node_modules`), and the list of other specs (`CPLAT spec list --all`).
4. `CPLAT spec check <spec_id>`. On errors, send them back to the product-manager once; if they persist, stop and show them.
5. **Questions loop** (section Q).
6. Commit `docs(spec): <spec_id> — <title>` and finish with section F.

## C. --amend <id> <change>

1. `CPLAT spec list --all --json` to find the spec and its status. Switch to `feature/<spec_id>` (create it from `main` if the spec is already merged).
2. If the status is not `draft`: `CPLAT spec set-status <id> draft --reason "amend: <one line>"`. Tell the user that it needs a new approval, and, if it has a plan and the criteria change, a new plan.
3. **product-manager**: `MODE: amend`, `SPEC_DIR`, the change verbatim, plus any answers the user gave.
4. `CPLAT spec check <id>`, then the questions loop (Q), then commit `docs(spec): amend <spec_id> — <one line>` and section F.

## D. --from-plan <plan> [<repo-id>] (one repo of a multi-repo plan)

The plan lives in the gitops-app repo (ADR-011); never edit it from here.

1. Read the plan file; pick the `repos[]` entry whose `id` is `<repo-id>` (default: this repo's name, or `repo` in `.platform-app.yml`). Its `arguments` block is the request; its `summary` is the title.
2. Section B with that request and `--parent <gitops_app>:<plan_id>` on `spec new`. Include the plan's `## Contract` section in the product-manager prompt: the criteria must match it.
3. **When run unattended by `/app:run-plan`** (its prompt says so): skip the questions loop. If `OPEN QUESTIONS` is `none`, run `CPLAT spec approve <id>` (the user approved the product plan) and continue with `/svc:plan` and `/svc:build` as instructed; otherwise stop and report the questions verbatim. Never answer them yourself.
4. Remind the user to run `/app:plans start <slug>` before and `/app:plans done <slug> <repo-id>` (in the gitops-app repo) after the PR merges.

## Q. Questions loop

The product-manager ends with an `OPEN QUESTIONS:` list. While it is not `none` (at most 3 rounds):

1. Ask the user with **AskUserQuestion**, up to 4 questions per call. For each: the question as the header text, the suggested answer as the first option marked "(Recommended)", one or two sensible alternatives; the user can always type their own answer.
2. Send the answers to the product-manager: `MODE: amend`, "answers to open questions: …". It strikes the questions through and folds the answers into criteria.
3. `CPLAT spec check <spec_id>` again.

If the user wants to stop answering, leave the remaining questions in the spec: it stays `draft` and cannot be approved until they are answered.

## F. Finish

Print:

```
## Spec <spec_id> — <title>   [<status>]
<n> acceptance criteria:
- AC-NNN.1 …   (one line each, shortened)
Open questions: <n or none> · Non-goals: <short list>
File: docs/specs/<spec_id>/spec.md · Branch: feature/<spec_id>
```

If there are no open questions, ask with AskUserQuestion whether to approve now ("Approve (Recommended)" / "I'll review the file first"). On approve run section A. Otherwise print the next step: `/svc:spec approve <NNN>` after review, or `/svc:spec --amend <NNN> <change>`.

## Rules

- Never write code, a plan, or tests. Never change `status` except through `CPLAT spec`.
- Never answer an open question on the user's behalf; never approve without the user's word (the only exception is D.3, where the user approved the product plan).
- Commits stay local; nothing is pushed here (`/svc:build` opens the PR).

> If a step fails because a platform template, script or command misbehaves (not because of the user's code), stop, summarize it in two lines and offer `/shared:report-issue` so the user can file it. Never file anything without their OK.
