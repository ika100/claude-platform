# CLAUDE.md

This file is for Claude Code working inside the `ika100/claude-platform` repo itself.

## Purpose

This repo is **the source of truth** for Claude Code agents, slash commands, and Copier templates used across the ika100 services fleet. Changes here propagate to many downstream repos — be careful.

## Layout

| Path | What it is |
|---|---|
| `.claude-plugin/marketplace.json` | Marketplace catalog. Bump plugin versions here when a plugin changes. |
| `plugins/<name>/.claude-plugin/plugin.json` | Per-plugin manifest. Mirror the version in the marketplace catalog. |
| `plugins/<name>/agents/*.md` | Subagent definitions (YAML frontmatter + system prompt). |
| `plugins/<name>/commands/*.md` | Slash commands (description frontmatter + body using `$ARGUMENTS`). |
| `plugins/<name>/hooks/hooks.json` | Plugin-scoped hooks. All three plugins ship a SessionStart hook that checks devbox is on PATH and runs `devbox install` if a `devbox.json` is present. |
| `devbox.json` | Repo-root devbox env (jq, uv, python, copier) + smoke-test scripts (`validate`, `smoke-service`, `smoke-library`). |
| `plugins/<name>/settings.json` | Plugin-scoped permission allowlists. |
| `templates/service-python/{{ project_name }}/` | Copier-templated service repo skeleton. |
| `templates/library-python/{{ project_name }}/` | Copier-templated library repo skeleton. |
| `docs/AGENTS.md` | The orchestration model — read before changing agents or commands. |

## Conventions

- **Don't break the marketplace schema.** `marketplace.json` is consumed by every project that pins this repo. Validate locally before pushing — see `.github/workflows/ci.yml`.
- **Bump versions in both places.** When a plugin changes, update both `marketplace.json` and `plugins/<name>/.claude-plugin/plugin.json`. Use semver — major bump only for breaking changes consumers must react to (renamed commands, removed agents).
- **Template Jinja gotcha.** GitHub Actions uses `${{ var }}` syntax, which Copier (Jinja) would otherwise interpret. The escape pattern is `${{ '{{' }} var {{ '}}' }}` — already applied in the existing CI workflows. Don't unescape it.
- **Don't put project-specific content in plugin agents.** Agents are shared across repos. Anything project-specific belongs in the Copier template (which gets parameterised per-repo) or in the consumer's own `CLAUDE.md`.
- **No backwards-compat hacks for old marketplace ref.** When breaking, ship a new major version and document the migration in `docs/CHANGELOG.md`.

## Common changes

### Add an agent

1. Decide which plugin (`svc` / `gitops` / `shared`).
2. Write `plugins/<plugin>/agents/<name>.md` with YAML frontmatter (`name`, `description`, `tools`, `model`).
3. Update the plugin's README.
4. Bump `plugins/<plugin>/.claude-plugin/plugin.json` version (minor for additions, patch for fixes).
5. Bump the matching entry in `.claude-plugin/marketplace.json`.

### Add a slash command

1. Write `plugins/<plugin>/commands/<name>.md` with `description:` frontmatter and `$ARGUMENTS` in the body.
2. The command will be available as `/<plugin>:<name>` in consumer repos after version bump + `/plugin marketplace update`.

### Change a Copier template

1. Edit files under `templates/<template>/{{ project_name }}/`.
2. Test locally: `copier copy ./templates/service-python /tmp/test --defaults --data project_name=test-svc --data module_name=test_svc`.
3. Add to `_skip_if_exists` in `copier.yml` if the file should NOT be overwritten by `/shared:update-service` (project-owned files).
4. Tag a release in the platform repo.
5. Downstream repos run `/shared:update-service` to pull the change.

## Smoke test before pushing

This repo itself ships a `devbox.json` so the smoke-test runs through the same `devbox run <script>` entry point used everywhere else.

```bash
devbox install          # one-time: pulls jq, uv, python, gh, copier
devbox run validate     # jq-checks marketplace.json + every plugin.json + every hook.json
devbox run smoke-service  # copier copy → devbox install → devbox run quality
devbox run smoke-library  # same, for the library template
devbox run smoke        # all of the above
```

(`devbox` must be available on the host — everything else is provided by `devbox install`. Host install: `curl -fsSL https://get.jetify.com/devbox/install.sh | bash`.)
