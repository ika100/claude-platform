# CHANGELOG

All notable changes to the `ika100/claude-platform` marketplace and templates.

Format: each section lists changes for a tagged release. Plugin and template versions are independent — a release may bump only one channel.

## [Unreleased]

### Plugins
- **svc 0.1.0**: initial release. 8 agents (product-manager, architect, coder, tester, migrations, observability, release, deployment) + 5 commands (plan-feature, build-feature, quick-task, fix-bug, release).
- **gitops 0.1.0**: initial release. 2 agents (deployment, promote) + 1 command (promote). ArgoCD ApplicationSet conventions documented.
- **shared 0.1.0**: initial release. 2 agents (quality, security) + 2 commands (check-quality, new-service).

### Templates
- **service-python**: initial. Full Python service skeleton — devbox, CI (quality/test/security/pr-title/docker), Dockerfile, k8s base + overlays, FastAPI scaffolding, optional observability/migrations toggles.
- **library-python**: initial. Slim Python library skeleton — devbox, CI (quality/test/security/pr-title), no Docker, no k8s.

### Docs
- AGENTS.md lifted from money-maker; orchestration model documented.
- ADOPTING.md: green-field + existing-repo migration paths.
- ARCHITECTURE.md: design rationale.
