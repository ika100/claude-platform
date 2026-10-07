---
description: "Runs only the product-manager and architect phases (no code written). Produces user stories and an implementation plan ready for review before committing to implementation. Usage: /svc:plan-feature <feature description>"
---

You are the **orchestrator** in planning mode. Do NOT write any production code. Your goal is a reviewed, ready-to-implement plan.

**Feature request:** $ARGUMENTS

---

## Phase 0 — Pre-flight

Before starting planning work:

1. Run `git status --porcelain`. If the working tree is dirty, stop: "Working tree has uncommitted changes — commit or stash before planning a new feature."
2. Run `git symbolic-ref --short HEAD` and print the current branch. Planning is branch-agnostic (no branch creation), but the user should know where they are.
3. Resolve the shape: run this in one Bash call: `P="${XDG_CACHE_HOME:-$HOME/.cache}/claude-platform"; { [ -d "$P/.git" ] && git -C "$P" fetch -q --depth 1 origin main && git -C "$P" checkout -q FETCH_HEAD; } || { rm -rf "$P"; git clone -q --depth 1 https://github.com/ika100/claude-platform.git "$P"; }; uv run "$P/scripts/cplat/cplat.py" shape` It prints JSON: `shape`, `plugin`, `deployable`, `library` and `agents` (the subagent type for every role — spawn each role with exactly that type, e.g. `agents.coder`). If `unsupported` is present, stop and show it. Roles missing from `agents` (e.g. deployment for a library) are skipped. Print `Shape: <shape>` and pass it to the architect so the plan records `shape: <shape>`.

---

## Phase 1 — Product Definition

Use the **product-manager** agent to produce user stories and acceptance criteria for the feature. Save to `docs/backlog.md`.

---

## Phase 2 — Architecture

Use the **architect** agent to produce:
1. An implementation plan (numbered task list) saved to `docs/plan/<feature-slug>.md`
2. Any relevant ADRs in `docs/adr/`

---

## Output

Print a summary:

```
## Plan ready: <feature name>

**User stories:** docs/backlog.md
**Implementation plan:** docs/plan/<slug>.md

### Tasks
1. ...
2. ...

### Acceptance criteria
- [ ] ...

Run `/svc:build-feature <feature>` to execute the plan, or review the docs first.
```

> If a step fails because a platform template, script or command misbehaves (not because of the user's code), stop, summarize it in two lines and offer `/shared:report-issue` so the user can file it. Never file anything without their OK.
