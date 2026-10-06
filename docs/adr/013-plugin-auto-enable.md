# ADR-013: Plugin auto-enable on `/shared:new-service`

**Status:** Accepted
**Date:** 2026-05-22

## Context

When `/shared:new-service <name> --type service-java` creates a new repo, the resulting `.claude/settings.json` must enable the right marketplace plugins so the next Claude Code session has access to the shape's agents. Without auto-enable, every new repo would require a manual `/plugin enable svc-java@ika100-claude` step that's easy to forget — and easy to get wrong (typo, wrong marketplace name).

## Decision

**`/shared:new-service` templates `.claude/settings.json` with the matching plugin enabled.** The plugin set is determined by the shape:

| Shape | Plugins auto-enabled |
|---|---|
| `service-python` | `svc`, `shared` |
| `library-python` | `svc`, `shared` |
| `web-nextjs` | `web`, `shared` |
| `gitops-app` | `gitops`, `shared` |
| `service-java` | `svc-java`, `shared` |
| `service-go` | `svc-go`, `shared` |

`shared` is always enabled. The shape-specific plugin is selected from `shapes.yml` ([ADR-015](015-shape-registry-as-code.md)) `plugin:` field.

### Existing repos (migration flow)

Repos onboarded via the existing `ADOPTING.md` flow (not via `/shared:new-service`) still require explicit `enabledPlugins` edits. Migrators know what they're doing; we don't want auto-magic touching their `settings.json`.

## Rationale

- **Zero-step bootstrap.** A user runs `/shared:new-service my-svc --type service-go` and starts coding immediately — no `/plugin enable` interlude.
- **One source of truth.** Plugin selection comes from `shapes.yml`, not from per-template hand-maintained settings. Adding a shape per [§4.1](../requirements/platform-vision.md#41-adding-a-new-shape-the-extensibility-contract) automatically wires its plugin into bootstrap.
- **Preserves explicit control where it matters.** Adoption flows (which often modify existing `settings.json` blocks) stay explicit; only greenfield repos auto-enable.

## Consequences

- Every Copier template ships a `.claude/settings.json.jinja` whose `enabledPlugins` block is rendered from the shape's plugin field at bootstrap time.
- The marketplace reference (`extraKnownMarketplaces.ika100-claude`) is also templated, pinned to the platform tag the Copier template was rendered against.
- Disabling auto-enabled plugins is a one-line edit by the consumer — no friction for users who want a different setup.
- SessionStart hooks fire immediately on first Claude Code invocation in the new repo, so `devbox install` / `uv sync` / `pnpm install` are ready before the first agent runs.

## References

- [platform-vision.md §6 A1](../requirements/platform-vision.md)
- [ADR-015](015-shape-registry-as-code.md) — source of the plugin mapping
- [ADOPTING.md](../ADOPTING.md) — the migration flow that does NOT auto-enable
- [end-to-end-scenario.md Q19](../requirements/end-to-end-scenario.md)

## Amendment (implementation, phase 3)

`gitops-app` repos (and every shape whose orchestration is driven by `/svc:*` commands: `web-nextjs`, `service-java`, `service-go`) enable **`svc` in addition to the shape plugin and `shared`**. The `/svc:*` orchestrators and the shape-agnostic `product-manager` / `architect` agents live in `svc` (see `plugins/svc/fragments/shape-dispatch.md`), so a repo without `svc` cannot run `/svc:build-feature`. Resulting sets: `gitops-app` → `gitops, svc, shared`; `web-nextjs` → `web, svc, shared`; `service-java` → `svc-java, svc, shared`; `service-go` → `svc-go, svc, shared`.
