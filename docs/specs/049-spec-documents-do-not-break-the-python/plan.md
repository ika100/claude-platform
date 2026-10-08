---
spec_id: 049-spec-documents-do-not-break-the-python
spec_hash: 1690d2e1cc54
summary: Python templates exclude docs/ from ruff
tasks:
- id: t1
  title: Exclude docs/ in the Python templates' ruff config
  files: [templates/service-python/pyproject.toml, templates/library-python/pyproject.toml, tests/cplat/test_spec_driven.py]
  covers: [AC-049.1, AC-049.2]
  parallel_safe: true
  depends_on: []
  done: true
---

## t1 — Exclude docs/ in the Python templates' ruff config

**Files:** templates/service-python/pyproject.toml, templates/library-python/pyproject.toml, tests/cplat/test_spec_driven.py
**Covers:** AC-049.1, AC-049.2
**Goal:** Markdown code blocks in docs never fail `devbox run quality`.

**Implementation notes:**
- `[tool.ruff] extend-exclude = ["docs"]` in both templates.
- Test: both pyproject files exclude docs; a render with an unformatted python block in `docs/specs/x/design.md` passes `ruff format --check`.

**Done when:** Tests pass.
