---
spec_id: 063-acceptance-test-diff-looks-only-at-test
spec_hash: 89e9d26d3dfe
summary: cplat spec test-diff selects only files under the shape's test_globs, never docs
tasks:
- id: t1
  title: test-diff default selection limited to test_globs
  files: [scripts/cplat/spec.py, tests/cplat/test_spec.py]
  covers: [AC-063.1, AC-063.2, AC-063.3]
  parallel_safe: true
  depends_on: []
  done: true
- id: t2
  title: Build keeps stopping on a test-diff failure (contract test) and changelog
  files: [tests/cplat/test_spec_agents.py, docs/CHANGELOG.md]
  covers: [AC-063.4]
  parallel_safe: true
  depends_on: []
  done: true
---

## t1 — test-diff default selection limited to test_globs

**Files:** scripts/cplat/spec.py, tests/cplat/test_spec.py
**Covers:** AC-063.1, AC-063.2, AC-063.3
**Goal:** Only acceptance tests are compared; plan and spec documents never are.

**Implementation notes:**
- Filter `changed` by `test_globs(repo_shape(root))` (fnmatch with `**`, as `trace` does), then drop `docs/**` and `*.md`.

**Done when:** Tests in a temp git repo: only `plan.md` changed (`done: true`) → "no acceptance test changed", exit 0; a test under `tests/` with a changed assertion → exit 1; no `.platform-version` → `docs/` never selected.

## t2 — Build keeps stopping on a test-diff failure (contract test) and changelog

**Files:** tests/cplat/test_spec_agents.py, docs/CHANGELOG.md
**Covers:** AC-063.4
**Goal:** The stop rule can't silently disappear from `/svc:build`.

**Implementation notes:**
- Assert build.md contains `cplat spec test-diff` with "stop" in the same step, for Phase 2 and after the fan-out.
- CHANGELOG `[Unreleased]`.

**Done when:** Tests pass.
