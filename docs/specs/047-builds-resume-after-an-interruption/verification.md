# Verification — 047-builds-resume-after-an-interruption Builds resume after an interruption

**Result:** pass
**Commit:** d51ae8e · **Base:** 8621fd2 · **Trace:** 4/4 criteria named by tests · **Suite:** `tests/cplat` green (slow render tests included)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-047.1 | met | `tests/cplat/test_spec_agents.py` | plugins/svc/commands/build.md Phase 0 step 1 (WIP commit for the first task not done, coder gets the WIP diff) | |
| AC-047.2 | met | `tests/cplat/test_spec_agents.py` | same: stale staged entries → git restore --staged, named | |
| AC-047.3 | met | `tests/cplat/test_spec_agents.py` | same: dirty tree on a spec not building → clean-tree stop | |
| AC-047.4 | met | `tests/cplat/test_spec_agents.py` | plugins/svc/commands/build.md Phase 7: squash-merge note for wip( commits | |

## Non-goals

Respected (see spec).

## Notes and deviations

- Prompt rules, tested by their text; they codify the workarounds that worked in the end-to-end run.
- Built directly from the plan in the platform repo (no shape, so no `/svc:build` coder routing); tests written first and seen failing.
