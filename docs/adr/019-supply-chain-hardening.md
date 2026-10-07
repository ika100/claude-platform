# ADR-019: Supply-chain hardening for generated repos

**Status:** Accepted
**Date:** 2026-10-07

## Decision

1. **Actions are pinned by commit SHA** (`uses: owner/repo@<40 hex> # vX`) in the platform's own workflows and in every generated repo. A mutable tag such as `@v4` lets a compromised upstream release run in our CI with our tokens. `scripts/pin-actions.py` resolves and rewrites pins; `--check` is a CI guard on the platform. Dependabot's `github-actions` ecosystem (now configured in every generated repo and in the platform) keeps the SHAs current and understands the version comment.
2. **Least-privilege tokens**: every workflow declares `permissions: contents: read` at top level; only the image jobs add `packages: write`. `--check` fails on a workflow without it.
3. **Images are scanned and carry an SBOM**: after pushing each architecture by digest, Trivy scans it for fixable HIGH/CRITICAL findings. Release builds (`v*.*.*` tags) fail on findings; main builds only report them, so a fresh CVE never blocks day-to-day work but never reaches a release unnoticed. A CycloneDX SBOM per architecture is kept as a workflow artifact for 90 days. Tags are applied only in the later manifest job, so a failed scan publishes no usable tag.
4. **Cluster credentials are split**: `cluster-up` takes `REPO_TOKEN` (fine-grained PAT, Contents: read on the GitOps repo) for ArgoCD and `PULL_TOKEN` (classic PAT, read:packages) for the pull secret. Without them it falls back to your login token and says so.

## Not included (deliberately)

- **Keyless signing / SLSA attestations** (cosign, `actions/attest-build-provenance`): attestations need GitHub Enterprise for private repos, and cosign's public-good Sigstore writes the repository identity to a public transparency log. Revisit when a repo is public or a private Sigstore is available. BuildKit's own provenance attestation stays at its default.
