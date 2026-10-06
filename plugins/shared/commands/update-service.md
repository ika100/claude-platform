---
description: Pull the latest platform skeleton (CI, Dockerfile, devbox recipes, CLAUDE.md, …) into the current repo on a review branch; project-owned files are never touched. Usage: /shared:update-service [--ref <tag>] [--data key=value ...]
---

Update the current repo with the platform script. **Request:** $ARGUMENTS

Prefix for each call (one Bash call each):

```bash
P="${XDG_CACHE_HOME:-$HOME/.cache}/claude-platform"; { [ -d "$P/.git" ] && git -C "$P" fetch -q --depth 1 origin "${REF:-main}" && git -C "$P" checkout -q FETCH_HEAD; } || { rm -rf "$P"; git clone -q --depth 1 --branch "${REF:-main}" https://github.com/ika100/claude-platform.git "$P"; }; uv run "$P/scripts/cplat/cplat.py" update-service <ARGS>
```

1. **Preview** with `--dry-run`; show it verbatim. Stop on errors (they carry a `fix:` line; typical: dirty tree, no `.copier-answers.yml`).
2. **Run** without `--dry-run` (the user asked for the update; nothing is pushed).
3. **Report** the script's output. Then run the repo's own checks if `devbox` is available (`devbox run quality && devbox run test-fast`) and report failures without fixing them. If the output lists MODIFIED skeleton files, remind the user to review them for lost local customisations.

Rules: never push or open a PR unless asked; never edit the update's result by hand — the template is the source of truth.
