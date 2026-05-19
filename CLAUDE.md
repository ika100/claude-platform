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
| `plugins/<name>/hooks/hooks.json` | Plugin-scoped hooks (currently: svc SessionStart syncs uv). |
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
3. Add to `_skip_if_exists` in `copier.yml` if the file should NOT be re-templated on `copier update` (project-owned files).
4. Tag a release in the platform repo.
5. Downstream repos run `copier update` to pull the change.

## Smoke test before pushing

```bash
# Validate marketplace + plugin manifests (CI does this; also run locally)
jq -e . .claude-plugin/marketplace.json
for f in plugins/*/.claude-plugin/plugin.json; do jq -e . "$f"; done

# Smoke-test the Copier template
copier copy ./templates/service-python /tmp/test-svc \
  --defaults --data project_name=test-svc --data module_name=test_svc --data description=test

cd /tmp/test-svc && devbox install && devbox run quality
```

(`copier`, `devbox`, and `jq` must be available on the host. `copier` install: `uv tool install copier`.)
