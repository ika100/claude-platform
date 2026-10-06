# Adding a new shape (template authoring guide)

A **shape** is a kind of repo the platform can bootstrap and operate: `service-python`, `library-python`, `web-nextjs`, `gitops-app`, `service-java`, `service-go`. This guide is the contract from [platform-vision §4.1](requirements/platform-vision.md) made concrete; `service-go` and `service-java` are the worked examples (copy their layout), and `web-nextjs` shows a non-Python JS stack. `uv run scripts/shapes.py check` (run in CI) enforces everything marked **[checked]** below.

Deliver all of it in one PR.

## 1. Registry entry — `shapes.yml` [checked]

Add the shape (see [ADR-015](adr/015-shape-registry-as-code.md) for every field). Start with `status: planned` while the template is incomplete; switch to `stable` in the same PR that makes the check pass. `deployable: true` means `/shared:new-service` adds the `deployable-service` topic. Add a row to the PRD §4 table (the check compares shape id, plugin and template).

## 2. Copier template — `templates/<id>/`

Required files [checked unless noted]:

| File | Notes |
|---|---|
| `copier.yml` | `_templates_suffix: .jinja` (see below), `_answers_file: .copier-answers.yml`, `_skip_if_exists` for project-owned files, `_tasks` for bootstrap (they are skipped in CI with `--skip-tasks`, so the rendered tree must already be valid) |
| `{{ _copier_conf.answers_file }}.jinja` | Copier's answers file — **load-bearing**: shape detection reads `_src_path` from it |
| `devbox.json[.jinja]` | The canonical recipes: `lint`, `lint-fix`, `quality`, `test`, `test-fast`, `security`; deployable shapes also `image-build`, `image-scan`, `deploy-check` (plus `dev`, `deploy`, `typecheck`, `audit`, `secrets-scan` by convention). Recipes wrap the language tools — agents never call them directly |
| `CLAUDE.md[.jinja]` | Shape-specific: recipe table, the "never call X directly" rule, conventions, branch workflow |
| `.claude/settings.json[.jinja]` | Enables the shape's plugin **and `shared`** and, for shapes driven by `/svc:*`, **`svc`** ([ADR-013 amendment](adr/013-plugin-auto-enable.md)); pins the marketplace ref |
| `.github/workflows/ci.yml` | `quality`, `test`, `security`, `pr-title`, `branch-name`, and `docker` for deployable shapes |
| `Dockerfile`, `k8s/base`, `k8s/overlays/{local,staging,prod}` | Deployable shapes. `k8s/base` must be a valid standalone Kustomize base (gitops-app repos consume `path: k8s/base`) and the image must be named `<registry>/<project_name>` |
| `docs/adr/000-bootstrap.md`, `docs/env-vars.md`, `README.md` | Project-owned after generation |

**Always re-templated vs project-owned.** Skeleton files (CI, devbox, Dockerfile, k8s base, CLAUDE.md, lint config) are overwritten by `copier update`. Application files (`src/`, `app/`, `cmd/`, `internal/`, `tests/`, manifests of the dependency tree like `go.mod`/`pom.xml`/`package.json` once created, `docs/adr/**`) go in `_skip_if_exists`.

### Pitfalls found while building the Go, Java and web shapes

- **Use `_templates_suffix: .jinja`** for non-Python shapes. Without it every file is rendered and anything with `{{ }}` (GitHub Actions `${{ }}`, Argo `{{name}}`, JSX, Go templates) needs escaping. With it, only `*.jinja` files render; filenames and directory names always render (so `src/main/java/{{ package_path }}/` works).
- **Question order matters.** A default that references another question (`github.com/{{ github_org }}/…`) sees an empty value if that question comes later in `copier.yml`.
- **Derive, don't ask:** use `when: false` questions for computed values (`package_name`, `package_path`).
- **Ship lockfiles that make the CI render valid** when the toolchain cannot resolve them offline (Go: pre-resolved `go.mod`/`go.sum`, conditional on optional features; pnpm: `pnpm-workspace.yaml` with `allowBuilds`). Verify with the toolchain's own "tidy"/"frozen" command that the shipped files produce no diff.
- **Optional features:** gate files with `_exclude` entries like `"{% if not needs_x %}path{% endif %}"` — the pattern must match the *rendered* path, i.e. without the `.jinja` suffix.
- **Do not trust a render you have not run.** Run the recipes (`quality`, `test`, build) on a rendered project for *every* optional-feature combination; the template tests found lint failures, coverage-gate failures and Spring test-slice quirks that reading the files did not.
- **macOS:** `devbox run` that calls another `devbox run` breaks under `/tmp` (symlink to `/private/tmp` changes the generated script path mid-run: `pecheck: command not found`). Verify in `/private/tmp/...` or your home directory; it is not a template bug.

## 3. Plugin — `plugins/<plugin>/` (new or existing)

[checked for non-gitops plugins: agents exist] Agents: at minimum `coder` and `tester`; deployable shapes also `deployment`, `observability`, `release`. A new plugin needs `.claude-plugin/plugin.json`, an entry in `.claude-plugin/marketplace.json` with the **same version** (CI compares), a `README.md`, and `hooks/hooks.json` if the repo needs a SessionStart step. Rules every agent follows:

- Everything goes through `devbox run <recipe>`; one-off tool calls use `devbox run -- <tool> …`.
- `coder` writes the shape's idioms and never edits lock/format config by hand; `tester` never fixes bugs; `deployment` verifies manifests with `deploy-check`; `observability` verifies-then-extends the scaffolding the template ships.
- The `release` agent differs only in how the version is bumped ([ADR-012](adr/012-per-plugin-release-agent.md)).

The `/svc:*` orchestrators route to `<plugin>:<role>` through `plugins/svc/fragments/shape-dispatch.md`; nothing in `svc` needs editing for a new backend shape.

## 4. Detection [checked]

- `scripts/detect-shape.sh`: add a `templates/<id>` case (primary) and a sniff rule positioned so it stays unambiguous ([ADR-008](adr/008-shape-detection.md)).
- `scripts/test-detect-shape.sh`: add a sniff fixture; the copier-answers fixtures iterate `shapes.yml` automatically.
- Update the sniff list in `plugins/shared/fragments/shape-detection.md`.

## 5. CI and docs

- `.github/workflows/ci.yml`: a `smoke-test-<id>` job that renders the template (`--skip-tasks`, plus the optional-feature variants) and runs the real build/test/lint with the toolchain.
- `devbox.json` (platform): a `smoke-<id>` recipe, added to `smoke`.
- Docs: `docs/AGENTS.md` (agents + model rationale), `docs/ADOPTING.md` (migration section), README tables, `docs/CHANGELOG.md`, and an ADR for any decision the PRD left open (stack choices).
