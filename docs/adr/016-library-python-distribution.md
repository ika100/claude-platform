# ADR-016: `library-python` distribution — git+https via `uv`

**Status:** Accepted
**Date:** 2026-05-22

## Context

The `library-python` shape exists and publishes its own Copier-templated repo, but the **consumption** story for services that depend on a library was never formalized. PRD §4 says libraries are "publishable to a private index" without specifying which.

Real options for an `ika100`-org setup:
1. `uv add git+https://github.com/ika100/<lib>@v1.2.3` with `GITHUB_TOKEN` auth.
2. GitHub Pages-hosted simple PyPI index (publish wheels to a `gh-pages` branch).
3. Third-party private index (Gemfury, JFrog, self-hosted devpi).
4. GitHub Packages PyPI — **not available** in 2026; GitHub Packages supports npm, Maven, NuGet, RubyGems, and OCI, but not PyPI.

## Decision

**Services consume `library-python` packages via `uv add git+https://github.com/<org>/<lib>@v<tag>` with `GITHUB_TOKEN` authentication.**

### Mechanics

- The library is a private GitHub repo. Its `/svc:release` flow (`svc` plugin's release agent, per [ADR-012](012-per-plugin-release-agent.md)) bumps `pyproject.toml`, writes CHANGELOG, and pushes a `v<semver>` tag.
- Consuming service repos add the library to `pyproject.toml`:
  ```toml
  [project]
  dependencies = [
      "taskboard-models @ git+https://github.com/ika100/taskboard-models@v1.0.0",
  ]
  ```
- CI authenticates with `GITHUB_TOKEN` (auto-injected by GitHub Actions). Local development uses a personal access token via `~/.netrc` or a `git credential` helper.
- `uv lock` resolves the git URL to a specific commit, giving reproducible installs.

### Bumping a library

- Service repos update the tag in `pyproject.toml`, run `devbox run -- uv sync`, commit the new lockfile.
- The `svc` plugin's `coder` agent (when handed a multi-repo plan from [ADR-011](011-multi-repo-plan-format.md) that names a library bump) does this edit and re-sync.

## Rationale

- **Zero infrastructure.** No registry to host, no auth system to administer. Works today with the tools already in the platform.
- **Fully GitHub-native.** Aligns with the marketplace + GHCR posture; one auth model (`GITHUB_TOKEN`) covers everything.
- **Reproducible.** `uv lock` pins to a commit sha, so the same install resolves identically across CI, dev, and prod.
- **Trade-off accepted: slower than a wheel registry.** A git+https install clones the repo each time (cached on subsequent installs). For libraries that ship one wheel per release, GitHub Pages or a third-party index would be marginally faster — but the speed difference is irrelevant at the fleet's scale. Revisit if a library ever ships > 50MB of compiled extensions.

## Consequences

- The `library-python` Copier template includes a `README.md` snippet showing the install line for consumers.
- The `service-python` Copier template's example `pyproject.toml` shows how to declare a library dependency by git URL (commented out as a hint).
- The `coder` agent prompt (svc plugin) is updated to know about this dependency style — it edits `pyproject.toml` directly and never runs `uv add` raw (still gated through `devbox run`).
- A future PR may swap to a GitHub Pages-hosted simple index for faster installs; consumers update their `pyproject.toml` URLs at that time. No platform-level migration needed.

## References

- [platform-vision.md §4](../requirements/platform-vision.md) — `library-python` shape
- [ADR-012](012-per-plugin-release-agent.md) — the release flow that produces library tags
- [end-to-end-scenario.md Q4](../requirements/end-to-end-scenario.md)
