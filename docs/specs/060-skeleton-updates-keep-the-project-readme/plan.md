---
spec_id: 060-skeleton-updates-keep-the-project-readme
spec_hash: d509b4477cab
summary: README project-owned in every template; update merges devbox.json and reports what it kept and replaced
tasks:
- id: t1
  title: README.md project-owned in every template, enforced by shapes.py
  files: [templates/service-python/copier.yml, templates/library-python/copier.yml, templates/service-java/copier.yml, templates/service-go/copier.yml,
    templates/web-nextjs/copier.yml, templates/gitops-app/copier.yml, scripts/shapes.py, tests/cplat/test_spec_driven.py]
  covers: [AC-060.2, AC-060.3]
  parallel_safe: true
  depends_on: []
  done: false
- id: t2
  title: update.py merges devbox.json and reports README and recipes
  files: [scripts/cplat/update.py, tests/cplat/test_update_doctor.py]
  covers: [AC-060.1, AC-060.4, AC-060.5, AC-060.6, AC-060.7]
  parallel_safe: true
  depends_on: []
  done: false
- id: t3
  title: Command and docs describe what an update keeps
  files: [plugins/shared/commands/update-service.md, docs/ADOPTING.md, docs/CHANGELOG.md]
  covers: [AC-060.4, AC-060.7]
  parallel_safe: false
  depends_on: [t1, t2]
  done: false
---

## t1 — README.md project-owned in every template, enforced by shapes.py

**Files:** the six `copier.yml`, scripts/shapes.py, tests/cplat/test_spec_driven.py
**Covers:** AC-060.2, AC-060.3
**Goal:** New repos get the README; updates never touch it; a template that forgets is caught.

**Implementation notes:**
- Add `README.md` to `_skip_if_exists` in each template.
- shapes.py: `README.md` must be in `_skip_if_exists` (next to the existing `docs/specs/**` check).

**Done when:** `shapes.py check` fails on a fixture template without the entry; `copier copy` of each template still writes `README.md` (existing smoke tests).

## t2 — update.py merges devbox.json and reports README and recipes

**Files:** scripts/cplat/update.py, tests/cplat/test_update_doctor.py
**Covers:** AC-060.1, AC-060.4, AC-060.5, AC-060.6, AC-060.7
**Goal:** An update keeps project recipes and packages and the README, and says what it kept and replaced.

**Implementation notes:**
- `merge_devbox(project: dict, template: dict) -> tuple[dict, list[str], list[tuple[str, str]]]`, as in design.md.
- In `execute`: read `devbox.json` before Copier runs, merge it after, then build the report lines; README next step via `git diff --quiet <old> <new> -- templates/<t>/README.md.jinja`.
- Leave `devbox.json` out of `modified` unless something was replaced.

**Done when:** Unit tests for `merge_devbox` (kept script, kept package with version, replaced template script, `env`, invalid JSON); an update test on a rendered repo with a changed README and an extra recipe shows both untouched and reported.

## t3 — Command and docs describe what an update keeps

**Files:** plugins/shared/commands/update-service.md, docs/ADOPTING.md, docs/CHANGELOG.md
**Covers:** AC-060.4, AC-060.7
**Goal:** Users know that the README is theirs and how `devbox.json` is merged.

**Implementation notes:**
- update-service.md: relay the kept/replaced lines; the README is never updated.
- ADOPTING → skeleton updates: the merge table in short. CHANGELOG `[Unreleased]`.

**Done when:** Docs say it; links resolve.
