---
spec_id: 048-acceptance-tests-may-be-reformatted
spec_hash: 3a285768cd1b
summary: Acceptance tests may be reformatted, checked by `cplat spec test-diff`
tasks:
- id: t1
  title: Add `cplat spec test-diff`
  files: [scripts/cplat/spec.py, tests/cplat/test_spec.py]
  covers: [AC-048.2, AC-048.3]
  parallel_safe: true
  depends_on: []
- id: t2
  title: Build runs lint-fix on acceptance tests and checks them
  files: [plugins/svc/commands/build.md, plugins/svc/skills/spec-format/references/testing.md, plugins/svc/agents/coder.md,
    plugins/web/agents/coder.md, plugins/svc-java/agents/coder.md, plugins/svc-go/agents/coder.md]
  covers: [AC-048.1, AC-048.2]
  parallel_safe: false
  depends_on: [t1]
- id: t3
  title: Contract tests
  files: [tests/cplat/test_spec_agents.py]
  covers: [AC-048.1, AC-048.2]
  parallel_safe: false
  depends_on: [t2]
---

## t1 — Add `cplat spec test-diff`

**Files:** scripts/cplat/spec.py, tests/cplat/test_spec.py
**Covers:** AC-048.2, AC-048.3
**Goal:** A deterministic check that a test file changed only in formatting since a base commit.

**Implementation notes:**
- `cplat spec test-diff <base-ref> [files…]` (default: files naming a criterion of building specs); per design.md: Python via `tokenize` without NL/COMMENT-whitespace and with import blocks sorted, others with all whitespace removed.
- Exit 0 and `formatting only` per file, exit 1 with the first differing token otherwise.

**Done when:** Tests: reflowed Python call passes, sorted imports pass, changed literal fails, removed test fails, changed criterion id fails, TS whitespace change passes.

## t2 — Build runs lint-fix on acceptance tests and checks them

**Files:** plugins/svc/commands/build.md, plugins/svc/skills/spec-format/references/testing.md, plugins/svc/agents/coder.md, plugins/web/agents/coder.md, plugins/svc-java/agents/coder.md, plugins/svc-go/agents/coder.md
**Covers:** AC-048.1, AC-048.2
**Goal:** Formatting of acceptance tests is allowed; anything else stops the build.

**Implementation notes:**
- Phase 2/3: after `lint-fix`, run `cplat spec test-diff <phase-1 commit>`; failure → stop and ask.
- Coder rule and testing.md: 'never edit, skip or weaken' stays; formatting through lint-fix is allowed.

**Done when:** Command and agents state the rule.

## t3 — Contract tests

**Files:** tests/cplat/test_spec_agents.py
**Covers:** AC-048.1, AC-048.2
**Goal:** Guard the rule in the build and the coders.

**Implementation notes:**
- Assert `spec test-diff` in build.md and the formatting allowance in every coder.

**Done when:** Tests pass.
