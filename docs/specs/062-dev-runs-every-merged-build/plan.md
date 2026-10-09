---
spec_id: 062-dev-runs-every-merged-build
spec_hash: 599a38c05acc
summary: Service CI dispatches a pin to the gitops-app, which opens an auto-merging PR pinning dev to sha-<7>
tasks:
- id: t1
  title: gitops-app pin.py and the pin-dev workflow
  files: [templates/gitops-app/scripts/pin.py, templates/gitops-app/.github/workflows/pin-dev.yml, templates/gitops-app/devbox.json,
    tests/cplat/test_gitops.py]
  covers: [AC-062.1, AC-062.2, AC-062.6]
  parallel_safe: true
  depends_on: []
  done: true
- id: t2
  title: pin-dev job in the four deployable service templates
  files: [templates/service-python/.github/workflows/ci.yml, templates/service-java/.github/workflows/ci.yml, templates/service-go/.github/workflows/ci.yml,
    templates/web-nextjs/.github/workflows/ci.yml, scripts/shapes.py, tests/cplat/test_spec_driven.py]
  covers: [AC-062.1, AC-062.4]
  parallel_safe: true
  depends_on: []
  done: true
- id: t3
  title: new-service / new-app set up auto-merge and name the token step
  files: [scripts/cplat/newsvc.py, scripts/cplat/newapp.py, scripts/cplat/update.py, tests/cplat/test_newsvc.py, tests/cplat/test_newapp.py]
  covers: [AC-062.4]
  parallel_safe: true
  depends_on: []
  done: true
- id: t4
  title: status shows the intended pin and an open pin PR
  files: [scripts/cplat/status.py, tests/cplat/test_gitops.py]
  covers: [AC-062.3]
  parallel_safe: false
  depends_on: [t1]
  done: true
- id: t5
  title: ADR-027, docs, agents and commands describe dev following main
  files: [docs/adr/027-dev-follows-main-through-pin-prs.md, docs/adr/README.md, docs/USER-JOURNEY.md, docs/HOW-IT-WORKS.md,
    templates/gitops-app/CLAUDE.md.jinja, plugins/app/commands/build.md, plugins/svc/agents/deployment.md, plugins/web/agents/deployment.md,
    plugins/svc-java/agents/deployment.md, plugins/svc-go/agents/deployment.md, site/src/content/docs/concepts/environments.md,
    docs/CHANGELOG.md, tests/cplat/test_spec_agents.py]
  covers: [AC-062.5]
  parallel_safe: false
  depends_on: [t1, t2, t3, t4]
  done: true
---

## t1 — gitops-app pin.py and the pin-dev workflow

**Files:** templates/gitops-app/scripts/pin.py, templates/gitops-app/.github/workflows/pin-dev.yml, templates/gitops-app/devbox.json, tests/cplat/test_gitops.py
**Covers:** AC-062.1, AC-062.2, AC-062.6
**Goal:** A dispatched `{service, tag}` becomes an auto-merging PR that pins `dev`.

**Implementation notes:**
- `pin.py` as in design.md; `devbox run pin -- dev <svc> <tag>` recipe for humans.
- `pin-dev.yml`: payload validation, pin, `render.py --check`, branch, PR, close superseded pin PRs, `gh workflow run ci.yml --ref`, `gh pr merge --auto --squash`; Actions pinned by SHA (`pin-actions.py --check`).

**Done when:** Tests: pin.py sets the tag and refuses an unknown service, a wrong env and `latest`; a re-render keeps the pin; the workflow parses, triggers on `repository_dispatch: [pin-dev]`, declares the three permissions, and dispatches `ci.yml`.

## t2 — pin-dev job in the four deployable service templates

**Files:** the four `ci.yml`, scripts/shapes.py, tests/cplat/test_spec_driven.py
**Covers:** AC-062.1, AC-062.4
**Goal:** Every merge to a service's `main` asks its gitops-app to pin `dev`.

**Implementation notes:**
- Job `pin-dev` after `docker-publish`, main only; reads `.platform-app.yml`; notices for a missing file or token; Jinja escaping of `${{ }}`.
- shapes.py: deployable shapes' `ci.yml` has a `pin-dev` job that `needs: docker-publish`.

**Done when:** `shapes.py check` passes and fails on a fixture without the job; rendered workflows parse (existing smoke tests).

## t3 — new-service / new-app set up auto-merge and name the token step

**Files:** scripts/cplat/newsvc.py, scripts/cplat/newapp.py, scripts/cplat/update.py, tests/cplat/test_newsvc.py, tests/cplat/test_newapp.py
**Covers:** AC-062.4
**Goal:** A new product needs exactly one manual step, and it is printed.

**Implementation notes:**
- gitops-app repos: `allow_auto_merge` + Actions-may-create-PRs, with a warning and the command on failure (like `protection_cmd`).
- Deployable service with an app: next step with the token link and `gh secret set GITOPS_TOKEN -R …`; `new-app` prints one loop for all components; `update-service` adds the same step when `pin-dev` appears.

**Done when:** Tests on the planned `gh` commands and next steps (no network).

## t4 — status shows the intended pin and an open pin PR

**Files:** scripts/cplat/status.py, tests/cplat/test_gitops.py
**Covers:** AC-062.3
**Goal:** A pin that is merged but not healthy, or not merged yet, is visible.

**Implementation notes:**
- `pin PR` column from `gh pr list --head pin/dev-<svc>-` (best effort, `—` without gh).

**Done when:** Tests with faked `gh`/`kubectl` output: unhealthy row shows the tag and `Degraded`; open pin PR shown.

## t5 — ADR-027, docs, agents and commands describe dev following main

**Files:** see frontmatter
**Covers:** AC-062.5
**Goal:** Nothing claims `dev` tracks `latest` any more.

**Implementation notes:**
- ADR-027 (context: run 2 finding 3; options a/b/c; decision a; consequences: one token per service repo, auto-merge setting).
- Replace "dev tracks latest" wording; site pages synced from docs where they are copies, edited where they are not.
- Contract test: no "tracks latest" / "dev runs `latest`" in docs/, plugins/, templates/.

**Done when:** Test passes; links resolve; site builds.
