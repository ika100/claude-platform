# Security policy

## Supported versions

Security fixes are released for the **latest minor version** of claude-platform (for example 2.1.x) and, where relevant, the plugins published from it. Older minors receive fixes only when a maintainer decides the issue is severe.

## Reporting a vulnerability

Please **do not open a public issue** for a vulnerability. Report it privately through GitHub:

**<https://github.com/ika100/claude-platform/security/advisories/new>** (Security tab → "Report a vulnerability")

Include what you found, how to reproduce it, which version or commit, and the impact you expect. You can expect an acknowledgement within **5 working days** and an assessment (accepted, needs more information, or declined with a reason) within **14 days**. We will agree on a disclosure date with you, credit you in the advisory unless you prefer otherwise, and publish a fixed release before disclosure.

## What is in scope

- The `cplat` CLI and the scripts under `scripts/` and `templates/*/scripts/` (command injection, path traversal, unsafe temp files, credential handling).
- The **secure defaults of the generated output**: Kubernetes manifests rendered by the GitOps template (security contexts, policies), generated GitHub Actions workflows (permissions, pinned actions, token scope), Dockerfiles, and how secrets are handled (they must never be written to git).
- Plugin agents and commands that could be made to leak data or run unintended destructive commands.

Out of scope: vulnerabilities in third-party software the templates install (report those upstream), findings that need an already-compromised machine or repository, and the example applications' own business logic.

## Hardening already in place

Actions are pinned by commit SHA and updated through Dependabot; workflows run with read-only tokens by default; images are scanned with Trivy and ship an SBOM; secrets are created in the cluster by External Secrets Operator and never stored in git; Kyverno guard rails are available for the GitOps repo. See ADR-018, ADR-019 and ADR-022.
