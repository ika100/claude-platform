# ADR-012: Per-plugin release agent

**Status:** Accepted
**Date:** 2026-05-22

## Context

`/svc:release` exists today in the `svc` plugin and handles Python services (bumps `pyproject.toml [project] version`, generates CHANGELOG via Conventional Commits, opens a release PR, tags after merge). When the platform gains `web-nextjs`, `service-java`, and `service-go` shapes, each has a different version source — and the platform must decide whether to extend one shape-aware agent or ship per-plugin agents.

## Decision

**Each plugin ships its own `release` agent.** The `/svc:release` slash command is dispatched per [ADR-008](008-shape-detection.md) shape detection to the matching plugin's release agent.

| Plugin | Version source | Bump tool |
|---|---|---|
| `svc` (Python service & library) | `pyproject.toml` `[project] version` | `uv version` or sed |
| `web` (Next.js) | `package.json` `version` | `pnpm version <bump>` (no git tag — the agent tags separately) |
| `svc-java` | `pom.xml` `<version>` | `mvn versions:set -DnewVersion=<v>` |
| `svc-go` | git tag + ldflags injection (no in-tree version string) | `git tag v<v>` (release agent doesn't edit files — see below) |

Shape detection for the release agent uses the same `.copier-answers.yml` + sniffing fallback established in ADR-008.

### Go is special

Go services conventionally embed the version via build-time ldflags (`-ldflags "-X main.Version=v1.2.3"`) rather than maintaining a version string in code. The `service-go` `release` agent therefore:
- Updates only `CHANGELOG.md` and creates the release PR.
- After merge, pushes the git tag (`v<v>`).
- The Dockerfile's build stage reads the tag via `git describe --tags` (or the CI workflow injects it as a build arg) and passes it to `-ldflags`.

## Rationale

- **Symmetry with `coder` and `tester`.** Those are per-plugin and shape-aware; making `release` an exception just to centralize one agent creates a special case in the orchestration model.
- **One language's evolution doesn't touch others.** If Maven 4 changes how `versions:set` works, only `svc-java/release.md` updates. A shape-aware single agent would risk regressing other languages with each edit.
- **Smaller system prompts.** Each agent's prompt covers exactly one language's release workflow — clearer and cheaper to run than a multi-branch shape-aware prompt.

## CHANGELOG conventions (cross-plugin)

To make `/app:release` (PRD §6 C4, P2) able to aggregate per-component changelogs, all shapes follow the same conventions:

- Conventional Commits in commit messages (already enforced via PR-title check).
- `CHANGELOG.md` in Keep-a-Changelog format, one section per version.
- Semver versioning (`vMAJOR.MINOR.PATCH`).

Per-plugin release agents enforce these conventions; deviations break `/app:release` aggregation.

## Consequences

- Four release agents to maintain instead of one. Cost is real but bounded — release flows change infrequently.
- A future `/app:release` agent (in the `gitops` plugin) aggregates per-component changelogs into an application-level CHANGELOG; its design depends on this ADR.
- Adding a new shape per [§4.1](../requirements/platform-vision.md#41-adding-a-new-shape-the-extensibility-contract) requires shipping a release agent in the new plugin if the shape produces a versioned artifact.

## References

- [platform-vision.md §6 C3, §11.10](../requirements/platform-vision.md)
- [ADR-008](008-shape-detection.md) — shape detection used to dispatch
- [end-to-end-scenario.md Q17](../requirements/end-to-end-scenario.md)
