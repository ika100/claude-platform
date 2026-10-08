---
spec_id: 030-hardened-ci-in-every-generated-repo
title: Hardened CI in every generated repo
status: done
priority: P0
---

# 030 — Hardened CI in every generated repo

## Stories

As a founder, I want generated CI to be safe and to publish usable images.

## Acceptance criteria

- **AC-030.1** The workflow triggers on pushes to `main`, which publish `latest` and `sha-*` images; version tags publish semver images.
- **AC-030.2** Images are native multi-arch (amd64 and arm64) merged into one manifest; the Trivy scan on each architecture uses `TRIVY_PLATFORM`.
- **AC-030.3** All Actions are pinned by commit SHA (`scripts/pin-actions.py --check`); workflows use `permissions: contents: read` with `packages: write` only on image jobs.
- **AC-030.4** Trivy blocks fixable HIGH/CRITICAL on `v*.*.*` releases and reports on `main`; a CycloneDX SBOM is kept for 90 days.
- **AC-030.5** Dockerfiles run as a numeric non-root user and carry the `org.opencontainers.image.source` label.
- **AC-030.6** Superseded PR runs are cancelled; a PR title edit re-runs the title check without cancelling a running build; Dependabot is monthly and grouped.
- **AC-030.7** `actionlint` runs over the platform's and the templates' workflows.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Source:** ADR-019, CHANGELOG 1.1.1, 2.0.0, 2.1.0, 3.0.3

## Changelog

- 2026-10-08 migrated from STORY-030 in docs/backlog.md
