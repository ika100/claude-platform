---
description: "Create a repo of any shape (python, web, gitops, java, go, library) from its template plus a GitHub repo (private by default). Usage: /shared:new-service <name> <description> [--web|--gitops|--library|--type <shape>] [--app <repo>] [--public] [--data k=v]"
---

Create a repo with the platform script (all logic and tests live in `scripts/cplat`). **Request:** $ARGUMENTS

`cplat` is on the Bash PATH while the shared plugin is enabled and runs the platform script at the version your plugins were installed from (no fetch); one call per Bash invocation:

```bash
cplat new-service <ARGS>
```

With `--ref <tag>`, prefix every call with `CPLAT_REF=<tag>` so the templates come from that release.

1. **Preview.** Run it with `--dry-run` and the user's arguments (quote the description words). Show the output verbatim. If it exits non-zero, show the error and its `fix:` line and stop — do not retry with guesses. A missing name/description is the only thing you may ask the user about, once, in plain text.
2. **Run.** The preview lists steps marked `[outward]` (GitHub repo creation, topic). The user's request to create the repo is the confirmation; do not ask again unless the preview shows something they did not ask for. Run the same command without `--dry-run`.
3. **Report.** Relay the script's *What happened / Next / To undo* output; add nothing else. The repo is ready to work in as soon as it is created: development starts on a feature branch (`/svc:spec` creates it), so never wait for the bootstrap pipeline on `main` before starting. The first feature is planned before it is built: `/svc:spec "<description>"` in the new repo, then `/svc:plan <NNN>` and `/svc:build <NNN>` (gitops-app: `/app:spec`, `/app:plan`, `/app:build`). Never suggest building the first feature without a plan.

Rules: never create public repos; never overwrite a non-empty directory; if `gh` is missing the script prints the GitHub commands instead of failing.

> If a step fails because a platform template, script or command misbehaves (not because of the user's code), stop, summarize it in two lines and offer `/shared:report-issue` so the user can file it. Never file anything without their OK.
