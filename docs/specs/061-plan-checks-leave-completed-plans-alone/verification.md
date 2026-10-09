# Verification — 061-plan-checks-leave-completed-plans-alone Plan checks leave completed plans alone

**Result:** pass
**Commit:** 7abca37 · **Base:** dadb0f5 · **Trace:** 4/4 criteria named by tests · **Suite:** `tests/cplat` green (493 passed, 3 skipped; `devbox run ci-local` OK)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-061.1 | met | `tests/cplat/test_plan.py` | templates/gitops-app/scripts/plan.py `check_all` (errors, warnings); `validate` prints warnings, exits on errors |  |
| AC-061.2 | met | `tests/cplat/test_plan.py` | same rules stay errors for draft/in_progress |  |
| AC-061.3 | met | `tests/cplat/test_plan.py` | check_contract messages: ``add a line `### Timeouts` under `## Contract` …`` |  |
| AC-061.4 | met | `tests/cplat/test_plan.py` | fixture `tests/cplat/fixtures/plans/001-todo-list.md` (ika100/todo `b7feaf8`) + its spec | output: `WARNING: docs/plan/001-todo-list.md: completed before specs 045/053 — no gitops: list, no ### Errors, no ### Timeouts (nothing to do)` |

## Non-goals

Respected (see spec).

## Notes and deviations

- The spec fixture was added next to the plan fixture (plan.md file list updated).
- Built directly from the plan in the platform repo (no shape, so no `/svc:build` coder routing); tests written first and seen failing.
