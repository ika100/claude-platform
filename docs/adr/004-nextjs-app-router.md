# ADR-004: Next.js router — App Router only

**Status:** Accepted
**Date:** 2026-05-22

## Context

Next.js ships two routing models: the legacy Pages Router and the modern App Router (RSC-first, layouts, streaming).

## Decision

The `web-nextjs` template scaffolds **App Router only**. Pages Router is not supported by the template or by web-shape agents.

## Rationale

- New Vercel/Next.js documentation assumes App Router; learning materials are App-Router-first in 2026.
- Pages Router is in maintenance mode upstream.
- Supporting both routers in a single template forces the web `coder` agent to handle two mental models, roughly doubling its surface area.

## Consequences

- Agents always read/write `app/` directory layouts (`app/page.tsx`, `app/layout.tsx`, `app/api/<route>/route.ts`).
- Existing Pages-Router repos cannot adopt this template wholesale; they'd need a migration (manual, not platform-supported).
- API routes use the App Router `route.ts` handler convention; health/ready/metrics endpoints live at `app/api/{health,ready,metrics}/route.ts`.

## References

- [platform-vision.md §11.3](../requirements/platform-vision.md)
