# ADR-024: Spec-driven bootstrap

**Status:** Accepted; the `--plan` flag, `STORY-NNN` stories and `docs/plan/` for single-repo plans are superseded by [ADR-026](026-feature-specs.md) (svc 3.0)
**Date:** 2026-10-07
**Builds on:** [ADR-008](008-shape-detection.md), [ADR-011](011-multi-repo-plan-format.md), [ADR-015](015-shape-registry-as-code.md)

## Context

The platform has the pieces of spec-driven development: the product-manager writes stories into `docs/backlog.md`, the architect writes a plan into `docs/plan/<slug>.md`, `/svc:plan-feature` produces both without code. The path between them was missing:

- `/shared:new-service` and `/shared:new-app` printed `/svc:build-feature` as the first step, so `plan-feature` was never suggested.
- `/svc:build-feature` always re-ran the product-manager and architect phases. Running `plan-feature` first meant planning twice and overwriting the reviewed plan; only the multi-repo `--from-plan` (ADR-011) consumed a finished plan.
- No template shipped `docs/backlog.md`, and only gitops-app shipped `docs/plan/`. Stories had no ids a plan or a PR could cite.
- The `CLAUDE.md` of the templates listed the workflows but did not say a feature starts with a plan.

## Decision

1. **Plan first in every bootstrap output.** For service, library and web shapes the *Next* steps start with `/svc:plan-feature "<description>"` followed by `/svc:build-feature --plan docs/plan/<slug>.md`; for gitops-app and `new-app` they start with `/app:build-feature` followed by `/app:run-plan`. Bootstrap stays a deterministic script: it prints the command with the description filled in and does not start an agent (planning needs the new repo as working directory).
2. **`/svc:build-feature --plan <path>`** builds a plan that was already produced and reviewed. Phases 1 and 2 are skipped. The plan must start with the YAML metadata block, its `shape` must equal the repo's shape and every id in `stories:` must exist in `docs/backlog.md`. The acceptance criteria of those stories drive testing and the PR; Phase 6 marks exactly those stories done. It excludes `--from-plan`. Without `--plan` the command is unchanged and writes the same artifacts.
3. **Stories and plans reference each other.** Stories are `#### STORY-NNN — <title>` (ids continue the highest in the file); plan metadata lists `stories: [STORY-NNN, …]`; the PR description names the story ids.
4. **Every template seeds the spec directories.** `docs/backlog.md` (format header, no stories) and `docs/plan/` are project-owned (`_skip_if_exists`). Existing repos do not get the files; they get the `CLAUDE.md` rule on their next `/shared:update-service`.
5. **Every template's `CLAUDE.md` has a "Spec first" section** with the rule. Quick tasks and bug fixes are exempt.
6. **The contract is enforced.** `shapes.py check` fails when a template lacks `docs/plan/`, the seeded `docs/backlog.md` (gitops-app needs only `docs/plan/`) or the "Spec first" section, so a future shape cannot skip them.

## Consequences

- The first feature of any new repo goes through a reviewable spec. The cost is one extra command before building; `/svc:build-feature` without `--plan` still works for people who want one step.
- Enforcement is by convention and contract, not by a gate. A hard CI check that PRs cite a story is deferred until this version has been used; a plan approval step (`status: approved`, refused when `draft`) follows as STORY-036.
- Plans edited after review can drift from their stories: validation checks that the stories exist, not that their criteria are unchanged.
- `svc` 2.2.0 (new flag, `stories:` metadata), `shared` 0.8.1 (next steps).

## Not included

A CI story check, the approval status, retrofitting stories into existing repos, and running `plan-feature` automatically from the bootstrap command.
