---
description: Preflight check of the platform setup (tools, gh scopes, Docker, kube context, plugin versions, this repo's platform version) with a concrete fix per problem. Usage: /shared:doctor
---

Run the platform doctor. One Bash call:

```bash
P="${XDG_CACHE_HOME:-$HOME/.cache}/claude-platform"; { [ -d "$P/.git" ] && git -C "$P" fetch -q --depth 1 origin main && git -C "$P" checkout -q FETCH_HEAD; } || { rm -rf "$P"; git clone -q --depth 1 https://github.com/ika100/claude-platform.git "$P"; }; uv run "$P/scripts/cplat/cplat.py" doctor
```

Show the output verbatim. If it reports outdated plugins, say plainly that **Claude Code must be restarted** to load updated plugin prompts (a running session keeps the old ones). Offer to run the `fix:` commands that are safe (`gh auth refresh -s …`, `claude plugin update …`, `open -a Docker`); never run anything that touches a non-local kube context.
