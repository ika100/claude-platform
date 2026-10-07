---
description: "Report a platform problem or idea as a GitHub issue, with diagnostics and secrets removed. Nothing is sent without your OK. Usage: /shared:report-issue [what went wrong]"
---

Help the user report a problem (or an idea) about the platform. **Context from the user:** $ARGUMENTS

1. **Gather**: what was running (command or step), what happened versus what was expected, and the error text from this session. Use what you already know; ask at most one short question for anything essential that is missing. Never include secrets or the user's code unless it is needed to reproduce.
2. **Draft** (nothing is sent). Write the error output to a temp file under `$CLAUDE_JOB_DIR/tmp` (or `$TMPDIR`) and run:

```bash
P="${XDG_CACHE_HOME:-$HOME/.cache}/claude-platform"; { [ -d "$P/.git" ] && git -C "$P" fetch -q --depth 1 origin main && git -C "$P" checkout -q FETCH_HEAD; } || { rm -rf "$P"; git clone -q --depth 1 https://github.com/ika100/claude-platform.git "$P"; }; uv run "$P/scripts/cplat/cplat.py" feedback --kind bug|idea --title "<one line>" --what "<what happened>" --command "<the command or step>" --details-file <file>
```

3. **Show the draft verbatim and ask**: "File this issue on ika100/claude-platform?" The draft already has tokens, e-mail addresses and home-directory names removed, but the user must read it first.
4. **Only after an explicit yes**, run the same command again with `--submit` and give the user the issue URL. Without `gh`, the command prints a prefilled browser link instead; hand that over.

Rules: never submit without the user's yes; never paste secrets, tokens or private code; one issue per problem; if `cplat` itself crashed, include its error text.
