# Verification — 048-acceptance-tests-may-be-reformatted Acceptance tests may be reformatted, never weakened

**Result:** pass
**Commit:** 851478f · **Base:** 8621fd2 · **Trace:** 3/3 criteria named by tests · **Suite:** `tests/cplat` green (slow render tests included)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-048.1 | met | `tests/cplat/test_spec_agents.py` | plugins/svc/commands/build.md §2.4 step 2 and after Phase 3; coders and testing.md allow lint-fix formatting | |
| AC-048.2 | met | `tests/cplat/test_spec.py`, `tests/cplat/test_spec_agents.py` | scripts/cplat/spec.py test_diff + build stop on exit 1 | |
| AC-048.3 | met | `tests/cplat/test_spec.py` | scripts/cplat/spec.py formatting_only: Python AST (imports sorted, strings whitespace-collapsed), others whitespace-free text, criterion ids equal | |

## Non-goals

Respected (see spec).

## Notes and deviations

- Real evidence: on ika100/todo-api, `cplat spec test-diff 7979bed tests/test_todos_api.py` (the red commit of the end-to-end run vs. main after the manual `style: fix template lint`, +25/-5 lines) reports `formatting only`.
- Deviation from design.md (updated): Python is compared by AST instead of token stream, because wrapping a long line adds parentheses that change tokens but not the AST.
- Built directly from the plan in the platform repo (no shape, so no `/svc:build` coder routing); tests written first and seen failing.
