---
title: "Guard rails"
description: "The platform's own conventions as Kyverno policy, checked before merge and enforced in the cluster."
sidebar:
  order: 6
---

Opt in with `policies: {}` in `app.yaml`. The platform then renders a namespaced Kyverno policy per environment that encodes its conventions for every Deployment:

- numeric non-root user, read-only root filesystem, no privilege escalation, all capabilities dropped,
- no privileged containers, host namespaces or `hostPath` volumes,
- CPU and memory requests and a memory limit,
- the `app.kubernetes.io/part-of` label,
- images only from allowed registries (derived from your services' images, plus addon images and `policies.registries`),
- no `:latest` or untagged images outside dev.

**Modes per environment:** `Audit` (report), `Enforce` (deny) or `Off`; defaults are Audit in dev and staging, Enforce in production.

**Shift-left:** `devbox run validate` (and CI) build each overlay and evaluate it with the Kyverno CLI, so a violating change fails its pull request in every mode. Together with pinned CI actions, image scanning with an SBOM and least-privilege tokens this is the platform's [security posture](/claude-platform/scenarios/harden-for-audit/) ([ADR-019](/claude-platform/reference/adr/019/), [ADR-022](/claude-platform/reference/adr/022/)).
