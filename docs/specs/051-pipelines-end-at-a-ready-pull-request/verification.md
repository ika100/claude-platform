# Verification — 051-pipelines-end-at-a-ready-pull-request Pipelines end at a ready pull request

**Result:** pass
**Commit:** 7c8bb50 · **Base:** 8621fd2 · **Trace:** 2/2 criteria named by tests · **Suite:** `tests/cplat` green (slow render tests included)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-051.1 | met | `tests/cplat/test_spec_agents.py` | plugins/svc/commands/{build,quick-task,fix-bug}.md and plugins/app/commands/build.md: fallback paragraph (.git/PR_BODY.md, exact command, not an error) | |
| AC-051.2 | met | `tests/cplat/test_spec_agents.py` | same: the command is the last line; /app:build lists one command per repo below the table | |

## Non-goals

Respected (see spec).

## Notes and deviations

- Prompt rules, tested by their text; in the end-to-end run the agents already did this when told to — now it is the documented default.
- Built directly from the plan in the platform repo (no shape, so no `/svc:build` coder routing); tests written first and seen failing.
