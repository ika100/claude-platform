---
spec_id: 057-spec-check-says-what-happened
spec_hash: 105071cd45c8
summary: spec-check messages
tasks:
- id: t1
  title: Clear messages in spec-check.sh
  files: [templates/service-python/scripts/spec-check.sh, templates/library-python/scripts/spec-check.sh, templates/web-nextjs/scripts/spec-check.sh,
    templates/service-java/scripts/spec-check.sh, templates/service-go/scripts/spec-check.sh, templates/gitops-app/scripts/spec-check.sh,
    tests/cplat/test_spec_driven.py]
  covers: [AC-057.1, AC-057.2]
  parallel_safe: true
  depends_on: []
  done: true
---

## t1 — Clear messages in spec-check.sh

**Files:** templates/service-python/scripts/spec-check.sh, templates/library-python/scripts/spec-check.sh, templates/web-nextjs/scripts/spec-check.sh, templates/service-java/scripts/spec-check.sh, templates/service-go/scripts/spec-check.sh, templates/gitops-app/scripts/spec-check.sh, tests/cplat/test_spec_driven.py
**Covers:** AC-057.1, AC-057.2
**Goal:** Branch on the ref: `main` without spec checks → 'the platform has no spec checks yet; skipped'; a tag → 'platform <tag> predates spec checks; using main'.

**Implementation notes:**
- The six copies stay identical (existing test).

**Done when:** Script test covers both messages.
