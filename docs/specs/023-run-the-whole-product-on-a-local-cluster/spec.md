---
spec_id: 023-run-the-whole-product-on-a-local-cluster
title: Run the whole product on a local cluster
status: done
priority: P1
---

# 023 — Run the whole product on a local cluster

## Stories

As a founder, I want `devbox run cluster-up` to give me a working local environment.

## Acceptance criteria

- **AC-023.1** Creates a k3d cluster with ArgoCD, repo credentials (`REPO_TOKEN`, read-only) and a GHCR pull secret (`PULL_TOKEN`, `read:packages`), per-environment namespaces `<app>-<env>`, and the Traefik Gateway provider. ESO, CloudNativePG and Kyverno are installed only when the product uses them.
- **AC-023.2** Busy host ports (`LOCAL_HTTP_PORT`, `REGISTRY_PORT`) stop the script before anything is created, naming the holder and a free port; `LOCAL_HTTP_PORT=auto` picks one from 8088.
- **AC-023.3** `cluster-down` removes it; `devbox run cluster-ui` opens k9s on `<app>-dev`.
- **AC-023.4** A nightly end-to-end test renders a gitops-app, a Java service and a web app from the real templates, builds the images and verifies them in the cluster.

## Non-goals

## Open questions

## References

- Legacy metadata: **Status:** done · **Priority:** P1 · **Source:** CHANGELOG 1.1.1, 2.0.0, 3.1.0, 3.2.0 · **Code:** `templates/gitops-app/scripts/local-cluster.sh`

## Changelog

- 2026-10-08 migrated from STORY-023 in docs/backlog.md
