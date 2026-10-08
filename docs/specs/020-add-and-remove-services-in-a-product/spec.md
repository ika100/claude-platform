---
spec_id: 020-add-and-remove-services-in-a-product
title: Add and remove services in a product
status: done
priority: P1
---

# 020 — Add and remove services in a product

## Stories

As a founder, I want `/gitops:compose add|remove <service...>` to edit `services.yaml` for me.

## Acceptance criteria

- **AC-020.1** Writes a complete entry using the shape's defaults from `shapes.yml`, renders the manifests and opens one PR.
- **AC-020.2** Validates that the service repo carries the `deployable-service` topic.
- **AC-020.3** New services start in `dev` only, tracking `latest`.
- **AC-020.4** Options: `--expose [host]`, `--env K=V`, `--replicas N`, `--generate S=K,K`, `--secret S=K,K`, `--uses postgres`, `--secret-ref NAME`, `--from-k8s` (seed from a v1 service), `--pr`.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P1 · **Source:** PRD B5, ADR-014 · **Code:** `scripts/cplat/compose.py`

## Changelog

- 2026-10-08 migrated from STORY-020 in docs/backlog.md
