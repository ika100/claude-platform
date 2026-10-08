---
spec_id: 006-six-supported-shapes-registered-as-code
title: Six supported shapes, registered as code
status: done
priority: P0
---

# 006 — Six supported shapes, registered as code

## Stories

As a maintainer, I want one machine-readable registry of shapes, so that docs, templates, plugins and detection cannot drift apart.

## Acceptance criteria

- **AC-006.1** `shapes.yml` has one entry per shape with plugin, template, `deployable`, `library`, detection rules, default stack, runtime (port, probes, metrics path, user, volumes, resources) and status.
- **AC-006.2** `scripts/shapes.py check` (in CI) verifies the registry against templates, plugins, the PRD §4 table and the ADR index.
- **AC-006.3** Deployable service templates ship no `k8s/` directory (ADR-017).

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Source:** PRD §4, ADR-015, ADR-009, ADR-010 · **Code:** `shapes.yml`, `scripts/shapes.py`

## Changelog

- 2026-10-08 migrated from STORY-006 in docs/backlog.md
