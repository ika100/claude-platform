---
spec_id: 027-plan-a-feature-across-repos
title: Plan a feature across repos
status: done
priority: P1
---

# 027 — Plan a feature across repos

## Stories

As a founder, I want `/app:build-feature <description>` in a gitops-app repo to plan the work in every affected repo.

## Acceptance criteria

- **AC-027.1** Writes `docs/plan/<slug>.md` with YAML (`plan_id`, `feature`, `gitops_app`, `status: draft`, `repos[]` with `id`, `shape`, `summary`, `arguments`, `depends_on`, `done`, plus `gitops_pin[]`), validated by `plan.py` (shape ids exist, dependencies resolve, no cycles; also part of `devbox run validate`).
- **AC-027.2** Includes a `## Contract` section so dependent repos (for example a backend and its UI) can start together.
- **AC-027.3** Plan-only: it opens no PRs outside the gitops-app repo and edits no component repo. It prints the per-repo `/svc:build-feature` hand-off commands.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P1 · **Source:** PRD C2, ADR-007, ADR-011 · **Code:** `plugins/app/agents/planner.md`, `templates/gitops-app/scripts/plan.py`

## Changelog

- 2026-10-08 migrated from STORY-027 in docs/backlog.md
