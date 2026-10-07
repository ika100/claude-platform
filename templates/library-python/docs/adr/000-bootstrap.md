# ADR-000: Bootstrap

## Status

Accepted on bootstrap.

## Context

`{{ project_name }}` was created from the `library-python` Copier template at `ika100/sdlc-foundry`. This template encodes the library-flavored conventions:

- Python {{ python_version }} via devbox
- pytest with ≥80% coverage gate
- ruff + mypy for quality
- pip-audit + detect-secrets + bandit for security
- Claude Code agents from `sdlc-foundry` (`svc` + `shared`)

No HTTP server, no Dockerfile, no k8s — this is a library distributed as a wheel.

## Decision

Adopt the platform conventions verbatim. Marketplace pinned to `{{ platform_marketplace_ref }}` in `.claude/settings.json`. Skeleton updates via `copier update`.

## Consequences

**Positive:** consistent quality bar across libraries; agents work identically.

**Negative:** if a library needs library-specific tooling (e.g. doc generation with sphinx), upstream it to the template rather than working around it locally.
