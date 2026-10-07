# Contributing to claude-platform

Thanks for helping. claude-platform is a marketplace of Claude Code plugins (agents and slash commands), Copier templates and a small tested CLI (`cplat`) that together take a product from "new repo" to "running in Kubernetes via GitOps". Changes here reach every repo generated from it, so we favour small, tested, well-explained pull requests.

By contributing you agree that your contribution is licensed under the [Apache License 2.0](LICENSE) (inbound = outbound; no CLA, no DCO sign-off required). Please read the [Code of Conduct](CODE_OF_CONDUCT.md).

## Ways to contribute

- **Report a problem or an idea.** In Claude Code run `/shared:report-issue`: it drafts the issue with your versions and the error output and removes secrets before anything is sent. Or [open an issue](https://github.com/ika100/claude-platform/issues/new/choose) yourself.
- **Ask a question or share a use case** in [Discussions](https://github.com/ika100/claude-platform/discussions).
- **Fix a bug, improve docs, add a template, agent or command** with a pull request (below). For anything larger than a fix, open an issue first so we can agree on the approach.
- **Security issues** go through [SECURITY.md](SECURITY.md), not public issues.

## Repository map

| Path | What lives there |
|---|---|
| `plugins/<name>/` | Claude Code plugins: `agents/*.md`, `commands/*.md`, `.claude-plugin/plugin.json` |
| `.claude-plugin/marketplace.json` | Marketplace catalog; plugin versions must match each `plugin.json` |
| `templates/<shape>/` | Copier templates (`service-python`, `service-java`, `service-go`, `web-nextjs`, `library-python`, `gitops-app`) |
| `shapes.yml` | The shape registry (single source of truth, validated by `scripts/shapes.py`) |
| `scripts/cplat/` | The tested CLI behind the commands (`new-service`, `compose`, `promote`, `addon`, `doctor`, `feedback`, ...) |
| `tests/` | `tests/cplat` (pytest), `tests/e2e` (full cluster test), fixtures |
| `docs/` | Guides, ADRs (`docs/adr`), the changelog |

Read [CLAUDE.md](CLAUDE.md) (conventions and "how to add X" recipes), [docs/AGENTS.md](docs/AGENTS.md) (orchestration model) and [docs/HOW-IT-WORKS.md](docs/HOW-IT-WORKS.md) before changing agents, commands or templates.

## Development setup

You need `git`, [`uv`](https://docs.astral.sh/uv/) and `copier` (`uv tool install copier`). Docker, `kubectl` and `k3d` are only needed for the end-to-end test. [`devbox`](https://www.jetify.com/devbox) provides the same tools in one shell (`devbox shell`).

```bash
git clone https://github.com/ika100/claude-platform && cd claude-platform
```

## Checks to run before you open a PR

```bash
uv run scripts/shapes.py check                                              # registry, templates, plugins, descriptions
python3 scripts/pin-actions.py --check                                      # every GitHub Action pinned by SHA, workflows have permissions
uv run --with pytest --with pyyaml --with ruamel.yaml pytest tests/cplat -q # CLI + render tests (3 tests need the Kyverno CLI and skip without it)
copier copy ./templates/web-nextjs /tmp/try --defaults --trust --skip-tasks --data project_name=try   # render a template you touched
bash tests/e2e/run.sh                                                       # whole stack on a local k3d cluster (Docker, k3d, kubectl)
```

CI runs the same checks plus a smoke test per template (generated repos must pass their own `quality` and `test` recipes). Pull requests that only touch documentation run a reduced set of jobs.

## Pull request rules

- **Conventional Commits** for the PR title (`feat(web): ...`, `fix(cplat): ...`, `docs: ...`); the title is checked and becomes the squash-commit message. Use branch names like `feat/...`, `fix/...`, `docs/...`.
- **One logical change per PR**, with tests. Behaviour in `scripts/cplat` needs a test in `tests/cplat`; a template change needs the template's own tests to pass when rendered.
- **Plugins**: when you change anything under `plugins/<name>/`, bump the version in both `plugins/<name>/.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json` (semver: patch for fixes, minor for additions, major for breaking changes).
- **Keep always-on text small.** Agent and command `description:` front matter is loaded into every session (max 260 characters, enforced). Put detail in the body.
- **Changelog**: add a line under `## [Unreleased]` in `docs/CHANGELOG.md` for anything users can notice.
- **Decisions**: a change that alters how the platform works gets an ADR in `docs/adr/` (next free number; context, decision, consequences, what is not included).
- **GitHub Actions** must be pinned by commit SHA with a `# vX` comment (`python3 scripts/pin-actions.py` does it for you) and every workflow needs top-level `permissions:`.
- **No secrets** in code, tests or fixtures; build token-shaped test strings at runtime so scanners stay quiet.

## Releases

Maintainers release: move `[Unreleased]` under a new `## [x.y.z] - date` heading in `docs/CHANGELOG.md` (the platform version is read from the first such heading), make sure plugin and marketplace versions match, merge, tag `vX.Y.Z` and publish a GitHub release with the changelog section as notes.

## CI cost

CI is free for this public repository, but forks and private copies may pay per minute. The `changes` job skips template smoke tests and the cluster test when a PR does not touch them, superseded runs are cancelled, and Dependabot batches its updates. Run the checks above locally to avoid waiting for CI.
