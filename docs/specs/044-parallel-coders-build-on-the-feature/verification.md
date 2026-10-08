# Verification — 044-parallel-coders-build-on-the-feature Parallel coders build on the feature branch

**Result:** pass
**Commit:** 2b1d6bd · **Base:** 8621fd2 · **Trace:** 4/4 criteria named by tests · **Suite:** `tests/cplat` green (slow render tests included)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-044.1 | met | `tests/cplat/test_spec_driven.py` | templates/*/.claude/settings.json(.jinja): worktree.baseRef "head" | |
| AC-044.2 | met | `tests/cplat/test_spec_driven.py` | same + scripts/shapes.py check_contract (verified: removing it from service-go fails the check) | |
| AC-044.3 | met | `tests/cplat/test_spec_agents.py` | plugins/svc/commands/build.md §2.2 (probe reports HEAD, mismatch → sequential with reason) | |
| AC-044.4 | met | `tests/cplat/test_spec_agents.py` | plugins/svc/commands/build.md §2.2 (task branches start at the feature head) | |

## Non-goals

Respected (see spec).

## Notes and deviations

- The probe behaviour is a prompt rule; tested by its text, not by a live parallel build (that comes with the next end-to-end run).
- Built directly from the plan in the platform repo (no shape, so no `/svc:build` coder routing); tests written first and seen failing.
