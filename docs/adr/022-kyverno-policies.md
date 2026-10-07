# ADR-022: Kyverno guard rails, checked before merge and enforced in the cluster

**Status:** Accepted
**Date:** 2026-10-07
**Builds on:** ADR-017 (the GitOps repo generates every manifest), ADR-020/021 (addons)

## Context

`render.py` produces hardened manifests (non-root numeric user, read-only filesystem, dropped capabilities, resource limits), but nothing stops a hand-edited manifest, a third-party chart or a mistaken `services.yaml` from deploying something weaker, and nothing says so before merge. We want the platform's own conventions to be policy.

## Decision

1. **Opt-in per application.** A `policies:` section in `app.yaml` renders one Kyverno policy per environment (`policies: {}` = defaults). It is opt-in because it makes Kyverno a cluster prerequisite; existing repos that update their template are unaffected.
2. **CEL-based `NamespacedValidatingPolicy`** (`policies.kyverno.io/v1`), not the classic `Policy`: Kyverno 1.19 marks `kyverno.io/v1 Policy` deprecated and recommends the CEL types (verified on a live cluster). The policy lives in the environment's namespace (`<app>-<env>`), so several products can share a cluster, and targets Deployments only (the manifests we render; operator-managed pods such as the database are out of scope).
3. **Rules** (the platform's conventions): numeric non-root user, `readOnlyRootFilesystem`, no privilege escalation and all capabilities dropped, no privileged containers / host namespaces / `hostPath`, CPU and memory requests plus a memory limit, the `app.kubernetes.io/part-of` label, images only from allowed registries, and no `:latest` or untagged image outside dev. Allowed registries are derived from the services' own `image` fields, plus the addon images (`otel/` for the collector) and `policies.registries`.
4. **Mode per environment**: `Audit` (report), `Enforce` (deny) or `Off`; defaults Audit in dev and staging, Enforce in prod. Synced by `<app>-policies-<env>` ApplicationSets (pruned).
5. **Shift-left**: `devbox run validate` (and CI) runs `scripts/check-policies.sh`: every service overlay and addon of an environment is built with kustomize and evaluated offline with the Kyverno CLI (`kyverno@1.19.0` in devbox). A violation fails the pull request in **every** mode, so Audit environments do not accumulate violations. Because the check evaluates the kustomize output, an environment that still runs `:latest` after `compose` fails until `/gitops:promote` pins a tag.
6. **Operator**: `cluster-up` installs Kyverno (chart 3.9.1) when `policies:` is present; real clusters install it themselves. `doctor` checks for the CRDs.

## Not included

Policies for pods created by operators (CloudNativePG), image signature verification (revisit with signing, ADR-019), mutating/generating policies, exceptions management and a `PolicyReport` summary in `cplat status`.
