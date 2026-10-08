# Verification — 046-unattended-builds-survive-long-runs Unattended builds survive long runs

**Result:** pass
**Commit:** d51ae8e · **Base:** 8621fd2 · **Trace:** 2/2 criteria named by tests · **Suite:** `tests/cplat` green (slow render tests included)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-046.1 | met | `tests/cplat/test_spec_agents.py` | plugins/app/commands/build.md loop step 4: foreground calls, never run_in_background | |
| AC-046.2 | met | `tests/cplat/test_spec_agents.py` | docs/ADOPTING.md section 'Unattended runs' | |

## Non-goals

Respected (see spec).

## Notes and deviations

- AC-046.1 is a prompt rule, tested by its text; the next headless /app:build run is the live check.
- Built directly from the plan in the platform repo (no shape, so no `/svc:build` coder routing); tests written first and seen failing.
