# Design — 060 Skeleton updates keep the project README and devbox recipes

## README: project-owned

- `README.md` joins `_skip_if_exists` in all six `copier.yml`. `copier copy --overwrite` skips an existing file but still writes it into a new repo, so creation is unchanged (AC-060.2) and updates leave it alone (AC-060.1).
- `scripts/shapes.py check`: every template must list `README.md` in `_skip_if_exists` (AC-060.3).
- Report (AC-060.4): `update.py` compares `templates/<t>/README.md.jinja` between the repo's old platform ref and the new one with `git diff --quiet <old> <new> -- <path>` in the platform checkout. If it changed, or the old ref is unknown, a next step says the README was kept and prints `git -C <platform> show <new>:templates/<t>/README.md.jinja`.

## devbox.json: merge instead of overwrite

`update.py` reads the project's `devbox.json` before Copier runs, then calls `merge_devbox(project, template) -> (merged, kept, replaced)` on the rendered file:

| Key | Rule |
|---|---|
| `packages` (list or map) | the template's entries, plus project packages whose name (before `@`) the template doesn't have |
| `shell.scripts` | the template's recipes, plus recipes only the project has |
| `env` | the template's variables, plus variables only the project has |
| anything else (`shell.init_hook`, `include`, …) | the template's |

- **Same key, different value:** the template wins (the answered question). `replaced` keeps `(key, project value)` and the report shows the old line. A template change since the old version shows up there too. Telling a project edit apart from a template change would need the old template rendered again, and the report stays correct either way: it shows what the file had before.
- **Output:** written with 2-space indentation and the template's key order. Kept entries are appended in the project's order.
- **Report (AC-060.7):** `kept in devbox.json: scripts bundle-check; packages k6` and `replaced in devbox.json: test (was "pnpm vitest run --reporter=dot")`. `devbox.json` is no longer listed among the MODIFIED files that need a manual check, unless the merge replaced something.
- **Invalid JSON:** if the project's file isn't valid JSON, it is overwritten as today and the report says so.

## Not chosen

- A managed block inside the README: rejected in the answered question.
- Moving project recipes to a second file (`devbox.project.json`): devbox has no include for scripts, and the projects already have them in `devbox.json`.
