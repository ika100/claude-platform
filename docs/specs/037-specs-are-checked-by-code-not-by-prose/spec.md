---
spec_id: 037-specs-are-checked-by-code-not-by-prose
title: Specs are checked by code, not by prose
status: done
priority: P0
---

# 037 — Specs are checked by code, not by prose

## Stories

As a founder, I want every check and state change of a feature spec to be a tested `cplat spec` subcommand, so that commands and agents cannot skip or misread the rules.

## Acceptance criteria

- **AC-037.1** `cplat spec new <title>` creates `docs/specs/<NNN>-<slug>/spec.md` as `draft`; the number continues the highest spec or legacy `STORY-NNN` id; the repo's shape is recorded when it has one.
- **AC-037.2** `cplat spec check [--require STATUS]` validates spec front matter, criterion ids (`AC-<NNN>.<n>`, unique, of this spec), the repo's shape, and, when `plan.md` exists: every active criterion covered by a task, no withdrawn or unknown criterion covered, no dependency cycle, no shared file between parallel-safe tasks of one level, and `spec_hash` equal to the current criteria.
- **AC-037.3** `cplat spec approve` refuses a spec with open questions or without criteria; other transitions go through `set-status` and are restricted (`approved → building → done`, back to `draft` to amend, `superseded` from anywhere).
- **AC-037.4** `cplat spec trace` lists, per active criterion, the test files that name it (`AC-007.1` never matches `AC-007.10`), using `test_globs` from `shapes.yml`, and exits 1 when one is missing.
- **AC-037.5** `cplat spec index` regenerates the table between the spec-index markers in `docs/backlog.md` and keeps the rest; `cplat spec list` shows status, criteria, open questions, task progress and the next command.
- **AC-037.6** `cplat spec migrate` converts legacy `STORY-NNN` stories (both heading styles) into spec folders with numbered criteria, keeps legacy metadata and plan links, removes headings left empty and keeps every other section; without `--write` it writes nothing.
- **AC-037.7** Every shape in `shapes.yml` declares `test_globs`; `shapes.py check` fails without it.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Source:** user request 2026-10-08 · **ADR:** [026](../../adr/026-feature-specs.md) · **Code:** `scripts/cplat/spec.py`

## Changelog

- 2026-10-08 migrated from STORY-037 in docs/backlog.md
