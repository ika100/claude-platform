# ADR-026: Feature specs drive the build

**Status:** Accepted (S1, the `cplat spec` core, is built; S2–S6 follow, see [STORY-037](../backlog.md) to STORY-042)
**Date:** 2026-10-08
**Builds on:** [ADR-024](024-spec-driven-bootstrap.md), [ADR-011](011-multi-repo-plan-format.md), [ADR-015](015-shape-registry-as-code.md)
**Supersedes, when S3 ships:** the `--plan` flag of ADR-024 and the single-repo half of STORY-036

## Context

ADR-024 put a plan before the build, but the spec still does not drive the build:

- A spec has no home. Stories accumulate in one `docs/backlog.md`; a feature's behaviour is never described in one place that changes with the feature.
- Acceptance criteria are free-text checkboxes. A test, a task or a review cannot cite them, and nothing proves that each one is covered.
- Tests are written after the code (`build-feature` Phase 4), so coders have no executable definition of done.
- Plan validation (`--plan`) is prose the LLM follows; only gitops-app has a deterministic checker.
- No approval gate exists (STORY-036), and a spec edited after planning goes unnoticed.
- Subagents cannot ask the user, so the product-manager guesses instead of asking.

## Decision

1. **One folder per feature:** `docs/specs/<NNN>-<slug>/` holds `spec.md` (problem, stories, acceptance criteria, non-goals, open questions, changelog), optional `design.md` (decisions, contract), `plan.md` (tasks) and `verification.md` (result of the verify step). `docs/backlog.md` keeps a table generated between `<!-- spec-index:start/end -->` markers; the text around it stays hand-written.
2. **Criteria have ids:** `- **AC-<NNN>.<n>** Given …, when …, then …`. Ids are never reused or renumbered; a withdrawn criterion stays, struck through (`~~**AC-007.3**~~ reason`). The spec number replaces `STORY-NNN` and continues its numbering.
3. **Lifecycle:** `draft → approved → building → done`, and `superseded`. Only `cplat spec approve` moves `draft → approved`, and it refuses while an open question is unanswered or no criterion exists. An amendment moves a spec back to `draft`.
4. **Plans cite criteria:** each task has `covers: [AC-…]`; every active criterion is covered; `spec_hash` records the criteria the plan was made from, and a changed spec fails the check until it is re-planned. Tasks carry `done` so a build can resume.
5. **Tests cite criteria:** every active criterion appears in at least one test (name or comment). The test locations come from `test_globs` in `shapes.yml`, so the trace is the same for every language. The build writes these tests first, from the spec, and they must fail before any code is written.
6. **All of it is `cplat spec`:** `new`, `check [--require STATUS]`, `approve`, `set-status`, `task-done`, `hash`, `trace`, `index`, `list`, `migrate`. Commands and agents call it; they never validate specs in prose.
7. **Commands are renamed in a new major** (`svc` 3.0, `app` 1.0): `/svc:spec`, `/svc:plan`, `/svc:build`, `/svc:verify`, `/svc:specs` and the same verbs under `/app:`. Quick tasks and bug fixes stay spec-free but update a spec whose criteria they change.

## Consequences

- Every criterion is traceable from the spec to a task, a test and the PR, and the checks are deterministic and tested.
- More files per feature, and a migration for existing repos: `cplat spec migrate` converts `STORY-NNN` stories, keeping their numbers and every non-story section of the backlog. It is opt-in and shows what it would do first.
- The plan format is a superset of today's single-repo plan (`covers`, `spec_hash`, `done` added); `templates/gitops-app/scripts/plan.py` stays self-contained because it ships into generated repos.
- The renamed commands are a breaking change; `docs/CHANGELOG.md` maps old to new. There are no aliases (CLAUDE.md: no backwards-compat hacks).

## Not included

A required CI gate on traced criteria (it warns first; it becomes required in the next major), test results as evidence (the trace proves a test exists; the build proves it passes), and cross-repo criteria tracing beyond the per-repo spec slice.
