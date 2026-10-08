---
spec_id: 002-generated-repos-enable-their-plugins
title: Generated repos enable their plugins automatically
status: done
priority: P0
---

# 002 — Generated repos enable their plugins automatically

## Stories

As a founder, I want a new repo's first Claude Code session to have the right plugins enabled, so that `/svc:*` commands work immediately.

## Acceptance criteria

- **AC-002.1** Each template's `.claude/settings.json` enables the plugin(s) for its shape and carries the committed permission allowlist (no prompts for `devbox run`, read-only git, feature-branch pushes; prompts for anything remote-destructive).
- **AC-002.2** `shapes.py check` fails if a template does not enable its shape's plugin.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Source:** ADR-013

## Changelog

- 2026-10-08 migrated from STORY-002 in docs/backlog.md
