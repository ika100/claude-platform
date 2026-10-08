# Verification — 056-criteria-stay-environment-neutral Criteria stay environment-neutral

**Result:** pass
**Commit:** 2b1d6bd · **Base:** 8621fd2 · **Trace:** 2/2 criteria named by tests · **Suite:** `tests/cplat` green (slow render tests included)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-056.1 | met | `tests/cplat/test_spec_agents.py` | plugins/svc/skills/spec-format/references/spec.md (Environment-neutral); plugins/svc/agents/product-manager.md rule 2 | |
| AC-056.2 | met | `tests/cplat/test_cluster_ports.py` | templates/gitops-app/scripts/local-cluster.sh: unset LOCAL_HTTP_PORT → preferred port or next free (LOCAL_HTTP_PORT_BASE for tests) | |

## Non-goals

Respected (see spec).

## Notes and deviations

- An explicit busy LOCAL_HTTP_PORT still stops with the fix line (existing test).
- Built directly from the plan in the platform repo (no shape, so no `/svc:build` coder routing); tests written first and seen failing.
