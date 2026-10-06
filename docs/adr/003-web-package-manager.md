# ADR-003: Web package manager — pnpm

**Status:** Accepted
**Date:** 2026-05-22

## Context

The `web-nextjs` shape needs a default package manager. Options: npm, pnpm, bun.

## Decision

Use **pnpm**. Pinned via `packageManager` field in `package.json` and the corresponding Corepack-compatible version, with a `devbox run install` recipe wrapping `pnpm install --frozen-lockfile`.

## Rationale

- Strict lockfile + content-addressed store: fast CI installs, no phantom dependencies.
- Workspace support is first-class — useful if we ever move to a monorepo without changing tools.
- Mature, broadly adopted in serious TS projects in 2026.
- npm: slower CI, looser hoisting (phantom-deps bugs). Bun: faster but still ecosystem-young; some Next.js features assume Node at runtime.

## Consequences

- Web agents always run `devbox run install` / `devbox run dev` / `devbox run test`, never raw `pnpm`.
- Dockerfile uses `corepack enable && corepack prepare pnpm@<version> --activate` in the build stage.
- Consumers can override by editing `devbox.json` recipes, but the template default is pnpm.

## References

- [platform-vision.md §11.2](../requirements/platform-vision.md)
