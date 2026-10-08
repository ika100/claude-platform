# Verification — 052-repo-specs-know-the-gitops-wiring Repo specs know the gitops wiring

**Result:** pass
**Commit:** 7c8bb50 · **Base:** 8621fd2 · **Trace:** 2/2 criteria named by tests · **Suite:** `tests/cplat` green (slow render tests included)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-052.1 | met | `tests/cplat/test_spec.py` | scripts/cplat/spec.py provided_by_product + addon_env (render.py ADDONS, the ADR-020 contract) in slice_from_plan | |
| AC-052.2 | met | `tests/cplat/test_spec_agents.py` | plugins/svc/commands/build.md Phase 5: ask only for wiring not listed under Provided by the product | |

## Non-goals

Respected (see spec).

## Notes and deviations

- Addon env names are read from the gitops repo's render.py, falling back to the platform's gitops-app template (the tests exercise the fallback, i.e. the real ADDONS table).
- Built directly from the plan in the platform repo (no shape, so no `/svc:build` coder routing); tests written first and seen failing.
