# Shape detection (canonical workflow)

Commands and agents whose behaviour depends on the repo's shape (`service-python`, `library-python`, `web-nextjs`, `gitops-app`, `service-java`, `service-go`, …) resolve it with one call. This file is the canonical description; the algorithm lives in `scripts/detect-shape.sh` of the platform repo ([ADR-008](../../../docs/adr/008-shape-detection.md)), the registry in `shapes.yml` ([ADR-015](../../../docs/adr/015-shape-registry-as-code.md)).

## Procedure

1. Read `_src_path` from `.copier-answers.yml` at the repo root. If its tail is `templates/<shape>`, that is the shape.
2. Otherwise sniff, first match wins: `applications/*/applicationset.yaml` → `gitops-app`; `next.config.*` or `"next"` in `package.json` → `web-nextjs`; `pom.xml` / `build.gradle*` → `service-java`; `go.mod` → `service-go`; `pyproject.toml` + `Dockerfile` → `service-python`; `pyproject.toml` alone → `library-python`.
3. If nothing matches, **ask the user** — never guess.

Copier answers win over sniffing (a Python service with an admin UI is still `service-python`).

## In a consumer repo

Consumer repos do not carry `scripts/`. Resolve with the two steps above directly (reading two or three files), record the result as `$SHAPE`, and look up `plugin` / `deployable` / `library` for it in the platform's `shapes.yml` (`https://raw.githubusercontent.com/ika100/claude-platform/main/shapes.yml`, or the local clone when working inside the platform repo).

## Rule for new shapes

Extend all three together or the PR is rejected: `shapes.yml`, the case/sniff list in `scripts/detect-shape.sh`, and a fixture in `scripts/test-detect-shape.sh`.
