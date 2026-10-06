---
description: "Create a new repo of any shape (service-python, web-nextjs, gitops-app, service-java, service-go, library-python) from the platform template, with a private GitHub repo. Usage: /shared:new-service <name> <one-line description> [--web|--gitops|--library|--type <shape>] [--app <org>/<gitops-repo>] [--org <org>] [--ref <tag>]"
---

Create a repo with the platform script (all logic and tests live in `scripts/cplat`). **Request:** $ARGUMENTS

Every call below uses this prefix, which keeps a cached checkout of the platform up to date (one Bash call each — shell state is not shared):

```bash
P="${XDG_CACHE_HOME:-$HOME/.cache}/claude-platform"; { [ -d "$P/.git" ] && git -C "$P" fetch -q --depth 1 origin "${REF:-main}" && git -C "$P" checkout -q FETCH_HEAD; } || { rm -rf "$P"; git clone -q --depth 1 --branch "${REF:-main}" https://github.com/ika100/claude-platform.git "$P"; }; uv run "$P/scripts/cplat/cplat.py" new-service <ARGS>
```

1. **Preview.** Run it with `--dry-run` and the user's arguments (quote the description words). Show the output verbatim. If it exits non-zero, show the error and its `fix:` line and stop — do not retry with guesses. A missing name/description is the only thing you may ask the user about, once, in plain text.
2. **Run.** The preview lists steps marked `[outward]` (GitHub repo creation, topic). The user's request to create the repo is the confirmation; do not ask again unless the preview shows something they did not ask for. Run the same command without `--dry-run`.
3. **Report.** Relay the script's *What happened / Next / To undo* output; add nothing else.

Rules: never create public repos; never overwrite a non-empty directory; if `gh` is missing the script prints the GitHub commands instead of failing.
