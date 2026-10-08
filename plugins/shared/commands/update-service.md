---
description: "Pull the latest platform skeleton (CI, Dockerfile, devbox, CLAUDE.md) into this repo on a review branch. Usage: /shared:update-service [--ref <tag>] [--data k=v] [--migrate]"
---

Update the current repo with the platform script. **Request:** $ARGUMENTS

`cplat` is on the Bash PATH while the shared plugin is enabled and runs the platform script at the version your plugins were installed from (no fetch); one call per Bash invocation:

```bash
cplat update-service <ARGS>
```

With `--ref <tag>`, prefix every call with `CPLAT_REF=<tag>` (for example `CPLAT_REF=v4.0.0 cplat update-service --ref v4.0.0 --dry-run`) so the templates come from that release.

1. **Preview** with `--dry-run`; show it verbatim. Stop on errors (they carry a `fix:` line; typical: dirty tree, no `.copier-answers.yml`).
2. **Run** without `--dry-run` (the user asked for the update; nothing is pushed).
3. **Report** the script's output. Then run the repo's own checks if `devbox` is available (`devbox run quality && devbox run test-fast`) and report failures without fixing them. If the output lists MODIFIED skeleton files, remind the user to review them for lost local customisations.

Rules: never push or open a PR unless asked; never edit the update's result by hand — the template is the source of truth.

> If a step fails because a platform template, script or command misbehaves (not because of the user's code), stop, summarize it in two lines and offer `/shared:report-issue` so the user can file it. Never file anything without their OK.
