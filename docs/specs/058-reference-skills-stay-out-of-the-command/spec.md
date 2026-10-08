---
spec_id: 058-reference-skills-stay-out-of-the-command
title: Reference skills stay out of the command list
status: building
priority: P2
---

# 058 — Reference skills stay out of the command list

## Problem

The `spec-format` skill is reference material for agents, but it appears in every session as a user command `/svc:spec-format`.

## Stories

As a contributor, I want the command list to contain only commands, so that I find the workflow steps quickly.

## Acceptance criteria

- **AC-058.1** Given a session with the svc plugin, when the user lists slash commands, then `/svc:spec-format` is not among them (its SKILL.md sets `user-invocable: false`).
- **AC-058.2** Given the product-manager, architect and reviewer, when they run, then they still read the spec-format references.

## Non-goals

- None.

## Open questions

- ~~Does skill frontmatter support hiding a skill from the user while keeping its files readable (for example `user-invocable: false`)? (suggested: check the docs; otherwise move the references out of `skills/`; affects AC-058.1)~~ Answered: yes: `user-invocable: false` in SKILL.md frontmatter (Claude Code skills docs); Claude can still use the skill.

## References

- [End-to-end run 2026-10-08, issue 16](../../e2e/2026-10-08-todo-spec-driven.md#issues-and-workarounds)

## Changelog

- 2026-10-08 created from issue 16 of the todo end-to-end run
- 2026-10-08 open question answered: yes: `user-invocable: false` in SKILL.md frontmatter (Claude Code skills docs); Claude can still use the skill.
- 2026-10-08 approved
- 2026-10-08 building
