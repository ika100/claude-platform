---
spec_id: 001-create-a-repo-of-any-shape-with-one
title: Create a repo of any shape with one command
status: done
priority: P0
---

# 001 — Create a repo of any shape with one command

## Stories

As a founder, I want `/shared:new-service <name> <description> [--type <shape>]` to create a working repo, so that I never copy boilerplate.

## Acceptance criteria

- **AC-001.1** Valid shapes are exactly the ids in `shapes.yml`: `service-python`, `library-python`, `web-nextjs`, `gitops-app`, `service-java`, `service-go`. An unknown shape lists the valid ones.
- **AC-001.2** No flag produces a `service-python` repo. `--library`, `--web` and `--gitops` are aliases for `--type`.
- **AC-001.3** A private GitHub repo is created, the template is rendered, and the first commit is pushed. Deployable shapes get the `deployable-service` topic; `library-python` and `gitops-app` do not.
- **AC-001.4** A dry-run preview shows what will happen (including PUBLIC or PRIVATE) before anything is created.
- **AC-001.5** The command ends with next steps and says how to undo.
- **AC-001.6** `--public` / `--visibility public` creates a public repo.
- **AC-001.7** `--data KEY=VALUE` sets template options at creation; keys are validated against the template's `copier.yml` and an unknown key lists the valid ones.
- **AC-001.8** `--app <org>/<gitops-repo>` links a service to its product's gitops-app (`.platform-app.yml`).
- **AC-001.9** Development can start on a feature branch immediately, without waiting for the bootstrap CI on `main`.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Source:** PRD A1/A2, ADR-001, ADR-015 · **Code:** `scripts/cplat/newsvc.py`

## Changelog

- 2026-10-08 migrated from STORY-001 in docs/backlog.md
