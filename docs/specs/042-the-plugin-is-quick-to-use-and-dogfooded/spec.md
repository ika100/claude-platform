---
spec_id: 042-the-plugin-is-quick-to-use-and-dogfooded
title: The plugin is quick to use and dogfooded
status: done
priority: P1
---

# 042 — The plugin is quick to use and dogfooded

## Stories

As a contributor, I want commands to run the `cplat` version that matches my plugins without a network fetch, to tell me the next step, and the platform to use its own spec workflow, so that the plugin is fast, predictable and proven.

## Acceptance criteria

- **AC-042.1** Commands call `cplat` (the shared plugin's `bin/`), which runs the platform from a local checkout, an explicit ref, the plugin's own repo or the installed marketplace checkout (offline, the version the plugins came from), and fetches `main` only when none exists; `/shared:doctor` reports which one.
- **AC-042.2** `/svc:specs` and every stop of `/svc:build` print the next command.
- **AC-042.3** This repo's backlog is migrated with `cplat spec migrate`, and platform changes start with `/svc:spec`.
- **AC-042.4** `docs/AGENTS.md`, `docs/USER-JOURNEY.md`, `docs/HOW-IT-WORKS.md` and the plugin READMEs describe the new flow; the drift found in the review is fixed (product-manager model, non-existent gitops agents, heading styles).

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P1 · **Depends on:** STORY-039 · **Code:** `plugins/shared/bin/cplat`, `cplat doctor`

## Changelog

- 2026-10-08 migrated from STORY-042 in docs/backlog.md
