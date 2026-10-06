# ADR-002: Web testing stack — Vitest + Playwright opt-in

**Status:** Accepted
**Date:** 2026-05-22

## Context

The `web-nextjs` shape needs a testing stack. Options considered: Vitest only, Vitest + Playwright opt-in, Jest + Playwright.

## Decision

Vitest is on by default for unit and component tests. The `web-nextjs` Copier template includes a `needs_e2e?` prompt — when `true`, an `e2e/` directory with a Playwright scaffold is generated plus a `devbox run e2e` recipe.

## Rationale

- Vitest is the modern default for TS/ESM projects: faster than Jest, native TS, native ESM, Vite-aligned.
- Playwright is the right e2e tool but adds CI weight (browser downloads, flakiness budget). Making it opt-in keeps simple repos lean.
- A single Copier prompt is a cheaper UX than asking every team to bolt Playwright on later.

## Consequences

- The web `tester` agent handles both `vitest` and (when present) `playwright` — must inspect the repo to know which to run.
- CI workflow template has two jobs: `test` (always) and `e2e` (conditional on `e2e/` existing).
- Trade-off: a repo that initially opted out can `copier update --data needs_e2e=true` to add Playwright later.

## References

- [platform-vision.md §11.1](../requirements/platform-vision.md)
