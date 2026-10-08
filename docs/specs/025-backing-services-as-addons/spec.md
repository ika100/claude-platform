---
spec_id: 025-backing-services-as-addons
title: Backing services as addons
status: done
priority: P1
---

# 025 — Backing services as addons

## Stories

As a founder, I want to declare a database or observability once and use it by name.

## Acceptance criteria

- **AC-025.1** `/gitops:addon add|remove|list postgres|observability`; services opt in with `uses: [postgres]`.
- **AC-025.2** Postgres: a CloudNativePG cluster per environment where used; services receive `DATABASE_URL` and `PG*` from the operator's Secret.
- **AC-025.3** Removing an addon never deletes data (`prune: false`) and is refused while a service still uses it.
- **AC-025.4** Observability: an OpenTelemetry Collector per environment receives OTLP, scrapes each service's `metrics:` path, and exports OTLP/HTTP when `exportTo` is set; `ui: lgtm` adds Grafana, Tempo, Loki and Prometheus locally (dev only).

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P1 · **Source:** ADR-020, ADR-021 · **Code:** `scripts/cplat/addon.py`

## Changelog

- 2026-10-08 migrated from STORY-025 in docs/backlog.md
