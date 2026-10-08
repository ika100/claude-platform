---
spec_id: 019-the-gitops-app-repo-owns-every
title: The gitops-app repo owns every Kubernetes manifest
status: done
priority: P0
---

# 019 — The gitops-app repo owns every Kubernetes manifest

## Stories

As a founder, I want one repo per product that declares its services and renders their manifests, so that services only ship an image.

## Acceptance criteria

- **AC-019.1** `services.yaml` entries (port, probes, user, volumes, env, secretRefs, replicas, resources, expose, environments) render `deployment.yaml`, `service.yaml`, `httproute.yaml` and `kustomization.yaml` per environment under `applications/<app>/overlays/{dev,staging,prod}/`; rendered output is checked in CI (`devbox run validate`).
- **AC-019.2** Env-only overlays (no regions). A root Argo Application (app-of-apps) is generated; after one human `devbox run bootstrap` per cluster, all changes deploy through merged PRs.
- **AC-019.3** `bootstrap` requires an explicit `KUBE_CONTEXT`.
- **AC-019.4** Optional Gateway API exposure per service with per-environment hostname templates (dev default `{service}.{app}-dev.localhost`).

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P0 · **Source:** ADR-006, ADR-014, ADR-017 · **Code:** `templates/gitops-app/scripts/render.py`

## Changelog

- 2026-10-08 migrated from STORY-019 in docs/backlog.md
