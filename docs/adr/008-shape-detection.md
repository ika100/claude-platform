# ADR-008: Shape detection — `.copier-answers.yml` with sniffing fallback

**Status:** Accepted
**Date:** 2026-05-22

## Context

Agents and slash commands behave differently per repo shape (today: `service-python`, `library-python`, `web-nextjs`, `gitops-app`, `service-java`, `service-go`; more under the §4.1 extensibility contract). Each invocation needs to detect the current shape. Options: an explicit `.platform-shape` file, parsing `.copier-answers.yml`, or pure file-presence sniffing.

## Decision

**Primary:** read `_src_path` from `.copier-answers.yml` at the repo root. The path tail identifies the shape:

| `_src_path` ends in | Shape |
|---|---|
| `templates/service-python` | `service-python` |
| `templates/library-python` | `library-python` |
| `templates/web-nextjs` | `web-nextjs` |
| `templates/gitops-app` | `gitops-app` |
| `templates/service-java` | `service-java` |
| `templates/service-go` | `service-go` |

**Fallback** (for repos that pre-date Copier adoption — see [ADOPTING.md](../ADOPTING.md) Step 5): sniff in this order, first match wins (most distinctive marker first):

1. `applications/*/applicationset.yaml` → `gitops-app`
2. `next.config.*` or `package.json` containing `"next"` in `dependencies` → `web-nextjs`
3. `build.gradle*` or `pom.xml` at repo root → `service-java`
4. `go.mod` at repo root → `service-go`
5. `pyproject.toml` + `Dockerfile` at repo root → `service-python`
6. `pyproject.toml` without `Dockerfile` → `library-python`

If neither path resolves a shape, agents prompt the user rather than guessing.

**Rule for new shapes:** every shape added under the §4.1 extensibility contract of [platform-vision.md](../requirements/platform-vision.md) MUST extend both tables — the primary mapping (one row) and the fallback sniffing list (one entry, positioned to remain unambiguous against existing markers). Reviewers reject the shape PR otherwise.

## Rationale

- `.copier-answers.yml` already exists in every templated repo and is the source of truth Copier itself uses for updates. Reusing it avoids a parallel `.platform-shape` file that could drift.
- Pure sniffing is brittle: a service-python repo that adds a Next.js admin UI under `admin/` would be misdetected.
- The fallback ordering puts the most distinctive marker (`applicationset.yaml`) first.

## Consequences

- The `shared:new-service` command must ensure `.copier-answers.yml` is committed for every new repo (it already is, but this ADR makes it load-bearing).
- A shared helper (likely a small script in `scripts/` or a snippet duplicated in agent prompts) implements the detection; agents call it rather than re-implementing.
- Migrated repos (per ADOPTING.md Step 5) must write `.copier-answers.yml` for detection to work without falling back to sniffing.
- **Architect plans without an explicit `shape:` field default to `service-python`** for backward compatibility with plans authored before the multi-shape refactor. The orchestrator logs a deprecation notice when applying this default. New plans must be explicit.

## References

- [platform-vision.md §11.7](../requirements/platform-vision.md)
- [ADOPTING.md Step 5](../ADOPTING.md)
