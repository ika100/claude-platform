---
spec_id: 007-a-shape-is-added-by-following-a
title: A shape is added by following a documented contract
status: done
priority: P1
---

# 007 — A shape is added by following a documented contract

## Stories

As a maintainer, I want adding a shape to be a checklist, so that Rust or Kotlin would not need a new PRD.

## Acceptance criteria

- **AC-007.1** A shape needs: a template with `copier.yml`, `CLAUDE.md` and the canonical devbox recipes; a plugin with at least `coder` and `tester`; a registry entry plus a sniff rule in `scripts/detect-shape.sh`.
- **AC-007.2** `shapes.py check` enforces each of these and fails the PR when one is missing.
- **AC-007.3** Java and Go are the worked examples in `docs/templates.md`.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P1 · **Source:** PRD §4.1/A3/D3, `docs/templates.md`

## Changelog

- 2026-10-08 migrated from STORY-007 in docs/backlog.md
