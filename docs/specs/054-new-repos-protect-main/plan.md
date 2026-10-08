---
spec_id: 054-new-repos-protect-main
spec_hash: 570ac7a15b1e
summary: New repos protect main with their CI checks
tasks:
- id: t1
  title: Branch protection in new-service (and so new-app)
  files: [scripts/cplat/newsvc.py, shapes.yml, scripts/shapes.py]
  covers: [AC-054.1, AC-054.2]
  parallel_safe: true
  depends_on: []
- id: t2
  title: Tests with a faked gh
  files: [tests/cplat/test_newsvc.py]
  covers: [AC-054.1, AC-054.2]
  parallel_safe: false
  depends_on: [t1]
---

## t1 — Branch protection in new-service (and so new-app)

**Files:** scripts/cplat/newsvc.py, shapes.yml, scripts/shapes.py
**Covers:** AC-054.1, AC-054.2
**Goal:** After the first push, `gh api -X PUT repos/<slug>/branches/main/protection` with the shape's required checks (new `ci_checks` list per shape in shapes.yml), no review requirement; `[outward]` in the preview; on failure a warning with the manual command.

**Implementation notes:**
- shapes.py validates `ci_checks` against the template's ci.yml job names.

**Done when:** Code path present; preview lists the step.

## t2 — Tests with a faked gh

**Files:** tests/cplat/test_newsvc.py
**Covers:** AC-054.1, AC-054.2
**Goal:** The fake gh records the protection call with the shape's checks and `required_pull_request_reviews: null`; a 403 makes it warn and succeed.

**Implementation notes:**
- —

**Done when:** Tests pass.
