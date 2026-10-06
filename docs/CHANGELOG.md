# CHANGELOG

All notable changes to the `ika100/claude-platform` marketplace and templates.

Format: each section lists changes for a tagged release. Plugin and template versions are independent — a release may bump only one channel.

## [Unreleased]

Phase 1 of the multi-shape platform redesign ([platform-vision](requirements/platform-vision.md), ADR-008/013/015). Foundation only — no new shapes ship yet.

### Added

- **`shapes.yml`** — machine-readable shape registry (all six PRD shapes; the four new ones are `status: planned`).
- **`scripts/detect-shape.sh`** — shape detection from `.copier-answers.yml` with sniffing fallback (ADR-008), plus `scripts/test-detect-shape.sh` fixtures.
- **`scripts/shapes.py`** — validates `shapes.yml` and checks it against templates, plugins and the PRD §4 table.
- **`plugins/shared/fragments/shape-detection.md`** — canonical detection procedure for commands and agents.
- **`scripts/shapes.py check` now enforces the add-a-shape contract** (PRD §4.1): canonical devbox recipes, CLAUDE.md, plugin enablement in the template settings, plugin agents, detection registration. Documented in the new `docs/templates.md`.
- CI job `validate-shapes`; `devbox run shapes-check` and `devbox run test-detect` (included in `devbox run smoke`).

### Plugins

- **shared 0.5.0** (docs/UX pass): new `/shared:update-service [--ref] [--data k=v]` — `copier update` cannot work on repos bootstrapped by `/shared:new-service` (the template has no git history of its own), so the command re-applies the template with the repo's recorded answers on a review branch and lists overwritten skeleton files. `/shared:new-service` now records a stable `_src_path`, no longer passes the Python-style `module_name` to non-Python templates (it had turned the Go module path into `my_saas`), and runs its clone+copier steps in one shell. All docs that pointed at `copier update` now point at `/shared:update-service`; ADOPTING has a shape table, an end-to-end product flow, and a corrected migration guide (`/shared:check-quality`, not `/svc:check-quality`).
- **shared 0.4.0**: `/shared:new-service` gains `--type <shape>` (aliases `--library`, `--web`, `--gitops`); template, topic and `--python` handling are read from `shapes.yml`. With no flag it still produces a `service-python` repo. Requesting a `planned` shape fails with a clear message.

- **svc 1.1.0** (phase 2): every orchestration command resolves `$SHAPE` and routes coder/tester/deployment/observability/release to `$SHAPE_PLUGIN:<role>` via the new `plugins/svc/fragments/shape-dispatch.md`. The architect plan metadata gains a required `shape:` field (missing → `service-python` with a deprecation notice). `/svc:build-feature` gains `--from-plan <path> [<repo-id>]` (ADR-011) and skips deployment for non-deployable shapes. `/svc:release` dispatches to the shape's release agent. `/shared:check-quality` and the quality/security agents are shape-neutral.

- **gitops 0.3.0** (phase 3): new `compose` agent and `/gitops:compose add|remove <service...>`; `/gitops:promote` works in `gitops-app` repos, from a service repo via `.platform-app.yml`, with batch/`--all` and one PR per invocation.

- **web 0.1.0** (new, phase 4): `coder`, `tester`, `deployment`, `observability`, `release` agents for Next.js repos, plus a SessionStart hook that runs `devbox run install`. The `svc` SessionStart hook now only runs `uv sync` when `pyproject.toml` exists.

- **app 0.1.0** (new, phase 5): `/app:build-feature <desc>` (PM stories per repo → `planner` agent → validated topo-sorted multi-repo plan; **plan-only**, ADR-007) and `/app:plans list|show|start|done|abandon` (ADR-011 lifecycle).
- svc: `/svc:build-feature --from-plan` no longer edits the plan file (it lives in the gitops-app repo); progress is recorded with `/app:plans`.

- **svc-go 0.1.0** and **svc-java 0.1.0** (new, phase 6): `coder`, `tester`, `deployment`, `observability`, `release` agents for Go and Spring Boot repos; releases follow ADR-012 (`pom.xml` via `versions:set`; Go has no version file — the git tag is the version).

### Templates

- **service-go** (new, phase 6): chi + slog, golangci-lint v2, `govulncheck`, optional Prometheus `/metrics`, distroless static image with ldflags version, pre-resolved `go.mod`/`go.sum`. Verified by running `devbox run test`/`quality`/`audit` on rendered projects (both observability variants).
- **service-java** (new, phase 6): Spring Boot 3.5 / JDK 21 / Maven, Spotless (google-java-format) + Checkstyle, JUnit 5 + JaCoCo 80% gate, Actuator probes, optional Micrometer Prometheus + OTel Java agent, distroless java21 image. Verified by running `devbox run lint`/`test`/`quality` on rendered projects and booting the jar.
- ADR-009 / ADR-010 amendments record where the implementation differs from the ADR text.
- **gitops-app** gains `scripts/plan.py` (plan validation + lifecycle), `devbox run plan-check` (part of `validate`), and enables the `app` plugin.
- **web-nextjs** (new, phase 4): Next.js 16 App Router, TypeScript strict, pnpm (`packageManager` pinned, `pnpm-workspace.yaml` with `allowBuilds`), Node 24 LTS pinned in `package.json`/`devbox.json`/Dockerfile, Vitest + Testing Library (80% gate), optional Playwright (`needs_e2e`), optional `/api/metrics` + OpenTelemetry (`needs_observability`), `/api/health` + `/api/ready`, standalone-output multi-stage non-root Dockerfile, Kustomize base/overlays, CI. The rendered project is verified in CI (`pnpm install`, lint, typecheck, test, build).
- **gitops-app** (new, phase 3): product-scoped GitOps repo — `applications/<app>/{services.yaml,applicationset.yaml,overlays/<env>/<service>/}` generated by `scripts/render.py`, devbox recipes (`render`, `validate` = render-check + kustomize + kubeconform, `security`), CI, CLAUDE.md. See the ADR-013/014 amendments.
- `/shared:new-service` gains `--app <org>/<repo>` (writes `.platform-app.yml`).

### Documentation

- `docs/templates.md` (new): template authoring guide with the pitfalls found while building the Go, Java and web shapes. README, ARCHITECTURE, ADOPTING (web and gitops-app migration sections), AGENTS updated; PRD marked implemented.

### Migration

- Run `/plugin marketplace update`. No `copier update` needed for existing Python repos (their templates are unchanged).
- New repos: `/shared:new-service <name> --web | --gitops | --type service-java | --type service-go`.

## [1.0.1] — 2026-05-22

CI-only patch. No plugin or template behavior changes.

### Fixed

- **CI smoke-test** no longer fails on `devbox: not found`. The copier templates' bootstrap `_tasks` (which invoke `devbox install`) are now skipped via `--skip-tasks` in `.github/workflows/ci.yml`; CI verifies template rendering only. The full render-and-bootstrap path remains covered by `devbox run smoke` locally. Broken since v0.2.1.

## [1.0.0] — 2026-05-19

Phase 3 of the agentic efficiency overhaul. **First stable major.** Orchestration commands restructured for parallelism and to skip wasted work; per-command preludes deduplicated.

### Breaking changes

- **`/svc:build-feature` phase numbering changed.** The old Phase 3a (intermediate quality gate), Phase 4 (tester), Phase 4a (security) are merged into a single **Phase 4 — parallel QA fan-out** that runs quality + tester + security in one orchestrator turn. Phase 5 stays "deployment"; old Phases 6/7 are unchanged. Any consumer scripts that grep transcripts for `Phase 4a complete` need updating.
- **`/svc:fix-bug` phase numbering changed.** Old "Phase 5 — Commit and open PR" is now "Phase 4 — Commit and open PR" after the redundant intermediate phase was dropped in v0.1.4.
- **`/svc:quick-task` phase numbering changed.** Old "Phase 4 — Commit and open PR" is now "Phase 3 — Commit and open PR".

### Plugins

- **svc 1.0.0**:
  - **Scope classifier** (`/svc:build-feature` Phase 0a): the orchestrator now classifies the request before running PM + Architect. Typos / docs / one-file tweaks are routed to `/svc:quick-task`; bug reports are routed to `/svc:fix-bug`; standard features get a "confirm full pipeline?" prompt. Saves PM + Architect on requests that don't need them.
  - **Parallel QA fan-out** (`/svc:build-feature` Phase 4, `/svc:quick-task` Step 2): quality + tester + security (build-feature) or quality + tester (quick-task) now spawn in a single orchestrator turn, mirroring `/shared:check-quality`. Wall-clock is the longest leg, not the sum.
  - **Pre-computed subagent context:** every orchestrator now computes `$PROJECT_MAP` (top-level dirs) and `$TOUCHED_FILES` (`git diff --name-only $BASE_REF..HEAD`) up-front and prepends them as `<project-map>` / `<touched-files>` blocks to every subagent prompt. Each agent saves 2–5 exploratory Glob/Grep calls.
  - **Phase prelude fragment**: new `plugins/svc/fragments/phase-prelude.md` documents the canonical pre-Phase-1 workflow (git status check, branch creation, base-ref capture, context pre-compute). The three orchestration commands now reference it instead of carrying drifted copies.

### Migration

- Run `/plugin marketplace update` to pull svc 1.0.0.
- Existing service repos do **not** need a `copier update` for this release — only plugin contracts changed, no template files.
- If you watch for specific phase headers in agent output (CI greps, dashboards), update them per the breaking changes above.

## [0.4.0] — 2026-05-19

Phase 2 of the agentic efficiency overhaul: boilerplate that the `svc` agents used to regenerate on every invocation is now part of the `service-python` Copier template. Agents become verify-and-extend instead of generate-from-scratch. Non-breaking for consumers — run `copier update` to pull the new template files.

### Templates

- **service-python**: new pre-rendered observability files under `src/{{ module_name }}/`:
  - `tracing.py` — OpenTelemetry OTLP exporter wired via `OTLP_ENDPOINT` env var.
  - `main.py` now exposes `/metrics` (Prometheus `generate_latest`) and conditionally calls `configure_tracing()`.
  - `k8s/monitoring/alerts.yaml` — default PrometheusRule with `HighErrorRate`, `HighLatencyP95`, `PodRestarting`.
  - `docs/env-vars.md` — documents `LOG_LEVEL`, `OTLP_ENDPOINT`, `METRICS_PORT`, and `DATABASE_URL` when applicable.
- **service-python**: new pre-rendered Alembic scaffolding (gated by `needs_migrations`):
  - `alembic.ini` with `script_location = migrations`.
  - `migrations/env.py` that requires `DATABASE_URL` from env and leaves a TODO for wiring `target_metadata`.
  - `migrations/script.py.mako` with typed `upgrade()` / `downgrade()` signatures.
- **service-python copier.yml**: new `_exclude` block skips `alembic.ini` and `migrations/` when `needs_migrations=false`. `_skip_if_exists` extended with `docs/env-vars.md` and `k8s/monitoring/**` so they're project-owned after bootstrap.

### Plugins

- **svc 0.2.0**: three agents slimmed against the template now owning the boilerplate:
  - `observability.md`: 158 → 45 lines. Verifies the templated logging/metrics/tracing files exist, then focuses on service-specific instrumentation and alert tuning.
  - `deployment.md`: 100 → 61 lines. References the template's `Dockerfile` + `.github/workflows/ci.yml` instead of restating the YAML; verifies CI integrity and the dry-run gate.
  - `migrations.md`: 139 → 77 lines. Skips the `alembic init` boilerplate (template handles it); focuses on wiring `target_metadata`, generating + verifying migrations, and maintaining the runbook.

## [0.3.0] — 2026-05-19

Devbox awareness extended to every plugin and the platform repo itself. No breaking changes — repos without `devbox.json` see the new hooks as a silent no-op.

### Plugins

- **shared 0.3.0**: new `hooks/hooks.json` with a `SessionStart` hook. Checks `devbox` is on `PATH` (prints install URL if missing, exits 0 — non-blocking) and runs `devbox install` if a `devbox.json` is present. Makes any consumer repo that uses the `shared` plugin (library repos, GitOps repos, the platform repo) devbox-aware out of the box.
- **gitops 0.2.0**: same new `hooks/hooks.json` as `shared`. GitOps repos that add a `devbox.json` (for `kubectl`, `argocd`, `kustomize`) get automatic sync; older GitOps repos see a no-op.
- **svc 0.1.3**: existing `SessionStart` hook hardened with the same `command -v devbox` host-check, plus a `[ -f devbox.json ]` guard so it no-ops cleanly in non-devbox directories.

### Platform repo

- New root `devbox.json`: pins `jq`, `python@3.13`, `uv`, `git`, `gh`, and `init_hook`-installs `copier` (invoked at runtime via `uv tool run --from copier copier ...` so it's reachable from inside the devbox PATH). New scripts: `validate` (jq-checks marketplace + plugin manifests + hook files), `smoke-service`, `smoke-library`, `smoke` (runs all three). Smoke recipes run individual `devbox run lint` + `devbox run typecheck` instead of the chained `devbox run quality` recipe — devbox 0.17.2 has a wrapper bug that mis-evaluates the chained recipe even though both children succeed; tracked separately.
- `CLAUDE.md` smoke-test section rewritten to use `devbox run validate` / `smoke-service` / `smoke-library` instead of host-installed `jq` + `copier`. Only host requirement is `devbox` itself.
- `docs/AGENTS.md` documents the new SessionStart hooks under the golden-rule section.

## [0.2.1] — 2026-05-19

Bugfix release. Resolves the two issues raised after the `/shared:new-service` UX overhaul ([#1](https://github.com/ika100/claude-platform/issues/1), [#2](https://github.com/ika100/claude-platform/issues/2)).

### Templates

- **service-python + library-python (#1)**: `_tasks` in `copier.yml` now runs `devbox install` and `devbox run -- uv sync --all-extras` to materialize `devbox.lock` and `uv.lock`, then makes an initial `chore: bootstrap` commit. A fresh `copier copy …` now leaves `git status` clean instead of two lockfiles untracked. Requires `devbox` on `PATH` at template-render time (already a prerequisite for all other recipes in the template).
- **service-python (#2)**: tightened the `docker` job's login and `build-push-action` conditions from `github.event_name != 'pull_request'` to `github.event_name == 'push' && (github.ref == 'refs/heads/main' || startsWith(github.ref, 'refs/tags/v'))`. Feature-branch pushes now build only, matching the policy documented in the template's `CLAUDE.md` (and avoiding the 403 from a brand-new repo's `GITHUB_TOKEN` lacking `packages: write`).

### Plugins

- **shared 0.2.1**: `/shared:new-service` Phase 3 rewritten for the new copier-side commit. Instead of `git add -A && git commit`, it now `git commit --amend --reset-author`s the bootstrap commit produced by `_tasks` so the user owns it with the richer `/shared:new-service` commit message. Falls back to the legacy `add && commit` path if `_tasks` didn't produce a commit (older templates).

## [0.2.0] — 2026-05-19

UX overhaul for `/shared:new-service` based on dogfooding feedback. Non-breaking — old flag form (`--description "..."`) still works.

### Plugins

- **shared 0.2.0**: `/shared:new-service` rewritten for fewer interactions:
  - **Natural-language args.** First token = project name, the rest = description. `/shared:new-service hello-world a simple rest api` now scaffolds end-to-end with zero further prompts. Old `--description "..."` flag still accepted.
  - **Auto-preflight.** Silently runs `uv tool install copier` if `copier` is missing. If `gh` is missing, automatically falls back to "skip GitHub steps" mode and emits the exact `gh repo create` / `gh repo edit` commands in the final report (instead of aborting).
  - **Auto-detect `GITHUB_ORG`.** Tries `gh api user -q .login`, falls back to the copier template's `ika100` default. No prompt.
  - **No confirmation table.** Resolved inputs go on one compact line; bootstrap proceeds immediately. The user can correct after the fact — everything is local and reversible until Phase 4.
  - **Empty/stub directory auto-clean.** If `./<name>` is empty or contains only `.claude/`, removes it with one warning line. Non-empty directories still abort.
  - **Single-round prompt when truly missing.** If both name and description are absent, asks once via plain text (`<name> <description>` on one line) — no `AskUserQuestion`, no batched dialog.
  - **Handles missing git identity.** Falls back to one-off `-c user.name=... -c user.email=...` on the bootstrap commit so fresh hosts without global git config don't error out.

### Templates

No template changes in this release.

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
