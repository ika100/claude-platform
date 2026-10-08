---
spec_id: 055-template-action-pins-match-the-platform
spec_hash: 6188ca7c7758
summary: One pin per action across platform and templates
tasks:
- id: t1
  title: pin-actions --check enforces one SHA per action
  files: [scripts/pin-actions.py]
  covers: [AC-055.1]
  parallel_safe: true
  depends_on: []
- id: t2
  title: Align the template pins and update them together
  files: [templates/service-python/.github/workflows/ci.yml, templates/library-python/.github/workflows/ci.yml, templates/web-nextjs/.github/workflows/ci.yml,
    templates/service-java/.github/workflows/ci.yml, templates/service-go/.github/workflows/ci.yml, templates/gitops-app/.github/workflows/ci.yml,
    .github/dependabot.yml]
  covers: [AC-055.1, AC-055.2]
  parallel_safe: false
  depends_on: [t1]
- id: t3
  title: Test
  files: [tests/cplat/test_workflows.py]
  covers: [AC-055.1]
  parallel_safe: true
  depends_on: [t1]
---

## t1 — pin-actions --check enforces one SHA per action

**Files:** scripts/pin-actions.py
**Covers:** AC-055.1
**Goal:** `--check` collects `owner/repo@sha` from `.github/workflows` and every `templates/*/.github/workflows`, and fails when an action has more than one SHA.

**Implementation notes:**
- —

**Done when:** Running it on today's tree reports actions/checkout v5 vs v7.

## t2 — Align the template pins and update them together

**Files:** templates/service-python/.github/workflows/ci.yml, templates/library-python/.github/workflows/ci.yml, templates/web-nextjs/.github/workflows/ci.yml, templates/service-java/.github/workflows/ci.yml, templates/service-go/.github/workflows/ci.yml, templates/gitops-app/.github/workflows/ci.yml, .github/dependabot.yml
**Covers:** AC-055.1, AC-055.2
**Goal:** Templates use the platform's SHAs; the platform's Dependabot config groups actions updates for `/` and `/templates/*` so one PR updates all.

**Implementation notes:**
- —

**Done when:** `pin-actions.py --check` passes.

## t3 — Test

**Files:** tests/cplat/test_workflows.py
**Covers:** AC-055.1
**Goal:** A test runs the check over the repo and over a fixture with two SHAs.

**Implementation notes:**
- —

**Done when:** Tests pass.
