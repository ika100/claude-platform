# ADR-006: gitops-app overlay structure — env-only

**Status:** Accepted
**Date:** 2026-05-22

## Context

The new `gitops-app` shape needs an overlay layout under `applications/<name>/overlays/`. Options: env-only (`dev/staging/prod`), env+region nested (`dev/us-east/`, `dev/eu-west/`, …), or env-only with regions opt-in via Copier prompt.

## Decision

Use **env-only**: exactly three overlays — `overlays/dev/`, `overlays/staging/`, `overlays/prod/`.

## Rationale

- Matches every upstream Argo example and the existing platform-wide gitops repo.
- Simplest mental model; one promotion axis (`dev → staging → prod`).
- Multi-region is a real but separable problem — and a real multi-region design needs more than just folder nesting (e.g. shared vs region-specific resources, cross-region routing, failover semantics). Pre-building the folders without solving the rest is fake progress.

## Consequences

- `/gitops:promote` and `/gitops:compose` agents have a fixed three-overlay assumption.
- A product that genuinely needs multi-region today must fork the template; we treat it as a signal to revisit this ADR rather than accommodate two layouts in parallel.
- Revisit when: ≥1 SaaS product on the platform genuinely requires multi-region from day one, or when the platform-wide gitops repo itself adopts multi-region.

## References

- [platform-vision.md §11.5](../requirements/platform-vision.md)
