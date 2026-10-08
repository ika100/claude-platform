---
spec_id: 038-agents-share-one-spec-format-and-stop
title: Agents share one spec format and stop guessing
status: done
priority: P0
---

# 038 — Agents share one spec format and stop guessing

## Stories

As a founder, I want the product-manager, architect, testers and a new reviewer to work from one format reference and to hand open questions back to me, so that specs are complete before they are approved.

## Acceptance criteria

- **AC-038.1** One format reference (the `spec-format` skill in the svc plugin, enabled in every repo; agents read it through `${CLAUDE_PLUGIN_ROOT}`, which only resolves inside the agent's own plugin) describes `spec.md`, `design.md`, `plan.md` and the per-shape test tagging; agents link to it instead of restating formats.
- **AC-038.2** The product-manager is shape-agnostic, writes `spec.md`, and returns unanswered questions in `## Open questions` instead of assuming.
- **AC-038.3** The architect writes `design.md` (with the contract) and `plan.md` with `covers` and `spec_hash`, and fixes every `cplat spec check` error before returning.
- **AC-038.4** Every tester (svc, web, svc-java, svc-go) has an acceptance mode that writes failing tests tagged with criterion ids before the code exists.
- **AC-038.5** A read-only `reviewer` agent compares the diff with the criteria, non-goals and plan and writes `verification.md`; `cplat shape` routes it.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Depends on:** STORY-037 · **Code:** `plugins/svc/skills/spec-format/`, `plugins/*/agents/`

## Changelog

- 2026-10-08 migrated from STORY-038 in docs/backlog.md
