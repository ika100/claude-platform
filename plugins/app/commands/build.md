---
description: "Build a planned product spec: every ready repo in parallel (one agent each) through its own /svc:spec → plan → build, ending at open PRs; never merges for you. Usage: /app:build <spec-id> [--max N]"
---

You are the **product build executor** ([ADR-023](../../../docs/adr/023-parallel-plan-execution.md), [ADR-026](../../../docs/adr/026-feature-specs.md)). The plan `docs/plan/<spec_id>.md` lists the product's repos with `depends_on`; repos whose dependencies are done are built **at the same time**. You run one wave after the other and stop wherever a human decision is needed.

**Arguments:** $ARGUMENTS (`<spec-id>`; `--max N` limits parallel agents, default 3)

## cplat

First call (updates the cached platform checkout, one Bash call):

```bash
P="${XDG_CACHE_HOME:-$HOME/.cache}/sdlc-foundry"; { [ -d "$P/.git" ] && git -C "$P" fetch -q --depth 1 origin "${REF:-main}" && git -C "$P" checkout -q FETCH_HEAD; } || { rm -rf "$P"; git clone -q --depth 1 --branch "${REF:-main}" https://github.com/ika100/sdlc-foundry.git "$P"; }; uv run "$P/scripts/cplat/cplat.py" shape
```

It must report `shape: gitops-app`, else stop. Later calls: `CPLAT <args>` = `uv run "${XDG_CACHE_HOME:-$HOME/.cache}/sdlc-foundry/scripts/cplat/cplat.py" <args>`.

## Pre-flight

1. Resolve `<spec_id>` (`CPLAT spec list --all --json`). `CPLAT spec check <spec_id> --require approved` must pass; `docs/plan/<spec_id>.md` must exist (otherwise `/app:plan <NNN>`).
2. `devbox run plan-check`; the plan must be `draft` or `in_progress`. `devbox run -- uv run scripts/plan.py start <spec_id>` (draft → in_progress); if the spec is `approved`, `CPLAT spec set-status <spec_id> building`. Commit both on the plan's branch or `main` as the user prefers.
3. Show `devbox run -- uv run scripts/plan.py show <spec_id>` and ask the user to confirm: this opens PRs in several repositories.

## Loop (one wave per iteration)

1. `devbox run -- uv run scripts/plan.py ready <spec_id> --json` → the repos that can start now. Empty and not completed → a PR of the previous wave is still open: go to 4.
2. For each ready repo (at most `--max`): make sure a clone exists next to this repo (`gh repo clone <org>/<repo> ../<repo>` if missing); refuse a clone with uncommitted changes.
3. **In a single message**, start one subagent per ready repo (Agent tool, general-purpose) so they run concurrently. Each prompt contains the repo path, the absolute plan path, the repo id, and these instructions:
   *Work only inside that clone. Run the `/svc:spec --from-plan <abs plan path> <repo-id>` steps **unattended**: the user approved the product spec and plan, so if the repo spec has no open questions, approve it; if it has any, stop and report them verbatim, never answer them. Then run the `/svc:plan <n>` and `/svc:build <n>` pipelines. Stop with an open pull request: never merge, never push to `main`. Report the repo spec id, the PR URL, the CI result and the verification result; if blocked, report why instead of guessing.*
4. Collect the reports. Print one table: repo, repo spec, PR, CI, verification, state. Open questions from a repo go to the user (AskUserQuestion); after answering, re-run `/app:build <NNN>` (state is in the plan file and the repo specs). A failed or blocked repo stops the loop: say which repos are untouched.
5. Ask the user to review and merge the PRs (or to say "merge" for green ones: only then `gh pr merge --squash` on those). For each `MERGED` PR (`gh pr view --json state`): `devbox run -- uv run scripts/plan.py done <spec_id> <repo-id>`. Then the next wave.

## When the plan is completed

`CPLAT spec set-status <spec_id> done` and `CPLAT spec index`; commit both with the plan. Show the `gitops_pin` entries and the exact `/gitops:promote` commands; do not apply pins or touch `services.yaml` or overlays yourself.

## Rules

- Parallel only within a wave; a repo never starts before its `depends_on` are done (merged).
- Never merge without the user's explicit word, never force-push, never pin images.
- Agents write only inside their own clone; two agents never share one.
- Print `plan.py` output verbatim.

> If a step fails because a platform template, script or command misbehaves (not because of the user's code), stop, summarize it in two lines and offer `/shared:report-issue` so the user can file it. Never file anything without their OK.
