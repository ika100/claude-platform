---
spec_id: 059-security-scans-are-quiet-and-the-base
spec_hash: 3102bc09782a
summary: Quiet secrets scan; base-image findings summarised
tasks:
- id: t1
  title: Regenerate the web template's secrets baseline
  files: [templates/web-nextjs/.secrets.baseline.json, tests/cplat/test_ci_templates.py]
  covers: [AC-059.1]
  parallel_safe: true
  depends_on: []
  done: true
- id: t2
  title: Security agent summarises unfixable base-image findings
  files: [plugins/shared/agents/security.md, tests/cplat/test_spec_agents.py]
  covers: [AC-059.2]
  parallel_safe: true
  depends_on: []
  done: true
---

## t1 — Regenerate the web template's secrets baseline

**Files:** templates/web-nextjs/.secrets.baseline.json, tests/cplat/test_ci_templates.py
**Covers:** AC-059.1
**Goal:** The baseline lists detect-secrets' default plugins, so the hook scans; check every template's baseline has non-empty `plugins_used`.

**Implementation notes:**
- —

**Done when:** Test fails on an empty `plugins_used`; rendered web repo's `devbox run secrets-scan` prints no 'No plugins' line.

## t2 — Security agent summarises unfixable base-image findings

**Files:** plugins/shared/agents/security.md, tests/cplat/test_spec_agents.py
**Covers:** AC-059.2
**Goal:** Report HIGH/CRITICAL without a fixed version as one line: base image, count, 'no fix released'; fixable findings listed separately.

**Implementation notes:**
- —

**Done when:** Agent text and a contract test.
