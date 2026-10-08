---
spec_id: 010-web-next-js-template
title: Web (Next.js) template
status: done
priority: P0
---

# 010 — Web (Next.js) template

## Stories

As a founder, I want a Next.js App Router starter that is ready for production.

## Acceptance criteria

- **AC-010.1** Next.js App Router only, TypeScript strict, pnpm with a pinned `packageManager`, a pinned Node LTS.
- **AC-010.2** Vitest and Testing Library by default; Playwright and `e2e/` only when `needs_e2e` is enabled.
- **AC-010.3** Serves `/api/health`, `/api/ready` and `/api/metrics` on port 3000, as numeric user 1000.
- **AC-010.4** Ships a designed starter UI (light/dark themes, header, hero) which `update-service` never adds to an existing app.
- **AC-010.5** `package.json` is project-owned.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Source:** ADR-002..005, CHANGELOG 2.2.0

## Changelog

- 2026-10-08 migrated from STORY-010 in docs/backlog.md
