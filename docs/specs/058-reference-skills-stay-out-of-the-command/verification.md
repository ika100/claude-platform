# Verification — 058-reference-skills-stay-out-of-the-command Reference skills stay out of the command list

**Result:** pass
**Commit:** 2b1d6bd · **Base:** 8621fd2 · **Trace:** 2/2 criteria named by tests · **Suite:** `tests/cplat` green (slow render tests included)

| Criterion | Verdict | Tests | Implementation | Notes |
|---|---|---|---|---|
| AC-058.1 | met | `tests/cplat/test_spec_agents.py` | plugins/svc/skills/spec-format/SKILL.md `user-invocable: false` | |
| AC-058.2 | met | `tests/cplat/test_spec_agents.py` | agents' ${CLAUDE_PLUGIN_ROOT} reference paths unchanged | |

## Non-goals

Respected (see spec).

## Notes and deviations

- AC-058.1 rests on the frontmatter and the Claude Code docs (`user-invocable: false` hides a skill from the `/` menu). A headless session still lists `/svc:spec-format` when asked, because Claude itself may still use the skill; the user's menu cannot be inspected headless.
- Built directly from the plan in the platform repo (no shape, so no `/svc:build` coder routing); tests written first and seen failing.
