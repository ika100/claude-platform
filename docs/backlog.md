# Product backlog: existing features (retrospective spec)

This backlog describes what sdlc-foundry already does, written as the product-manager phase of `/svc:plan-feature` would have written it: user stories with testable acceptance criteria. Nothing here is new work. The features were built from the PRD, ADRs and PRs, not through the plan/build pipeline, so this file records the contract after the fact.

**Sources:** [platform-vision.md](requirements/platform-vision.md) (PRD), [ADRs](adr/README.md), [CHANGELOG](CHANGELOG.md), `shapes.yml`, `scripts/cplat/`, `plugins/*/commands`.
**Status values:** `done` (shipped, covered by tests or CI), `partial`, `not built`.
**Priority:** P0 blocks a usable platform, P1 completes it, P2 is optional.
**Personas:** *Founder* (builds products on the platform), *Contributor* (works in one repo), *Agent* (a Claude subagent that follows a repo's `CLAUDE.md`).

Stories PRD'd but not built are at the end, so the gaps are visible.

---

## Epic A. Bootstrap and update

#### STORY-001: Create a repo of any shape with one command
**Status:** done · **Priority:** P0 · **Source:** PRD A1/A2, ADR-001, ADR-015 · **Code:** `scripts/cplat/newsvc.py`

As a founder, I want `/shared:new-service <name> <description> [--type <shape>]` to create a working repo, so that I never copy boilerplate.

**Acceptance criteria:**
- [ ] Valid shapes are exactly the ids in `shapes.yml`: `service-python`, `library-python`, `web-nextjs`, `gitops-app`, `service-java`, `service-go`. An unknown shape lists the valid ones.
- [ ] No flag produces a `service-python` repo. `--library`, `--web` and `--gitops` are aliases for `--type`.
- [ ] A private GitHub repo is created, the template is rendered, and the first commit is pushed. Deployable shapes get the `deployable-service` topic; `library-python` and `gitops-app` do not.
- [ ] A dry-run preview shows what will happen (including PUBLIC or PRIVATE) before anything is created.
- [ ] The command ends with next steps and says how to undo.
- [ ] `--public` / `--visibility public` creates a public repo.
- [ ] `--data KEY=VALUE` sets template options at creation; keys are validated against the template's `copier.yml` and an unknown key lists the valid ones.
- [ ] `--app <org>/<gitops-repo>` links a service to its product's gitops-app (`.platform-app.yml`).
- [ ] Development can start on a feature branch immediately, without waiting for the bootstrap CI on `main`.

#### STORY-002: Generated repos enable their plugins automatically
**Status:** done · **Priority:** P0 · **Source:** ADR-013

As a founder, I want a new repo's first Claude Code session to have the right plugins enabled, so that `/svc:*` commands work immediately.

**Acceptance criteria:**
- [ ] Each template's `.claude/settings.json` enables the plugin(s) for its shape and carries the committed permission allowlist (no prompts for `devbox run`, read-only git, feature-branch pushes; prompts for anything remote-destructive).
- [ ] `shapes.py check` fails if a template does not enable its shape's plugin.

#### STORY-003: Pull template updates into an existing repo safely
**Status:** done · **Priority:** P0 · **Source:** PRD D2, CHANGELOG 0.5.0, 3.0.1, 3.0.2 · **Code:** `scripts/cplat/update.py`

As a founder, I want `/shared:update-service` to bring the latest skeleton (CI, Dockerfile, devbox recipes, CLAUDE.md) into my repo, so that fixes propagate without losing my work.

**Acceptance criteria:**
- [ ] Changes land on a review branch (unique name if today's already exists), never on `main`.
- [ ] Files in a template's `_skip_if_exists` (dependency manifests, app code, tests, project docs) are never overwritten, and new files copier would add inside those paths are removed and reported.
- [ ] The report lists overwritten skeleton files and the changelog range since the repo's `.platform-version`.
- [ ] `--ref <tag>` pins a platform version; `--data k=v` changes template options; `--migrate` converts a v1 repo (removes `k8s/`).
- [ ] A test asserts that every template protects its dependency manifest.

#### STORY-004: Preflight check of the setup
**Status:** done · **Priority:** P1 · **Source:** CHANGELOG 2.0.0 · **Code:** `scripts/cplat/doctor.py`

As a founder, I want `/shared:doctor` to check my machine and repo, so that I find problems before a command fails midway.

**Acceptance criteria:**
- [ ] Checks tools, `gh` scopes, Docker, kube context (warns on a non-local context), installed plugin versions, and the repo's platform version.
- [ ] Every problem comes with a concrete fix. A plugin installed under the old marketplace id gets the migration steps. Missing cluster operators (ESO, CloudNativePG, Kyverno) are warned about only when the app uses them.

#### STORY-005: Report a platform problem without leaking secrets
**Status:** done · **Priority:** P2 · **Source:** CHANGELOG 2.2.0 · **Code:** `scripts/cplat/feedback.py`

As a contributor, I want `/shared:report-issue` to draft a GitHub issue with diagnostics, so that platform bugs reach the maintainer.

**Acceptance criteria:**
- [ ] Nothing is sent without explicit confirmation.
- [ ] Secrets are removed from the diagnostics.
- [ ] Every agent and command tells Claude to stop and offer this when a platform template, script or command misbehaves.

---

## Epic B. Shapes and the extension contract

#### STORY-006: Six supported shapes, registered as code
**Status:** done · **Priority:** P0 · **Source:** PRD §4, ADR-015, ADR-009, ADR-010 · **Code:** `shapes.yml`, `scripts/shapes.py`

As a maintainer, I want one machine-readable registry of shapes, so that docs, templates, plugins and detection cannot drift apart.

**Acceptance criteria:**
- [ ] `shapes.yml` has one entry per shape with plugin, template, `deployable`, `library`, detection rules, default stack, runtime (port, probes, metrics path, user, volumes, resources) and status.
- [ ] `scripts/shapes.py check` (in CI) verifies the registry against templates, plugins, the PRD §4 table and the ADR index.
- [ ] Deployable service templates ship no `k8s/` directory (ADR-017).

#### STORY-007: A shape is added by following a documented contract
**Status:** done · **Priority:** P1 · **Source:** PRD §4.1/A3/D3, `docs/templates.md`

As a maintainer, I want adding a shape to be a checklist, so that Rust or Kotlin would not need a new PRD.

**Acceptance criteria:**
- [ ] A shape needs: a template with `copier.yml`, `CLAUDE.md` and the canonical devbox recipes; a plugin with at least `coder` and `tester`; a registry entry plus a sniff rule in `scripts/detect-shape.sh`.
- [ ] `shapes.py check` enforces each of these and fails the PR when one is missing.
- [ ] Java and Go are the worked examples in `docs/templates.md`.

#### STORY-008: Commands detect the repo's shape
**Status:** done · **Priority:** P0 · **Source:** ADR-008 · **Code:** `scripts/detect-shape.sh`, `scripts/cplat/shapecmd.py`

As an agent, I want `cplat shape` to tell me the shape and which subagent type to use for each role, so that I route work correctly.

**Acceptance criteria:**
- [ ] The shape comes from `_src_path` in `.copier-answers.yml`; if absent, from sniffing (`next.config.*` → web; `pyproject.toml` + `Dockerfile` → service-python; `pyproject.toml` without `Dockerfile` → library-python; `applications/*/applicationset.yaml` → gitops-app; and so on).
- [ ] Output is JSON with `shape`, `plugin`, `deployable`, `library` and `agents` (role → subagent type). Roles a shape lacks (for example deployment for a library) are absent.
- [ ] An unknown repo returns `unsupported` and the commands stop with that message.
- [ ] `scripts/test-detect-shape.sh` covers the fixtures.

#### STORY-009: Python service and library templates
**Status:** done · **Priority:** P0 · **Source:** PRD §4, ADR-016

As a founder, I want Python 3.12 / uv / FastAPI services and uv-distributed libraries.

**Acceptance criteria:**
- [ ] `service-python` serves `/health`, `/ready` and `/metrics` on port 8080, runs as numeric user 10001, and includes Alembic migrations scaffolding.
- [ ] `library-python` has no Dockerfile and no deployable topic; consumers install it via `git+https` with `uv` (ADR-016).

#### STORY-010: Web (Next.js) template
**Status:** done · **Priority:** P0 · **Source:** ADR-002..005, CHANGELOG 2.2.0

As a founder, I want a Next.js App Router starter that is ready for production.

**Acceptance criteria:**
- [ ] Next.js App Router only, TypeScript strict, pnpm with a pinned `packageManager`, a pinned Node LTS.
- [ ] Vitest and Testing Library by default; Playwright and `e2e/` only when `needs_e2e` is enabled.
- [ ] Serves `/api/health`, `/api/ready` and `/api/metrics` on port 3000, as numeric user 1000.
- [ ] Ships a designed starter UI (light/dark themes, header, hero) which `update-service` never adds to an existing app.
- [ ] `package.json` is project-owned.

#### STORY-011: Java (Spring Boot) template
**Status:** done · **Priority:** P1 · **Source:** ADR-009, CHANGELOG 3.1.0

As a founder, I want a Spring Boot 3.x / JDK 21 / Maven service.

**Acceptance criteria:**
- [ ] Spotless + Checkstyle, JUnit 5, and a JaCoCo coverage gate; Actuator probes; optional Micrometer Prometheus and OpenTelemetry Java agent; distroless image running as a numeric user.
- [ ] `needs_database=true` adds JPA, Bean Validation, Flyway and the PostgreSQL driver; config reads the platform's `PG*` variables; Hibernate only validates; readiness includes the database; the service waits for its database at startup.
- [ ] CI has a smoke variant with a real PostgreSQL next to the image.

#### STORY-012: Go template
**Status:** done · **Priority:** P1 · **Source:** ADR-010

As a founder, I want a Go service on `chi` and `log/slog`.

**Acceptance criteria:**
- [ ] `golangci-lint`, `govulncheck`, stdlib `testing` with `go test -cover`, optional Prometheus `/metrics`, distroless static image with the version injected by ldflags.
- [ ] `go.mod` / `go.sum` are project-owned and pre-resolved.

---

## Epic C. Feature pipelines (svc plugin)

#### STORY-013: Plan a feature without writing code
**Status:** done · **Priority:** P0 · **Source:** `plugins/svc/commands/plan-feature.md`

As a founder, I want `/svc:plan-feature <description>` to produce stories and a plan, so that I can review before anything is built.

**Acceptance criteria:**
- [ ] Refuses to run on a dirty working tree; prints the current branch and the resolved shape.
- [ ] Product-manager writes `docs/backlog.md`; architect writes `docs/plan/<slug>.md` (and ADRs when a decision is significant). No production code is written.
- [ ] Ends with a summary of tasks and acceptance criteria and points to `/svc:build-feature`.

#### STORY-014: Build a feature end to end
**Status:** done · **Priority:** P0 · **Source:** PRD C1, ADR-008, ADR-023 · **Code:** `plugins/svc/commands/build-feature.md`

As a founder, I want `/svc:build-feature <description>` to take a request to an open PR.

**Acceptance criteria:**
- [ ] Phases: pre-flight → product-manager → architect → parallel coders → quality, tests and security in parallel → deployment/observability where the shape needs them.
- [ ] Every role is spawned with the subagent type from `cplat shape`, so a Go repo uses `svc-go:coder` and a web repo `web:tester`.
- [ ] The plan starts with a YAML block (`plan_id`, `shape`, `tasks[]` with `files`, `parallel_safe`, `depends_on`); tasks that are `parallel_safe` run in separate git worktrees and are merged back one by one with a quality gate between merges.
- [ ] Work happens on a `feature/*` branch; nothing is committed to `main`.
- [ ] `--no-pm` skips the product-manager phase; `--from-plan <plan> [<repo-id>]` takes the repo's `arguments` from a multi-repo plan.
- [ ] Agents run commands only through `devbox run <recipe>`.

#### STORY-015: Small changes and bug fixes
**Status:** done · **Priority:** P1

As a contributor, I want a light path for small tasks and bugs.

**Acceptance criteria:**
- [ ] `/svc:quick-task` runs coder → quality → tester with a fix loop; no PM, architect, security or deployment.
- [ ] `/svc:fix-bug` runs coder → tester in a loop until the bug is resolved.

#### STORY-016: Release with semver, changelog and tag
**Status:** done · **Priority:** P0 · **Source:** ADR-012, PRD C3

As a founder, I want `/svc:release` to cut a release for any shape.

**Acceptance criteria:**
- [ ] Runs quality, tests and security first, then a per-plugin `release` agent bumps the version (Python `pyproject.toml`, Java `pom.xml` via `versions:set`, Go has no version file, web `package.json`), writes the changelog and opens a PR from `release/vX.Y.Z`.
- [ ] The release agent never commits to `main` and never creates the tag; the orchestrator tags after the PR merges.
- [ ] The tag triggers a semver-tagged image publish (`X.Y.Z`).

#### STORY-017: Per-shape specialist agents
**Status:** done · **Priority:** P0 · **Source:** PRD B1..B3, E2

As an agent, I want idiomatic coder, tester, deployment, observability and release roles for each shape.

**Acceptance criteria:**
- [ ] `svc`, `web`, `svc-java` and `svc-go` each ship `coder`, `tester`, `deployment`, `observability` and `release`; `svc` also ships `product-manager`, `architect` and `migrations`.
- [ ] Deployment agents own the Dockerfile and CI image job only; they do not write Kubernetes manifests (ADR-017).
- [ ] The product-manager tags stories per repo for multi-repo features and folds client issues labelled `triage` into the backlog.

#### STORY-018: Quality and security checks for every shape
**Status:** done · **Priority:** P0 · **Source:** PRD E1

As a contributor, I want `/shared:check-quality` to audit my repo read-only.

**Acceptance criteria:**
- [ ] Runs the shape's `quality` and `security` devbox recipes (Python ruff/mypy/pip-audit, web ESLint/tsc/audit, Java Spotless/Checkstyle/OWASP or trivy, Go gofmt/vet/staticcheck/govulncheck) plus detect-secrets and trivy, in parallel.
- [ ] Produces one combined report and changes no code.

---

## Epic D. Product composition and deployment (GitOps)

#### STORY-019: The gitops-app repo owns every Kubernetes manifest
**Status:** done · **Priority:** P0 · **Source:** ADR-006, ADR-014, ADR-017 · **Code:** `templates/gitops-app/scripts/render.py`

As a founder, I want one repo per product that declares its services and renders their manifests, so that services only ship an image.

**Acceptance criteria:**
- [ ] `services.yaml` entries (port, probes, user, volumes, env, secretRefs, replicas, resources, expose, environments) render `deployment.yaml`, `service.yaml`, `httproute.yaml` and `kustomization.yaml` per environment under `applications/<app>/overlays/{dev,staging,prod}/`; rendered output is checked in CI (`devbox run validate`).
- [ ] Env-only overlays (no regions). A root Argo Application (app-of-apps) is generated; after one human `devbox run bootstrap` per cluster, all changes deploy through merged PRs.
- [ ] `bootstrap` requires an explicit `KUBE_CONTEXT`.
- [ ] Optional Gateway API exposure per service with per-environment hostname templates (dev default `{service}.{app}-dev.localhost`).

#### STORY-020: Add and remove services in a product
**Status:** done · **Priority:** P1 · **Source:** PRD B5, ADR-014 · **Code:** `scripts/cplat/compose.py`

As a founder, I want `/gitops:compose add|remove <service...>` to edit `services.yaml` for me.

**Acceptance criteria:**
- [ ] Writes a complete entry using the shape's defaults from `shapes.yml`, renders the manifests and opens one PR.
- [ ] Validates that the service repo carries the `deployable-service` topic.
- [ ] New services start in `dev` only, tracking `latest`.
- [ ] Options: `--expose [host]`, `--env K=V`, `--replicas N`, `--generate S=K,K`, `--secret S=K,K`, `--uses postgres`, `--secret-ref NAME`, `--from-k8s` (seed from a v1 service), `--pr`.

#### STORY-021: Promote images through environments
**Status:** done · **Priority:** P0 · **Source:** PRD B6, CHANGELOG 1.1.1, 2.0.0 · **Code:** `scripts/cplat/promote.py`

As a founder, I want `/gitops:promote <service...|--all> <from> <to>` to move a version up one environment.

**Acceptance criteria:**
- [ ] Pins an image tag only: staging `sha-<7>`, prod `X.Y.Z`. The tag is verified to exist in GHCR before the PR opens.
- [ ] One PR per invocation, including batches and `--all`. `--version vX.Y.Z` and `--sha <full-sha>` override the default.
- [ ] Works from inside the gitops-app repo or from a service repo via `.platform-app.yml`.

#### STORY-022: See what is deployed where
**Status:** done · **Priority:** P1 · **Source:** CHANGELOG 2.0.0 · **Code:** `scripts/cplat/status.py`

As a founder, I want `/shared:status` in a gitops-app repo to show one table per product.

**Acceptance criteria:**
- [ ] Per service and environment: the pinned tag; CI state of each service's `main`; ArgoCD sync and health (`--context` selects the cluster). Addon health is included.

#### STORY-023: Run the whole product on a local cluster
**Status:** done · **Priority:** P1 · **Source:** CHANGELOG 1.1.1, 2.0.0, 3.1.0, 3.2.0 · **Code:** `templates/gitops-app/scripts/local-cluster.sh`

As a founder, I want `devbox run cluster-up` to give me a working local environment.

**Acceptance criteria:**
- [ ] Creates a k3d cluster with ArgoCD, repo credentials (`REPO_TOKEN`, read-only) and a GHCR pull secret (`PULL_TOKEN`, `read:packages`), per-environment namespaces `<app>-<env>`, and the Traefik Gateway provider. ESO, CloudNativePG and Kyverno are installed only when the product uses them.
- [ ] Busy host ports (`LOCAL_HTTP_PORT`, `REGISTRY_PORT`) stop the script before anything is created, naming the holder and a free port; `LOCAL_HTTP_PORT=auto` picks one from 8088.
- [ ] `cluster-down` removes it; `devbox run cluster-ui` opens k9s on `<app>-dev`.
- [ ] A nightly end-to-end test renders a gitops-app, a Java service and a web app from the real templates, builds the images and verifies them in the cluster.

#### STORY-024: Secrets without values in git
**Status:** done · **Priority:** P1 · **Source:** ADR-018 · **Code:** `scripts/cplat/secret.py`

As a founder, I want secrets handled by External Secrets Operator, so that git holds references only.

**Acceptance criteria:**
- [ ] `secrets.generate: [KEY…]` makes ESO create stable random values once per environment; `secrets.remote` reads from the store named in `app.yaml`.
- [ ] `/gitops:secret set <service> <secret> <KEY> [--env dev]` reads the value from a hidden prompt or stdin; `list` shows which exist. Values never appear in output or git.

#### STORY-025: Backing services as addons
**Status:** done · **Priority:** P1 · **Source:** ADR-020, ADR-021 · **Code:** `scripts/cplat/addon.py`

As a founder, I want to declare a database or observability once and use it by name.

**Acceptance criteria:**
- [ ] `/gitops:addon add|remove|list postgres|observability`; services opt in with `uses: [postgres]`.
- [ ] Postgres: a CloudNativePG cluster per environment where used; services receive `DATABASE_URL` and `PG*` from the operator's Secret.
- [ ] Removing an addon never deletes data (`prune: false`) and is refused while a service still uses it.
- [ ] Observability: an OpenTelemetry Collector per environment receives OTLP, scrapes each service's `metrics:` path, and exports OTLP/HTTP when `exportTo` is set; `ui: lgtm` adds Grafana, Tempo, Loki and Prometheus locally (dev only).

#### STORY-026: Guard rails before merge and in the cluster
**Status:** done · **Priority:** P2 · **Source:** ADR-022

As a founder, I want security conventions enforced, so that a rendered manifest cannot break them.

**Acceptance criteria:**
- [ ] `policies:` in `app.yaml` renders namespaced Kyverno policies (numeric non-root, read-only filesystem, no escalation, dropped capabilities, no privileged).
- [ ] `devbox run validate` and CI evaluate rendered overlays and addons offline with the Kyverno CLI (checksum-pinned download).

---

## Epic E. Multi-repo features (app plugin)

#### STORY-027: Plan a feature across repos
**Status:** done · **Priority:** P1 · **Source:** PRD C2, ADR-007, ADR-011 · **Code:** `plugins/app/agents/planner.md`, `templates/gitops-app/scripts/plan.py`

As a founder, I want `/app:build-feature <description>` in a gitops-app repo to plan the work in every affected repo.

**Acceptance criteria:**
- [ ] Writes `docs/plan/<slug>.md` with YAML (`plan_id`, `feature`, `gitops_app`, `status: draft`, `repos[]` with `id`, `shape`, `summary`, `arguments`, `depends_on`, `done`, plus `gitops_pin[]`), validated by `plan.py` (shape ids exist, dependencies resolve, no cycles; also part of `devbox run validate`).
- [ ] Includes a `## Contract` section so dependent repos (for example a backend and its UI) can start together.
- [ ] Plan-only: it opens no PRs outside the gitops-app repo and edits no component repo. It prints the per-repo `/svc:build-feature` hand-off commands.

#### STORY-028: Manage plan lifecycle
**Status:** done · **Priority:** P1 · **Source:** ADR-011

As a founder, I want `/app:plans` to track a plan's progress.

**Acceptance criteria:**
- [ ] `list` shows `draft` and `in_progress` (`--all` includes terminal states); `show <slug>` shows a checklist; `start`, `done <slug> <repo-id>` and `abandon <slug>` apply the state machine `draft → in_progress → completed | abandoned`.
- [ ] The plan becomes `completed` when every repo is `done`.

#### STORY-029: Run a plan in parallel
**Status:** done · **Priority:** P1 · **Source:** ADR-023, CHANGELOG 3.2.0

As a founder, I want `/app:run-plan <slug>` to build every repo whose dependencies are done at the same time.

**Acceptance criteria:**
- [ ] `plan.py ready` computes the wave; one agent runs `/svc:build-feature --from-plan` per ready repo (`--max N` limits concurrency).
- [ ] Each repo ends at an open PR. The command merges only when told to and never pins images.
- [ ] A failure in one repo pauses its dependents and reports the state; the plan stays recoverable.

---

## Epic F. Supply chain, CI and repository hygiene

#### STORY-030: Hardened CI in every generated repo
**Status:** done · **Priority:** P0 · **Source:** ADR-019, CHANGELOG 1.1.1, 2.0.0, 2.1.0, 3.0.3

As a founder, I want generated CI to be safe and to publish usable images.

**Acceptance criteria:**
- [ ] The workflow triggers on pushes to `main`, which publish `latest` and `sha-*` images; version tags publish semver images.
- [ ] Images are native multi-arch (amd64 and arm64) merged into one manifest; the Trivy scan on each architecture uses `TRIVY_PLATFORM`.
- [ ] All Actions are pinned by commit SHA (`scripts/pin-actions.py --check`); workflows use `permissions: contents: read` with `packages: write` only on image jobs.
- [ ] Trivy blocks fixable HIGH/CRITICAL on `v*.*.*` releases and reports on `main`; a CycloneDX SBOM is kept for 90 days.
- [ ] Dockerfiles run as a numeric non-root user and carry the `org.opencontainers.image.source` label.
- [ ] Superseded PR runs are cancelled; a PR title edit re-runs the title check without cancelling a running build; Dependabot is monthly and grouped.
- [ ] `actionlint` runs over the platform's and the templates' workflows.

#### STORY-031: Platform repository rules and local CI
**Status:** done · **Priority:** P1 · **Source:** CONTRIBUTING.md, CHANGELOG 2.2.0, 3.0.0, 3.2.0 · **Code:** `scripts/ci-local.sh`, `scripts/check-*.py`, `scripts/bump_template_pins.py`

As a maintainer, I want changes to the shared source of truth to be checked before they reach every downstream repo.

**Acceptance criteria:**
- [ ] `main` requires a pull request and the single status `ci-success`; commits are DCO signed-off (`git commit -s`, `scripts/check-dco.py`).
- [ ] `devbox run validate` checks `marketplace.json`, every `plugin.json` and `hooks.json`; plugin versions match between the marketplace and each manifest.
- [ ] The CI runs only the jobs a change needs (docs-only changes run the validation jobs only); `scripts/ci-local.sh` runs the cheap checks locally; Markdown links are checked.
- [ ] A weekly job bumps template dependency pins, verifies by re-rendering, and opens a PR; it never bumps `packageManager`.

#### STORY-032: Documentation site and onboarding
**Status:** done · **Priority:** P1 · **Source:** PRD F1..F3, CHANGELOG 2.2.0

As a founder, I want guides that match the product.

**Acceptance criteria:**
- [ ] `ADOPTING.md`, `AGENTS.md`, `ARCHITECTURE.md`, `HOW-IT-WORKS.md`, `USER-JOURNEY.md`, `templates.md` and the ADR index exist and are link-checked.
- [ ] Each template ships a shape-specific `CLAUDE.md`.
- [ ] A GitHub Pages site (no analytics, no third-party requests) publishes the docs.

---

## Epic G. Whole-product bootstrap

#### STORY-033: Bootstrap a whole product from a manifest
**Status:** done · **Priority:** P0 · **Source:** end-to-end scenario Phase 1, UX-2, UX-3 · **Plan:** [plan/new-app.md](plan/new-app.md) · **Code:** `scripts/cplat/newapp.py`

As a founder, I want `/shared:new-app <manifest>` to create the gitops-app repo and every component repo and wire them together, so that standing up a product is one command instead of one `new-service` per repo plus a `compose`.

**Manifest (`app.yml`):**
```yaml
app: taskboard            # name of the gitops-app repo; also the --app value of every service
org: ika100               # optional, default: your gh login
visibility: private       # optional, private|public
components:
  - name: taskboard-api
    description: Task CRUD API
    shape: service-python
    data: {needs_database: "true"}   # optional template options, same as new-service --data
  - name: taskboard-web
    description: Taskboard frontend
    shape: web-nextjs
```

**Acceptance criteria:**
- [ ] `--dry-run` validates everything and prints every repo, shape, topic and template option that would be created, in creation order, without any side effect (no directory, no GitHub call that writes).
- [ ] Validation runs before any side effect and aborts on the first problem with a `fix:` line: unknown keys; names not matching `^[a-z][a-z0-9-]{1,39}$`; duplicate names; a component named like the app; a shape not in `shapes.yml`, `planned`, or `gitops-app` (the app repo is implicit); unknown `data` keys (checked against the template's `copier.yml`); a target directory that exists and is not empty; a GitHub repo that already exists (`gh repo view`); `gh` missing or not logged in.
- [ ] Creation order is independent of the order in the file: gitops-app first, then libraries, then services (Python, Java, Go), then web frontends.
- [ ] Each repo is created with the same code path as `/shared:new-service` (same template rendering, bootstrap commit, topic rules, plugin auto-enable); deployable components get `--app <org>/<app>`, libraries get none.
- [ ] After the repos exist, one `compose add` pins all deployable components in the gitops-app repo and opens a single PR. Libraries are not composed.
- [ ] Failure midway stops at once and reports which repos were created, which were not, and the undo commands. Re-running with `--resume` skips repos that already exist and continues with the rest, including the compose PR.
- [ ] `--no-github` renders everything locally and prints the GitHub and compose commands instead of running them.
- [ ] The output follows the `Report` convention: what I will do (with `[outward]` marks) / what happened / next / how to undo.
- [ ] Interactive mode is out of scope for this story.

#### STORY-034: Every new repo and app starts spec-first
**Status:** planned · **Priority:** P0 · **Source:** user request 2026-10-07 · **Plan:** [plan/spec-driven-bootstrap.md](plan/spec-driven-bootstrap.md)

As a founder, I want creating a service, library, web app or whole product to lead into `plan-feature` and then `build-feature`, so that every feature has a reviewed story and plan before code, and the repo always holds the artifacts (`docs/backlog.md`, `docs/plan/<slug>.md`) that tie the code to its spec.

**Acceptance criteria:**
- [ ] The *Next* steps of `/shared:new-service` (service-python, service-java, service-go, web-nextjs, library-python) name `/svc:plan-feature "<the repo's description>"` as the first step, followed by `/svc:build-feature --plan docs/plan/<slug>.md`. For gitops-app they name `/app:build-feature`. No bootstrap output suggests `/svc:build-feature` without a plan as the first step.
- [ ] The *Next* steps of `/shared:new-app` name `/app:build-feature "<first product feature>"` in the gitops-app repo, then `/app:run-plan <slug>`; each component's own first feature follows from that plan via `--from-plan`.
- [ ] Every template ships a `docs/backlog.md` skeleton (story format, no stories) and a `docs/plan/` directory (gitops-app already has one). Both are project-owned: `/shared:update-service` never overwrites them and never adds them to an existing repo.
- [ ] Every template's `CLAUDE.md` states the rule: a feature starts with `/svc:plan-feature` (or `/app:build-feature`), is built from the approved plan, and its PR cites the story ids. Small changes stay on `/svc:quick-task` and bugs on `/svc:fix-bug`.
- [ ] `/svc:plan-feature` ends by printing `/svc:build-feature --plan docs/plan/<slug>.md`. Plans and stories reference each other: stories have ids (`STORY-NNN`), the plan's metadata lists `stories: [STORY-NNN, …]`.
- [ ] `/svc:build-feature --plan <path>` skips the product-manager and architect phases, validates the plan (YAML block, `shape` equals the repo's shape, referenced stories exist), takes the acceptance criteria from those stories, and builds. Phase 6 marks those stories done and the PR description lists them. Without `--plan` the command behaves as today and still writes the same artifacts.
- [ ] The platform's add-a-shape contract requires the seed `docs/backlog.md` and the `CLAUDE.md` rule; `shapes.py check` fails when a template lacks them.
- [ ] Tests cover the bootstrap output of each shape, the templates' seed files and rule, and the plan validation of `--plan`.

## Not built (specified in the PRD, absent from the code)

| Item | PRD ref | State | Evidence |
|---|---|---|---|
| `/shared:shapes` (list valid shapes) | UX-4 | dropped 2026-10-07 | no such command, by decision; an unknown `--type` lists the valid shapes instead (STORY-001) |
| `/app:release` (coordinated release across an app) | C4, P2 | not built | PRD marks it deferred |
| Web security agent extensions | E3, P2 | not built | PRD marks it deferred; `shared:security` covers web via `devbox run security` (STORY-018) |
| Cross-shape dependency awareness in the architect (for example a service depending on a shared library) | end-to-end scenario Q6 | open | agent-quality concern, no acceptance test |

## Decisions and open questions

1. Decided 2026-10-07: `new-app` is built (STORY-033); `shapes` is dropped; `/app:release` and the web security extensions stay deferred.
2. Open: this repo has no shape (it is the platform source), so `/svc:plan-feature` cannot run here; `cplat shape` fails with "cannot determine the repo's shape". Proposal: keep ADR + PR for platform changes and add a `STORY-0NN` with acceptance criteria to this file before any non-trivial change.
