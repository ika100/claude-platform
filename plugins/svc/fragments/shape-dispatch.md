# Shape dispatch (canonical workflow)

Every `svc` orchestration command resolves the repo's **shape** once, in its prelude, and then routes each role to the plugin that owns that shape. This file is the canonical source of truth — keep each command's inline "Shape dispatch" block in sync with it. Registry: `shapes.yml` ([ADR-015](../../../docs/adr/015-shape-registry-as-code.md)); detection: `plugins/shared/fragments/shape-detection.md` ([ADR-008](../../../docs/adr/008-shape-detection.md)).

## Resolve

1. Detect the shape per `plugins/shared/fragments/shape-detection.md` → `$SHAPE`. If undetectable, ask the user once.
2. Look up `$SHAPE` in `shapes.yml` → `$SHAPE_PLUGIN` (`plugin`), `$DEPLOYABLE` (`deployable`), `$IS_LIBRARY` (`library`). If the shape's `status` is `planned` and its plugin is not installed, stop and say which plugin to enable.
3. Print `Shape: $SHAPE (plugin: $SHAPE_PLUGIN)`.

## Route

| Role | Subagent | Notes |
|---|---|---|
| product-manager, architect | `svc:<role>` | shape-agnostic; the architect records `shape:` in the plan |
| coder, tester | `$SHAPE_PLUGIN:<role>` | `svc:<role>` for `service-python` / `library-python` |
| deployment, observability | `$SHAPE_PLUGIN:<role>` | skip entirely when `$DEPLOYABLE` is false |
| migrations | `svc:migrations` | `service-python` only |
| release | `$SHAPE_PLUGIN:release` | |
| quality, security | `shared:<role>` | shape-agnostic; they run the repo's `devbox run` recipes |

If a plan names a different `shape:` than the one detected, trust the plan only when the user confirms (cross-repo plans are run per repo).

### `gitops-app` repos

`/svc:build-feature`, `quick-task` and `fix-bug` do not apply to a `gitops-app` repo. Stop and point to `/gitops:compose`, `/gitops:promote`, or `/app:build-feature` for multi-repo work.

## Recipe contract

Orchestrators call only these `devbox run` recipes, which every shape's template provides: `lint`, `lint-fix`, `quality`, `test`, `test-fast`, `security`, `image-build`, `image-scan` (deployable shapes), `deploy-check` (deployable shapes). Never call language tools directly.
