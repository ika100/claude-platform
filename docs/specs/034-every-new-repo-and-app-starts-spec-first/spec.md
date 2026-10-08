---
spec_id: 034-every-new-repo-and-app-starts-spec-first
title: Every new repo and app starts spec-first
status: done
priority: P0
---

# 034 — Every new repo and app starts spec-first

## Stories

As a founder, I want creating a service, library, web app or whole product to lead into `plan-feature` and then `build-feature`, so that every feature has a reviewed story and plan before code, and the repo always holds the artifacts (`docs/backlog.md`, `docs/plan/<slug>.md`) that tie the code to its spec.

## Acceptance criteria

- **AC-034.1** The *Next* steps of `/shared:new-service` (service-python, service-java, service-go, web-nextjs, library-python) name `/svc:plan-feature "<the repo's description>"` as the first step, followed by `/svc:build-feature --plan docs/plan/<slug>.md`. For gitops-app they name `/app:build-feature`. No bootstrap output suggests `/svc:build-feature` without a plan as the first step.
- **AC-034.2** The *Next* steps of `/shared:new-app` name `/app:build-feature "<first product feature>"` in the gitops-app repo, then `/app:run-plan <slug>`; each component's own first feature follows from that plan via `--from-plan`.
- **AC-034.3** Every template ships a `docs/backlog.md` skeleton (story format, no stories) and a `docs/plan/` directory (gitops-app already has one). Both are project-owned: `/shared:update-service` never overwrites them and never adds them to an existing repo.
- **AC-034.4** Every template's `CLAUDE.md` states the rule: a feature starts with `/svc:plan-feature` (or `/app:build-feature`), is built from the approved plan, and its PR cites the story ids. Small changes stay on `/svc:quick-task` and bugs on `/svc:fix-bug`.
- **AC-034.5** `/svc:plan-feature` ends by printing `/svc:build-feature --plan docs/plan/<slug>.md`. Plans and stories reference each other: stories have ids (`STORY-NNN`), the plan's metadata lists `stories: [STORY-NNN, …]`.
- **AC-034.6** `/svc:build-feature --plan <path>` skips the product-manager and architect phases, validates the plan (YAML block, `shape` equals the repo's shape, referenced stories exist), takes the acceptance criteria from those stories, and builds. Phase 6 marks those stories done and the PR description lists them. Without `--plan` the command behaves as today and still writes the same artifacts.
- **AC-034.7** The platform's add-a-shape contract requires the seed `docs/backlog.md` and the `CLAUDE.md` rule; `shapes.py check` fails when a template lacks them.
- **AC-034.8** Tests cover the bootstrap output of each shape, the templates' seed files and rule, and the plan validation of `--plan`.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Source:** user request 2026-10-07 · **Plan:** [plan/spec-driven-bootstrap.md](../../plan/spec-driven-bootstrap.md) · **ADR:** [024](../../adr/024-spec-driven-bootstrap.md)

## Changelog

- 2026-10-08 migrated from STORY-034 in docs/backlog.md
