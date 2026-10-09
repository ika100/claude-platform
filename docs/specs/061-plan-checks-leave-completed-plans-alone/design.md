# Design — 061 Plan checks leave completed plans alone

## Which rules depend on the plan's status

`check(path)` in `templates/gitops-app/scripts/plan.py` returns `(errors, warnings)` instead of a flat list:

| Rule | Active plan (`draft`, `in_progress`) | Finished plan (`completed`, `abandoned`) |
|---|---|---|
| frontmatter keys, `plan_id` = file name, status value, repo ids, shapes, `depends_on`, `done` booleans, criteria assigned, cycles, completed ⇒ all repos done | error | error |
| spec 045: `gitops:` list on the gitops-app entry | error | warning |
| spec 053: `## Contract` with `### Errors` and `### Timeouts` | error | warning |

- **Warnings:** `validate` prints at most one line per finished plan, for example `WARNING: docs/plan/001-todo.md: completed before spec 045/053 — no gitops list, no ### Timeouts (nothing to do)`. The exit code ignores warnings (AC-061.1).
- **Errors** name the missing heading and the exact line to add (AC-061.3), e.g. ``the contract has no `### Timeouts` section — add a line `### Timeouts` under `## Contract` with the timeout per call (spec 053)``. A missing `## Contract` gets the three lines to paste.
- `plan.py done`/`start` call `check` too. They keep refusing finished plans as today, so the warnings never block them.

## Fixture

`tests/cplat/fixtures/plans/001-todo-list.md` is plan 001 from ika100/todo as it was before the run-2 workaround (`b7feaf8`, the completed plan before the hand edit; the file keeps its name because `plan_id` must equal it), with its spec reduced to the criteria it assigns. `tests/cplat/test_plan.py` renders the gitops-app template, copies the fixture and the spec in, and asserts `devbox run test-fast`'s plan step (`plan.py validate`) exits 0 with one warning (AC-061.4).
