# Verification — 060-skeleton-updates-keep-the-project-readme Skeleton updates keep the project README and devbox recipes

**Result:** pass
**Commit:** 7abca37 · **Base:** dadb0f5 · **Trace:** 7/7 criteria named by tests · **Suite:** `tests/cplat` green (493 passed, 3 skipped; `devbox run ci-local` OK)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-060.1 | met | `tests/cplat/test_spec_driven.py`, `tests/cplat/test_update_doctor.py` | README.md in `_skip_if_exists` of all six templates |  |
| AC-060.2 | met | `tests/cplat/test_spec_driven.py` | templates still ship README.md(.jinja); `copier copy` writes it for new repos |  |
| AC-060.3 | met | `tests/cplat/test_spec_driven.py` | scripts/shapes.py check_contract |  |
| AC-060.4 | met | `tests/cplat/test_update_doctor.py` | scripts/cplat/update.py `_readme_changed` + next step with `git show HEAD:templates/<t>/README.md.jinja` |  |
| AC-060.5 | met | `tests/cplat/test_update_doctor.py` | update.py `merge_devbox`, `merge_devbox_file`, `_insert_kept` | kept entries are inserted into the rendered text, so aligned template recipes stay byte-for-byte |
| AC-060.6 | met | `tests/cplat/test_update_doctor.py` | merge_devbox: template wins |  |
| AC-060.7 | met | `tests/cplat/test_update_doctor.py` | report: `kept in devbox.json: …`, `replaced in devbox.json … (was …)`; devbox.json left out of MODIFIED unless replaced |  |

## Non-goals

Respected (see spec).

## Notes and deviations

- Real evidence: `cplat update-service` from this branch on a fresh clone of ika100/todo-web reported `kept in devbox.json: scripts bundle-check` and kept the recipe (run 2 lost it with v4.0.0). The recipe moves to the end of the scripts block (one-time reorder).
- Deviation from design.md: the rewrite inserts kept entries into the template's text instead of `json.dumps`, because four templates align their recipes and a dump would reformat the whole block on every update.
- Built directly from the plan in the platform repo (no shape, so no `/svc:build` coder routing); tests written first and seen failing.
