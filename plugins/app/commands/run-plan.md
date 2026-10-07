---
description: "Execute a multi-repo plan: build every ready repo in parallel (one agent per repo), open PRs, never merge for you. Usage: /app:run-plan <slug> [--max N]"
---

You are the **plan executor** (ADR-023). A plan from `/app:build-feature` lists the product's repos with `depends_on`; repos whose dependencies are done can be built **at the same time**. You run one wave after the other, each wave in parallel, and stop wherever a human decision is needed.

**Arguments:** $ARGUMENTS (`<slug>` of a plan in `docs/plan/`; `--max N` limits parallel agents, default 3)

## Pre-flight

Resolve the shape: run this in one Bash call: `P="${XDG_CACHE_HOME:-$HOME/.cache}/sdlc-foundry"; { [ -d "$P/.git" ] && git -C "$P" fetch -q --depth 1 origin main && git -C "$P" checkout -q FETCH_HEAD; } || { rm -rf "$P"; git clone -q --depth 1 https://github.com/ika100/sdlc-foundry.git "$P"; }; uv run "$P/scripts/cplat/cplat.py" shape` It must report `shape: gitops-app`, else stop. Confirm `scripts/plan.py` exists; if not, tell the user to run `/shared:update-service` (older skeleton) and stop.

Then: `devbox run plan-check`; the plan must be `draft` or `in_progress`. If it has a `## Contract` section, you will give it to every agent (below). Print the plan with `devbox run -- uv run scripts/plan.py show <slug>` and ask the user to confirm the execution (this opens PRs in several repositories).

## Loop (one wave per iteration)

1. `devbox run -- uv run scripts/plan.py ready <slug> --json` gives the repos that can start now. If empty and the plan is not completed, a PR of the previous wave is still open: go to step 4.
2. For each ready repo (at most `--max`): make sure a local clone exists next to this repository (`gh repo clone <org>/<repo> ../<repo>` if missing; refuse to touch a clone with uncommitted changes).
3. **In a single message**, start one subagent per ready repo (the Agent tool, general-purpose) so they run concurrently. Each prompt contains: the repo path, the repo's `arguments` text from the plan, the plan's `## Contract` section, and these instructions: *work only inside that clone; run the `/svc:build-feature --from-plan <abs plan path> <repo-id>` pipeline; stop with an open pull request (never merge, never push to `main`); report the PR URL and the CI result; if blocked, report why instead of guessing.*
4. Collect the reports. Print one table: repo, PR URL, CI, state. A failed or blocked repo stops the loop: say which repos are untouched and that re-running `/app:run-plan <slug>` resumes (state is in the plan file).
5. Ask the user to review and merge the PRs (or to say "merge" for green ones: only then run `gh pr merge --squash` on those). When a PR is merged (`gh pr view --json state` says `MERGED`), run `devbox run -- uv run scripts/plan.py done <slug> <repo-id>`. Then next wave.

## When the plan is completed

Show the `gitops_pin` entries and the exact `/gitops:promote` commands; do not apply pins or touch `services.yaml` or overlays yourself.

## Rules

- Parallel only within a wave; a repo never starts before its `depends_on` are `done` (merged).
- Never merge without the user's explicit word, never force-push, never pin images in gitops.
- Agents write only inside their own clone. Two agents never share a clone.
- Print the script's output verbatim; do not paraphrase tables from `plan.py`.

> If a step fails because a platform template, script or command misbehaves (not because of the user's code), stop, summarize it in two lines and offer `/shared:report-issue` so the user can file it. Never file anything without their OK.
