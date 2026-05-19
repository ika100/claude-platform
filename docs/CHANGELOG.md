# CHANGELOG

All notable changes to the `ika100/claude-platform` marketplace and templates.

Format: each section lists changes for a tagged release. Plugin and template versions are independent — a release may bump only one channel.

## [0.1.1] — 2026-05-19

Bugfix release. All five issues found during the hello-world dogfood are resolved.

### Plugins

- **shared 0.1.1**: `/shared:new-service` now shallow-clones the platform repo before invoking Copier instead of using the unsupported `gh:<owner>/<repo>/<subdir>` URL form. Also passes `--trust` because the templates declare `_tasks`.

### Templates

- **service-python**:
  - **CI**: added `workflow_dispatch:` trigger so freshly-bootstrapped repos can run their first validation without needing a PR.
  - **devbox.json**: dropped `--frozen` from the init_hook so fresh repos can `uv sync` and generate `uv.lock` on first session.
  - **pyproject.toml**: added `ruff`, `mypy`, `pip-audit` to dev deps so `uv run <tool>` uses venv-installed versions (the devbox-Nix versions can't see project deps like pydantic). Excluded `tests/` from mypy and disabled `disallow_untyped_decorators` (FastAPI decorators lack stubs).
  - **Python source files**: pre-formatted to ruff style — added blank line between module docstring and first import. Generated trees now pass `ruff format --check` on first bootstrap.
  - **Dockerfile + .dockerignore**: README.md is now included in the docker build context (hatchling needs it to satisfy `readme = "README.md"` in pyproject.toml).

- **library-python**:
  - Same `workflow_dispatch:` trigger, dropped `--frozen`, and the same dev-dep + mypy additions as service-python.

### Validated by

- `ika100/hello-world` — green CI on all 6 jobs after applying these fixes locally. Bumping the platform to 0.1.1 means a fresh `/shared:new-service` invocation produces a green-on-first-PR repo.

## [0.1.0] — 2026-05-19

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
