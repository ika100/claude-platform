---
spec_id: 043-python-templates-pass-their-own-quality
spec_hash: 5e2d0d1ec0ac
summary: Make the Python templates lint-clean and check them in platform CI
tasks:
- id: t1
  title: Fix the service-python template's lint errors
  files: ['templates/service-python/src/{{ module_name }}/tracing.py', templates/service-python/tests/test_tracing.py]
  covers: [AC-043.1, AC-043.4]
  parallel_safe: true
  depends_on: []
- id: t2
  title: Lint, type-check and test the rendered Python templates in platform CI
  files: [.github/workflows/ci.yml, tests/cplat/test_ci_templates.py]
  covers: [AC-043.2, AC-043.3]
  parallel_safe: true
  depends_on: []
---

## t1 — Fix the service-python template's lint errors

**Files:** templates/service-python/src/{{ module_name }}/tracing.py, templates/service-python/tests/test_tracing.py
**Covers:** AC-043.1, AC-043.4
**Goal:** The rendered service-python passes `ruff check` and `ruff format --check` with the template's own config (line length 100).

**Implementation notes:**
- Wrap the two long OTLP exporter imports in `tracing.py` with parenthesised `import ... as` and sort the import block.
- Shorten the module docstring and the long tuple in `test_tracing.py`; no behaviour change.
- Render with `project_name=todo-api` (the run's name) and with the defaults, and run ruff and mypy on both.

**Done when:** `uvx ruff check` and `uvx ruff format --check` pass on both renders; `mypy` passes.

## t2 — Lint, type-check and test the rendered Python templates in platform CI

**Files:** .github/workflows/ci.yml, tests/cplat/test_ci_templates.py
**Covers:** AC-043.2, AC-043.3
**Goal:** The existing template matrix job for service-python and library-python runs ruff, mypy and pytest with uv on the rendered project, so a template lint error fails the platform PR.

**Implementation notes:**
- In the job that already renders the Python templates (`--skip-tasks`), add steps: `uv sync --all-extras`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy src`, `uv run pytest -q`.
- Keep `devbox run smoke` as the local full check; mention it in the job comment.
- A static test asserts that the Python template job contains the ruff, mypy and pytest steps.

**Done when:** `tests/cplat/test_ci_templates.py` passes; a deliberately long line in the template makes the new CI steps fail (checked once locally with act-like render + uv).
