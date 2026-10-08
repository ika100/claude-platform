---
description: "Set or list values of remote (store-backed) secrets in the local cluster. Usage: /gitops:secret set <service> <secret> <KEY> [--env dev] | list"
---

Run the platform script inside the gitops-app repo. **Request:** $ARGUMENTS

```bash
cplat secret <ARGS>
```

- `list` shows every declared secret and which remote keys are still missing; `generate` secrets need nothing.
- `set` prompts for the value without echo, which only works in a terminal: never ask the user to paste a secret into this chat and never pass it as an argument. Tell them to run it themselves with `! <the command>` (use `--value-stdin` only for piped input).
- Real clusters have their own store (Vault, AWS, GCP): values are managed there, not with this command.

> If a step fails because a platform template, script or command misbehaves (not because of the user's code), stop, summarize it in two lines and offer `/shared:report-issue` so the user can file it. Never file anything without their OK.
