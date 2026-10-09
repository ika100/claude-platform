# Verification — 063-acceptance-test-diff-looks-only-at-test Acceptance-test diff looks only at test files

**Result:** pass
**Commit:** 7abca37 · **Base:** dadb0f5 · **Trace:** 4/4 criteria named by tests · **Suite:** `tests/cplat` green (493 passed, 3 skipped; `devbox run ci-local` OK)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-063.1 | met | `tests/cplat/test_spec.py` | scripts/cplat/spec.py `test_diff`: changed ∩ `test_globs(repo_shape)` |  |
| AC-063.2 | met | `tests/cplat/test_spec.py` | unchanged comparison for selected test files |  |
| AC-063.3 | met | `tests/cplat/test_spec.py` | never `docs/` or `*.md`, even under broad globs |  |
| AC-063.4 | met | `tests/cplat/test_spec_agents.py` | plugins/svc/commands/build.md: stop on exit 1, "never decide yourself that it is a false alarm" |  |

## Non-goals

Respected (see spec).

## Notes and deviations

- Real evidence: on ika100/todo-web at `31137f1` (task t2 done) against the red commit `3257a5c`, v4.0.0 reports `plan.md: changed` (the run-2 false alarm); this branch reports `no acceptance test changed`.
- New finding (not fixed here): an unknown base commit makes `test-diff` crash with "unexpected failure … platform bug" instead of a clear error.
- Built directly from the plan in the platform repo (no shape, so no `/svc:build` coder routing); tests written first and seen failing.
