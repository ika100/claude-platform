---
spec_id: 041-templates-ship-the-spec-contract
title: Templates ship the spec contract
status: done
priority: P1
---

# 041 — Templates ship the spec contract

## Stories

As a founder, I want every new repo to start with `docs/specs/`, the rule in `CLAUDE.md` and a `spec-check` CI job, so that the workflow is the default everywhere.

## Acceptance criteria

- **AC-041.1** Every template seeds `docs/specs/README.md`, a backlog with the index markers, and `docs/specs/**` in `_skip_if_exists`.
- **AC-041.2** Every template's `CLAUDE.md` "Spec first" section names the new commands.
- **AC-041.3** A `spec-check` CI job (`specs` workflow, `devbox run spec-check`) runs `cplat spec ci` at the repo's platform version: every spec valid, every criterion of a building or done spec named by a test; it warns in this major (`SPEC_CHECK_STRICT=1` fails).
- **AC-041.4** `shapes.py check` and the template tests enforce all three.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P1 · **Depends on:** STORY-039 · **Code:** `templates/*/scripts/spec-check.sh`, `templates/*/.github/workflows/specs.yml`, `cplat spec ci`

## Changelog

- 2026-10-08 migrated from STORY-041 in docs/backlog.md
