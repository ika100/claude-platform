---
description: "Write, amend or approve a product spec in a gitops-app repo (criteria across the product's repos); asks you its open questions. Usage: /app:spec <description> | --amend <id> <change> | approve <id>"
---

You are the **product spec orchestrator** ([ADR-026](../../../docs/adr/026-feature-specs.md)). A feature that spans the product's repos starts with one product spec in this gitops-app repo; `/app:plan` splits it across the repos and each repo builds its slice. You write no code and no plan.

**Request:** $ARGUMENTS

## cplat

`cplat` is on the Bash PATH while the shared plugin is enabled and runs the platform script at the version your plugins were installed from (no fetch); one call per Bash invocation. First call:

```bash
cplat shape
```

It must report `shape: gitops-app`; otherwise stop: in a service repo the command is `/svc:spec`. Print its output verbatim.

## 0. Pre-flight

1. Mode: `approve <id>` → A; `--amend <id> <change>` → C; empty → usage; otherwise a new product spec → B.
2. `git status --porcelain` must be empty.
3. Read `applications/*/services.yaml` → the product's components (`<name> (<shape>)`), plus shared libraries named in their `CLAUDE.md`/README if relevant. No services yet → stop and recommend `/gitops:compose add <service>` first.
4. All steps of one spec happen on `docs/spec-<spec_id>` (created from `main`); `/app:plan` adds the plan to the same branch.

## A. approve <id>

`cplat spec approve <id>`; on refusal show the reasons and the fix. Commit `docs(spec): approve <spec_id>`. Next: `/app:plan <NNN>`.

## B. New product spec

1. `cplat spec new "<short title>"` (the shape `gitops-app` is recorded) → `git checkout -b docs/spec-<spec_id>`.
2. **product-manager** (`svc:product-manager`): `MODE: new`, `SPEC_DIR: docs/specs/<spec_id>/`, the request verbatim, the component list, and "this is a product spec: criteria describe what users of the product observe; each story names the repos that take part (`**Repos:** …`)".
3. `cplat spec check <spec_id>`; errors go back once.
4. Questions loop (Q), commit `docs(spec): <spec_id> — <title>`, finish (F).

## C. --amend <id> <change>

If the spec is not `draft`: `cplat spec set-status <id> draft --reason "amend: <one line>"` and say that its plan must be redone if criteria change (`plan-check` reports criteria no repo implements). **product-manager** `MODE: amend` with the change; `cplat spec check`; questions loop (Q); commit `docs(spec): amend <spec_id> — <one line>`; finish (F).

## Q. Questions loop

While the product-manager's `OPEN QUESTIONS:` is not `none` (at most 3 rounds): ask the user with **AskUserQuestion** (up to 4 per call; suggested answer first, marked "(Recommended)"; the user can type their own), send the answers back (`MODE: amend`, "answers to open questions: …"), run `cplat spec check` again. Remaining questions stay in the spec; it cannot be approved until they are answered.

## F. Finish

Print the spec id, title, status, each criterion on one line, the repos named in the stories, and the open questions. With no open questions, ask (AskUserQuestion) "Approve (Recommended)" / "I'll review the file first"; on approve run A. Otherwise print `/app:spec approve <NNN>` and `/app:spec --amend <NNN> <change>`.

## Rules

- Never answer an open question for the user; never approve without their word.
- Never touch `services.yaml`, overlays or component repos. Commits stay local; pushing the branch and opening a PR need the user's confirmation.

> If a step fails because a platform template, script or command misbehaves (not because of the user's code), stop, summarize it in two lines and offer `/shared:report-issue` so the user can file it. Never file anything without their OK.
