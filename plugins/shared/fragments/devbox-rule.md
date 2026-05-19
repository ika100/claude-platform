# The devbox-run rule (canonical)

Every shell command an agent runs in a service or library repo MUST go through `devbox run <script>`.

The canonical recipes live in the repo's `devbox.json`. The repo's `devbox.json` pins the toolchain — Python version, `uv`, `ruff`, `mypy`, `pytest`, `alembic`, `docker`, `trivy`, `kubectl`, etc. Going through `devbox run` guarantees that humans, CI, and agents all execute the same versions with the same flags.

**Do not** invoke any of these directly:

- `pip`, `pip install` (use `devbox run -- uv add <pkg>`)
- bare `uv`, `ruff`, `mypy`, `pytest`, `alembic`, `bandit`, `pip-audit`, `detect-secrets`
- bare `docker`, `trivy`, `kubectl`

If a recipe you need doesn't exist in `devbox.json`, **add it first** as a `devbox run` script, then call that script. Don't reach for `devbox run -- <ad-hoc command>` as a routine pattern — that's an escape hatch for one-off operations, not the daily workflow.

This rule is non-negotiable: agents that bypass `devbox run` will get drift between local, CI, and other agents' environments, and reproducibility breaks. When an agent prompt says "use `devbox run <something>`," it is referring to this rule.
