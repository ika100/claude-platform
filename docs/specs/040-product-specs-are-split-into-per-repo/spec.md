---
spec_id: 040-product-specs-are-split-into-per-repo
title: Product specs are split into per-repo specs
status: done
priority: P1
---

# 040 — Product specs are split into per-repo specs

## Stories

As a founder, I want `/app:spec`, `/app:plan`, `/app:build` and `/app:specs` to give each component repo its own slice of the product spec, so that every repo builds from criteria instead of a free-text prompt.

## Acceptance criteria

- **AC-040.1** The product plan lists per repo the criteria it implements (`acs:`) and the contract; `plan-check` fails when an active product criterion is assigned to no repo.
- **AC-040.2** `cplat spec new --from <product-spec> <repo-id>` writes the repo's `spec.md` with `parent:` set.
- **AC-040.3** `app` 1.0.0 replaces `build-feature`, `run-plan` and `plans`; ADR-011 is amended.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P1 · **Depends on:** STORY-039 · **Code:** `plugins/app/commands/`, `scripts/cplat/spec.py` (`--from-plan`), `templates/gitops-app/scripts/plan.py`

## Changelog

- 2026-10-08 migrated from STORY-040 in docs/backlog.md
