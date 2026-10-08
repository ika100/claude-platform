---
description: "List the repo's feature specs with status, criteria, task progress and the next command; refresh the backlog table or migrate legacy STORY-NNN stories. Usage: /svc:specs [--all | index | migrate]"
---

Show and maintain the repo's specs with the platform script ([ADR-026](../../../docs/adr/026-feature-specs.md)). **Request:** $ARGUMENTS

`cplat` is on the Bash PATH while the shared plugin is enabled and runs the platform script at the version your plugins were installed from (no fetch); one call per Bash invocation:

```bash
cplat spec <ARGS>
```

- **(no argument) / `--all`**: run `list` (`list --all` includes done and superseded). Print the output verbatim. If it is empty, suggest `/svc:spec <description>`; if `docs/backlog.md` contains `STORY-NNN` stories, suggest `/svc:specs migrate`.
- **`index`**: run `index`, show `git diff --stat docs/backlog.md`, and commit it as `docs(backlog): refresh spec index` only if the user agrees.
- **`migrate`**: converts legacy `STORY-NNN` stories in `docs/backlog.md` into `docs/specs/<NNN>-<slug>/spec.md` (numbers kept, criteria numbered `AC-<NNN>.<n>`, legacy metadata and plan links kept; the backlog keeps every non-story section and gets the generated table).
  1. `git status --porcelain` must be empty.
  2. Run `migrate` (dry run) and show the output verbatim.
  3. After the user confirms: `git checkout -b docs/migrate-specs` (from `main`), run `migrate --write`, then `check`. Show `git diff --stat`, and commit `docs(spec): migrate backlog stories to docs/specs` on the user's OK. Migrated specs keep their status: `done` stays `done`, open stories become `draft` (they need criteria review and approval before they can be planned).

Never edit specs from this command. To change one, use `/svc:spec --amend <id> <change>`.

> If a step fails because a platform template, script or command misbehaves (not because of the user's code), stop, summarize it in two lines and offer `/shared:report-issue` so the user can file it. Never file anything without their OK.
