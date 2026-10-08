# Verification — 055-template-action-pins-match-the-platform Template action pins match the platform

**Result:** pass
**Commit:** 2b1d6bd · **Base:** 8621fd2 · **Trace:** 2/2 criteria named by tests · **Suite:** `tests/cplat` green (slow render tests included)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-055.1 | met | `tests/cplat/test_workflows.py` | scripts/pin-actions.py --check (one SHA per action); 12 template workflows moved to checkout v7.0.1 | |
| AC-055.2 | met | `tests/cplat/test_workflows.py` | .github/dependabot.yml: one grouped github-actions update for / and every template | |

## Non-goals

Respected (see spec).

## Notes and deviations

- None.
- Built directly from the plan in the platform repo (no shape, so no `/svc:build` coder routing); tests written first and seen failing.
